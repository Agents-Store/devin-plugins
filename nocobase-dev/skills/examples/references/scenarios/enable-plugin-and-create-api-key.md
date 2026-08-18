# Scenario 3 — Enable the API Keys plugin and mint a token

Goal: turn on the `api-keys` plugin via CLI, create an API key over HTTP, then make an authorised call using the new token. The full bootstrap path for any agent integration.

## Prerequisites

- Admin-level access (CLI on the host or admin token).
- `nb` CLI installed and pointed at the right NocoBase project.

```bash
export NB_URL="https://app.example.com"
export ADMIN_TOKEN="<existing-admin-bearer-token>"
H='Authorization: Bearer '"${ADMIN_TOKEN}"
J='Content-Type: application/json'
```

## 1. Enable the plugin (CLI)

```bash
nb pm enable api-keys
```

Verify:

```bash
nb pm list | grep api-keys
```

Should report `enabled`. If it isn't already installed: `nb pm add @nocobase/plugin-api-keys` first, then enable.

## 2. Create a non-expiring key for a bot identity (API)

The token inherits the role you specify — pick the *least-privileged* role that can do the bot's job. `nocobase-acl-manage` covers role design.

```bash
NEW_KEY=$(curl -s -X POST -H "$H" -H "$J" \
  -d '{"name":"agent-bot","role":"member"}' \
  "${NB_URL}/api/apiKeys:create" \
  | jq -r '.data.token')

echo "store this immediately, it is shown only once: ${NEW_KEY}"
```

For an expiring key, add `"expiresIn": "30d"` to the payload (NocoBase accepts ISO durations and absolute timestamps).

## 3. Use the new token

```bash
curl -H "Authorization: Bearer ${NEW_KEY}" \
     "${NB_URL}/api/app:getInfo"
```

Should return `200` with the app metadata. A `403` here means the role attached to the key cannot read `app:getInfo` — check the role policy.

## 4. List existing keys

```bash
curl -H "$H" "${NB_URL}/api/apiKeys:list" \
  | jq '.data[] | {id, name, role, expiresIn, createdAt}'
```

## 5. Revoke the key when the bot is decommissioned

```bash
KEY_ID=$(curl -s -H "$H" "${NB_URL}/api/apiKeys:list" \
  | jq -r '.data[] | select(.name=="agent-bot") | .id')

curl -X POST -H "$H" \
     "${NB_URL}/api/apiKeys:destroy?filterByTk=${KEY_ID}"
```

## Rotation

There is no in-place key rotation. Rotate by:

1. Create the new key (`apiKeys:create`).
2. Deploy the new value to the bot.
3. Verify a request succeeds with the new token.
4. Delete the old key (`apiKeys:destroy`).

## Why both surfaces

- `nb pm enable` is the cleanest way to turn on a plugin — no JSON payload, no auth setup, atomic with respect to the running app.
- `apiKeys:*` endpoints are HTTP-only because the key needs to be returned in a response, and the CLI does not have a "give me back this string" channel.

## Related skills

- `auth` — what to do with the token once you have it; how to swap it out for an OAuth flow if needed.
- `nocobase-acl-manage` — design the role the key inherits before issuing it.
- `nocobase-plugin-manage` — full grammar of `nb pm` (`add`, `remove`, `update`, version pinning).
