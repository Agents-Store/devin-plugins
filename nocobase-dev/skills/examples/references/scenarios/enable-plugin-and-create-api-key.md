# Scenario 3 — Enable the API Keys plugin and mint a token

Goal: make sure the `api-keys` plugin is on (via CLI), create an API key over HTTP, then make an authorised call using the new token. The full bootstrap path for any agent integration.

## Prerequisites

- Admin-level access (CLI on the host or admin token).
- `nb` CLI installed with an env for the target NocoBase (`nb env add …`, see `cli-recipes`); add `-e <env>` to the commands below if it is not the current env.

```bash
export NB_URL="https://app.example.com"
export ADMIN_TOKEN="<existing-admin-bearer-token>"
H='Authorization: Bearer '"${ADMIN_TOKEN}"
J='Content-Type: application/json'
```

## 1. Make sure the plugin is enabled (CLI)

`API keys` is a built-in plugin and is enabled by default, so this step is usually a check:

```bash
nb plugin list | grep plugin-api-keys
```

Should report it as enabled. If it is disabled, enable it:

```bash
nb plugin enable @nocobase/plugin-api-keys
```

`nb plugin` takes full package names and has no install-from-registry command; a plugin that is not bundled is brought in with `nb plugin import <archive|url|npm-spec>` first, then enabled.

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

- `nb plugin enable` is the cleanest way to turn on a plugin — no JSON payload, atomic with respect to the running app, and the env carries the credential.
- `apiKeys:*` return the key once, in the response body, so the REST form shows the exact payload. The CLI generates an `nb api api-keys` group from the same OpenAPI schema (confirm with `nb api api-keys --help`); use it when the env is already set up, and keep the curl form for hosts without `nb`.

## Related skills

- `auth` — what to do with the token once you have it; how to swap it out for an OAuth flow if needed.
- `nocobase-acl-manage` — design the role the key inherits before issuing it.
- `nocobase-plugin-manage` — full grammar of `nb plugin` (`list`, `enable`, `disable`, `import`) and its error handling.
