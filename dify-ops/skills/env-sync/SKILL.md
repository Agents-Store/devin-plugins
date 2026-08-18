---
name: env-sync
description: >
  Synchronize .env with .env.example for Dify Docker deployments — detect new variables, add
  missing ones with default values, preserve existing customizations. Use when syncing env
  variables, checking for new Dify configuration variables, comparing .env.example vs .env,
  "env sync", "new env variables", "missing environment variables", or after pulling Dify updates.
---

## Location

Both `.env.example` and `.env` live in `dify/docker/` (DOCKER_DIR). All commands below run from that directory.

## Edge Case: .env Does Not Exist

```bash
cd $DOCKER_DIR

if [ ! -f ".env" ]; then
  echo "WARNING: .env does not exist"
  echo "Creating from .env.example..."
  cp .env.example .env
  echo "CREATED .env from .env.example"
  echo ""
  echo "IMPORTANT: Review and set these security-sensitive values:"
  grep -E '^(SECRET_KEY|DB_PASSWORD|REDIS_PASSWORD|INIT_PASSWORD)=' .env
fi
```

After creating, show the user the critical variables that need manual attention.

## Edge Case: Official dify-env-sync.sh

Check if Dify's own sync script exists before using the manual algorithm:

```bash
if [ -f "$DOCKER_DIR/dify-env-sync.sh" ]; then
  echo "Found official dify-env-sync.sh"
  echo "This script:"
  echo "  - One-way sync from .env.example to .env"
  echo "  - Preserves all existing custom values"
  echo "  - Creates timestamped backup in env-backup/"
  echo ""
  echo "Run it with: bash dify-env-sync.sh"
fi
```

Offer the user a choice: use the official script or the manual algorithm below.

## Sync Algorithm

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

For each new key, get the full `KEY=VALUE` line from `.env.example`:

```bash
for KEY in $NEW_KEYS; do
  LINE=$(grep -E "^${KEY}=" .env.example | head -1)
  VALUE=$(echo "$LINE" | cut -d= -f2-)
  echo "$KEY=$VALUE"
done
```

### Step 4: Show User What Will Be Added

Present as a table before making changes:

```
| Variable              | Default Value      | Action Required? |
|-----------------------|-------------------|-----------------|
| NEW_FEATURE_FLAG      | false             | No              |
| PLUGIN_API_KEY        | (empty)           | YES — set value |
| NEW_TIMEOUT_SECONDS   | 300               | No              |
```

**Flag as "Action Required"** any variable matching these patterns:
- `*SECRET*`
- `*PASSWORD*`
- `*KEY*` (but not `*_TIMEOUT*` or `*_SIZE*`)
- `*TOKEN*`
- Value is empty

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

### Step 6: Cleanup

```bash
rm -f /tmp/dify-env-example-keys /tmp/dify-env-keys
```

## Checking Removed Variables

Also check for variables in `.env` that are no longer in `.env.example`:

```bash
REMOVED_KEYS=$(comm -13 /tmp/dify-env-example-keys /tmp/dify-env-keys)
if [ -n "$REMOVED_KEYS" ]; then
  echo ""
  echo "Note: These variables are in .env but no longer in .env.example:"
  echo "$REMOVED_KEYS"
  echo "They may be deprecated. Check Dify release notes before removing."
fi
```

Do NOT automatically remove these — just inform the user. They may be custom additions.

## Security-Sensitive Variables

When adding new variables, flag these for special attention:

| Pattern | Why |
|---------|-----|
| `SECRET_KEY` | Application secret — must be unique per instance |
| `*_PASSWORD` | Database, Redis passwords — must match service config |
| `*_API_KEY` | External service credentials |
| `*_SECRET` | OAuth, webhook secrets |
| `*_TOKEN` | Auth tokens |
| `INIT_PASSWORD` | Initial admin password |

If any of these are added with empty defaults, warn the user explicitly.
