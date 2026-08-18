# Scenario: Update to Specific Version Tag

## Context

User wants to update their Dify instance to version `0.15.0` specifically, not the latest main. They have a custom Docker project name `dify-prod` because the folder was renamed.

## Starting State

- Branch: `dev`
- Working tree: one uncommitted change in docker-compose.yaml (added comment)
- Docker project: `dify-prod` (custom folder name)
- All containers running

## Walkthrough

### 1. User runs `/dify-ops:update 0.15.0`

### 2. Directory Detection

```
$ pwd
/opt/dify-prod

Detected: DIFY_ROOT=/opt/dify-prod, DOCKER_DIR=/opt/dify-prod/docker
```

### 3. Pre-flight

```
$ git branch --show-current
dev
$ git status --porcelain
 M docker/docker-compose.yaml
$ git rev-parse --short HEAD
aaa1111

WARNING: Uncommitted changes detected:
  M docker/docker-compose.yaml

Options:
  1. Commit changes first
  2. Stash changes (restore after update)
  3. Abort

User chooses: stash

$ git stash
Saved working directory and index state WIP on dev: aaa1111 last commit msg
```

### 4. Fetch and Merge Tag

```
$ git fetch origin --tags
$ git tag -l "0.15.0"
(empty — tag not found)

$ git tag -l "v0.15.0"
v0.15.0

Found tag: v0.15.0 (added v prefix)

$ git merge v0.15.0
Auto-merging docker/docker-compose.yaml
CONFLICT (content): Merge conflict in docker/docker-compose.yaml
Automatic merge failed; fix conflicts and then commit the result.
```

### 5. Conflict Resolution

```
Conflicted files:
  docker/docker-compose.yaml

=== docker/docker-compose.yaml ===
Conflict at lines 45-52:

<<<<<<< HEAD
    ports:
      - "8080:80"    # Custom: exposed on 8080
      - "8443:443"   # Custom: exposed on 8443
=======
    ports:
      - "${NGINX_PORT:-80}:80"
      - "${NGINX_SSL_PORT:-443}:443"
>>>>>>> v0.15.0

Upstream changed ports to use env variables.

Recommended resolution: Accept upstream and set NGINX_PORT=8080, NGINX_SSL_PORT=8443 in .env
```

User accepts recommendation:

```
$ git checkout --theirs docker/docker-compose.yaml
$ git add docker/docker-compose.yaml
$ git commit -m "Merge v0.15.0 into dev"
```

### 6. Env Sync

```
Found 5 new variables:

| Variable              | Default Value | Action Required? |
|-----------------------|--------------|-----------------|
| NGINX_PORT            | 80           | YES — set to 8080 |
| NGINX_SSL_PORT        | 443          | YES — set to 8443 |
| PLUGIN_DAEMON_PORT    | 5003         | No              |
| NEW_FEATURE_ENABLED   | true         | No              |
| RATE_LIMIT_API_KEY    | (empty)      | YES — set value |

Note: Set NGINX_PORT=8080 and NGINX_SSL_PORT=8443 to preserve your custom port mappings.

Append these to .env? (y/n) y
Added 5 new variables to .env
```

User then manually edits .env to set `NGINX_PORT=8080` and `NGINX_SSL_PORT=8443`.

### 7. Docker Project Detection

```
$ docker ps --format '{{.Names}}' | grep -E '-(api|web|worker)-' | head -1
dify-prod-api-1

Detected Docker project name: dify-prod
```

### 8. Volume Backup

```
$ cd /opt/dify-prod/docker
$ tar -cvf volumes-$(date +%s).tgz volumes
volumes/
volumes/postgres/
volumes/redis/
volumes/weaviate/
volumes/storage/
...
Volume backup created: volumes-1743091200.tgz
```

### 9. Rebuild

```
$ docker compose -p dify-prod up -d --build
[+] Building 52.1s (12/12) FINISHED
[+] Running 11/11
 ✔ Container dify-prod-db_postgres-1    Running
 ✔ Container dify-prod-redis-1          Running
 ...
 ✔ Container dify-prod-nginx-1          Started
```

### 10. Verification

```
All 11 containers running.
HTTP 200 — Dify web reachable at http://localhost:8080
```

### 11. Restore Stashed Changes

```
$ git stash pop
On branch dev
Changes not staged for commit:
  modified: docker/docker-compose.yaml

Note: The stashed comment was added to docker-compose.yaml.
The file was already modified by the merge, so review the stash pop result.
```

### 12. Summary

```
=== Dify Update Summary ===
Previous commit:  aaa1111
Current commit:   bbb2222
Branch:           dev
Merged from:      v0.15.0
New env vars:     5 added to .env (2 require manual values)
Conflicts:        1 resolved (docker-compose.yaml — port env vars)
Docker project:   dify-prod
Containers:       All running
Stash:            Restored
Volume backup:    volumes-1743091200.tgz
Rollback:         git reset --hard aaa1111
```
