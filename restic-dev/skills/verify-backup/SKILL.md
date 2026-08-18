---
name: verify-backup
description: This skill should be used when the user asks to "verify my restic backup works", "test a restic restore", "check restic snapshots and integrity", "validate backups before enabling the schedule", or needs to run the first backup, confirm snapshots, run restic check, test-restore, then enable the timer.
---

# Verify the Backup (the enable gate)

A backup you have never restored is not a backup. Run the first backup by hand, confirm it, prove a restore works, **then** enable the schedule. This is the gate `scheduling` depends on.

## Step 1 — First run

```bash
# (optional) preview what would be captured, without writing a snapshot:
#   set -a; . /root/.restic/r2.env; set +a
#   restic backup --dry-run -v --files-from /etc/restic/backup-paths.txt --exclude-file /etc/restic/excludes.txt
/usr/local/sbin/restic-backup.sh   # the real first run (slowest — full upload)
```

The first run uploads everything and is the slowest; later runs are incremental (restic deduplicates).

## Step 2 — Confirm the snapshot

```bash
set -a; . /root/.restic/r2.env; set +a
restic snapshots                 # a new snapshot exists; paths + time look right
restic stats latest              # size is plausible for what you intended
```

Cross-check the captured paths against the `discover-backup-sources` plan — confirm the **right** directories and the DB dumps were included, and nothing huge/regenerable slipped in.

## Step 3 — Integrity check

```bash
restic check                     # verifies repository structure + metadata
restic check --read-data-subset=5%   # also downloads & verifies 5% of pack data from R2
```

`check` validates structure for free; `--read-data-subset` actually reads data back from R2 to catch storage-side corruption without the cost of a full `--read-data`.

## Step 4 — Test restore + diff (the real proof)

```bash
mkdir -p /tmp/restic-verify
restic restore latest --target /tmp/restic-verify --include /usr/local/sbin/restic-backup.sh
diff /tmp/restic-verify/usr/local/sbin/restic-backup.sh /usr/local/sbin/restic-backup.sh \
  && echo "RESTORE OK"
rm -rf /tmp/restic-verify
```

Pick a file you know and restore it to a scratch target, then `diff` against the original. For a DB, restore the dump and confirm it is non-empty and parses (e.g. `zcat | head`).

## Step 5 — Enable the schedule (only now)

```bash
systemctl enable --now restic-backup.timer
systemctl list-timers restic-backup.timer    # shows the next run
```

## Verification checklist

- [ ] `restic snapshots` shows a fresh snapshot with the expected paths
- [ ] captured paths match the discovery plan (right data, no regenerable junk)
- [ ] `restic check` reports no errors
- [ ] `restic check --read-data-subset=5%` passes
- [ ] test-restore + `diff` succeeds (and DB dump restores/parses)
- [ ] only after all the above → timer enabled, `list-timers` shows the next run

## Gotchas

- **Verify is the enable gate** — never enable the timer before a clean snapshot + check + test-restore.
- **Restore to scratch, never over the source** — `--target /tmp/...`, then discard.
- **Confirm the right paths** — a backup that ran successfully but captured the wrong directories is still a failure; cross-reference the discovery plan.
- **Check the DB dump is real** — a dump created with `docker exec -t` (wrong) can be empty yet the run still "succeeds." Restore it and look.
- **First-run time/cost** — the initial full upload to R2 can take a while; set expectations. Subsequent runs are incremental.

## What this skill does NOT cover

- Building the script / schedule → `backup-script`, `scheduling`
- Ongoing health (freshness, alerts, periodic check) → `monitoring`
- Real recovery → `disaster-recovery`
