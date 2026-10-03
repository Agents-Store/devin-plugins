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
- Session tokens expire — just re-run the `setup` login to get a fresh one. For unattended use, switch to a **personal access token** (see `api-reference` → `auth-sessions.md`).
- **A PAT that suddenly returns `401` has probably expired** (v11.9+ lets a PAT carry `expires_at`; an expired PAT is rejected with `401`, like a revoked one). Check the token's metadata with `GET /users/{user_id}/tokens` (the secret is never returned): a non-zero `expires_at` that is in the past means expired (it stays listed until the hourly reaper removes it), `0` means no expiry, `is_active:false` means disabled. Also read the owner's direct messages from the system bot — v11.10+ warns 7, 3 and 1 days before expiry. Fix: `POST /users/tokens/rotate` (new secret, old one dies immediately) or mint a new PAT with a fresh `expires_at`. A token created without `expires_at` has no expiry at all, so a `401` there means it was revoked or disabled (an admin can also bulk-revoke non-compliant tokens, see `auth-sessions.md`).
- Creating a PAT fails on a server whose admin set `MaximumPersonalAccessTokenLifetimeDays` to a non-zero value: the policy requires an expiry within that many days — send `expires_at` (Unix ms).

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

## A post shows my name instead of the custom name/icon (v12.0)

**Cause:** from Mattermost v12.0 the server **silently strips** `from_webhook`, `from_bot`, `from_oauth_app`, `from_plugin`, `override_username`, `override_icon_url`, `override_icon_emoji` and `webhook_display_name` from `props` on posts made with a user session or PAT. The post is created, no error is returned, and the author is the authenticating user.

- Fix: post through an **incoming webhook** (`/hooks/<id>` with `username`/`icon_url`, allowed when the System Console overrides are enabled — `ServiceSettings.EnablePostUsernameOverride` / `EnablePostIconOverride`), a **slash command response**, or a **bot account** (posts as the bot). See `api-reference` → `integrations.md`.
- On a v11 server the old trick still works — it is going away, do not build new automation on it.

## `last_viewed_at` is `-1` (or missing) on channel members (v12.0)

**Cause:** for *other* users' memberships the API sanitises `last_viewed_at`/`last_update_at` to `-1` (read as 1969-12-31). From v12.0 the fields are **omitted** instead. Your own membership keeps real values (`0` = never viewed). Code that reads the `-1` sentinel or assumes the field is always present must treat "absent" and `-1` the same way. Affects `GET /channels/{id}/members[/{user_id}]`, `POST /channels/{id}/members[/ids]`, `GET /users/{id}/teams/{team_id}/channels/members` and `GET /users/{id}/channel_members`.

## Optional convenience MCP

If you'd rather call tools than curl for the most common read/post operations, use the **official Mattermost MCP server, built into the Mattermost Agents plugin** (Mattermost Server v11.2+). Admin: System Console → Plugins → Agents → Model Context Protocol (MCP) → set **Enable Mattermost MCP Server (HTTP)** to true; endpoint (streamable HTTP, no SSE): `${MATTERMOST_API_URL%/}/plugins/mattermost-ai/mcp-server/mcp`; auth: a personal access token as `Authorization: Bearer` (works without any extra setup) or OAuth 2.0 (an admin must first set *Integrations → Integration Management → Enable OAuth 2.0 Service Provider*; add *Enable OAuth 2.0 Dynamic Client Registration* for automatic client registration). It exposes 16 native tools (`read_post`, `read_channel`, `search_posts`, `create_post`, `dm`, `group_message`, `create_channel`, `get_channel_info`, `get_team_info`, `search_users`, `get_channel_members`, `add_channel_member`, `get_user_channels`, `get_team_members`, `add_team_member`, `list_agents`) plus an extended catalogue loaded on demand through `search_tools` / `load_tool`; read-only tools work on every licence level, state-changing tools need Enterprise or above, and every call runs with the calling user's own permissions. Docs: https://docs.mattermost.com/administration-guide/configure/agents-admin-guide.html#mattermost-mcp-server — and the announcement https://mattermost.com/blog/mattermost-mcp-server/. Community servers (`kakehashi-inc/mcp-server-mattermost`, `pvev/mattermost-mcp`) also exist.

None of these cover admin, RBAC or integration management — use the REST endpoints in `api-reference` for those. MCP is not a dependency of this plugin.
