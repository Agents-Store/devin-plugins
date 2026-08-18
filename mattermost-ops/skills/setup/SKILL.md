---
name: setup
description: This skill should be used when the user wants to "connect to Mattermost", "log into Mattermost", "authenticate with Mattermost", "get a Mattermost token", "set up Mattermost access", or before running any Mattermost REST API call. Establishes the session token (read from the login Token response header) and the global request conventions (base path, headers, pagination, rate limits).
---

# Mattermost Setup & Authentication

Establish access to a Mattermost instance and learn the conventions every other call depends on. Do this once per session before any other Mattermost operation.

## Environment variables

The user sets these in their shell or repo `.env`. Read them — never hardcode or print credentials.

| Variable | Required | Meaning |
|----------|----------|---------|
| `MATTERMOST_API_URL` | yes | Server root URL, e.g. `https://mattermost.mycompany.com`. The API lives under `${MATTERMOST_API_URL}/api/v4`. |
| `MATTERMOST_ADMIN_USERNAME` | yes | Username **or** email used to obtain a token. |
| `MATTERMOST_ADMIN_PASSWORD` | yes | Password for that account. For system administration it must hold the **System Admin** role. |
| `MATTERMOST_TOKEN` | derived | Session token obtained at runtime from the login call below; reused for the rest of the session. |

If `MATTERMOST_API_URL` is missing, ask the user for it. Always normalize the trailing slash with `${MATTERMOST_API_URL%/}` — the API path is built as `${MATTERMOST_API_URL%/}/api/v4/...`. Pass the server **root**, not a URL that already ends in `/api/v4`.

## Step 1 — Obtain the session token

**The most important Mattermost-specific fact: the session token is returned in the `Token` HTTP response *header*, not in the JSON body.** The body holds the user object. You must read headers (`curl -i`/`-si`) to capture the token — this is the #1 cause of "login worked but I have no token" failures.

```bash
# Log in and capture the session token from the response header.
MATTERMOST_TOKEN=$(curl -si -X POST "${MATTERMOST_API_URL%/}/api/v4/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"login_id\":\"${MATTERMOST_ADMIN_USERNAME}\",\"password\":\"${MATTERMOST_ADMIN_PASSWORD}\"}" \
  | awk 'tolower($1)=="token:"{print $2}' | tr -d '\r')
export MATTERMOST_TOKEN
[ -n "$MATTERMOST_TOKEN" ] && echo "Got a session token." || echo "No Token header — check credentials/URL."
```

Notes:
- `login_id` accepts the **username or the email** (or AD/LDAP ID). If one fails, try the other.
- Add `"token":"<mfa-code>"` to the body if the account has MFA enabled.
- The JSON body (what `curl` prints after the headers) is the logged-in user object — `id`, `username`, `email`, `roles`. The presence of `system_admin` in `.roles` confirms admin rights.

## Step 2 — Verify access

```bash
curl -s -H "Authorization: Bearer ${MATTERMOST_TOKEN}" \
  "${MATTERMOST_API_URL%/}/api/v4/users/me" | jq '{id, username, email, roles}'
```

A `200` with your user object confirms the token works. Check `roles` contains `system_admin` before attempting any system-administration operation.

## When the token expires

Session tokens expire and are revoked on logout. When a call returns `401` mid-session, simply re-run Step 1 to obtain a fresh token. To end a session deliberately: `POST /api/v4/users/logout` with the Bearer header.

## Personal access tokens (preferred for unattended integrations)

For long-lived, non-interactive automation, a **personal access token (PAT)** is better than repeatedly logging in with a password. A system admin enables PATs in the System Console, then issues one:

```bash
# As admin, mint a PAT for a user (userId "me" = the current user)
curl -s -X POST -H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json" \
  -d '{"description":"automation token"}' \
  "${MATTERMOST_API_URL%/}/api/v4/users/me/tokens" | jq '{id, token}'
```

A PAT is used **identically** to a session token — `Authorization: Bearer <pat>` — but never expires until revoked. If the user already has a PAT, they can set `MATTERMOST_TOKEN` to it directly and skip Step 1. See `api-reference` → `references/auth-sessions.md`.

## Global conventions (apply to every call)

These rules hold across the entire API. Internalize them now so individual operations stay short.

- **Base path**: every endpoint is `${MATTERMOST_API_URL%/}/api/v4/...`.
- **Headers**: send `Authorization: Bearer ${MATTERMOST_TOKEN}` on authenticated calls and `Content-Type: application/json` on any request with a JSON body. File uploads use `multipart/form-data` instead.
- **No optimistic version locking.** Unlike many APIs, Mattermost edits do not require a `version`/`etag` in the body. Update with the resource's dedicated verb:
  - `PUT /api/v4/<resource>/{id}` — full update (send the complete object).
  - `PUT /api/v4/<resource>/{id}/patch` — partial update (send only changed fields). Most resources (users, channels, teams, posts) expose a `/patch` variant — prefer it so you change only what was asked.
- **Pagination**: list endpoints take `?page=<n>&per_page=<size>` where **`page` is 0-indexed** and `per_page` maxes at 200 (default 60). Responses are plain JSON arrays — walk pages by incrementing `page` until a short/empty page returns. A few endpoints (e.g. channel search, threads) return an object with a paging cursor instead; check the reference file.
- **IDs, not names.** The API addresses objects by 26-character IDs, but humans use names. Resolve first with the `by_name`/`by_username`/`by_email` endpoints (e.g. `GET /teams/name/{team_name}`, `GET /teams/{team_id}/channels/name/{channel_name}`, `GET /users/username/{username}`) before acting. A `404` usually means a name was passed where an ID was expected.
- **Rate limiting**: responses carry `X-Ratelimit-Limit`, `X-Ratelimit-Remaining`, and `X-Ratelimit-Reset`. Exceeding the limit returns HTTP `429` (`limit exceeded`) — back off until the reset epoch. Inspect with `curl -s -D - ...`.
- **Permissions**: a `403` means the account lacks the permission for that action — respect it, don't try to route around it. System-wide endpoints (`/system/*`, `/config`, `/roles`, `/ldap`, `/data_retention`) require the System Admin role.

## Next steps

- For everyday workflows (post a message, create a channel, onboard users, build a report) → use the `common-operations` skill.
- For the full endpoint catalog of every resource → load the `api-reference` skill and open the relevant `references/*.md` file (or the bundled OpenAPI spec).
- When a call fails → use the `troubleshoot` skill.
