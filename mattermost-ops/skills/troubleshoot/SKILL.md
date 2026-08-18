---
name: troubleshoot
description: This skill should be used when a Mattermost REST API call fails or behaves unexpectedly — "Mattermost returns 401 / 403 / 404 / 429", "Mattermost login fails", "I got no token after login", "can't find the channel/user", "pagination missing results", "permission denied", or any Mattermost error response. Maps symptoms to causes and fixes.
---

# Mattermost Troubleshooting

Match the symptom, apply the fix. Most Mattermost API failures come from an empty/expired token, a name used where an ID is required, or a missing System Admin permission.

## Login "succeeds" but I have no token

**Cause:** the session token is in the **`Token` response header**, not the JSON body. Reading only the body (`curl -s`) discards it.

Fix — use `-i`/`-si` and extract the header:
```bash
MATTERMOST_TOKEN=$(curl -si -X POST "${MATTERMOST_API_URL%/}/api/v4/users/login" \
  -H "Content-Type: application/json" \
  -d "{\"login_id\":\"${MATTERMOST_ADMIN_USERNAME}\",\"password\":\"${MATTERMOST_ADMIN_PASSWORD}\"}" \
  | awk 'tolower($1)=="token:"{print $2}' | tr -d '\r')
```
If it's still empty, the login itself failed — see below.

## Login itself fails (401 on `/users/login`)

- `login_id` accepts **username or email** — try the other one.
- Verify `MATTERMOST_API_URL` is the server **root** (e.g. `https://mm.example.com`), not a URL ending in `/api/v4`. The skill builds `${MATTERMOST_API_URL%/}/api/v4/users/login`.
- If the account has MFA, add `"token":"<6-digit-code>"` to the body.
- Repeated failures can trip the login rate limit / account lockout — wait, then retry.

## 401 Unauthorized (mid-session)

**Cause:** the session token expired or was revoked (e.g. logout, password change, "revoke all sessions").

- Confirm the header is exactly `Authorization: Bearer ${MATTERMOST_TOKEN}` (Bearer, not `Token`).
- Session tokens expire — just re-run the `setup` login to get a fresh one. For unattended use, switch to a **personal access token** (never expires until revoked; see `api-reference` → `auth-sessions.md`).

## 403 Forbidden

**Cause:** authenticated, but the account lacks permission for that action.

- System endpoints (`/config`, `/system/*`, `/license`, `/roles`, `/ldap`, `/data_retention`, `/compliance`, `/plugins`) require the **System Admin** role. Confirm with `GET /users/me` → `.roles` contains `system_admin`.
- Team/channel actions need the matching team/channel role or a scheme that grants the permission. Check `GET /roles/name/{role_name}`.
- A `403` is a real boundary — don't try to route around it; ask the user to use an account with the right role.

## 404 / "Not found" or "Unable to find the …"

**Cause:** almost always a **name used where a 26-char ID is required** (or the object is archived/deleted).

- Resolve first: `GET /teams/name/{name}`, `GET /teams/{team_id}/channels/name/{channel_name}`, `GET /users/username/{username}`, `GET /users/email/{email}`.
- Archived teams/channels need `?include_deleted=true` on some lookups, or restore them (`POST /channels/{id}/restore`).

## 429 Too Many Requests

**Cause:** rate limiting. Mattermost limits requests per second per session/IP.

- Inspect headers: `curl -s -D - ... | grep -i x-ratelimit`. `X-Ratelimit-Reset` is the UTC epoch when the window resets.
- Back off until reset; add a small `sleep` between bulk calls; raise `per_page` (up to 200) to make fewer requests.

## A list seems to be missing rows

**Cause:** pagination. List endpoints return one page (default 60).

- Walk pages with `?page=0&per_page=200`, then `page=1`, … until a page returns fewer than `per_page` rows (or empty). **`page` is 0-indexed.**
- Some endpoints (channel/post search, threads) wrap results in an object with its own cursor — check the reference file for that resource.

## A write returns 400 / "invalid"

- Send `-H "Content-Type: application/json"` on any request with a body; omitting it is a common 400 cause.
- Required fields differ per resource — e.g. creating a channel needs `team_id`, `name`, `display_name`, `type`. Check the reference file.
- For DMs/GMs the body is a **bare JSON array of user ids**, not an object.
- Uploads (`/files`, `/emoji`, `/plugins`, images) are **multipart** (`-F`), not JSON.

## Optional convenience MCP

If you'd rather call tools than curl for the most common read/post operations, the official Mattermost MCP server (PAT auth; read/search/create posts) and community servers (`kakehashi-inc/mcp-server-mattermost`, `pvev/mattermost-mcp`) exist. They cover a small subset — for full coverage (admin, RBAC, integrations) use the REST endpoints in `api-reference`. These are not dependencies of this plugin.
