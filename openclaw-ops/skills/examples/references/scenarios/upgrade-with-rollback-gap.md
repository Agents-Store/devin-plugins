# Scenario: upgrade when there is no rollback

The fleet is three versions apart across four instances. Someone asks for "everyone on the latest".
The honest version of that request is: perform an irreversible in-place state-schema migration on four
production instances, where the only rollback anybody actually has is an archive you take yourself.

Everything below exists because of that one sentence.

## Step 0 — refuse the shape of the request

| Asked | Answered |
|---|---|
| "upgrade everything" | a mutation may not use an empty selector or `all` (`fleet.py resolve --mutation`, exit 3) |
| "to latest" | a moving tag is not a target. It is rebuilt on a schedule under the same name, so what runs is not what was reviewed |
| "today" | authentication is repaired **first**. Upgrading a fleet whose credentials are broken makes an upgrade regression indistinguishable from yesterday's failure |

`legacy-one` is refused with its reason printed — a different deployment shape is a migration project.
`delta` is a zombie: triaged before it is upgraded, never during.

## Step 1 — resolve the target, and refuse two of the three obvious answers

```
${CLAUDE_PLUGIN_ROOT}/scripts/versions.py --table
```

Dist-tags say where the channel points **now**. The release entry for that exact version says when it
was promoted, which is what starts the soak clock — the registry publish date is weeks earlier,
because a build lands on a pre-release tag first and is promoted later without a version bump.

The soak gate accepts the target only if it was promoted at least the configured number of days ago
**and** no correction release followed on the same line. Exit 3 is a rejected target — a rejection is
the gate working, not an obstacle to route around.

Then pin: record the **image digest** for the accepted version (`gate.pin`). Without a recorded
immutable identifier there is no expressible rollback, so the mutation is refused rather than warned
about.

## Step 2 — baseline, so that "new breakage" is a measurable thing

Capture before touching anything: the lint findings, the schedule inventory, the loaded plugins, the
config, the credential state.

Only **new** findings block the upgrade. On a fleet that already carries findings, an
any-finding-blocks rule means nothing ever upgrades, and the rule gets disabled — a gate people route
around is worse than no gate (`fleet.upgrade.new-lint-findings`).

## Step 3 — the backup, and the honest ROLLBACK line

| Layer | Protects | Note |
|---|---|---|
| config snapshot outside the `.bak` ring | the human's own last-known-good | four automatic edits evict the ring |
| the runtime's own backup, **verified** | catalogued content | verification must have **passed**; an unverified backup rejects the upgrade (`fleet.upgrade.no-verified-backup`, red line `upgrade-without-verified-backup`) |
| stop the gateway, **then** archive the state directory | the only real rollback | stopping is what quiesces the writers; archiving a live state directory copies a torn moment |

The `ROLLBACK` block of the plan must be an **executable command**, not a description — a validator
rejects prose (`gate.Plan.validate`). Here it reads: stop the gateway, restore the archive into a
clean state directory, start the pinned digest. And it carries the cost out loud, because that is the
gap in the title:

- the schema migration is in place, with no pre-migration backup taken for you;
- restore works into a **clean** target, not over a half-migrated one;
- everything written between the archive and the failure is gone.

That is what makes this R4: `--yes` plus a typed confirmation naming the instance
(`gate.confirm_phrase`), in a turn after the plan was shown.

## Step 4 — waves, canary first

```
/openclaw-ops:update beta --to <pinned>            # dry-run, eight blocks
/openclaw-ops:update beta --to <pinned> --yes      # a later turn
```

Order: canary → soak → low-traffic standard instances → the reference → `gamma` in its own window,
because it carries the revenue-bearing schedule. Direction is good-to-changed, so the batch is
**fail-fast**: a failure on the third of four cloned instances is systemic, and a half-upgraded fleet
is described by no document (`gate.batch_policy`).

## Step 5 — post-upgrade, where the traps live

| Check | Trap it catches |
|---|---|
| version and the running **digest** | you upgraded the tag, not the artefact |
| the readiness endpoint **with the bearer** | without it the answer is a bare negative with no list of what failed |
| the health document | a top-level success does **not** mean every delivery queue is clear (`fleet.liveness.queue-backlog`) |
| the post-upgrade lint | any error-level entry exits non-zero — that is the contract |
| schedule inventory vs the baseline | the upgrade **duplicates schedules**: copies arrive enabled, fire two or three times per tick, and lose their agent binding. Dedupe by keeping, in each `(name, schedule)` group, the row whose agent binding is non-empty (`fleet.cron.duplicates-after-upgrade`). Extra care where the money schedule lives |
| the runtime override on each model entry | config migration silently rewrites a CLI-backed primary into a provider reference and drops the override. Nothing fails now; a session-expired error arrives later. Restore it from the snapshot (`fleet.model.primary-overwritten`) |

**A gateway that stays stopped after the upgrade is the design, not a fault.** If startup repairs
cannot complete safely it exits instead of reporting healthy. Retry budget is zero
(`fleet.upgrade.gateway-stopped`): do not restart in a loop — that spins the backoff and overwrites
the log lines holding the cause. One failure means the restore path, and only the restore path.

## Step 6 — the wave gate

Continue to the next wave only when the upgraded instances have run at least one full scheduled cycle:
lint delta clean against the baseline, schedule count equal to the baseline, no new fallback burn, and
the log moving. "It came up" is not a wave gate.

## What this scenario is not allowed to do

- Pin a channel-named tag "because it is the stable one". Moving tags are rebuilt under the same name.
- Take the archive without stopping the gateway first, to save a minute of downtime. That yields an
  archive of a torn moment, which is worse than no archive, because it will be trusted.
- Treat a rejected soak gate as a reason to pass an override.
- Upgrade the reference first. It is the shape everything else is compared against; the canary exists
  precisely so that the comparison survives.
