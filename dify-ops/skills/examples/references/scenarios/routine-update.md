# Scenario: Routine Update to the Latest Stable Tag

## Context

User runs Dify 1.16.1. The repository is checked out on `main` (the branch that tracks upstream) while the customizations live on `dev`; a custom host port is set in `.env`. The vector store is Qdrant (`VECTOR_STORE=qdrant`), so the Weaviate migration gate does not apply. They want the latest stable release.

## Starting State

- Branch: `main` at `fed9876`; `dev` at `abc1234` (their customization commits)
- Working tree: clean
- Docker project: `docker` (default)
- Running version: 1.16.1 (image tag in `docker-compose.yaml`)
- All containers running

## Walkthrough

### 1. User runs `/dify-ops:update`

No argument: the target is the latest stable tag, not `main`.

### 2. Directory Detection

```
$ pwd
<DIFY_DIR>/docker

Detected: DOCKER_DIR=<DIFY_DIR>/docker, DIFY_ROOT=<DIFY_DIR>
```

### 3. Pre-flight

```
$ git branch --show-current
main
$ git status --porcelain
(clean)
Branch: main   Commit: fed9876...   dev tip: abc1234...
                (the rollback resets dev to abc1234 — not to HEAD — and returns to main)

$ docker compose version --short
2.29.7                      (>= 2.24.0: OK)

Docker project: docker      (from the labels of the running api container)

$ git fetch origin --tags
$ git tag --list | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1
1.17.1

Current: 1.16.1   Target: 1.17.1 (images 1.17.1)
Weaviate gate: pass (VECTOR_STORE=qdrant, volumes/weaviate data: no)
```

### 4. Release Notes

```
=== 1.17.0 ===
## Environment Variable Changes   (EDITION -> DEPLOYMENT_EDITION, defaults changed)
## Database Migrations            (add_conversation_cleanup_index: slow on a large conversations table)
## Upgrade Guide
=== 1.17.1 ===
## Environment Variable Changes   (DIFY_AGENT_RUN_RETENTION_SECONDS: 3 days -> 2 hours)
## Database Migrations            (3 migrations; the model-type one cannot be reversed)
## Upgrade Guide                  (bundled Weaviate 1.27.0 -> 1.39.2 — not applicable here)
```

Claude summarises: nothing blocks this instance; the model-type migration is one-way, which is why the backup comes first.

### 5. Plan

```
DIFY UPDATE PLAN   1.16.1 -> 1.17.1
TARGET    <DIFY_DIR> · compose project docker · merge 1.17.1 into dev
PRECHECK  tree clean · Compose 2.29.7 · Weaviate gate: n/a (qdrant) · release notes read
CHANGE    git merge 1.17.1 · env sync · docker compose pull && docker compose up -d
BACKUP    <backup-dir>/20261003-101500: docker-compose.yaml, .env, volumes.tgz — stack down first
IMPACT    downtime from down to up · start-up runs 3 DB migrations, one is irreversible
VALIDATE  docker compose ps · HTTP check · test retrieval in one knowledge base · model list
ROLLBACK  export COMPOSE_PROJECT_NAME=docker && cd <DIFY_DIR>/docker && docker compose down && git -C <DIFY_DIR> checkout -f dev && git -C <DIFY_DIR> reset --hard abc1234 && git -C <DIFY_DIR> checkout main && cp -p <backup-dir>/20261003-101500/.env .env && sudo mv volumes "volumes.failed-$(date +%s)" && mkdir volumes && sudo tar -xzpf <backup-dir>/20261003-101500/volumes.tgz -C volumes && docker compose up -d
APPLY     waiting for the user's go

Apply this plan? (y/n) y
```

### 6. Backup, Stack Down

```
BACKUP_DIR=<backup-dir>/20261003-101500   COMPOSE_PROJECT_NAME=docker
$ docker compose stop -t 120 nginx api api_websocket worker worker_beat
$ docker compose down -t 120
(no container of this stack is left running)
$ sudo tar -czpf <backup-dir>/20261003-101500/volumes.tgz -C volumes .
$ sudo tar -tzf <backup-dir>/20261003-101500/volumes.tgz > /dev/null
Backup OK
-rw------- 1 root root  412M  volumes.tgz
-rw------- 1 user user  330B  state.env
-rw------- 1 user user  3.1K  docker-compose.yaml
-rw------- 1 user user  9.4K  .env
```

Only names and sizes are listed: the archive and `.env` hold secrets and are never printed.

### 7. Merge

```
$ set -a; . <backup-dir>/20261003-101500/state.env; set +a
$ git checkout dev            (the update started on main; the merge happens on dev)
$ git merge 1.17.1
Merge made by the 'ort' strategy.
 docker/.env.example           | 12 ++++-----
 docker/docker-compose.yaml    | 42 ++++++++++++++++++++-----
 docker/envs/core-services/dify-agent.env.example | 8 ++++--
 ...
 94 files changed, 3120 insertions(+), 410 deletions(-)
```

No conflicts. The custom host port lives in `.env` (`EXPOSE_NGINX_PORT`), not in the generated compose file, so nothing collides.

### 8. Env Sync

```
$ bash dify-env-sync.sh      (through the masking filter)
[INFO] Backed up existing .env to env-backup/.env.backup_<timestamp>
[1] DIFY_AGENT_API_TOKEN
  .env (current)      : ***
  .env.example (recommended): ***
[2] CELERY_BROKER_URL
  .env (current)      : ***
  .env.example (recommended): ***
[SUCCESS] Partial synchronization of .env file completed
[INFO]   Preserved .env values: 211
[WARNING] The following environment variables have been removed from .env.example:
[WARNING]   - DIFY_AGENT_RUN_RETENTION_SECONDS
[WARNING]   - DIFY_AGENT_SHELLCTL_AUTH_TOKEN
[WARNING]   - DIFY_AGENT_SHELLCTL_ENTRYPOINT
[WARNING]   - SMTP_PASSWORD
[WARNING]   ...
[WARNING] Consider manually removing these variables from .env
```

The user changed `DIFY_AGENT_API_TOKEN` from its development default, and `CELERY_BROKER_URL` carries the Redis password, so both differ from the example — the filter prints `***` for both (and for any string value). The closing "consider manually removing" line is misleading: the script rebuilt `.env` from the new example and **has already dropped** every key that is not in it. New keys added to `.env`:

| Variable                              | Default Value               | Action Required? |
|---------------------------------------|-----------------------------|------------------|
| DIFY_AGENT_RUNTIME_BACKEND            | local                       | No               |
| DIFY_AGENT_LOCAL_SANDBOX_ENDPOINT     | http://local_sandbox:5004   | No               |
| DIFY_AGENT_SANDBOX_FILES_BASE_URL     | http://api:5001             | No               |
| DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN   | (empty)                     | Review — empty token, used by the middleware-only stack |
| TURNSTILE_SITE_KEY                    | (empty)                     | Review — empty, optional |
| PLUGIN_MAX_FILE_SIZE                  | 52428800                    | No               |
| SSRF_PROXY_ALLOW_PRIVATE_IPS          | (empty)                     | No               |

Claude then compares the key **names** of `<backup-dir>/20261003-101500/.env` with the new `.env`:

```
DIFY_AGENT_RUN_RETENTION_SECONDS -> envs/core-services/dify-agent.env
DIFY_AGENT_SHELLCTL_AUTH_TOKEN -> .env   (no template declares it: custom, or removed upstream)
DIFY_AGENT_SHELLCTL_ENTRYPOINT -> .env   (no template declares it: custom, or removed upstream)
SMTP_PASSWORD -> envs/core-services/shared.env envs/security.env
```

Names only, never values. The release notes of 1.17.0 list the two `DIFY_AGENT_SHELLCTL_*` keys as removed, so they stay dropped. The user restores the other two by copying their lines from the backup (nothing is printed): `DIFY_AGENT_RUN_RETENTION_SECONDS` into `envs/core-services/dify-agent.env` to keep 3 days instead of the new 2-hour default, `SMTP_PASSWORD` (a mail setting the user had added to `.env` by hand) into `envs/security.env`. Without that step the update would have silently dropped the mail settings.

Last, Claude checks the other cases: `COMPOSE_PROFILES` already contains `collaboration`, and `EDITION` is not set, so no rename is needed.

### 9. Pull and Start

```
$ docker compose pull
$ docker compose up -d
[+] Running 17/17
 ✔ Container docker-init_permissions-1  Exited
 ✔ Container docker-db_postgres-1       Healthy
 ✔ Container docker-redis-1             Running
 ✔ Container docker-qdrant-1            Running
 ✔ Container docker-ssrf_proxy-1        Running
 ✔ Container docker-agent_ssrf_proxy-1  Running
 ✔ Container docker-sandbox-1           Started
 ✔ Container docker-local_sandbox-1     Started
 ✔ Container docker-plugin_daemon-1     Started
 ✔ Container docker-agent_backend-1     Started
 ✔ Container docker-api-1               Started
 ✔ Container docker-api_websocket-1     Started
 ✔ Container docker-worker-1            Started
 ✔ Container docker-worker_beat-1       Started
 ✔ Container docker-web-1               Started
 ✔ Container docker-nginx-1             Started
```

No image is built: the compose file only pulls.

### 10. Verification

```
$ docker compose ps
NAME                          STATUS                    PORTS
docker-api-1                  Up 40 seconds (healthy)   5001/tcp
docker-db_postgres-1          Up 40 seconds (healthy)   5432/tcp
docker-nginx-1                Up 20 seconds             0.0.0.0:8081->80/tcp
docker-init_permissions-1     Exited (0) 45 seconds ago
...

HTTP 200 — Dify web reachable at port 8081
```

`init_permissions` showing `Exited (0)` is expected. The port is read from `EXPOSE_NGINX_PORT` only. The user runs a test retrieval against one knowledge base (chunks come back) and checks that the model providers list their models.

### 11. Summary

```
=== Dify Update Summary ===
Previous version: 1.16.1 (dev tip abc1234)
Current version:  1.17.1 (def5678)
Branch:           dev (update started on main)
Merged from:      1.17.1
Backup:           <backup-dir>/20261003-101500 (volumes.tgz 412M)
New env vars:     7 added to .env (2 to review); 2 dropped keys restored from the backup (names only)
Conflicts:        None
Docker project:   docker
Containers:       All up; init_permissions Exited (0)
Rollback:         export COMPOSE_PROJECT_NAME=docker && cd <DIFY_DIR>/docker && docker compose down && git -C <DIFY_DIR> checkout -f dev && git -C <DIFY_DIR> reset --hard abc1234 && git -C <DIFY_DIR> checkout main && cp -p <backup-dir>/20261003-101500/.env .env && sudo mv volumes "volumes.failed-$(date +%s)" && mkdir volumes && sudo tar -xzpf <backup-dir>/20261003-101500/volumes.tgz -C volumes && docker compose up -d
Warning:          rollback restores the volumes; a database migration is not reversible any other way
```
