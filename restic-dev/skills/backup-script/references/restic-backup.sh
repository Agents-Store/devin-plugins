#!/usr/bin/env bash
#
# /usr/local/sbin/restic-backup.sh  (mode 700, root:root)
# Daily restic backup: dump databases -> back up discovered paths -> retention.
# Template from the restic-dev plugin. Edit the DATABASES section for your stack.
#
set -euo pipefail

# --- environment -----------------------------------------------------------
# cron/systemd have a minimal PATH; set an explicit one so docker/bunzip2/pg_dump resolve.
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# load repository + credentials (RESTIC_REPOSITORY, AWS_*, RESTIC_PASSWORD_FILE, ...)
set -a; . /root/.restic/r2.env; set +a

LOG=/var/log/restic-backup.log
exec >>"$LOG" 2>&1
echo "=== restic-backup $(date -Is) ==="

DUMPDIR=/var/backups/restic-dumps
install -d -m700 "$DUMPDIR"

# --- 1) DATABASE DUMPS -----------------------------------------------------
# Logical dumps only — never file-copy a live DB data dir.
# IMPORTANT: docker exec -i (NEVER -t / -it) — no TTY under cron/systemd.
# Add one block per database found by discover-backup-sources. Postgres example:
#
# if docker ps --format '{{.Names}}' | grep -qx 'myproj-postgres-1'; then
#   docker exec -i myproj-postgres-1 \
#     pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
#     | gzip > "$DUMPDIR/db-myproj-pg.sql.gz"
# fi
#
# See discover-backup-sources/references/database-dumps.md for mysql/mongo/redis.

# --- 2) BACK UP ------------------------------------------------------------
# Filter the include list down to paths that currently exist, so a removed
# project does not fail the whole run.
PATHS_SRC=/etc/restic/backup-paths.txt
PATHS_LIVE=$(mktemp)
trap 'rm -f "$PATHS_LIVE"' EXIT
if [ -f "$PATHS_SRC" ]; then
  while IFS= read -r p; do
    [ -z "$p" ] && continue
    case "$p" in \#*) continue;; esac
    [ -e "$p" ] && printf '%s\n' "$p" >>"$PATHS_LIVE"
  done < "$PATHS_SRC"
fi
# always include the DB dumps
printf '%s\n' "$DUMPDIR" >>"$PATHS_LIVE"

set +e
restic backup --tag daily \
  --files-from "$PATHS_LIVE" \
  --exclude-file /etc/restic/excludes.txt \
  --exclude-caches
rc=$?
set -e
# 0 = success, 3 = some files unreadable but a snapshot WAS created (not fatal).
if [ "$rc" -ne 0 ] && [ "$rc" -ne 3 ]; then
  echo "restic backup FAILED with exit code $rc" >&2
  exit "$rc"
fi

# --- 3) RETENTION ----------------------------------------------------------
restic forget --tag daily \
  --keep-daily 7 --keep-weekly 4 --keep-monthly 6 \
  --prune

echo "=== restic-backup done (rc=$rc) $(date -Is) ==="

# --- 4) OPTIONAL: healthcheck ping (see the monitoring skill) ---------------
# curl -fsS -m10 --retry 5 "https://hc-ping.com/<your-uuid>" >/dev/null || true
