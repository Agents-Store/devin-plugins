---
name: infisical-migration
description: Migrate an OpenClaw instance's secrets from plaintext .env into self-hosted Infisical, then wire the Docker stack to inject them at runtime. Use when the user wants to move .env secrets into Infisical, eliminate plaintext API keys, set up SecretRef-backed config, or asks "migrate my secrets to Infisical". Pairs with the /infisical-migrate command. OAuth/CLI credentials stay in OpenClaw's encrypted store and are out of scope.
---

# OpenClaw → Infisical Secret Migration

Move an OpenClaw instance off plaintext `.env` secrets onto self-hosted Infisical, and wire the Docker stack to inject them at runtime via a wrapper. Verify external CLI syntax with **docs-research** (Infisical CLI: `https://infisical.com/docs/cli/overview`).

Replace `<name>` with the instance name (`team`, `kub`, `pitline`, …; empty for the default `openclaw`).

## Scope

- **In scope:** plaintext API keys/tokens in `.env` and inline secrets referenced by `openclaw.json` SecretRefs.
- **Out of scope:** OAuth credentials and CLI-backend tokens (`openai-codex:default`, Claude CLI tokens). These stay in OpenClaw's **encrypted store** / `auth-profiles.json` — never push them to Infisical. See **provider-auth**.

## Prerequisites

- Machine identity `openclaw-server` exists in Infisical with at least `Viewer` on the target project (one identity serves all instances).
- Host creds at `/etc/openclaw/infisical.env` (mode 600): `INFISICAL_CLIENT_ID` + `INFISICAL_CLIENT_SECRET`. Never commit this file.
- `infisical` CLI installed on the host.
- Reference working instance to copy from: `/docker/openclaw-team/`.
- Self-hosted domain default: `https://k.macstack.ai`.

## Step 1 — Identify the keys to migrate

```bash
# SecretRef ids referenced by openclaw.json
grep -oP '"id":\s*"\K[A-Z_][A-Z0-9_]+' "$OPENCLAW_INSTANCE_DIR/openclaw.json" | sort -u

# Keys present in the instance .env (names only)
grep -oE '^[A-Z_][A-Z0-9_]*=' "$OPENCLAW_INSTANCE_DIR/.env" 2>/dev/null | tr -d '='
```

Also pull in any inline secrets flagged by the **security-audit** skill. The union of these is the set that must exist in Infisical before any plaintext is stripped.

## Step 2 — Authenticate and push to Infisical

```bash
source /etc/openclaw/infisical.env
export INFISICAL_TOKEN=$(infisical login --method=universal-auth \
  --client-id="$INFISICAL_CLIENT_ID" --client-secret="$INFISICAL_CLIENT_SECRET" \
  --domain="$INFISICAL_DOMAIN" --plain --silent)

# Push secrets (typically into the 'prod' environment)
infisical secrets set KEY1=VALUE1 KEY2=VALUE2 \
  --projectId="$PROJECT_ID" --env=prod --domain="$INFISICAL_DOMAIN" --token="$INFISICAL_TOKEN"

# Verify they list back
infisical secrets \
  --projectId="$PROJECT_ID" --env=prod --domain="$INFISICAL_DOMAIN" --token="$INFISICAL_TOKEN"
```

`infisical secrets set` accepts multiple `KEY=VALUE` pairs (and `KEY=@/path/to/file` for file-backed values). Read each value from the existing `.env` — never echo secret values into chat context.

## Step 3 — Server files

Create `.infisical.conf` in the project dir:

```bash
cat > /docker/openclaw-<name>/.infisical.conf <<EOF
INFISICAL_DOMAIN=https://k.macstack.ai
INFISICAL_PROJECT_ID=<PROJECT_ID>
INFISICAL_ENV=prod
INFISICAL_DISABLE_UPDATE_CHECK=true
EOF
chmod 600 /docker/openclaw-<name>/.infisical.conf
```

Copy the wrapper script from the reference instance:

```bash
mkdir -p /docker/openclaw-<name>/scripts
cp /docker/openclaw-team/scripts/openclaw-with-infisical \
   /docker/openclaw-<name>/scripts/openclaw-with-infisical
chmod +x /docker/openclaw-<name>/scripts/openclaw-with-infisical
```

## Step 4 — Patch Dockerfile

Before `USER node`:

```dockerfile
RUN npm install -g @infisical/cli
COPY --chmod=0755 scripts/openclaw-with-infisical /usr/local/bin/openclaw-with-infisical
```

Replace the ENTRYPOINT at the end:

```dockerfile
ENTRYPOINT ["tini", "-s", "--", "/usr/local/bin/openclaw-with-infisical"]
CMD ["node", "openclaw.mjs", "gateway", "--allow-unconfigured"]
```

## Step 5 — Patch docker-compose.yml

For **both** services (`openclaw-gateway-<name>` and `openclaw-cli-<name>`), set `env_file`:

```yaml
env_file:
  - .env
  - /etc/openclaw/infisical.env
  - .infisical.conf
```

For the **CLI service only**, replace `entrypoint`:

```yaml
entrypoint: ["tini", "-s", "--", "/usr/local/bin/openclaw-with-infisical", "node", "dist/index.js"]
```

## Step 6 — Build and start

```bash
cp /docker/openclaw-<name>/.env /docker/openclaw-<name>/.env.bak-pre-infisical
cd /docker/openclaw-<name>
docker compose build openclaw-gateway-<name>
docker compose down && docker compose up -d
docker compose logs openclaw-gateway-<name> --tail=50
```

**Success indicators:** `Injecting N Infisical secrets`, `[gateway] ready`, no `SecretRefResolutionError`, no crash-loop.

**On crash-loop with `SecretRefResolutionError`:** a key is missing in Infisical — either add the key, or disable the skill that needs it in `openclaw.json` with `"enabled": false`.

## Step 7 — Strip plaintext residue

Reduce `.env` to infrastructure-only vars:

```
OPENCLAW_IMAGE=openclaw:<name>
OPENCLAW_CONFIG_DIR=/root/.openclaw-<name>
OPENCLAW_WORKSPACE_DIR=/root/.openclaw-<name>/workspace
OPENCLAW_GATEWAY_PORT=<port>
OPENCLAW_BRIDGE_PORT=<port>
OPENCLAW_GATEWAY_BIND=lan
OPENCLAW_TZ=UTC
```

Migrate the Anthropic API key in `auth-profiles.json` from a literal to a SecretRef:

```json
"keyRef": { "source": "env", "provider": "default", "id": "ANTHROPIC_API_KEY" }
```

Validate JSON, remove an internal `.openclaw-<name>/.env` if it contains only secrets, then restart:

```bash
python3 -c "import json; json.load(open('/root/.openclaw-<name>/agents/main/agent/auth-profiles.json')); print('OK')"
cd /docker/openclaw-<name> && docker compose down && docker compose up -d
```

## Step 8 — Verify

```bash
docker compose exec openclaw-gateway-<name> openclaw secrets audit --check
```

Expected: `plaintext=1, unresolved=0, shadowed=0, legacy=0`. The remaining `plaintext=1` is `models.json:providers.codex.apiKey` (sentinel `"codex-app-server"`, **not** a real secret — false positive, do not touch). Then send a message to the instance's bot and confirm it replies. When working, remove the backup: `rm /docker/openclaw-<name>/.env.bak-pre-infisical`.

## Troubleshooting matrix

| Symptom | Cause | Fix |
|---------|-------|-----|
| `SecretRefResolutionError: missing or empty` | Key not in Infisical | Add key, or disable the skill in `openclaw.json` |
| `Injecting 0 secrets` | Identity lacks project access | Add the identity to the project in Infisical |
| Immediate crash-loop | `.infisical.conf` typo | Verify PROJECT_ID and env slug |
| `infisical: command not found` | Image not rebuilt | `docker compose build` |
| `unresolved=N` in audit but logs show `Injecting` | Audit ran outside wrapper context (cosmetic) | Inspect injected env: `cat /proc/$(pgrep -f "node openclaw")/environ \| tr "\0" "\n" \| grep -E "_API_KEY\|_TOKEN" \| cut -d= -f1 \| sort` |

## Maintenance commands

| Operation | Commands |
|-----------|----------|
| Rotate a key | Update in Infisical → `docker compose restart openclaw-gateway-<name>` |
| Add a key for a new skill | Add to Infisical + add SecretRef in `openclaw.json` → restart |
| Remove a key | Remove from Infisical + disable the skill in `openclaw.json` → restart |

## Critical rules

- Before stripping `.env`, ensure **every** SecretRef target exists in Infisical (Step 1 grep).
- Never commit `.infisical.conf` or `/etc/openclaw/infisical.env`.
- OAuth credentials (`openai-codex:default`, Claude CLI tokens) stay in OpenClaw's encrypted store — out of scope (see **provider-auth**).
- After OpenClaw version upgrades, re-run `openclaw secrets audit --check` to catch new SecretRef surfaces (see **release-migration**).
- Never print secret **values** into chat context — work with key names.
