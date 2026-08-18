---
name: disaster-recovery
description: This skill should be used when the user asks to "restore from a restic backup", "recover Docker data or a database from restic", "rebuild my server from backups", "do a full or partial restic restore", "my server died how do I get my data back", or needs to restore files, replay database dumps, and stand services back up.
---

# Disaster Recovery

Restore files, volumes, and databases — up to rebuilding on a brand-new server. Recovery is destructive by nature; **stop the affected stack first and restore to a staging path when unsure.**

## Prerequisite (no exceptions)

You need the **encryption password** and the **R2 credentials** (`/root/.restic/password` + `r2.env`, or your off-server copies). Without the password the repository is unreadable — there is no recovery path. If you have them, point restic at the repo:

```bash
set -a; . /root/.restic/r2.env; set +a   # or recreate this file from your off-server copy
restic snapshots                          # confirm access + list restore points
```

## Find what to restore

```bash
restic snapshots                 # list snapshots (note IDs / times)
restic ls latest                 # browse the file tree of a snapshot
restic find '*nginx.conf*'       # locate a path across snapshots
```

## Restore files

```bash
# full restore to a staging dir (safe), then move into place
restic restore latest --target /restore

# partial — just one project / path
restic restore latest --target /restore --include /docker/projectX

# a specific snapshot, with excludes
restic restore <snapshot-id> --target /restore --exclude '*.log'
```

Prefer restoring to `/restore` (staging) and moving files into place after inspection. Restoring directly with `--target /` or `--overwrite` overwrites live files — only do that deliberately, with the stack stopped.

## Restore a database (replay the dump)

Stream the dump straight from the repo into the DB container:

```bash
# Postgres
restic dump latest /var/backups/restic-dumps/db-myproj-pg.sql.gz \
  | zcat | docker exec -i myproj-postgres-1 psql -U <user> -d <db>

# MySQL/MariaDB
restic dump latest /var/backups/restic-dumps/db-myproj-mysql.sql.gz \
  | zcat | docker exec -i myproj-mysql-1 sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"'

# MongoDB
restic dump latest /var/backups/restic-dumps/db-myproj-mongo.archive.gz \
  | docker exec -i myproj-mongo-1 sh -c 'exec mongorestore --archive --gzip --drop \
      -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin'
```

Stop application containers (not the DB) before replaying, so nothing writes mid-restore.

## Rebuild on a new server

1. **Install restic** — follow `setup` (recon + binary).
2. **Recreate credentials** — restore `/root/.restic/password` and `r2.env` from your off-server copies (mode 600).
3. **Confirm access** — `restic snapshots`.
4. **Restore files/volumes** — `restic restore latest --target /` (or staged), placing named-volume data back under `/var/lib/docker/volumes/<name>/_data` (or recreate the volume and restore into it).
5. **Bring up databases** — `docker compose up -d` the DB services, then **replay the dumps** (above).
6. **Start the rest of the stack** and verify health.

## Gotchas

- **No password = no recovery.** This is why `repository-setup` forces an off-server copy.
- **Stop the stack before restoring live data** — restoring under a running app yields a torn, inconsistent state.
- **`--target /` / `--overwrite` is destructive** — restore to staging and move when unsure.
- **Map named-volume `_data` paths correctly** — restoring volume data to the wrong path silently leaves the app with empty storage. Recreate the volume if needed and restore into its `_data`.
- **Verify after** — `diff` a known file, check app health, confirm the DB has rows. A restore you didn't verify is a guess.
- **Anonymous/unnamed volumes** change hash on recreation — restore their data into the new volume's `_data`, or convert to named volumes during rebuild.

## What this skill does NOT cover

- Creating backups → `backup-script`, `scheduling`
- Diagnosing repo errors mid-restore (locks, AccessDenied) → `troubleshoot`
