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
   # 0 = ok, 3 = some files unreadable but snapshot created (NOT fatal)
   if [ "$rc" -ne 0 ] && [ "$rc" -ne 3 ]; then
     echo "restic backup failed: $rc" >&2; exit "$rc"
   fi
   ```
4. **Retention:**
   ```bash
   restic forget --tag daily \
     --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
   ```
5. **Log** to `/var/log/restic-backup.log`; optionally ping a healthcheck (see `monitoring`).

## Why exit code 3 must be tolerated

restic returns **3** when some source files couldn't be read (permissions, a file vanished mid-run) **but a snapshot was still created**. Under `set -e` an unguarded `restic backup` would abort the script before `forget`/`prune` and before the success ping — turning a healthy partial backup into a false failure. Guard it as shown. Only `1` (no snapshot), `10` (repo missing), `11` (locked), `12` (wrong password) are real failures.

## Retention policy

`--keep-daily 7 --keep-weekly 4 --keep-monthly 6` keeps a week of dailies, a month of weeklies, half a year of monthlies, then `--prune` reclaims space. Adjust to the user's recovery-window and budget. `forget` deletes snapshots; `prune` repacks and frees storage — keep them together (or run `prune` on its own less-frequent timer for very large repos).

## Excludes

Start from the discovery excludes (`/etc/restic/excludes.txt`). `--exclude-caches` additionally skips any directory containing a `CACHEDIR.TAG`. Consider `--exclude-larger-than 5G` to skip stray huge files, and `--one-file-system` **only deliberately** (see gotchas).

## Gotchas

- **`-t`/`-it` in `docker exec` under cron/systemd = the #1 silent failure** (no TTY → empty dump). Always `-i` only. Verify dumps are non-empty.
- **`set -e` vs exit 3** — wrap the `restic backup` call as shown, or a partial-but-successful run aborts before pruning and alerting.
- **`--one-file-system` silently skips data on separate mounts** — Docker named volumes under `/var/lib/docker/volumes` and separately-mounted disks get dropped. Use it only when you truly want single-filesystem scope, and cross-check captured paths in `verify-backup`.
- **Staging dir double-count** — `/var/backups/restic-dumps/` must not also be matched by another project's include glob.
- **Permissions** — script `root:root` mode `700`; it reads secret files and runs `docker`/dump tools.
- **Missing paths** — build the include list skipping nonexistent entries (`[ -e "$p" ]`) so a removed project doesn't fail the run. The `--files-from` file should only list paths that exist; regenerate it via `discover-backup-sources` when projects change.

## What this skill does NOT cover

- Scheduling the script → `scheduling`
- The first verified run + enabling → `verify-backup`
- Alerting / freshness → `monitoring`
