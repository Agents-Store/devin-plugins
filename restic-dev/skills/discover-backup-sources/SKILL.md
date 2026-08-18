---
name: discover-backup-sources
description: This skill should be used when the user asks to "figure out what to back up", "find all my Docker volumes", "discover backup sources", "what should I be backing up on this server", "scan my Docker projects for backup", or points at a projects folder and wants the plugin to inspect every container's mounts and databases and build a concrete backup plan.
---

# Discover Backup Sources

The heart of the plugin. Given a projects folder (e.g. `/docker`), inspect **every** container to produce a concrete, deduplicated **backup plan**: file paths to back up, exclude rules, and databases to dump logically — explicitly catching data that lives **outside** the named folder. Never back up blind.

The output is three on-server files that `backup-script` consumes:
`/etc/restic/backup-paths.txt`, `/etc/restic/excludes.txt`, `/etc/restic/databases.tsv`.

**Always present the plan and FLAGS to the user for confirmation before writing anything.**

## Phase A — Enumerate projects and containers (don't trust the folder alone)

The named folder is a starting point, not the whole truth. Containers often store state elsewhere.

```bash
# every container (running and stopped)
docker ps -a --format '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.State}}'

# per container: compose grouping + where the project actually lives on disk
for c in $(docker ps -aq); do
  printf '%s\t%s\t%s\t%s\n' "$c" \
    "$(docker inspect "$c" --format '{{index .Config.Labels "com.docker.compose.project"}}')" \
    "$(docker inspect "$c" --format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}')" \
    "$(docker inspect "$c" --format '{{.Config.Image}}')"
done

# independently list and size the named folder
ls -la /docker
du -sh /docker/* 2>/dev/null | sort -rh
```

**Union the `working_dir` labels with the folder listing.** Working-dir labels surface projects living outside `/docker` (e.g. `/agents/openclaw/…`, `/opt/…`, `/projects/…`). Group containers by compose project; keep non-compose containers individually.

## Phase B — Map where the data really lives (mounts)

```bash
docker inspect <container> --format \
  '{{range .Mounts}}{{.Type}}|{{.Name}}|{{.Source}}|{{.Destination}}|{{.RW}}{{"\n"}}{{end}}'
```

Classify each mount:

| `.Type` | Meaning | Backup candidate |
|---------|---------|------------------|
| `bind` | `.Source` is a host path | back up `.Source` |
| `volume` (named) | data at `/var/lib/docker/volumes/<name>/_data` | back up that `_data` path |
| `volume` (anonymous, hash name, no compose label) | often a **forgotten DB data dir** | include **and FLAG** |
| `tmpfs` | ephemeral RAM | skip |

## Phase C — Measure

```bash
du -sh <each bind source> <each volume _data> 2>/dev/null | sort -rh
du -sh /var/lib/docker/volumes/*/_data 2>/dev/null | sort -rh
```

Sizes drive exclusion decisions and set expectations for the first upload.

## Phase D — Classify and build excludes

Regenerable junk wastes storage and upload time. Build exclude globs:

```
**/node_modules
**/.cache
**/.npm
**/.npm-global
**/.venv
**/__pycache__
**/.mypy_cache
**/.pytest_cache
**/.ruff_cache
**/.cargo
**/.rustup
**/.gradle
**/.m2
**/target
**/dist
**/.next
**/.nuxt
**/.playwright-mcp
linuxbrew
tmp/
lost+found
```

Always hard-exclude Docker internals (huge, regenerable, not data):
`/var/lib/docker/overlay2`, `/var/lib/docker/image`, `/var/lib/docker/containers`, `/var/lib/docker/buildkit`.

## Phase E — Detect databases and choose a dump command

Match the image substring → database type → dump command. Get credentials from the container's own env (`docker exec <c> printenv <VAR>`). Full command matrix in [references/database-dumps.md](references/database-dumps.md).

| Image matches | Type | Strategy |
|---------------|------|----------|
| `postgres`, `postgis`, `timescale`, `pgvector`, `supabase/postgres` | Postgres | `pg_dump --clean --if-exists` (or `pg_dumpall`) |
| `mysql`, `mariadb`, `percona` | MySQL/MariaDB | `mysqldump --single-transaction --routines --triggers` |
| `mongo` | MongoDB | `mongodump --archive --gzip` |
| `redis`, `keydb`, `valkey` | Redis | usually cache → **exclude**; if persistent, `SAVE` then back up the rdb (FLAG) |
| `clickhouse`, `elasticsearch`, `influxdb`, `cassandra` | specialized | **FLAG** — needs a tool-specific export; do not file-copy live data |

For each detected DB: **remove its data dir from the file list and add it to the excludes**, record the dump command + credential source + output filename `db-<project>-<service>.sql.gz`, and confirm the container is **running** (a stopped DB cannot be dumped live → fall back to a file copy while it stays stopped, with a warning).

## Bind vs named-volume strategy

| Mount | Strategy | Why |
|-------|----------|-----|
| bind, non-DB | back up `.Source` | plain host files |
| named volume, non-DB | back up `/var/lib/docker/volumes/<name>/_data` | persistent app data |
| **any DB** (bind or volume) | **logical dump; exclude the data dir** | a live DB file copy is inconsistent / unrestorable |
| tmpfs | skip | ephemeral |
| anonymous volume | inspect → DB? dump : file-back + FLAG | often a forgotten DB data dir |

## Dedupe (path subsumption)

Normalize every path to absolute, strip the trailing `/`, sort shortest-first, then drop any path equal to or nested under an already-kept path (`p == K` or `p` starts with `K + "/"`). A project `working_dir` thus subsumes its child bind mounts — excludes handle the junk inside. Volumes under `/var/lib/docker/volumes` are siblings, not children, so they survive separately. **Never collapse upward into `/var/lib/docker`** (that would pull in overlay2).

## Output artifact (the contract)

Write three files (config, not secrets → `/etc/restic/`, mode 644):

- `/etc/restic/backup-paths.txt` — one include path per line → `restic backup --files-from`
- `/etc/restic/excludes.txt` — one exclude glob per line → `--exclude-file`
- `/etc/restic/databases.tsv` — `project · service · type · container · running · creds_env · dump_cmd · excluded_data_path`

Lead the plan with the **recon summary** (arch/init/tz from `setup`) and a **FLAGS** block listing anything that needs a human decision:

- anonymous volumes (possible hidden DB data)
- stopped DB containers (cannot dump live)
- redis/keydb treated as cache (excluded) — confirm it is not a persistence store
- specialized stores (clickhouse/elasticsearch/influxdb) needing a custom export

Get explicit confirmation, then hand off to `backup-script`.

## Gotchas

- **Real data is often outside the named folder** — always union `working_dir` labels and inspect mounts; folder listing alone misses it.
- **DBs must be dumped, never file-copied** — a snapshot of a live data dir can be torn and unrestorable.
- **Anonymous volumes hide DB data** — flag and inspect them; don't silently skip.
- **Don't collapse paths up into `/var/lib/docker`** — you'd back up overlay2 (tens of GB of regenerable layers).
- **Stopped containers** still have mounts and matter — `docker ps -a`, not just `docker ps`. But a stopped DB can't be dumped live.
