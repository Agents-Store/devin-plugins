# Scenario: Routine Update to Latest Main

## Context

User has a Dify instance running on the `dev` branch with custom port mappings. They want to update to the latest upstream version.

## Starting State

- Branch: `dev`
- Working tree: clean
- Docker project: `docker` (default)
- All containers running

## Walkthrough

### 1. User runs `/dify-ops:update`

### 2. Directory Detection

```
$ pwd
/opt/dify/docker

Detected: DOCKER_DIR=/opt/dify/docker, DIFY_ROOT=/opt/dify
```

### 3. Pre-flight

```
$ cd /opt/dify
$ git branch --show-current
dev
$ git status --porcelain
(clean)
$ git rev-parse --short HEAD
abc1234
```

### 4. Fetch and Merge

```
$ git fetch origin --tags
remote: Enumerating objects: 142, done.
remote: Counting objects: 100% (142/142), done.
...

$ git merge origin/main
Updating abc1234..def5678
Fast-forward
 api/core/model_runtime/...  | 45 +++++++
 docker/.env.example          | 3 +++
 docker/docker-compose.yaml   | 2 +-
 15 files changed, 234 insertions(+), 12 deletions(-)
```

No conflicts — clean fast-forward merge.

### 5. Env Sync

```
Checking for new environment variables...

Found 3 new variables:

| Variable              | Default Value | Action Required? |
|-----------------------|--------------|-----------------|
| PLUGIN_MAX_TIMEOUT    | 600          | No              |
| WORKFLOW_RETRY_COUNT  | 3            | No              |
| SANDBOX_ENABLE_NETWORK| false        | No              |

Append these to .env? (y/n) y

Added 3 new variables to .env
```

### 6. Docker Project Detection

```
$ docker ps --format '{{.Names}}' | grep -E '-(api|web|worker)-' | head -1
docker-api-1

Detected Docker project name: docker
```

### 7. Volume Backup

```
$ cd /opt/dify/docker
$ tar -cvf volumes-$(date +%s).tgz volumes
volumes/
volumes/postgres/
volumes/redis/
volumes/weaviate/
volumes/storage/
...
Volume backup created: volumes-1743091200.tgz
```

### 8. Rebuild

```
$ docker compose up -d --build
[+] Building 45.2s (12/12) FINISHED
[+] Running 11/11
 ✔ Container docker-db_postgres-1     Running
 ✔ Container docker-redis-1           Running
 ✔ Container docker-weaviate-1        Running
 ✔ Container docker-ssrf_proxy-1      Running
 ✔ Container docker-sandbox-1         Started
 ✔ Container docker-api-1             Started
 ✔ Container docker-worker-1          Started
 ✔ Container docker-worker_beat-1     Started
 ✔ Container docker-web-1             Started
 ✔ Container docker-plugin_daemon-1   Started
 ✔ Container docker-nginx-1           Started
```

### 9. Verification

```
$ docker compose ps
NAME                      STATUS          PORTS
docker-api-1              Up 30 seconds   5001/tcp
docker-db_postgres-1      Up 2 hours      5432/tcp
docker-nginx-1            Up 15 seconds   0.0.0.0:80->80/tcp
docker-redis-1            Up 2 hours      6379/tcp
docker-web-1              Up 25 seconds   3000/tcp
...

HTTP 200 — Dify web reachable
```

### 10. Summary

```
=== Dify Update Summary ===
Previous commit:  abc1234
Current commit:   def5678
Branch:           dev
Merged from:      origin/main
New env vars:     3 added to .env
Conflicts:        None
Docker project:   docker
Containers:       All running
Volume backup:    volumes-1743091200.tgz
Rollback:         git reset --hard abc1234
```
