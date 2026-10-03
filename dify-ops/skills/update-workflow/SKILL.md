---
name: update-workflow
description: >
  Git and backup workflow for updating self-hosted Dify — pick the target tag, pre-flight the
  bundled Weaviate migration path, back up volumes with the stack down, merge into dev, handle
  conflicts, pull images, verify, roll back. Use when updating Dify, merging upstream changes,
  handling merge conflicts in Dify, backing up before an update, or switching to a specific Dify
  version/tag. Triggers on "update dify", "pull dify changes", "merge main into dev", "upgrade dify",
  "dify version", "dify backup", "weaviate upgrade".
---

## Branch Model

User maintains two branches:
- **`main`** — tracks upstream `origin/main`
- **`dev`** — local customizations

Updates flow from a **release tag** into `dev`: `git merge <tag>`. `main` is merged only when the user asks for it: its deployment files track development and can drift from the latest release, while the images it pins are the latest released ones.

An official install (`git clone --branch <tag>`) leaves a detached HEAD and no `dev` branch. Create it before merging: `git switch -c dev`.

## Update Order

The order is fixed. Nothing in the working tree or the volumes changes before the backup exists.

1. **Pre-flight** (read-only): git state, Docker Compose version, project name, target tag, Weaviate gate, release notes
2. **Plan** — eight blocks (TARGET, PRECHECK, CHANGE, BACKUP, IMPACT, VALIDATE, ROLLBACK, APPLY), then confirmation
3. **Backup** — copy `docker-compose.yaml` and `.env`, stop the stack, `docker compose down`, archive `volumes/`
4. **Merge** the tag into `dev`, resolve conflicts
5. **Env sync** (see the `env-sync` skill)
6. **Pull and start** — `docker compose pull`, then `docker compose up -d`
7. **Verify**, including a test retrieval

`/dify-ops:update` runs exactly this. The release notes of Dify say the same: back up compose and env, `docker compose down`, archive `volumes/`, only then check out the new tag.

## Pre-flight Checks

Run from DIFY_ROOT (git repo root) before any update:

```bash
git rev-parse --git-dir >/dev/null 2>&1 || echo "ERROR: Not a git repo"
START_BRANCH=$(git branch --show-current)         # empty output = detached HEAD
START_COMMIT=$(git rev-parse HEAD)
DEV_TIP=$(git rev-parse -q --verify refs/heads/dev || echo "$START_COMMIT")   # dev's tip before the merge
echo "Branch: ${START_BRANCH:-detached HEAD}   Commit: $START_COMMIT   dev tip: $DEV_TIP"
git status --short                                # anything listed = dirty tree
docker compose version --short                    # must be >= 2.24.0
```

**Docker Compose >= 2.24.0** is required (`env_file … required: false`).

Record `DEV_TIP` and `START_BRANCH`, not just `HEAD`: the merge happens on `dev`, so a rollback has to put **`dev`** back where it was and then return to the branch the update started on. Resetting `dev` to a `HEAD` captured on `main` would discard the user's customization commits.

**If the working tree is dirty**, ask: (1) commit them, (2) stash them (`git stash` right before the merge, `git stash pop` after verification), (3) abort.

**Project name** — read it from the labels of the running `api` container, not from container names (names miss `api_websocket`, `agent_backend`, `local_sandbox`, `db_mysql` and others):

```bash
docker ps --filter "label=com.docker.compose.service=api" \
  --filter "label=com.docker.compose.project.working_dir=$DOCKER_DIR" \
  --format '{{.Label "com.docker.compose.project"}}'
```

`docker compose ls` lists every project. Without a running stack the project is the directory name (`docker` for `dify/docker`). Export `COMPOSE_PROJECT_NAME` **in the same block** as every `docker compose` call: the Bash tool keeps no shell variables between calls, and without the export `docker compose down` addresses the default project and stops nothing while the real stack keeps running. Always check, after `down` and before archiving, that no container of the stack is left.

## Choosing the Target

Dify tags carry **no `v` prefix** (`1.17.1`); GitHub release titles read `v1.17.1`, so drop a leading `v` the user types.

Default target — the latest **stable** tag, never `rc`, `alpha` or `beta`:

```bash
git fetch origin --tags
git tag --list | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1
```

`main` only when the user passes `main`. To see the stable tags after the running version, and each one's upgrade notes:

```bash
git tag --list | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -10
gh release view <tag> -R langgenius/dify --json body -q .body   # sections: Environment Variable Changes, Database Migrations, Upgrade Guide
```

Read the upgrade notes of **every** release between the running version and the target. Upgrade steps differ per release.

## Weaviate Migration Path (Dify 1.17.1)

From Dify 1.17.1 the bundled Weaviate server moves from `semitechnologies/weaviate:1.27.0` to `cr.weaviate.io/semitechnologies/weaviate:1.39.2` (a different registry). An existing data volume cannot cross 12 minor versions in one step. Pulling and restarting on top of the old volume can **silently and permanently** break vector search.

**The gate** — STOP before any change when all of these hold:

- the running Dify image is older than `1.17.1`
- the target is `1.17.1` or newer (`main` included)
- `VECTOR_STORE=weaviate` (the default when unset)
- `volumes/weaviate` holds data

A fresh install, an external Weaviate server and every other `VECTOR_STORE` are not affected. If the running version cannot be read, treat it as older.

**On STOP** do not merge and do not run `docker compose up -d`. Send the user to the official runbook, <https://docs.dify.ai/en/self-host/deploy/troubleshooting/weaviate-server-migration-path>, which is the source of truth for the image ladder. Its outline:

1. Check the current server version (`/v1/meta`). Below 1.27 start with the Weaviate v4 migration guide of Dify.
2. Stop Dify's request and worker services: `docker compose stop -t 120 nginx api api_websocket worker worker_beat` (omit `api_websocket` if the compose file has none) and keep them stopped until the last rung passes.
3. Record the object count, stop Weaviate with `docker compose stop -t -1 weaviate`, copy `volumes/weaviate` with `cp -a` (ownership preserved). In production prefer Weaviate's own backup module.
4. Step through every minor in order, `1.27` → `1.28` → … → `1.38`, each time the latest patch of that minor from the runbook's table, then exactly the version your `docker-compose.yaml` pins (`1.39.2`) as the last rung. Per rung: edit the `weaviate` image tag, `docker compose stop -t -1 weaviate`, `docker compose up -d weaviate`, wait at least 10 seconds (collections mount 4–9 s after `/v1/meta` answers from 1.31 on), verify version, collection list, object count and cluster synchronization.
5. Revert only the temporary image edit, then continue with the normal update below. Run a test retrieval before returning the stack to service.

Never `docker kill`, `docker rm -f` or a stop that falls back to SIGKILL: Weaviate keeps its vector index in memory and persists it through a commit log, a hard kill leaves it incomplete, and `near_vector` then misses objects without a single log line. Object count, listing and BM25 look healthy. The only repair is re-indexing the knowledge base.

Version check without printing the key:

```bash
cd "$DOCKER_DIR"
KEY=$(grep -m1 '^WEAVIATE_API_KEY=' .env | cut -d= -f2-)      # read, never echo
docker compose exec -T weaviate wget -qO- --header="Authorization: Bearer $KEY" http://localhost:8080/v1/meta \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])"
```

After the runbook, re-run `/dify-ops:update <tag> --weaviate-staged`. Other ways out: update only to a release below 1.17.1, or move to another vector store first.

## Backup

Backup comes **after the plan and before the merge**, with the stack down, so postgres and Weaviate files are consistent.

```bash
cd "$DOCKER_DIR"
umask 077                                       # the archive holds the database and the storage key
export COMPOSE_PROJECT_NAME=<project>           # the project detected above; skip when none is running
BACKUP_DIR="<backup-dir>/$(date +%Y%m%d-%H%M%S)"   # outside the git repository
mkdir -p "$BACKUP_DIR"
cp -p docker-compose.yaml "$BACKUP_DIR/docker-compose.yaml"
[ -f .env ] && cp -p .env "$BACKUP_DIR/.env"    # copied, never printed
docker compose stop -t 120 nginx api worker worker_beat   # add api_websocket when the compose file has it
docker compose stop -t -1 weaviate              # only when VECTOR_STORE=weaviate
docker compose down -t 120                      # never add -v
[ -z "$(docker ps -q --filter "label=com.docker.compose.project.working_dir=$DOCKER_DIR")" ] || { echo "ABORT: stack still running"; exit 1; }
sudo tar -czpf "$BACKUP_DIR/volumes.tgz" -C volumes . && sudo tar -tzf "$BACKUP_DIR/volumes.tgz" >/dev/null && echo "Backup OK"
```

- Volumes are owned by the container users (postgres, root), so the archive needs `sudo` unless you are root. `-p` preserves ownership and permissions.
- No `-v` on `tar`: a listing of thousands of paths is noise, and nothing in the output may carry a secret. Never `cat .env`.
- The real data lives in `volumes/db/data` (postgres), `volumes/redis/data`, `volumes/app/storage`, `volumes/plugin_daemon`, `volumes/weaviate`, `volumes/sandbox`, `volumes/certbot`. Since 1.14.1 an empty `SECRET_KEY` means the API generates a key and keeps it in `volumes/app/storage`: that directory must be in the backup, and the key must not change after start.
- Optional logical dump, taken **before** `down`: `docker compose exec -T db_postgres pg_dumpall -U "$DB_USERNAME" > "$BACKUP_DIR/postgres.sql"`. `pg_dump` of the `dify` database alone misses the plugin database `dify_plugin`. With `DB_TYPE=mysql` use `mysqldump --all-databases` in `db_mysql` instead.
- Save the non-secret state the later steps and the rollback need (`DIFY_ROOT`, `DOCKER_DIR`, `START_BRANCH`, `START_COMMIT`, `DEV_TIP`, `COMPOSE_PROJECT_NAME`) in `$BACKUP_DIR/state.env`; `/dify-ops:update` does this.
- Keep the backup until the new version is verified healthy. It holds secrets: never commit it, never leave it inside `dify/`.

## Merge

```bash
cd $DIFY_ROOT
git switch -c dev 2>/dev/null || git checkout dev   # official clones have no dev branch
git merge <tag>                                     # or origin/main when the user asked for main
```

If merge succeeds cleanly → proceed to env sync.

## Merge Conflict Handling

When `git merge` reports conflicts:

```bash
CONFLICTS=$(git diff --name-only --diff-filter=U)
echo "Conflicted files:"
echo "$CONFLICTS"
```

### Resolution Strategy by File

| File | Strategy | Reason |
|------|----------|--------|
| `docker/.env.example` | Accept theirs | `.env` is synced separately; the example must match upstream |
| `docker/docker-compose.yaml` | Accept theirs | Generated by `generate_docker_compose` ("do not modify"); a release can add services Dify needs |
| `docker/docker-compose-template.yaml` | Accept theirs | The source the compose file is generated from |
| `docker/envs/**/*.env.example` | Accept theirs | Templates; the user's own `*.env` files are untracked |
| Other files | Show diff, let user decide | Context-dependent |

Accepting theirs: `git checkout --theirs <path> && git add <path>`.

### Where Customizations Go

Customizations no longer live in `docker-compose.yaml`:

- **Ports and settings** → `.env`. Host ports are `EXPOSE_NGINX_PORT` and `EXPOSE_NGINX_SSL_PORT`; `NGINX_PORT` is the container-internal port. Example: `EXPOSE_NGINX_PORT=8081`, `EXPOSE_NGINX_SSL_PORT=8444`.
- **Extra volumes, services, labels, limits** → `docker/docker-compose.override.yaml`. Compose reads it automatically next to `docker-compose.yaml`, and upstream git ignores it, so it never conflicts. List fields such as `ports` are appended, not replaced, so prefer `.env` for ports.
- **Template-level changes** → edit `docker-compose-template.yaml`, then run `./generate_docker_compose` inside `docker/`.
- **Optional settings** → copy `envs/<group>/<name>.env.example` to `envs/<group>/<name>.env`; `.env` still wins.

Example override that caps the memory of the Celery worker:

```yaml
services:
  worker:
    mem_limit: 4g
```

### After Resolving All Conflicts

Stage the resolved files by name. `git add .` can pull in backup archives or env backups that do not belong in the repository (`docker/env-backup/*` and `docker/docker-compose.override.yaml` are ignored upstream, `volumes-*.tgz` is not).

```bash
git add <each resolved path>
git commit -m "Merge <tag> into dev"
```

## Pull and Start

The compose files have no `build:` sections except couchbase, so there is nothing to build:

```bash
cd $DOCKER_DIR
docker compose pull
docker compose up -d
```

Database migrations run at start-up: with `MIGRATION_ENABLED=true` the entrypoint runs `flask upgrade-db`. Run it by hand with `docker compose exec -T api flask upgrade-db`. Some migrations are slow on large tables (the conversation cleanup index in 1.17.0) and some cannot be reversed (the model-type migration in 1.17.1).

One manual step exists for targets from 1.15 up to 1.17.0 on an install that was upgraded from before 1.15: `docker compose exec -T api flask data-migrate legacy-model-types` (a dry run), review the output, then rerun it with `--apply` and send the output to a file in the backup directory. Targets from 1.17.1 on do it inside the automatic migration and need no command.

## Post-update Verification

```bash
docker compose ps
```

All services `Up` or `healthy`; `init_permissions` is a one-shot task and shows `Exited (0)`. Then:

- run a test retrieval against a knowledge base: getting chunks back confirms the vector index survived, an object count does not
- confirm the model providers still list their models
- open a large workflow in the editor

## Rollback

Dify has no downgrade path: migrations are forward-only. Rolling back means restoring the volumes taken in the backup step together with the old code:

```bash
export COMPOSE_PROJECT_NAME=<project> && cd <DOCKER_DIR> && docker compose down && git -C <DIFY_ROOT> checkout -f dev && git -C <DIFY_ROOT> reset --hard <dev-tip> && git -C <DIFY_ROOT> checkout <start-branch-or-commit> && cp -p <backup-dir>/.env .env && sudo mv volumes "volumes.failed-$(date +%s)" && mkdir volumes && sudo tar -xzpf <backup-dir>/volumes.tgz -C volumes && docker compose up -d
```

`<dev-tip>` is the commit `dev` pointed at before the merge (`DEV_TIP`), `<start-branch-or-commit>` the branch the update started on (the commit id when it started on a detached HEAD), `<project>` the compose project (the directory name when none was running). If the update was stashed, `git stash pop` afterwards. Delete `volumes.failed-*` only after the restored stack is verified.

For a failed Weaviate rung, the runbook has its own rollback: set the image back, stop with `-t -1`, move the broken `volumes/weaviate` aside, `cp -a` the backup in, start Weaviate, verify. Rolling only the image tag back without the data is not safe.

## Checking Available Updates

To check without applying anything:

```bash
cd $DIFY_ROOT
git fetch origin --tags

# Running version = the image tag in the compose file
grep -m1 -oE 'langgenius/dify-api:[0-9][^ ]*' $DOCKER_DIR/docker-compose.yaml

# Latest stable tag
git tag --list | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1
```

Compare the running version with the latest **stable tag**, not with `origin/main`, which is ahead of the last release by development commits.
