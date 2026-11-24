---
name: env-sync
description: >
  Synchronize .env with .env.example for Dify Docker deployments and review the envs/ defaults and
  override files — new, removed and changed variables, existing values kept, secrets never
  printed. Use when syncing env variables, checking for new configuration variables, comparing
  .env.example vs .env, "env sync", "new env variables", "missing environment variables", or after
  pulling Dify updates. Not for the git merge and backup (update-workflow) or the service layout
  (dify-docker-architecture).
---

## Location

`.env.example` and `.env` live in `dify/docker/` (DOCKER_DIR). All commands below run from that directory.

The configuration is layered (split in 1.14.1, restructured in 1.19.0 and 1.20.0):

- **Root `.env.example`** — only what needs a human decision. Since 1.19.0 it is a short file (`COMPOSE_PROFILES`, `DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN`); before it carried about 240 keys. `.env` is your copy plus your changes and holds deployment inputs and explicit overrides: profiles, host ports, volume paths, shared plugin keys.
- **`envs/**/*.defaults`** (1.19.0 and newer) — tracked defaults of each service, loaded automatically, replaced by every release. To change a service setting copy the file to the same name with `.env` (`envs/<group>/<name>.env`; the first comment lines name the path) and edit the copy: `envs/core-services/` (`api-worker`, `api`, `web`, `worker`, `worker-beat`, `sandbox`, `plugin-daemon`, `dify-agent`, `urls`, …), `envs/databases/`, `envs/infrastructure/`, `envs/vectorstores/`.
- **`envs/**/*.env.example`** — templates of optional integrations (`security.env.example`, the knowledge-fs files, `middleware.env.example`). Copy without the `.example` suffix. Before 1.19.0 every file under `envs/` was such a template, `shared.env.example` alone with more than 500 keys.

Precedence, highest first: root `.env`, the service's `envs/**/*.env` override, the tracked `.defaults`. Compose >= 2.35.0 is needed for it to hold. `*.env` files are gitignored; `.defaults` and `*.env.example` are tracked and change with every release. Apply a change with `docker compose up -d`; `docker compose restart` does not reload env files.

An `.env` copied from an older, monolithic `.env.example` still works: it is read last. It also pins the old defaults of every key it carries, so review empty assignments such as `CELERY_WORKER_AMOUNT=` that were copied from an old template: an empty value overrides the Docker default.

## Never Print Secrets

`.env` holds database and Redis passwords, `SECRET_KEY`, API keys and tokens. Never `cat .env`, never echo a value of a key whose name contains `SECRET`, `PASSWORD`, `PASSWD`, `TOKEN`, `KEY`, `CREDENTIAL`, `DSN`, `AUTH`, `URL`, `URI`, `JSON` or `BASE64`, nor any value that carries credentials, such as `redis://:<password>@host`. Show key **names** and, for harmless keys, the value from `.env.example` (the default). Output you produce lands in the session transcript.

## Edge Case: .env Does Not Exist

```bash
cd $DOCKER_DIR

if [ ! -f ".env" ]; then
  echo "WARNING: .env does not exist"
  echo "Creating from .env.example..."
  cp .env.example .env
  echo "CREATED .env from .env.example"
  echo ""
  echo "IMPORTANT: Review and set these security-sensitive keys:"
  grep -oE '^(SECRET_KEY|DB_PASSWORD|REDIS_PASSWORD|INIT_PASSWORD|DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN|DIFY_AGENT_API_TOKEN|DIFY_AGENT_SERVER_SECRET_KEY)=' .env
fi
```

`grep -o` with the `=` anchor prints the key names only. An empty `SECRET_KEY` is fine since 1.14.1: the API generates a key and stores it in `volumes/app/storage`. After creating, show the user which keys still carry development defaults.

## Default: the Official dify-env-sync.sh

When `dify-env-sync.sh` exists in DOCKER_DIR (there is also a `dify-env-sync.py`), run it first. It backs `.env` up to `env-backup/.env.backup_<timestamp>` before changing anything, and what it does next depends on its release, read from the script:

- **1.19.0 and newer:** appends the keys that `.env.example` has and `.env` lacks, under a "New deployment inputs" comment. Existing values, comments and extra keys stay. It lists the extra keys (not in the root example) as "local overrides that will be preserved" — with the short root example that is most of an old `.env`, which is expected. It does not look at `envs/`.
- **1.18.0 and older:** **rebuilds `.env` from the new `.env.example`**, line by line: a key still in the example keeps your value, a new key gets the example's value, and **every key that is not in the new example is dropped** — custom keys, keys that moved into `envs/` (SMTP and storage credentials, `DIFY_AGENT_RUN_RETENTION_SECONDS`) and keys removed upstream. Its closing "consider manually removing these variables" warning is misleading, because they are already gone; the only copy is the backup.

Both versions print the keys whose value differs from the example. The script in the working tree is the target release's once it is merged.

The manual algorithm below compares **key names** only and only appends, so it misses a changed default; the script reports the changed values.

**The script prints the current `.env` value of every differing key, passwords, secrets and credential-bearing URLs (`CELERY_BROKER_URL` ships as `redis://:<password>@redis:6379/1`) included.** Run it through a filter. It shows a value only when the key name does not look secret **and** the value is a number, a boolean or empty; everything else prints as `***`, and so do the analysis lines of a masked key. Any other line (the continuation of a multi-line value, such as a PEM key whose `\n` the script expands) is dropped:

```bash
cd $DOCKER_DIR
bash dify-env-sync.sh 2>&1 | awk '
  { gsub(/\033\[[0-9;]*m/, "") }
  /^\[[0-9]+\] [A-Za-z_][A-Za-z0-9_]*$/ { key = $2; hide = 0; print; next }
  /^  \.env +[(]current[)]/ {
    val = $0; sub(/^[^:]*: ?/, "", val)
    hide = (key ~ /SECRET|PASSWORD|PASSWD|TOKEN|KEY|CREDENTIAL|DSN|AUTH|URL|URI|JSON|BASE64/) || (tolower(val) !~ /^(true|false|[0-9]+)?$/)
    if (hide) sub(/:.*/, ": ***")
    print; next }
  /^  \.env\.example/ { if (hide) sub(/:.*/, ": ***"); print; next }
  /^  [^ ]/ { if (!hide) print; next }
  /^\[(INFO|SUCCESS|WARNING|ERROR)\]/ { print; next }
  /^$/ { print; next }
  { next }'                                                  # a continuation line of a multi-line value (a PEM key): never printed
```

The filter uses only POSIX awk and was checked with gawk, mawk and busybox awk; the output format of the script is the same in 1.17.1 and 1.20.0. Never run the script bare inside an agent session. If it fails, fall back to the manual algorithm.

### Restore the Dropped Keys

Only a script of 1.18.0 or older drops keys; with 1.19.0 and newer the comparison below finds nothing. After the script, compare the key **names** of the backup with the new `.env`, and say where each dropped key belongs. Never print values:

```bash
cd $DOCKER_DIR
DROPPED=$(comm -23 <(grep -oE '^[A-Z_][A-Z0-9_]*' "$BACKUP_DIR/.env" | sort -u) <(grep -oE '^[A-Z_][A-Z0-9_]*' .env | sort -u))
for K in $DROPPED; do
  T=$(grep -rlE "^#? ?$K=" envs --include='*.defaults' --include='*.env.example' 2>/dev/null | sed -E 's/\.(defaults|env\.example)$/.env/' | sort -u | paste -sd' ' -)
  if [ -n "$T" ]; then echo "$K -> $T"; else echo "$K -> .env   (nothing declares it: custom, or removed upstream)"; fi
done
```

`$BACKUP_DIR/.env` is the copy taken before the sync (the update command's backup; with a stand-alone sync use the file in `env-backup/`). Offer each key to the user:

- a key that a file under `envs/` declares goes into the matching `envs/**/*.env` override file (when several are listed, ask which; the file is created if missing and may hold just that key)
- a key that nothing declares is either custom (restore into `.env`) or removed upstream (check the release notes; leave it dropped)

Restore by copying the line from the backup, which prints nothing:

```bash
restore() { mkdir -p "$(dirname "$2")"; grep "^$1=" "$BACKUP_DIR/.env" | tail -1 >> "$2"; }   # restore <KEY> <target-file>
restore <KEY> <target-file>
```

## Sync Algorithm (manual fallback)

### Step 1: Extract Keys

```bash
cd $DOCKER_DIR

# Keys from .env.example (skip comments and empty lines)
grep -E '^[A-Z_][A-Z0-9_]*=' .env.example | cut -d= -f1 | sort > /tmp/dify-env-example-keys

# Keys from .env
grep -E '^[A-Z_][A-Z0-9_]*=' .env | cut -d= -f1 | sort > /tmp/dify-env-keys
```

### Step 2: Find New Variables

```bash
# Keys in .env.example that are NOT in .env
NEW_KEYS=$(comm -23 /tmp/dify-env-example-keys /tmp/dify-env-keys)

if [ -z "$NEW_KEYS" ]; then
  echo "No new environment variables found. .env is up to date."
else
  echo "Found new variables:"
  echo "$NEW_KEYS" | wc -l
fi
```

### Step 3: Extract Full Lines for New Variables

The new keys come from `.env.example`, so their values are defaults and safe to show:

```bash
for KEY in $NEW_KEYS; do
  LINE=$(grep -E "^${KEY}=" .env.example | head -1)
  VALUE=$(echo "$LINE" | cut -d= -f2-)
  echo "$KEY=$VALUE"
done
```

### Step 4: Show User What Will Be Added

Present as a table before making changes (the rows below are examples of the shape, not real variables):

```
| Variable                         | Default Value                    | Action Required? |
|----------------------------------|----------------------------------|------------------|
| DIFY_AGENT_API_TOKEN             | *-for-dev-only                   | YES — development default |
| DIFY_AGENT_SERVER_SECRET_KEY     | (development default)            | YES — development default |
| WEBSOCKET_MAX_HTTP_BUFFER_SIZE   | 10485760                         | No               |
```

**Flag as "Action Required"** any variable that:
- matches `*SECRET*`, `*PASSWORD*`, `*KEY*` (but not `*_TIMEOUT*` or `*_SIZE*`) or `*TOKEN*`
- has an empty value
- carries a **development default**: a value ending in `-for-dev-only`, `difyai123456`, or any value that the release notes say to change in production (`DIFY_AGENT_API_TOKEN`, `DIFY_AGENT_SERVER_SECRET_KEY` since 1.16.1)

### Step 5: Append to .env

After user confirms:

```bash
cd $DOCKER_DIR

echo "" >> .env
echo "# --- Added by dify-ops update on $(date +%Y-%m-%d) ---" >> .env

for KEY in $NEW_KEYS; do
  LINE=$(grep -E "^${KEY}=" .env.example | head -1)
  echo "$LINE" >> .env
done

echo "Added $(echo "$NEW_KEYS" | wc -l | tr -d ' ') new variables to .env"
```

## Optional Settings: envs/

For every `envs/**/*.env` the user created, compare it with its paired `.defaults` (1.19.0 and newer) or `.env.example`. Show new keys, never add them automatically:

```bash
cd $DOCKER_DIR
find envs -name '*.env' -type f | while read -r f; do
  tpl="${f%.env}.defaults"; [ -f "$tpl" ] || tpl="$f.example"
  [ -f "$tpl" ] || { echo "$f: no template (removed upstream?)"; continue; }
  new=$(comm -23 <(grep -oE '^#? ?[A-Z_][A-Z0-9_]*=' "$tpl" | tr -d '# =' | sort -u) <(grep -oE '^[A-Z_][A-Z0-9_]*' "$f" | sort -u))
  [ -n "$new" ] && { echo "$f — keys the defaults file knows and the override does not set:"; echo "$new"; }
done
```

The `.defaults` files also list optional settings as commented examples, so the list is long and mostly keys that are fine unset; look for what the release notes name. An override file that holds a copy of an old template pins the old defaults: show its keys to the user and ask which ones are intentional. Also list files that are new in this release and might be worth using (`git diff --name-status <old>..<new> -- docker/envs`). Creating or editing an override file is the user's decision.

## Cases That Need an Explicit Check

A key-by-key comparison does not catch these; check them after every update to 1.14.1 or newer:

| Key | What changed | Check |
|-----|--------------|-------|
| `COMPOSE_PROFILES` | Default gained `collaboration` in 1.14.1; the `api_websocket` service starts only with that profile | `grep -m1 '^COMPOSE_PROFILES=' .env` — add `collaboration` if an older `.env` lacks it |
| `EDITION` | Renamed `DEPLOYMENT_EDITION` in 1.17.0 (declared in `envs/core-services/api-worker.defaults` from 1.19.0, before in `shared.env.example`) | If `.env` sets `EDITION`, rename it |
| `DIFY_AGENT_RUN_RETENTION_SECONDS` | Default dropped from 3 days to 2 hours in 1.17.1 and the key moved from the root file into `envs/core-services/dify-agent` | An `.env` copied from 1.16.x pins 3 days; a script of 1.18.0 or older drops the key, so the 2-hour default applies — restore the key into `envs/core-services/dify-agent.env` to keep the old value, or leave it out on purpose |
| `DIFY_AGENT_SHELLCTL_AUTH_TOKEN`, `DIFY_AGENT_SHELLCTL_ENTRYPOINT` | Removed in 1.17.0 | Drop from `.env` |
| `EXPOSE_NGINX_PORT`, `EXPOSE_NGINX_SSL_PORT` | Host ports; `NGINX_PORT` is the container-internal port | Read `EXPOSE_NGINX_PORT` for the URL, never `NGINX_PORT` |
| `DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN` | Required from 1.18.0 (the local Agent sandbox needs a non-empty token); the root example ships it empty | Must be non-empty; if empty or absent write `openssl rand -hex 32` into the root `.env` without printing it, and keep it unchanged on later updates |
| `envs/core-services/shared.env` | Retired: from 1.20.0 no service loads it (1.19.0 still reads it before `api-worker.env`) | Rename it to `api-worker.env`; if that exists, merge only missing keys and keep existing values, empty ones included |
| `PLUGIN_DAEMON_KEY`, `PLUGIN_DIFY_INNER_API_KEY` | From 1.19.0 shared by several services, so they are root `.env` inputs | If set in a service override file, move them to the root `.env`; set in one place only they cause HTTP 401 between the daemon and its clients |
| `PASSWORD_PEPPER` | Setting a new one is not a transparent migration (1.18.0) | Never add or change it during an update |
| `OPENAPI_ENABLED` | Default became `true` in 1.20.0, which exposes `/openapi/v1/*` | Set `false` in `.env` when personal access tokens and `difyctl` are not used |
| `SECRET_KEY` | Empty means generated and stored in `volumes/app/storage` (1.14.1) | Never change after start; keep the storage directory in the backup |

Read the "Environment Variable Changes" section of every release between the old and the new version: `gh release view <tag> -R langgenius/dify --json body -q .body`.

## Checking Removed Variables

With the official script of 1.18.0 or older the removed keys are already dropped from `.env`: use "Restore the Dropped Keys" above; a script of 1.19.0 or newer keeps them and names them as local overrides. With the manual algorithm nothing is deleted, so check for variables in `.env` that are no longer in `.env.example`:

```bash
REMOVED_KEYS=$(comm -13 /tmp/dify-env-example-keys /tmp/dify-env-keys)
if [ -n "$REMOVED_KEYS" ]; then
  echo ""
  echo "Note: These variables are in .env but no longer in .env.example:"
  echo "$REMOVED_KEYS"
  echo "They may be deprecated or moved to envs/. Check Dify release notes before removing."
fi
```

Keys that left the root file may simply have moved into a template under `envs/`: search there (`grep -rl "^KEY=" envs`) before calling one deprecated. Do NOT automatically remove these — just inform the user. They may be custom additions.

Clean up the temporary key lists once both checks are done:

```bash
rm -f /tmp/dify-env-example-keys /tmp/dify-env-keys
```

## Security-Sensitive Variables

When adding new variables, flag these for special attention:

| Pattern | Why |
|---------|-----|
| `SECRET_KEY` | Application secret — unique per instance; empty = generated and stored in `volumes/app/storage` |
| `*_PASSWORD` | Database, Redis passwords — must match service config |
| `*_API_KEY` | External service credentials |
| `*_SECRET` | OAuth, webhook secrets |
| `*_TOKEN` | Auth tokens |
| `INIT_PASSWORD` | Initial admin password |
| `*-for-dev-only`, `difyai123456` | Development defaults — never keep them in production |
| `DIFY_AGENT_LOCAL_SANDBOX_AUTH_TOKEN` | Shared secret between the Agent backend and its sandbox; must be non-empty and the same everywhere |

If any of these are added with empty or development defaults, warn the user explicitly.
