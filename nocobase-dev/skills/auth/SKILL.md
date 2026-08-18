---
name: auth
description: "Use when the user wants to authenticate to a NocoBase v2 instance, asks \"how do I get a token for NocoBase\", \"how do I log in via API\", \"why is my request returning 401 from NocoBase\", or needs working curl/Node samples that send the bearer token. Covers the upstream login flow (NB_USER + NB_PASSWORD → auth:signIn → token), the long-lived API Key path, and the OAuth IdP path."
---

# Authentication — NocoBase v2

NocoBase v2 accepts `Authorization: Bearer <token>` on every `/api/` request. The OpenAPI spec declares this as the `api-key` security scheme (HTTP bearer). The variable names below match what the upstream `nocobase/skills` library uses — keep them identical in your `.env` so hand-maintained and upstream skills agree on one truth.

## Env vars contract

```bash
NB_URL=https://app.example.com           # required
NB_USER=admin@example.com                # required for Path A (sign-in)
NB_PASSWORD=<password>                   # required for Path A
NB_TOKEN=eyJhbGciOi...                   # optional, skips sign-in (Path B)
# NOCOBASE_API_TOKEN is a synonym for NB_TOKEN — upstream auth.ts reads either.
```

## Path A — Sign-in with admin credentials (upstream default)

This is what the upstream `nocobase-dsl-reconciler` skill uses. Username + password → `auth:signIn` → short-lived bearer token. Best for scripts that are OK re-logging in periodically.

```bash
export NB_URL="https://app.example.com"
export NB_USER="admin@example.com"
export NB_PASSWORD="<password>"

# 1. Sign in and capture the token
TOKEN=$(curl -sS -X POST "${NB_URL}/api/auth:signIn" \
  -H "Content-Type: application/json" \
  -d '{"account":"'"$NB_USER"'","password":"'"$NB_PASSWORD"'"}' \
  | jq -r '.data.token')

# 2. Use it as a Bearer
curl -H "Authorization: Bearer $TOKEN" \
     "${NB_URL}/api/collections:list"
```

The `NB_USER` value is whatever email you set during `nb init --ui` — the root-admin account.

## Path B — Long-lived API Key (when you want a static token)

Useful when you don't want to re-login every call: cron jobs, agents, deploy hooks, third-party integrations.

### 1. Enable the API Keys plugin

```bash
nb pm enable api-keys
```

The `nocobase-plugin-manage` skill covers `nb pm` semantics and error handling.

### 2. Create a token in the admin UI

Open NocoBase → `Settings → API keys → Create`:

- **Name** — short identifier (e.g. `agent-bot`).
- **Role** — pick the role whose permissions the key inherits. The token can do exactly what the role can; no more.
- **Expiration** — date or `Never`.

Copy the token; it is shown only once. Put it in `NB_TOKEN`.

### 3. Send authorised requests

```bash
export NB_URL="https://app.example.com"
export NB_TOKEN="<token-from-admin-ui>"

# List collections
curl -H "Authorization: Bearer ${NB_TOKEN}" \
     "${NB_URL}/api/collections:list"

# Create a record in the `posts` collection
curl -X POST \
     -H "Authorization: Bearer ${NB_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"title":"hello","body":"first post"}' \
     "${NB_URL}/api/posts:create"
```

### 4. Node.js

```js
// fetch (Node 18+)
const res = await fetch(`${process.env.NB_URL}/api/collections:list`, {
  headers: { Authorization: `Bearer ${process.env.NB_TOKEN}` },
});
const data = await res.json();
```

```js
// axios
import axios from "axios";

const nb = axios.create({
  baseURL: `${process.env.NB_URL}/api`,
  headers: { Authorization: `Bearer ${process.env.NB_TOKEN}` },
});

const { data } = await nb.get("/collections:list");
```

### Rotation and revocation

- Tokens are revoked from the same screen (`Settings → API keys → Delete`).
- Rotation: create the new token first, deploy it, then delete the old one — there is no in-place rotation.
- Tokens inherit the role at issuance. If the role is later restricted, the token is restricted on the next request.

## Path C — OAuth (IdP: OAuth, for end-user SSO flows)

For human users signing in through Keycloak / Auth0 / Google / Okta. Not for backend scripts — use Path A or B for those.

### 1. Enable the IdP: OAuth plugin

```bash
nb pm enable @nocobase/plugin-oidc-client
```

Plugin name may also appear as `oidc-client` or `idp-oauth` — `nb pm list` to confirm.

### 2. Configure the provider in the admin UI

`Settings → Authentication → Add → OAuth (OIDC)`:

- **Issuer URL** — your IdP's discovery URL.
- **Client ID / Client Secret** — from the IdP.
- **Redirect URI** — `${NB_URL}/api/auth:redirect?authenticator=<your-name>`.
- **Scopes** — typically `openid profile email`.

### 3. Authorisation-code flow

```text
Browser → GET ${NB_URL}/api/auth:redirect?authenticator=<name>
       → IdP login screen
       → Browser ← 302 to ${NB_URL}/?code=…&state=…
       → POST ${NB_URL}/api/auth:signIn?authenticator=<name>
              { code, state } → returns NocoBase access token (same shape as Path A)
```

The token you get back is the same shape as Path A — put it in `NB_TOKEN` for downstream calls.

## Choosing the right path

| Use case | Pick |
|---|---|
| Local dev, scripts that can store the admin password | **Path A** (sign-in, matches upstream skills) |
| CI job, cron, agent — wants a static token in env | **Path B** (API Key) |
| Multiple integrations needing per-key auditing | **Path B** (one API Key per integration) |
| End user clicking "Sign in with Google/Keycloak" in your UI | **Path C** (OAuth) |

## Common 401 / 403 causes

- Missing or wrong `Authorization` header — value is exactly `Bearer <token>`, single space, case-sensitive `Bearer`.
- Token expired (API Key with explicit expiration, sign-in token after TTL, OAuth access token).
- Role attached to the token has no permission — check `nocobase-acl-manage`.
- Plugin providing the token type is disabled — `nb pm list` to confirm `api-keys` or `@nocobase/plugin-oidc-client` is enabled.
- Multi-app instance — make sure the `X-App` header / hostname matches the app the token was issued for.

## OpenAPI declaration

The full spec at `${CLAUDE_PLUGIN_ROOT}/references/openapi/nocobase.json` declares:

```json
"securitySchemes": {
  "api-key": { "type": "http", "scheme": "bearer" }
}
```

All three paths (sign-in, API Key, OAuth) produce a bearer token that satisfies this scheme — the server validates the token, not its origin.
