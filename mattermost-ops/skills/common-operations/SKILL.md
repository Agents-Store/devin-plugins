---
name: common-operations
description: This skill should be used when the user wants to do collaboration work in Mattermost — "post a message to a channel", "send a DM in Mattermost", "create a channel", "add users to a team/channel", "deactivate a user", "create a team", "set up a webhook", "react to a post", or any everyday Mattermost operation. Provides plain-language workflows that drive the REST API and route to the exact endpoints.
---

# Mattermost Common Operations

Plain-language playbooks for everyday Mattermost work. Each one drives the REST API. For exact endpoint signatures and every field, open the `api-reference` skill's matching `references/*.md` file (named in each workflow).

## Before anything: ensure a token

If `MATTERMOST_TOKEN` is not already set this session, run the `setup` skill's login first (it reads the token from the login **`Token` response header**). Every call below assumes `MATTERMOST_TOKEN` and `MATTERMOST_API_URL` are set and uses `Authorization: Bearer ${MATTERMOST_TOKEN}`.

## The golden rules (why workflows look the way they do)

1. **Resolve names to IDs once.** Users say "the Engineering team, #general"; the API wants 26-char IDs. Resolve with the `by_name`/`by_username`/`by_email` endpoints first and keep the IDs. A `404` usually means a name slipped through where an ID was needed.
2. **Patch, don't replace.** Prefer `PUT /…/{id}/patch` so you change only what was asked. There is **no `version` field** to send — Mattermost has no optimistic locking.
3. **Mind the channel type.** `O` public, `P` private, `D` direct, `G` group. DMs/GMs are created (or fetched) by POSTing user-id arrays, not by name.
4. **Confirm before destructive or system-wide actions.** `DELETE`, user deactivation, and any `/config`, `/license`, `/data_retention`, `/plugins` write is high-impact — show the user what will change first.

## Workflow: resolve a team & channel by name

```bash
TEAM_ID=$(curl -s -H "Authorization: Bearer ${MATTERMOST_TOKEN}" \
  "${MATTERMOST_API_URL%/}/api/v4/teams/name/engineering" | jq -r .id)
CHANNEL_ID=$(curl -s -H "Authorization: Bearer ${MATTERMOST_TOKEN}" \
  "${MATTERMOST_API_URL%/}/api/v4/teams/${TEAM_ID}/channels/name/general" | jq -r .id)
```
(→ `teams.md`, `channels.md`)

## Workflow: post a message

```bash
curl -s -X POST -H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"channel_id\":\"${CHANNEL_ID}\",\"message\":\"Hello team :wave:\"}" \
  "${MATTERMOST_API_URL%/}/api/v4/posts" | jq '{id, message}'
```
- **Reply in a thread**: add `"root_id":"<root_post_id>"`.
- **Attach a file**: upload first (`POST /files`), then pass `"file_ids":["<id>"]` (→ `files-emoji.md`).
- **React**: `POST /reactions` with `{"user_id","post_id","emoji_name"}`. (→ `posts.md`)

## Workflow: send a direct message

```bash
# DM = a channel between two user ids
ME=$(curl -s -H "Authorization: Bearer ${MATTERMOST_TOKEN}" "${MATTERMOST_API_URL%/}/api/v4/users/me" | jq -r .id)
OTHER=$(curl -s -H "Authorization: Bearer ${MATTERMOST_TOKEN}" "${MATTERMOST_API_URL%/}/api/v4/users/username/alice" | jq -r .id)
DM=$(curl -s -X POST -H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json" \
  -d "[\"${ME}\",\"${OTHER}\"]" "${MATTERMOST_API_URL%/}/api/v4/channels/direct" | jq -r .id)
curl -s -X POST -H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"channel_id\":\"${DM}\",\"message\":\"ping\"}" "${MATTERMOST_API_URL%/}/api/v4/posts" >/dev/null
```
For a group message, POST an array of 3–8 ids to `/channels/group`. (→ `channels.md`)

## Workflow: create a channel and add members

1. **Create** — `POST /channels` with `{"team_id","name","display_name","type":"O"}` (`P` for private). (→ `channels.md`)
2. **Add a user** — `POST /channels/{channel_id}/members` with `{"user_id"}`.
3. **Set header/purpose** — `PUT /channels/{channel_id}/patch` with `{"header":"...","purpose":"..."}`.
4. **Make someone a channel admin** — `PUT /channels/{channel_id}/members/{user_id}/roles` with `{"roles":"channel_user channel_admin"}`.

## Workflow: create a team and invite people

1. `POST /teams` with `{"name","display_name","type":"O"}`. (→ `teams.md`)
2. Add existing users: `POST /teams/{team_id}/members` (one) or `/members/batch` (many).
3. Email-invite new people: `POST /teams/{team_id}/invite/email` with an array of emails.

## Workflow: manage users

1. **Find** — `GET /users/username/{username}` or `POST /users/search` with `{"term"}`. (→ `users.md`)
2. **Create** — `POST /users` with `{"email","username","password"}`.
3. **Deactivate** (reversible) — `PUT /users/{user_id}/active` with `{"active":false}`. Confirm first.
4. **Grant admin** — `PUT /users/{user_id}/roles` with `{"roles":"system_user system_admin"}`.

## Workflow: wire an incoming webhook

```bash
HOOK=$(curl -s -X POST -H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"channel_id\":\"${CHANNEL_ID}\",\"display_name\":\"CI\"}" \
  "${MATTERMOST_API_URL%/}/api/v4/hooks/incoming" | jq -r .id)
echo "Post to: ${MATTERMOST_API_URL%/}/hooks/${HOOK}"
```
(→ `integrations.md`)

## Workflow: report & audit

1. Counts: `GET /users/stats`, `GET /teams/{team_id}/stats`, `GET /channels/{channel_id}/stats`.
2. Analytics: `GET /analytics/old?name=standard` (admin). (→ `system-admin.md`)
3. Search messages: `POST /teams/{team_id}/posts/search` with `{"terms":"outage from:alice after:2026-01-01"}`. (→ `posts.md`)
4. List with pagination: walk `?page=0&per_page=200`, incrementing `page` until a short page returns.

When a call fails (401, 403, 404, 429), switch to the `troubleshoot` skill.
