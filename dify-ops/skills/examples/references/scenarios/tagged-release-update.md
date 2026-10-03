# Scenario: Update to a Specific Tag with the Bundled Weaviate

## Context

User runs Dify 1.16.1 with the bundled Weaviate (the default `VECTOR_STORE=weaviate`, knowledge bases already indexed) and wants version `1.17.1` specifically. The folder was renamed, so the Docker project is `dify-prod`. 1.17.1 moves the bundled Weaviate server from 1.27.0 to 1.39.2, which the old data volume cannot survive in one step: the update must stop at the pre-flight, send the user through the official runbook, and only then continue.

## Starting State

- Branch: `dev`
- Working tree: one uncommitted change in `docker-compose.yaml` (a comment) and host ports set directly in that generated file
- Docker project: `dify-prod` (custom folder name)
- Running version: 1.16.1, `VECTOR_STORE=weaviate`, `volumes/weaviate` holds data
- All containers running

## Walkthrough

### 1. User runs `/dify-ops:update 1.17.1`

### 2. Directory Detection

```
$ pwd
<DIFY_DIR>

Detected: DIFY_ROOT=<DIFY_DIR>, DOCKER_DIR=<DIFY_DIR>/docker
```

### 3. Pre-flight Stops

```
Branch: dev   Commit: aaa1111...
Docker project: dify-prod   (from the labels of the running api container)
Current: 1.16.1   Target: 1.17.1 (images 1.17.1)

STOP: this update crosses Dify 1.17.1 and the bundled Weaviate moves 1.27.0 -> 1.39.2.
An existing volume cannot jump 12 minor versions; a plain pull + up -d breaks vector search silently.
Nothing was changed. Runbook: https://docs.dify.ai/en/self-host/deploy/troubleshooting/weaviate-server-migration-path
```

No merge, no `docker compose up -d`. Claude offers three ways forward: follow the runbook and re-run with `--weaviate-staged`; update only to a release below 1.17.1; move to another vector store first. The user picks the runbook.

### 4. The Runbook (done by the user, outside the command)

```
$ docker compose stop -t 120 nginx api api_websocket worker worker_beat
$ docker compose stop -t -1 weaviate
$ sudo cp -a ./volumes/weaviate ./volumes/weaviate_backup_20261003
```

Then 13 rungs, `1.27` through `1.38` on each minor's latest patch and a last rung on exactly `1.39.2`. Every rung: edit the image tag, `docker compose stop -t -1 weaviate`, `docker compose up -d weaviate`, wait ten seconds, check the reported version, the collection list, the object count and the synchronization. Never `docker kill` or `docker rm -f`. After the last rung the temporary image edit is reverted and a test retrieval returns chunks.

### 5. User re-runs `/dify-ops:update v1.17.1 --weaviate-staged`

```
Target: 1.17.1    (the leading v is dropped: the git tag has none)
Weaviate gate: lifted by --weaviate-staged
```

### 6. Pre-flight Continues

```
$ git status --porcelain
 M docker/docker-compose.yaml

WARNING: Uncommitted changes detected:
  M docker/docker-compose.yaml

Options:
  1. Commit changes first
  2. Stash changes (restore after update)
  3. Abort

User chooses: stash
```

The stash runs in Step 5 of the command, right before the merge, after the backup.

### 7. Plan and Backup

```
DIFY UPDATE PLAN   1.16.1 -> 1.17.1
TARGET    <DIFY_DIR> · compose project dify-prod · merge 1.17.1 into dev
PRECHECK  Compose 2.29.7 · Weaviate gate: lifted (--weaviate-staged) · release notes read
CHANGE    git merge 1.17.1 · env sync · docker compose pull && docker compose up -d
BACKUP    <backup-dir>/20261003-142000: docker-compose.yaml, .env, volumes.tgz — stack down first
IMPACT    downtime from down to up · 3 DB migrations at start-up, one is irreversible
VALIDATE  docker compose ps · HTTP check · test retrieval · model list
ROLLBACK  export COMPOSE_PROJECT_NAME=dify-prod && cd <DIFY_DIR>/docker && docker compose down && git -C <DIFY_DIR> checkout -f dev && git -C <DIFY_DIR> reset --hard aaa1111 && git -C <DIFY_DIR> checkout dev && cp -p <backup-dir>/20261003-142000/.env .env && sudo mv volumes "volumes.failed-$(date +%s)" && mkdir volumes && sudo tar -xzpf <backup-dir>/20261003-142000/volumes.tgz -C volumes && docker compose up -d
APPLY     user's go
```

```
BACKUP_DIR=<backup-dir>/20261003-142000   COMPOSE_PROJECT_NAME=dify-prod
$ docker compose stop -t 120 nginx api api_websocket worker worker_beat
$ docker compose stop -t -1 weaviate
$ docker compose down -t 120
(no container of this stack is left running)
$ sudo tar -czpf <backup-dir>/20261003-142000/volumes.tgz -C volumes .
Backup OK
```

The project name was detected from the running `api` container's labels and exported **inside the block**: the folder is called `dify-prod`, so without `COMPOSE_PROJECT_NAME` a bare `docker compose down` would address a project named after the directory, stop nothing, and the archive would be taken from live postgres. The guard after `down` looks for any container of this stack still running and aborts if it finds one. The project name, the git state and the paths are saved in `state.env` next to the archive.

### 8. Fetch and Merge Tag

```
$ git stash
Saved working directory and index state WIP on dev: aaa1111 last commit msg

$ git merge 1.17.1
Auto-merging docker/docker-compose.yaml
CONFLICT (content): Merge conflict in docker/docker-compose.yaml
Automatic merge failed; fix conflicts and then commit the result.
```

### 9. Conflict Resolution

```
Conflicted files:
  docker/docker-compose.yaml

=== docker/docker-compose.yaml ===
<<<<<<< HEAD
    ports:
      - "8081:80"    # Custom: exposed on 8081
      - "8444:443"   # Custom: exposed on 8444
=======
    ports:
      - "${EXPOSE_NGINX_PORT:-80}:${NGINX_PORT:-80}"
      - "${EXPOSE_NGINX_SSL_PORT:-443}:${NGINX_SSL_PORT:-443}"
>>>>>>> 1.17.1

docker-compose.yaml is generated by generate_docker_compose ("do not modify").
Host ports are set with EXPOSE_NGINX_PORT and EXPOSE_NGINX_SSL_PORT in .env;
NGINX_PORT is the container-internal port and stays at its default.

Recommended resolution: take upstream's file, move the ports to .env.
```

User accepts the recommendation:

```
$ git checkout --theirs docker/docker-compose.yaml
$ git add docker/docker-compose.yaml
$ git commit -m "Merge 1.17.1 into dev"
```

The merged file also brings the Weaviate image `cr.weaviate.io/semitechnologies/weaviate:1.39.2`, which matches the volume the runbook left behind. The user then sets `EXPOSE_NGINX_PORT=8081` and `EXPOSE_NGINX_SSL_PORT=8444` in `.env` (Step 10). Anything else that was customised in the compose file moves to `docker-compose.override.yaml`.

### 10. Env Sync

```
$ bash dify-env-sync.sh      (through the masking filter)
[1] DIFY_AGENT_API_TOKEN
  .env (current)      : ***
  .env.example (recommended): ***
[WARNING] The following environment variables have been removed from .env.example:
[WARNING]   - DIFY_AGENT_RUN_RETENTION_SECONDS
[WARNING]   - DIFY_AGENT_SHELLCTL_AUTH_TOKEN
[WARNING]   - DIFY_AGENT_SHELLCTL_ENTRYPOINT
[WARNING]   - SMTP_PASSWORD
[WARNING] Consider manually removing these variables from .env
```

The "consider manually removing" line is misleading: the script rebuilt `.env` from the new example and has already dropped these keys. Claude lists the key names that are in `<backup-dir>/20261003-142000/.env` but no longer in `.env`, with the file each belongs to (names only, never values), and the user restores `DIFY_AGENT_RUN_RETENTION_SECONDS` into `envs/core-services/dify-agent.env` and `SMTP_PASSWORD` into `envs/security.env` by copying their lines from the backup. The two `DIFY_AGENT_SHELLCTL_*` keys were removed upstream in 1.17.0 and stay dropped.

New keys added to `.env`:

| Variable                              | Default Value               | Action Required? |
|---------------------------------------|-----------------------------|------------------|
| DIFY_AGENT_RUNTIME_BACKEND            | local                       | No               |
| DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN   | (empty)                     | Review — empty token, used by the middleware-only stack |

No port variable is new: `EXPOSE_NGINX_PORT` and `EXPOSE_NGINX_SSL_PORT` already sit in `.env` with their defaults (80 and 443). The user edits them to `EXPOSE_NGINX_PORT=8081` and `EXPOSE_NGINX_SSL_PORT=8444`, which is what the conflict in the previous step asked for.

### 11. Pull and Start

```
$ set -a; . <backup-dir>/20261003-142000/state.env; set +a      (exports COMPOSE_PROJECT_NAME=dify-prod)
$ docker compose pull
$ docker compose up -d
[+] Running 17/17
 ✔ Container dify-prod-db_postgres-1    Healthy
 ✔ Container dify-prod-redis-1          Running
 ✔ Container dify-prod-weaviate-1       Running
 ...
 ✔ Container dify-prod-nginx-1          Started
```

### 12. Verification

```
$ docker compose ps
All services Up or healthy; dify-prod-init_permissions-1 Exited (0) — expected.
HTTP 200 — Dify web reachable at http://localhost:8081
```

A test retrieval against a knowledge base returns chunks: the vector index survived the staged upgrade. The model providers list their models.

### 13. Restore Stashed Changes

```
$ git stash pop
On branch dev
Auto-merging docker/docker-compose.yaml
CONFLICT (content): Merge conflict in docker/docker-compose.yaml

Note: the stashed comment touches the generated compose file, which the merge replaced.
Drop it (git checkout --theirs docker/docker-compose.yaml, git stash drop) or move it to docker-compose.override.yaml.
```

### 14. Summary

```
=== Dify Update Summary ===
Previous version: 1.16.1 (aaa1111)
Current version:  1.17.1 (bbb2222)
Branch:           dev
Merged from:      1.17.1
Backup:           <backup-dir>/20261003-142000
New env vars:     2 added to .env (1 to review); host ports set in .env; 2 dropped keys restored from the backup
Conflicts:        1 resolved (docker-compose.yaml — host ports moved to .env)
Docker project:   dify-prod
Containers:       All up; init_permissions Exited (0)
Weaviate:         staged to 1.39.2 by the runbook before the update
Stash:            Conflict on pop — resolved by dropping the comment
Rollback:         export COMPOSE_PROJECT_NAME=dify-prod && cd <DIFY_DIR>/docker && docker compose down && git -C <DIFY_DIR> checkout -f dev && git -C <DIFY_DIR> reset --hard aaa1111 && git -C <DIFY_DIR> checkout dev && cp -p <backup-dir>/20261003-142000/.env .env && sudo mv volumes "volumes.failed-$(date +%s)" && mkdir volumes && sudo tar -xzpf <backup-dir>/20261003-142000/volumes.tgz -C volumes && docker compose up -d
```
