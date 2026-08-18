# Database dump matrix

How to take a **logical dump** of each database type from inside a Docker container, for inclusion in the daily backup. Never file-copy a live database data directory — the copy can be torn and unrestorable. Always dump.

**Critical for cron/systemd: use `docker exec -i`, never `-t` / `-it`.** There is no TTY under cron or systemd; `-t` makes the dump hang or produce an empty file. This is the single most common silent backup failure.

## Finding credentials

Database containers usually carry their own credentials as env vars. Read them from the container:

```bash
docker exec <container> printenv | grep -Ei 'PASS|USER|DB|MONGO|MYSQL|POSTGRES'
```

Common variables:

| Image | User var | Password var | DB var |
|-------|----------|--------------|--------|
| postgres | `POSTGRES_USER` (default `postgres`) | `POSTGRES_PASSWORD` | `POSTGRES_DB` |
| mysql / mariadb | `MYSQL_USER` / root | `MYSQL_ROOT_PASSWORD` / `MYSQL_PASSWORD` | `MYSQL_DATABASE` |
| mongo | `MONGO_INITDB_ROOT_USERNAME` | `MONGO_INITDB_ROOT_PASSWORD` | — |

Resolve the value at runtime inside the container (so the secret never lands in the script): `sh -c 'exec mysqldump ... -p"$MYSQL_ROOT_PASSWORD"'`.

## PostgreSQL

```bash
# single database (recommended: --clean --if-exists makes restore idempotent)
docker exec -i <c> pg_dump -U "$PGUSER" -d "$PGDATABASE" --clean --if-exists | gzip > db-<project>-pg.sql.gz

# all databases + roles + tablespaces
docker exec -i <c> sh -c 'exec pg_dumpall -U "$POSTGRES_USER"' | gzip > db-<project>-pgall.sql.gz
```

Restore: `restic dump latest /path/db.sql.gz | zcat | docker exec -i <c> psql -U <user> -d <db>`.

## MySQL / MariaDB

```bash
docker exec -i <c> sh -c 'exec mysqldump --single-transaction --routines --triggers \
  --all-databases -uroot -p"$MYSQL_ROOT_PASSWORD"' | gzip > db-<project>-mysql.sql.gz
```

`--single-transaction` gives a consistent snapshot for InnoDB without locking. For per-database: replace `--all-databases` with the DB name.

Restore: `restic dump latest /path/db.sql.gz | zcat | docker exec -i <c> sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"'`.

## MongoDB

```bash
docker exec -i <c> sh -c 'exec mongodump --archive --gzip \
  -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin' > db-<project>-mongo.archive.gz
```

Restore: `restic dump latest /path/db.archive.gz | docker exec -i <c> sh -c 'exec mongorestore --archive --gzip -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --drop'`.

## Redis / KeyDB / Valkey

Most Redis instances are caches → **exclude** the data dir, do not back up. If Redis is a persistence store (it holds the only copy of real data):

```bash
docker exec -i <c> redis-cli SAVE          # flush an RDB snapshot to disk
# then back up the dump.rdb file (its named volume _data path)
```

Flag this for the user — only back up Redis when it is authoritative, not a cache.

## Specialized stores (flag, don't file-copy)

ClickHouse, Elasticsearch/OpenSearch, InfluxDB, Cassandra each need a tool-specific export (`clickhouse-backup`, snapshot API, `influxd backup`, `nodetool snapshot`). Do not snapshot their live data directories with restic. Flag them in the discovery plan for a dedicated approach.

## Where dumps go

The backup script writes dumps to `/var/backups/restic-dumps/` (mode 700), then restic backs up that directory alongside the file paths. Keep the staging dir out of other projects' include globs so it isn't double-counted.
