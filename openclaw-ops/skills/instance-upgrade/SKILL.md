---
name: instance-upgrade
description: Use when an OpenClaw instance or a fleet of them is being upgraded, or when the question is which version to move to — version drift between instances, what the current stable is, a release channel or a registry dist-tag, an image tag or digest pin, a soak or hold-back window, a gateway that will not start after an update, schedules that started firing several times per tick, a session that expired some time after an update, or what a given release added.
---

# Instance upgrade

An upgrade is R4 on every instance, every time. The state schema migrates **in place**. Doctor does
save verified copies of the databases beside the originals before it advances a schema
(`<database>.pre-startup-migration-<id>.bak`, one group per run), and a package update keeps its
pre-migration snapshots until activation is verified — but **a package rollback cannot undo migrated
state**, an older release cannot open a newer schema, and full-state recovery needs a backup you took
yourself. Re-running a failed migration does not undo it either. Everything below follows from that.

## Precondition, not a step

**Repair authentication before upgrading anything.** On a fleet whose credentials are already
broken, the upgrade carries the breakage across and makes the two indistinguishable — afterwards
nobody can tell an upgrade regression from yesterday's failure. Same reason a zombie instance is
triaged first and a legacy-layout instance is refused outright: that one is a migration project,
not an upgrade.

## Choosing the target

The channel resolves from **registry dist-tags and nothing else**. A dist-tag is the only artefact
that states which build a channel points at right now. Every other signal is a reconstruction, and
the three obvious reconstructions each hand back a different, wrong number — worked through in
`references/channels-and-tags.md`:

1. **Highest version, skipping pre-releases.** Correction releases carry a numeric hyphen suffix,
   version ordering reads any hyphen suffix as a pre-release, so this filters out exactly the
   releases that exist to fix the one it keeps. You get the broken original and call it newest.
2. **Newest non-prerelease release entry, sorted by date.** The trailing extended channel is also
   published as a non-prerelease, roughly a month behind. This silently rolls the fleet back onto
   a channel nobody chose. No release *field* says which line an entry is on — the monthly patch
   number does: the high patch numbers are reserved for the extended line. `versions.py` reads that
   rule (`line` in its output) and refuses a build from the wrong line for the channel in use.
3. **Comparing registry publish dates with release dates.** They disagree by weeks, and it is not a
   bug: a build is published to the pre-release tag first and later **promoted without a version
   bump**. The publish date is when the artefact was built; only the release date starts the soak clock.

`${CLAUDE_PLUGIN_ROOT}/scripts/versions.py [selector] --json` does this: resolves the channel from
dist-tags, reads the promotion date from the release history, applies the soak gate, reports drift.
Exit 3 = target rejected, 5 = drift across the selection. Never plan around "we upgrade when version
X ships" — release lines die in pre-release without ever being promoted. Plan around a channel plus
a soak window (`policy.update_channel`, `policy.soak_days`).

How the four channel names resolve is not a plain lookup — `references/channels-and-tags.md` has the
detail: `beta` is the **newer** of the beta and latest tags (an old beta never replaces a newer
stable), `extended-stable` is package-only, foreground-only and fails closed rather than falling back,
and `dev` is the moving head of the git main branch — no package, never a production target.

### An old installation crosses the bridge first

An installation older than the cut-off upstream states cannot go straight to the current line: Doctor
stops before rewriting config that still carries retired keys and sends it through **one bridge
release** — the first hop imports the retired state files and rewrites the retired keys, the second
installs the current release. `versions.py` says so up front: the verdict is `bridge-required`
(exit 3), with the bridge version and the instances that need it in `gate.bridge`. The cut-off and
the bridge version are its two version constants, copied from the upstream updating guide
("Upgrading very old versions"); re-read that section when either looks wrong. Rules of the hop:

- take the **pre-update backup first** — an older release cannot open a schema a newer one already
  migrated, so a bridge attempted *after* a premature upgrade needs a backup from before it;
- on the bridge: install it, run `doctor --fix`, and **confirm what it imported** (tasks, flows,
  plugin state, channel state for the channels that are enabled) before moving on; resolve every
  failed or conflicting import first;
- keep the same owning account, installation prefix, profile and state paths throughout, and use a
  supported Node (for an image deployment the Node that matters is the image's, not the host's);
- then gate the real target again — the second hop is an ordinary upgrade with its own soak gate.

## Tags and pin-before-mutate

- Moving tags — channel names, branch names — are **rebuilt on a schedule under the same name**.
  What runs is not what was reviewed, and a rollback target pinned to one has already changed.
- Only **plain version tags and dated tags are immutable**. Each channel refresh publishes a dated tag.
- **Pin before mutate**: nothing that replaces an executable artefact runs until an immutable
  identifier is recorded — digest, plain version, or commit sha (`gate.pin`, `gate.require_pin`,
  `gate.is_moving_tag`). No pin, no rollback expression, so the mutation is refused, not warned about.

## Backup: three layers, one real rollback

| Layer | What it protects | Notes |
|---|---|---|
| Config snapshot outside the `.bak` ring | the human's own last-known-good, which four automatic edits would evict | `gate.snapshot`; the ring is a courtesy to people, not a plugin mechanism |
| The runtime's own backup, **verified** — `backup create --verify` | a WAL-aware archive of state, config, credentials and agent databases, validated right after it is written | an upgrade proposed without a backup that **passed** verification is rejected, not warned about (`fleet.upgrade.no-verified-backup`). Never copy only the main `.sqlite` of a live database: committed data can still sit in its `-wal`. `backup verify <archive>` re-checks one later; `backup sqlite create` / `list` / `verify` cover a single database |
| Stop the gateway, then archive the state directory **together with the `.bak` group** | **the only real rollback** | the order is deliberate: stopping is what quiesces the writers, so the archive is consistent. Archiving a live state directory produces a copy of a torn moment. Keep the `<database>.pre-startup-migration-<id>.bak` copies Doctor saved with it — a rollback restores matching state as well as the old image |

Every one of these is a **credential artefact**, not a scratch file: current OAuth tokens sit in the
state database in plaintext, so an archive, a snapshot or a tar of the state directory carries working
credentials. Owner-only mode, a private directory, never a shared path, and a stated retention; a
copy that leaves the host is answered by revoking at the source (`security-audit`,
`secrets-infisical`).

## Procedure per instance

1. **Preflight baseline** — lint, schedules, plugins, config, credential status, captured *before*
   the change. Only **new** findings block; a pre-existing finding must never veto every future
   upgrade, or nothing on a fleet like this is ever upgradeable again.
2. **Pin** the target (digest or plain version) and record it in the plan's BACKUP/TARGET blocks.
3. **Backups**, all three layers, verification included.
4. **Apply** the upstream procedure for this deployment shape — confirm its current form through the
   `docs-research` skill, do not recite it from memory. `/openclaw-ops:update <selector> [--to …]`
   builds the plan; `--yes` never in the turn the plan is first shown.
5. **Post-checks**, each answering a different question:
   - version echoed back by the runtime itself, compared with the pin;
   - `doctor` clean, then restart the gateway — **for an image deployment the entrypoint has already
     run `doctor --fix --non-interactive` under exclusive maintenance ownership before the gateway
     started**, so a routine image replacement needs no separate pass; run it by hand only when the
     entrypoint was replaced. For a package install, `openclaw update status` (`--json`) is the ledger
     of the last run and its recorded outcome;
   - `health --json` — the top-level rollup **does not** mean delivery queues are clear; check them;
   - the readiness endpoint **with the bearer** — without it you get a bare negative and no reason list;
   - `doctor --post-upgrade --json` — the acceptance gate; exit 1 means at least one finding with
     `level: "error"`, otherwise 0 — a **warning** (an official plugin on another release cohort than the
     upgraded CLI is one) never changes the code, so read the `{probesRun, findings}` envelope as well
     and follow the plugin update command it names (`ocjson.exit_meaning`);
   - lint compared against the preflight baseline, acting on the new findings only — always with the
     threshold pinned (`doctor --lint --json --severity-min info`), and an exit **2** is a failed run,
     not "warnings only".

## Two traps to check on every upgrade

- **Duplicated schedules.** Upgrades multiply schedule entries; the copies stay enabled, fire two or
  three times per tick, and **lose their agent binding**. Dedup rule: group by `(name, schedule)` and
  keep the member with a non-empty binding. Check this first wherever a schedule moves money
  (`fleet.cron.duplicates-after-upgrade`).
- **Silently rewritten primary.** Config migration can rewrite the primary model reference and drop
  the runtime override. Requests keep working until the session behind them expires, so the failure
  arrives *later* and the upgrade "looked fine". Verify the runtime override survived; restore it
  from the snapshot if it did not (`fleet.model.primary-overwritten`).

## A stopped gateway after an upgrade is the design

If startup repairs cannot complete safely the gateway **exits instead of reporting healthy** — with
exit code 78 when required state cannot be migrated safely (conflicting identities, unreadable data,
another writer owning the state, a filesystem without the primitives). That is a failed upgrade, not a
flaky start: read the first failed start's log, then recover. **Zero restart retries** — a restart loop
burns the log lines holding the cause and buys a longer backoff. Never delete the `.bak` group, a lock or
a claim file to silence it: they are the recovery inputs.

The documented way back is the **same image, once, against the same mounted state and config**, with
`doctor --fix` as the command, then a normal start. Cold mode admits `doctor` for exactly this: a read
posture (`--lint`, `--post-upgrade`) runs as is, while `doctor --fix` is an R4 like any other — the
door refuses it as a raw call, and the plan (BACKUP, an executable ROLLBACK, the typed confirmation)
comes first, with the cold run as its APPLY line for the operator.

## An update driven by the one older updater, across a schema bump

The upstream updating guide singles out one older updater release (section "Updating from … across a
schema bump") whose ledger writes outlive the schema change. What happens when it drives an update that
bumps the shared-state schema, and what to do — read the guide for the release in question, do not
recite it:

- **The normal case is deferral, not a fault.** The target applies the migration content but keeps
  publishing the old schema version until every affected update run has been terminal for a few
  minutes (a run that has not moved for much longer counts as abandoned for this purpose only). Doctor
  says so: schema content applied, version publication deferred. The new gateway runs on the migrated
  content in the meantime. Do not kill the run, hand-edit the database or "complete" the bump yourself.
- **`update-schema-bump-unfenced` is the refusal.** It appears when state metadata is missing or backup
  coverage cannot be verified, and it prints the database versions and the recovery instructions. Quote
  them. *Before* the package commit, let the failed update finish restoring the previous package — that
  older updater leaves the gateway **stopped** after a failed post-install verification, which is the
  designed outcome here too (zero restart retries). *After* the package commit the old package backup is
  gone: finish `doctor --fix` with the installed compatible build, then start the gateway.
- **If the compatible package still has to be installed,** it is a manual update from a shell *outside*
  the gateway: stop the gateway, install the exact target named in the refusal with the installation's
  own package manager, run `doctor --fix`, start the gateway — each step only after the previous one
  succeeded. All of it is an R4 with a plan; the refusal text is the source for the target version,
  never this page.
- **Package rollback cannot undo migrated state.** The verified backup taken before the update is what
  would; for a git checkout, a Doctor refusal before state writes prints source recovery commands only
  when the reflog identifies the previous commit unambiguously, and restoring source alone never
  restores state.

## There is no rollback — there is recovery

The migration is in place, and a restore path that exists only for a clean target is not a rollback.
Recovery order: stop the gateway → restore the state archive taken while it was stopped (with its
matching `.bak` group) → restore the config snapshot → start on the **pinned previous** artefact →
re-verify with the same post-checks → only then diagnose. Never migrate forward again from a
half-migrated state.

Upstream's managed path — `openclaw update --tag <good> --dry-run`, then the same without `--dry-run` —
exists for package installs, and only for a target that can still read the current state. A container
deployment has no package owner: there `openclaw update` records a skipped update and the upgrade *is*
the image replacement, so recovery is the order above on the pinned previous image. Whichever path:
set `OPENCLAW_NO_AUTO_UPDATE=1` in the gateway environment during a manual recovery, or the
auto-updater puts the newer release straight back; and verify before retiring anything —
`update cleanup --dry-run` previews what would go, and `update cleanup` itself is an R4 that retires the
migration recovery originals for good.

## Fleet waves

Reference instance first, then a hold; then low-load instances, then a hold; then the loaded ones;
then any revenue-bearing instance alone, in its own window. `gate.canary_barrier` enforces the first
wave, and a good→changed batch is **fail-fast**: the third instance failing in a row of clones is a
systemic fault, and a half-upgraded fleet matches no document and no rollback.

The hold between waves is a **gate, not a timer**. It opens on four observations, all four required:
a full scheduled cycle has completed on the upgraded instances, the lint delta against the preflight
baseline is clean, the schedule count equals the baseline (the duplication trap fires exactly here),
and the log is still moving. A wave released on elapsed time alone carries an undetected regression
into the next group, which is how one bad upgrade becomes a fleet incident.

## Common mistakes

- Treating "the newest release" as the target instead of the dist-tag the configured channel names.
- Pinning a moving tag and believing the deployment is reproducible.
- Upgrading with a backup that was created but never verified, or archived while running.
- Restarting a stopped post-upgrade gateway to "see if it comes back".
- Letting old lint findings block the upgrade, or new ones pass unread.
- Declaring success on the health rollup alone — queues and readiness answer different questions.
- Upgrading before credentials are fixed, then debugging both at once.
