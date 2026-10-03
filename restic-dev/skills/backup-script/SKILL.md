---
name: backup-script
description: This skill should be used when the user asks to "write the restic backup script", "add database dumps to my backup", "set restic retention/forget policy", "create excludes for restic", or needs the daily script that dumps databases, backs up the discovered paths, tolerates exit code 3, and prunes old snapshots.
---

# restic Backup Script

Assemble the daily script from the discovery artifacts. It dumps databases first, backs up the discovered paths, **tolerates partial-read exit code 3**, then applies retention. A ready-to-adapt template is in [references/restic-backup.sh](references/restic-backup.sh).

## Inputs (from `discover-backup-sources`)

- `/etc/restic/backup-paths.txt` — include paths
- `/etc/restic/excludes.txt` — exclude globs
- `/etc/restic/databases.tsv` — DB containers + dump commands

## The script: `/usr/local/sbin/restic-backup.sh` (mode 700, root)

Logical order — get it right or you back up inconsistent data:

1. **Set a clean environment.** Absolute `PATH` (cron/systemd have a minimal one), then `set -a; . /root/.restic/r2.env; set +a`.
2. **Dump databases first**, into `/var/backups/restic-dumps/` (mode 700). Use `docker exec -i` — **never `-t`/`-it`** (no TTY under cron/systemd → empty/hung dump). See the dump matrix in `discover-backup-sources/references/database-dumps.md`.
3. **Back up**, tolerating exit code 3:
   ```bash
   set +e
   restic backup --tag daily \
     --files-from /etc/restic/backup-paths.txt \
     --exclude-file /etc/restic/excludes.txt \
     --exclude-caches
   rc=$?
   set -e
   # 0 = ok; 3 = partial (unreadable files, or a missing source path on >=0.19) but snapshot created (NOT fatal)
   if [ "$rc" -eq 3 ]; then
     echo "restic backup: exit 3 - partial snapshot created; continuing" >&2
   elif [ "$rc" -ne 0 ]; then
     echo "restic backup failed: $rc" >&2; exit "$rc"
   fi
   ```
4. **Retention** — `forget` is **not** tolerated the same way: on restic ≥ 0.19 its exit 3 means a snapshot could not be removed, a real failure:
   ```bash
   restic forget --tag daily \
     --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune \
     || { frc=$?; echo "restic forget failed: $frc" >&2; exit "$frc"; }
   ```
5. **Log** to `/var/log/restic-backup.log`; optionally ping a healthcheck (see `monitoring`).

## Why `backup` exit code 3 must be tolerated (and `forget` exit 3 must not)

restic returns **3** from `backup` when some source data couldn't be read (permissions, a file vanished mid-run) **or — since 0.19.0 — a source path given on the command line doesn't exist**, **but a snapshot was still created** (earlier versions returned 0 for a missing top-level path). Under `set -e` an unguarded `restic backup` would abort the script before `forget`/`prune` and before the success ping — turning a healthy partial backup into a false failure. Guard it as shown and **log** the 3 so a quietly shrinking backup stays visible. Real failures of `backup`: `1` (no snapshot — includes "every source path is missing"), `10` (repo missing), `11` (locked), `12` (wrong password).

`forget` is different: since 0.19.0 it exits **3** when it fails to remove one or more snapshots (it used to return 0). Do **not** guard that one — the script should fail loudly, and the `/fail` ping (see `monitoring`) should fire. The template turns any non-zero `forget` into a logged failure with the original exit code.

## Retention policy

`--keep-daily 7 --keep-weekly 4 --keep-monthly 6` keeps a week of dailies, a month of weeklies, half a year of monthlies, then `--prune` reclaims space. Adjust to the user's recovery-window and budget. `forget` deletes snapshots; `prune` repacks and frees storage — keep them together (or run `prune` on its own less-frequent timer for very large repos).

## Excludes

Start from the discovery excludes (`/etc/restic/excludes.txt`). `--exclude-caches` additionally skips any directory containing a `CACHEDIR.TAG`. Consider `--exclude-larger-than 5G` to skip stray huge files, and `--one-file-system` **only deliberately** (see gotchas).

Since restic 0.19.0 these excludes (and `--exclude-if-present`, `--exclude-caches`, `--one-file-system`) **are not applied to the root paths themselves** — the ones named on the command line. With `--files-from`, that means the top-level entries of `backup-paths.txt`: an exclude pattern can no longer drop a whole listed root, only content *inside* it. To skip a root, remove it from the list.

## Optional daily-job flags (0.19+)

- `--skip-if-unchanged` — don't create a snapshot identical to its parent (no empty daily snapshots). `--keep-daily 7` counts days *that have a snapshot*, so the retention window stretches over unchanged days.
- `--retry-lock 5m` (global flag, before the subcommand) — wait for a lock held by a concurrent check/prune instead of failing with exit 11; replaces most `flock`/manual `unlock` workarounds.

## Gotchas

- **`-t`/`-it` in `docker exec` under cron/systemd = the #1 silent failure** (no TTY → empty dump). Always `-i` only. Verify dumps are non-empty.
- **`set -e` vs exit 3** — wrap the `restic backup` call as shown, or a partial-but-successful run aborts before pruning and alerting. Do **not** extend that tolerance to `forget` (exit 3 there = snapshots not removed).
- **`--one-file-system` silently skips data on separate mounts** — Docker named volumes under `/var/lib/docker/volumes` and separately-mounted disks get dropped. Use it only when you truly want single-filesystem scope, and cross-check captured paths in `verify-backup`.
- **Staging dir double-count** — `/var/backups/restic-dumps/` must not also be matched by another project's include glob.
- **Permissions** — script `root:root` mode `700`; it reads secret files and runs `docker`/dump tools.
- **Missing paths** — build the include list skipping nonexistent entries (`[ -e "$p" ]`) so a removed project doesn't fail the run. The `--files-from` file should only list paths that exist; regenerate it via `discover-backup-sources` when projects change. On restic ≥ 0.19 a missing path passed as a command-line argument turns the run into exit 3, and an entry in `--files-from` that matches nothing is skipped with a warning — filtering first keeps the exit code meaningful.

## What this skill does NOT cover

- Scheduling the script → `scheduling`
- The first verified run + enabling → `verify-backup`
- Alerting / freshness → `monitoring`
