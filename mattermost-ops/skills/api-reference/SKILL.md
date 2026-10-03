---
name: api-reference
description: This skill should be used when the user asks for "Mattermost API endpoints", "Mattermost REST API", "Mattermost curl examples", "Mattermost API documentation", the exact path/method for any Mattermost resource, or needs HTTP details for users, teams, channels, posts, reactions, files, emoji, webhooks, slash commands, bots, OAuth apps, system config, roles, schemes, groups, LDAP/SAML, compliance, or data retention. Index into the full per-domain endpoint catalog.
disable-model-invocation: true
---

# Mattermost REST API Reference

Complete endpoint catalog for the Mattermost REST API v4, split by domain. Official interactive docs: https://docs.mattermost.com/api (formerly api.mattermost.com)

The **exhaustive source of truth** is the bundled OpenAPI 3.0 spec: `references/mattermost-openapi-v4.yaml` — 512 path templates, 640 operations (GET/POST/PUT/PATCH/DELETE; 596 core Mattermost plus 44 Playbooks-plugin routes under `/plugins/playbooks/api/v0`). The curated `references/*.md` files below cover the core collaboration surface plus system administration in plain, copy-pasteable form. For rarely-used plugin/enterprise endpoints (Playbooks, Boards, Recaps, AI agents, access-control policies, shared/remote clusters), grep the spec.

**Where the bundled spec comes from.** No ready-made file is published, so it is built from the official `api/v4/source/*.yaml` of `mattermost/mattermost` at tag **v11.11.1** (2026-09-24) with the repo's own `make build-v4`, minus the Go step that only adds code samples; the Playbooks routes are merged in from the Playbooks plugin's `master` at build time. It describes server **v11.11**. Upstream's own build currently fails `swagger-cli validate` on three schema nits (bookmarks, custom profile attributes, content flagging) — harmless for grepping. Mattermost v12.0 (October 2026) changes behaviour that no spec shows: see the v12 notes in `posts.md`, `channels.md`, `integrations.md` and `troubleshoot`. Re-vendor after v12.0 ships; where a `references/*.md` note and the spec disagree, the note was checked against the live changelog and wins.

Load the `setup` skill first for authentication and the global conventions (Bearer header, base path, query pagination, rate limiting) — those rules apply to every endpoint here and are not repeated in each file.

## Global conventions (recap)

- Base: `${MATTERMOST_API_URL%/}/api/v4/...` — header `Authorization: Bearer ${MATTERMOST_TOKEN}`.
- Updates: `PUT /…/{id}` (full) or `PUT /…/{id}/patch` (partial). **No `version`/etag required** in the body.
- Lists paginate with `?page=<0-indexed>&per_page=<≤200>`; responses are JSON arrays. Walk pages until a short/empty page returns.
- Address objects by 26-char ID. Resolve names first: `GET /teams/name/{name}`, `GET /teams/{team_id}/channels/name/{channel_name}`, `GET /users/username/{username}`, `GET /users/email/{email}`.
- `403` = missing permission (respect it); `429` = rate limited (back off to `X-Ratelimit-Reset`).

## Domain index

Open the file matching the resource you need:

| Domain | File | Covers |
|--------|------|--------|
| Auth & sessions | `references/auth-sessions.md` | login/logout, sessions, MFA, personal access tokens (expiry, rotation, non-compliant revoke), terms of service |
| Users | `references/users.md` | users CRUD, search/autocomplete, roles, activation, password, status, preferences, profile image, audits, stats, custom profile attributes |
| Teams | `references/teams.md` | teams CRUD, members, invites (email/guest), stats, search, icon, scheme (Slack import → mmetl, see the note there) |
| Channels | `references/channels.md` | public/private channels, DM & group channels, members, stats, pinned, bookmarks, sidebar categories, moderation, privacy/restore/move, search |
| Posts | `references/posts.md` | posts & threads, ephemeral, pinning, reactions, drafts, scheduled posts, search, flagged, unread |
| Files & emoji | `references/files-emoji.md` | file upload (multipart)/metadata/thumbnail/preview/link/search, upload sessions, custom emoji |
| Integrations | `references/integrations.md` | incoming/outgoing webhooks, slash commands, bots, OAuth apps, interactive dialogs |
| System administration | `references/system-admin.md` | config, ping/health, analytics, audits, logs, license, jobs, plugins, compliance, data retention, cluster, brand, LDAP, SAML, Elasticsearch, exports/imports |
| Roles, schemes & groups | `references/roles-schemes-groups.md` | RBAC roles, permission schemes, custom & LDAP/SAML groups, permissions |

## How to use a reference file

Each file lists endpoints as `METHOD /api/v4/<path>` with purpose and key fields. To run one, wrap it with auth and `jq`:

```bash
curl -s -H "Authorization: Bearer ${MATTERMOST_TOKEN}" \
  "${MATTERMOST_API_URL%/}/api/v4/<path>" | jq .
```

For writes, add `-X POST|PUT|DELETE`, `-H "Content-Type: application/json"`, and `-d '<json>'`. For uploads, use `-F` (multipart) instead of `-d`.

## Examples

<example>
User: "What's the endpoint to post a message to a channel?"
→ Open `references/posts.md`. `POST /api/v4/posts` with `{"channel_id":"<id>","message":"text"}`. The `channel_id` is a 26-char ID — resolve it first via `GET /api/v4/teams/{team_id}/channels/name/{channel_name}`.
</example>

<example>
User: "How do I add a user to a channel?"
→ Open `references/channels.md`. `POST /api/v4/channels/{channel_id}/members` with `{"user_id":"<id>"}`.
</example>

<example>
User: "Give me the curl to create an incoming webhook on a channel."
→ Open `references/integrations.md`. `POST /api/v4/hooks/incoming` with `{"channel_id":"<id>","display_name":"CI"}` (requires manage-webhooks permission).
</example>
