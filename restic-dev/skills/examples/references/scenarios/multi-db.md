# Scenario: multi-database stack

One server runs several database engines at once — Postgres, MySQL/MariaDB, MongoDB, and a Redis used purely as a cache. The discovery and script handle all of them in a single nightly backup.

## Discovery results (`discover-backup-sources`)

| Container | Image | Type | Decision |
|-----------|-------|------|----------|
| `app-postgres-1` | `postgres:16` | Postgres | dump `pg_dump --clean --if-exists`, exclude data dir |
| `shop-mariadb-1` | `mariadb:11` | MariaDB | dump `mysqldump --single-transaction`, exclude data dir |
| `cms-mongo-1` | `mongo:7` | MongoDB | dump `mongodump --archive --gzip`, exclude data dir |
| `app-redis-1` | `redis:7` | Redis | **cache → exclude entirely** (FLAG: confirm not a persistence store) |

Non-DB app data (bind mounts + named volumes) goes into `/etc/restic/backup-paths.txt`; every DB data dir is added to `/etc/restic/excludes.txt`.

## Dump section of `/usr/local/sbin/restic-backup.sh`

```bash
# Postgres
if docker ps --format '{{.Names}}' | grep -qx 'app-postgres-1'; then
  docker exec -i app-postgres-1 \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
    | gzip > "$DUMPDIR/db-app-pg.sql.gz"
fi

# MariaDB (password resolved INSIDE the container; never lands in this script)
if docker ps --format '{{.Names}}' | grep -qx 'shop-mariadb-1'; then
  docker exec -i shop-mariadb-1 sh -c \
    'exec mysqldump --single-transaction --routines --triggers --all-databases -uroot -p"$MARIADB_ROOT_PASSWORD"' \
    | gzip > "$DUMPDIR/db-shop-mysql.sql.gz"
fi

# MongoDB
if docker ps --format '{{.Names}}' | grep -qx 'cms-mongo-1'; then
  docker exec -i cms-mongo-1 sh -c \
    'exec mongodump --archive --gzip -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin' \
    > "$DUMPDIR/db-cms-mongo.archive.gz"
fi

# Redis: cache only — NOT dumped, data dir excluded.
```

All use `docker exec -i` (never `-t`). The rest of the script (paths, exit-3 tolerance, retention) is unchanged.

## Verify each dump (`verify-backup`)

Don't trust an exit code — look at each dump:

```bash
set -a; . /root/.restic/r2.env; set +a
restic dump latest /var/backups/restic-dumps/db-app-pg.sql.gz   | zcat | head
restic dump latest /var/backups/restic-dumps/db-shop-mysql.sql.gz | zcat | head
restic dump latest /var/backups/restic-dumps/db-cms-mongo.archive.gz | gzip -dc | head -c 64 | xxd | head
```

Each should contain real SQL / archive bytes, not an empty stream (the classic `-t` mistake).

## Gotchas

- **Resolve DB passwords inside the container** (`sh -c 'exec mysqldump ... -p"$VAR"'`) so secrets never land in the script or process list on the host.
- **Redis as cache → exclude**; only dump it if it's the authoritative store (then `redis-cli SAVE` + back up the rdb).
- **One staging dir** (`/var/backups/restic-dumps/`) for all dumps; make sure it isn't matched by another include glob.
- **Stop the right things on restore** — replay each dump into its own container; stop apps, not the DBs, during replay.
