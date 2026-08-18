---
name: troubleshoot
description: This skill should be used when the user hits "restic errors", "restic backup fails in cron", "restic repository is locked", "restic AccessDenied on R2", "restic wrong password", "restic SignatureDoesNotMatch", or needs to diagnose restic exit codes, S3/R2 errors, locks, repo/index/cache problems, and cron/systemd-only failures.
---

# restic Troubleshooting

Diagnostics and fixes for common restic problems. Start with the exit code and the quick diagnostics, then jump to the matching table.

## Exit codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | success | — |
| 1 | fatal error — **no snapshot created** | real failure; read stderr |
| **3** | some files unreadable but **snapshot WAS created** | **not fatal** — tolerate in scripts (see `backup-script`) |
| 10 | repository does not exist (≥0.17) | check `RESTIC_REPOSITORY`; was it ever `init`ed? |
| 11 | repository is locked | another run in progress, or stale lock → `restic unlock` |
| 12 | wrong password (≥0.17.1) | wrong `RESTIC_PASSWORD_FILE`/value |
| 130 | cancelled (SIGINT/SIGTERM) | re-run |

## Quick diagnostics

```bash
set -a; . /root/.restic/r2.env; set +a
restic cat config           # repo reachable + password correct?
restic snapshots            # can it list?
restic list locks           # any locks held?
echo "$RESTIC_REPOSITORY"   # pointing where you think?
```

## R2 / S3 errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `AccessDenied` | token lacks Object Read & Write, or scope excludes bucket | re-issue R2 token (Object Read & Write, covering the bucket) |
| `AccessDenied` (token looks right) | endpoint `account_id` ≠ token's account | match endpoint account id to the token account |
| `SignatureDoesNotMatch` | **clock skew**, or wrong secret key | sync time (`timedatectl`, ntp); re-check `AWS_SECRET_ACCESS_KEY` |
| signature/region errors | region not set | `AWS_DEFAULT_REGION=auto` (or `-o s3.region=auto`) |
| `NoSuchBucket` | bucket missing | create it in the R2 dashboard |
| bucket lookup / vhost failures | provider needs path-style | `-o s3.bucket-lookup=path` |
| throttling / slow uploads | too many parallel connections | tune `-o s3.connections=<n>` |

## Locks

| Symptom | Cause | Fix |
|---------|-------|-----|
| exit 11 / "repository is locked" | a backup/check is running, or a previous run crashed | if nothing is running: `restic unlock`. **Never unlock during an active run.** |
| backups blocked every night | stale lock from a killed run | add `flock` (cron) and ensure only one scheduler triggers it |
| `unlock` doesn't help | exclusive lock from a live process | find and stop the other restic process first |

## cron / systemd-only failures (works by hand, fails scheduled)

| Symptom | Cause | Fix |
|---------|-------|-----|
| "command not found" (docker/bunzip2/pg_dump) | minimal cron PATH | set absolute `PATH` in the script (the template does) |
| `pg_dump`/`mysqldump` hangs or dumps empty | `docker exec -t`/`-it` — no TTY | use `docker exec -i` only |
| "Fatal: unable to open repo" only when scheduled | `r2.env` not sourced / wrong user | `set -a; . /root/.restic/r2.env; set +a`; run as root |
| nothing runs at all | timer not enabled / wrong tz | `systemctl list-timers`; `systemd-analyze calendar`; check `CRON_TZ` |

## Repository / index / cache health

```bash
restic check                         # structural integrity
restic check --read-data-subset=10%  # sample-verify pack data from R2
restic repair index                  # rebuild a corrupt/missing index (newer restic)
restic rebuild-index                 # older alias
restic repair snapshots              # drop unreadable trees from snapshots
restic cache --cleanup               # clear stale local cache
restic prune                         # repack / reclaim space (after forget)
```

## Compression seems off / repo is v1

`restic cat config` shows `"version":1` → created by an old binary. Upgrade in place:

```bash
restic migrate upgrade_repo_v2       # enables repo format v2 (then RESTIC_COMPRESSION applies)
```

## Performance / space

| Symptom | Cause | Fix |
|---------|-------|-----|
| backup fails: no space | restic cache filled a small root fs | `df -h ~/.cache`; set `RESTIC_CACHE_DIR` to a roomy fs |
| very slow first run | full initial upload | expected; later runs are incremental |
| prune very slow / RAM-heavy | large repo | run `prune` on its own less-frequent timer; ensure enough RAM |

## When to escalate

- `restic check` reports pack/blob errors that `repair` can't fix → restore what you can from a good earlier snapshot; the repo may be partially corrupt (often from external object deletion — see the R2 lifecycle warning in `repository-setup`).
- **Lost password** → unrecoverable. There is no reset; the data is gone. Re-init a new repo and start fresh.

## Gotchas

- **Exit 3 is not a failure** — don't alert on it.
- **Never `unlock` while a real backup runs** — you'd allow a concurrent run to corrupt state.
- **Clock skew breaks S3 signatures** — keep the host time synced.
