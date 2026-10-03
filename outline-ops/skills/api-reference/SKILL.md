---
name: api-reference
description: This skill should be used when the user asks for "Outline API endpoints", "Outline REST API", "Outline curl examples", "Outline API documentation", the exact method/parameters for any Outline resource, or needs HTTP details for documents, collections, comments, reactions, pins, subscriptions, notifications, stars, views, shares, webhook subscriptions, access requests, auth, API keys, users, groups, attachments, file operations, revisions, templates, events, OAuth clients, or data attributes. Index into the full per-domain endpoint catalog.
disable-model-invocation: true
---

# Outline REST API Reference

Complete catalog for the Outline REST API, split by domain. Official docs: https://www.getoutline.com/developers

The **exhaustive source of truth** is the bundled OpenAPI 3.0 spec: `references/outline-openapi.yml` (154 operations across 26 resource groups — snapshot of `outline/openapi` `spec3.yml` at commit `40f51b75ef`, 2026-09-23, matching Outline server v1.10.1; refresh with `curl -o references/outline-openapi.yml https://raw.githubusercontent.com/outline/openapi/main/spec3.yml`). The curated `references/*.md` files below cover every operation in plain, copy-pasteable form.

Load the `setup` skill first for authentication and the global conventions (RPC POST style, Bearer header, response envelope, limit/offset pagination, sorting, rate limiting, policies) — those rules apply to every method here and are not repeated in each file.

## Global conventions (recap)

- Every endpoint is a **`POST`** to `${OUTLINE_API_URL%/}/<method>` with a JSON body. No GETs, no path params. Empty body = `-d '{}'`.
- Headers: `Authorization: Bearer ${OUTLINE_API_KEY}`, `Content-Type: application/json`, `Accept: application/json`.
- Success: `{ ok, status, data, pagination?, policies? }` — read `.data`. Errors: `{ ok:false, error, status }`.
- Lists take `{"limit":25,"offset":0}` (default limit 25) and echo `pagination.nextPath`. Sort with `{"sort":"updatedAt","direction":"ASC|DESC"}`.
- Address by UUID; documents/collections/templates also accept a short `urlId`. Resolve titles via `documents.search` / `collections.list` first.
- `403` = a policy denies the action (respect it); `429` = rate limited (`Retry-After` header).

## Domain index

Open the file matching the resource you need:

| Domain | File | Covers |
|--------|------|--------|
| Documents | `references/documents.md` | info, list, documents (tree), drafts, viewed, search, search_titles, answerQuestion (AI), create, import, update (`lastRevision` → 409), templatize, unpublish, move, archive, restore, delete, duplicate, empty_trash, export, insights, users, memberships, add_user/remove_user, add_group/remove_group, group_memberships, archived, deleted (`list`, `search`, `search_titles`, `deleted` take structured `filters`) |
| Collections | `references/collections.md` | info, documents, list (+ `filters`), create, update, delete, archive, restore, move (reorder), duplicate, import, add_user, remove_user, memberships, add_group, remove_group, group_memberships, export, export_all |
| Comments, reactions, pins, subscriptions, notifications, stars & views | `references/comments-stars-views.md` | comments CRUD + list + resolve/unresolve + add_reaction/remove_reaction (inline anchors, threads; `update` takes `text` or `data`), reactions list, pins create/info/list/update/delete, subscriptions create/info/list/delete, notifications list/update/update_all, users notificationsSubscribe/Unsubscribe, stars create/list/update/delete, views list |
| Sharing, access, auth & webhooks | `references/sharing-access.md` | shares info/list/create/update/revoke, accessRequests create/info/approve/dismiss, auth info/config/delete, webhookSubscriptions create/list/update/delete (admin) |
| Users & groups | `references/users-groups.md` | users invite/resendInvite/info/list (+ `filters`)/update/updateEmail/update_role/suspend/activate/delete, groups info/list/create/update/delete/memberships/add_user/update_user/remove_user, userMemberships list/update, groupMemberships list |
| Attachments & file operations | `references/attachments-fileops.md` | attachments create/createFromUrl/list/redirect/delete, fileOperations info/list/redirect/delete |
| Revisions, templates & events | `references/revisions-templates-events.md` | revisions info/list/update/delete/export, templates create/list/info/update/delete/restore/duplicate, events list (audit log) |
| API keys, OAuth & data attributes | `references/oauth-data-attributes.md` | apiKeys create/list/delete, oauthClients CRUD + rotate_secret, oauthAuthentications list/delete, dataAttributes CRUD (Business/Enterprise) |

## How to use a reference file

Each file lists endpoints as `POST /<method>` with purpose and key body fields. To run one, wrap it with auth and `jq`:

```bash
curl -s -X POST "${OUTLINE_API_URL%/}/<method>" \
  -H "Authorization: Bearer ${OUTLINE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{ ...body... }' | jq '.data'
```

For rarely-needed fields or response shapes, grep the bundled spec: `grep -n "operationId: documentsSearch" references/outline-openapi.yml`.

## Examples

<example>
User: "What's the endpoint to create a document?"
→ Open `references/documents.md`. `POST /documents.create` with `{"title","text","collectionId","publish":true}`. `collectionId` (or `parentDocumentId`) is required to publish. `text` is markdown.
</example>

<example>
User: "How do I give a user write access to a collection?"
→ Open `references/collections.md`. `POST /collections.add_user` with `{"id":"<collectionId>","userId":"<userId>","permission":"read_write"}`.
</example>

<example>
User: "Give me the curl to make a public share link for a document."
→ Open `references/sharing-access.md`. `POST /shares.create` `{"documentId":"<id>"}` (starts unpublished), then `POST /shares.update` `{"id":"<shareId>","published":true}` to make it accessible without login.
</example>
