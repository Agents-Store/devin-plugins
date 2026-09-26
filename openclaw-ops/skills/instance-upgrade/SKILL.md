---
name: instance-upgrade
description: Use when an OpenClaw instance or a fleet of them is being upgraded, or when the question is which version to move to — version drift between instances, what the current stable is, a release channel or a registry dist-tag, an image tag or digest pin, a soak or hold-back window, a gateway that will not start after an update, schedules that started firing several times per tick, a session that expired some time after an update, or what a given release added.
---

# Instance upgrade

An upgrade is R4 on every instance, every time. The state schema migrates **in place**, no
pre-migration backup is taken for you, and re-running a failed migration does not undo it.
Everything below follows from that one sentence.

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
   a channel nobody chose — and there is no machine-readable field saying which line an entry is on.
3. **Comparing registry publish dates with release dates.** They disagree by weeks, and it is not a
   bug: a build is published to the pre-release tag first and later **promoted without a version
   bump**. The publish date is when the artefact was built; only the release date starts the soak clock.

`${CLAUDE_PLUGIN_ROOT}/scripts/versions.py [selector] --json` does this: resolves the channel from
dist-tags, reads the promotion date from the release history, applies the soak gate, reports drift.
Exit 3 = target rejected, 5 = drift across the selection. Never plan around "we upgrade when version
X ships" — release lines die in pre-release without ever being promoted. Plan around a channel plus
a soak window (`policy.update_channel`, `policy.soak_days`).

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
| The runtime's own backup, **verified** | catalogued, restorable content | an upgrade proposed without a backup that **passed** verification is rejected, not warned about (`fleet.upgrade.no-verified-backup`) |
| Stop the gateway, then archive the state directory | **the only real rollback** | the order is deliberate: stopping is what quiesces the writers, so the archive is consistent. Archiving a live state directory produces a copy of a torn moment |

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
   - `doctor` clean, then restart the gateway;
   - `health --json` — the top-level rollup **does not** mean delivery queues are clear; check them;
   - the readiness endpoint **with the bearer** — without it you get a bare negative and no reason list;
   - `doctor --post-upgrade` — the acceptance gate; its exit code is a contract, not a
     success/failure bit: clean, error-level findings, warn-level only (`ocjson.exit_meaning`);
   - lint compared against the preflight baseline, acting on the new findings only.

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

If startup repairs cannot complete safely the gateway **exits instead of reporting healthy**. That
is a failed upgrade, not a flaky start: read the first failed start's log, then restore. **Zero
restart retries** — a restart loop burns the log lines holding the cause and buys a longer backoff.

## There is no rollback — there is recovery

The migration is in place, and a restore path that exists only for a clean target is not a rollback.
Recovery order: stop the gateway → restore the state archive taken while it was stopped → restore
the config snapshot → start on the **pinned previous** artefact → re-verify with the same post-checks
→ only then diagnose. Never migrate forward again from a half-migrated state.

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
