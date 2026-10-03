---
name: common-operations
description: This skill should be used when the user wants to do knowledge-base work in Outline — "create a document", "search Outline", "update a doc", "move a document to a collection", "create a collection", "share a document", "invite users to Outline", "star a document", "comment on a doc", or any everyday Outline operation. Provides plain-language workflows that drive the REST API and route to the exact methods.
---

# Outline Common Operations

Plain-language playbooks for everyday Outline work. Each one drives the REST API. For exact method signatures and every field, open the `api-reference` skill's matching `references/*.md` file (named in each workflow).

## Before anything: ensure access

If `OUTLINE_API_KEY` / `OUTLINE_API_URL` aren't confirmed this session, run the `setup` skill first (one `auth.info` call). Every call below assumes both are set and uses these headers:

```bash
-H "Authorization: Bearer ${OUTLINE_API_KEY}" -H "Content-Type: application/json" -H "Accept: application/json"
```

Define them once for brevity in the recipes below:

```bash
OUT="${OUTLINE_API_URL%/}"
H_AUTH="Authorization: Bearer ${OUTLINE_API_KEY}"
```

## The golden rules (why workflows look the way they do)

1. **Everything is `POST ${OUT}/<method>` with a JSON body.** No GETs, no path params. An action with no inputs still needs `-d '{}'`.
2. **Read `.data`.** The useful payload is always under `.data` in the response envelope.
3. **Resolve titles to ids once.** Users say "the Welcome doc"; the API wants a UUID or `urlId`. Resolve with `documents.search` / `documents.search_titles` / `collections.list` and keep the id.
4. **Confirm before destructive actions.** `documents.delete` (trash), `permanent: true`, `documents.empty_trash`, `collections.delete`, `users.delete/suspend`, `shares.revoke`, `revisions.delete`, `apiKeys.delete`, `webhookSubscriptions.delete`, and `auth.delete` (sign out — ends the user's sessions and tokens) are high-impact — show the user what will change first.

## Workflow: find a document by title

```bash
DOC_ID=$(curl -s -X POST "${OUT}/documents.search_titles" -H "$H_AUTH" -H "Content-Type: application/json" \
  -d '{"query":"Welcome"}' | jq -r '.data[0].id')
```
Use `documents.search` instead when you need full-text matches with snippets/ranking. (→ `documents.md`)

## Workflow: create a document

```bash
# Publish under a collection (collectionId OR parentDocumentId is required to publish)
curl -s -X POST "${OUT}/documents.create" -H "$H_AUTH" -H "Content-Type: application/json" \
  -d "{\"title\":\"Welcome\",\"text\":\"# Hello\\n\\nWelcome aboard.\",\"collectionId\":\"${COLLECTION_ID}\",\"publish\":true}" \
  | jq '.data | {id, title, url}'
```
- **Draft**: omit `publish` (or set `false`); publish later with `documents.update` `{"id":"…","publish":true}`.
- **Child document**: pass `parentDocumentId` instead of (or with) `collectionId`.
- **From a file** (markdown/docx/csv/html): use `documents.import` (multipart). (→ `documents.md`)

## Workflow: update a document

```bash
# Full replace of the body
curl -s -X POST "${OUT}/documents.update" -H "$H_AUTH" -H "Content-Type: application/json" \
  -d "{\"id\":\"${DOC_ID}\",\"text\":\"# New body\"}" | jq '.data | {id, title}'
```
- **Append / prepend** without resending the whole doc: add `"editMode":"append"` (or `prepend`) with `text`.
- **Surgical edit**: `"editMode":"patch"` with `findText` (the existing text to replace) and `text` (the replacement). (→ `documents.md`)
- **Safe concurrent edit**: read the doc, then send `"lastRevision": <.data.revision>` with the update; a `409` means someone saved in between — re-read, merge, retry.

## Workflow: organize — move, archive, trash, restore

1. **Move** to another collection/parent: `documents.move` `{"id","collectionId"?, "parentDocumentId"?, "index"?}`.
2. **Archive** (hide, keep searchable): `documents.archive` `{"id"}`; reverse with `documents.restore`.
3. **Trash** (recoverable 30 days): `documents.delete` `{"id"}`; restore with `documents.restore`. Add `"permanent":true` to destroy immediately (confirm first).
4. **Empty trash** (admin, irreversible): `documents.empty_trash` — confirm. (→ `documents.md`)

## Workflow: create a collection and add documents

1. **Create** — `collections.create` `{"name","description"?,"permission"?,"color"?,"icon"?}` (`permission` is `read` or `read_write` for the default workspace access). (→ `collections.md`)
2. **Add docs** — create documents with that `collectionId`, or `documents.move` existing ones in.
3. **See the tree** — `collections.documents` `{"id"}` returns the nested navigation structure.
4. **Archive / restore / copy** — `collections.archive` `{"id","reason"?}` hides a collection and its documents (reversible with `collections.restore`); `collections.duplicate` `{"id","name"?}` copies it with its published documents. Prefer archive over `collections.delete`. (→ `collections.md`)
5. **Send either `description` or `data`** to `collections.create`/`update`, never both.

## Workflow: share a document publicly

```bash
SHARE_ID=$(curl -s -X POST "${OUT}/shares.create" -H "$H_AUTH" -H "Content-Type: application/json" \
  -d "{\"documentId\":\"${DOC_ID}\"}" | jq -r '.data.id')
# Shares start unpublished — publish to make it accessible without login
curl -s -X POST "${OUT}/shares.update" -H "$H_AUTH" -H "Content-Type: application/json" \
  -d "{\"id\":\"${SHARE_ID}\",\"published\":true}" | jq '.data | {id, url, published}'
```
Revoke with `shares.revoke` `{"id"}`. (→ `sharing-access.md`)

## Workflow: manage people & permissions

1. **Invite** — `users.invite` `{"invites":[{"email":"alice@acme.com","name":"Alice","role":"member"}]}`. (→ `users-groups.md`)
2. **Find / list** — `users.list` `{"query":"alice"}` or with the structured filter `{"filters":[{"field":"suspendedAt","operator":"isNull"}]}` (the older `{"filter":"active"}` still works but is deprecated). Re-send a pending invite with `users.resendInvite` `{"id"}`.
3. **Change role** — `users.update_role` `{"id","role":"admin|member|viewer|guest"}` (admin only).
4. **Suspend** (reversible, preferred over delete) — `users.suspend` `{"id"}`; reverse with `users.activate`. Confirm first.
5. **Grant collection access** — `collections.add_user` `{"id":"<collectionId>","userId","permission":"read_write"}`, or by group with `collections.add_group`. Per-document access uses `documents.add_user` / `documents.add_group`.

## Workflow: engage — star, comment, view counts

- **Star** a doc/collection for the sidebar: `stars.create` `{"documentId"}` or `{"collectionId"}`.
- **Comment**: `comments.create` `{"documentId","text":"…"}`; reply with `parentCommentId`; anchor inline with `anchorText`. Edit with `comments.update` `{"id","text":"…"}` (markdown `text` or editor `data`). Close a thread with `comments.resolve` `{"id"}` (`comments.unresolve` re-opens), react with `comments.add_reaction` `{"id","emoji":"👍"}`. (→ `comments-stars-views.md`)
- **Pin** a document to a collection top or the home screen (visible to everyone): `pins.create` `{"documentId","collectionId"?}`. **Follow** a document or collection: `subscriptions.create` `{"event":"documents","documentId"}`. **Clear notifications**: `notifications.update_all` `{"viewedAt":"<ISO date-time>"}`.
- **View counts** for a doc: `views.list` `{"documentId"}`.

## Workflow: files, webhooks & keys (admin-leaning)

- **Pull an image into a document** without the two-step upload: `attachments.createFromUrl` `{"url","documentId"?}` — Outline fetches it; embed the returned attachment `url`. (→ `attachments-fileops.md`)
- **Webhook** (workspace admin): `webhookSubscriptions.create` `{"name","url","events":["documents.publish"],"secret"?}` (`["*"]` = all events; cloud needs `https`). List/update/delete with the sibling methods. (→ `sharing-access.md`)
- **API key**: `apiKeys.create` `{"name","expiresAt"?,"scope"?}` — the full key is returned **once**; store it without printing it. Revoke with `apiKeys.delete`. (→ `oauth-data-attributes.md`)
- **Name a revision** `revisions.update` `{"id","name"}`; **export one** with `revisions.export` `{"id"}` and download via `fileOperations.redirect`. (→ `revisions-templates-events.md`)

## Workflow: report & audit

1. **Most-recent / by collection** — `documents.list` `{"collectionId"?, "sort":"updatedAt","direction":"DESC","limit":25}`.
2. **Activity insights** for a doc (Business/Enterprise, must be enabled) — `documents.insights` `{"id","startDate"?,"endDate"?}`.
3. **Audit trail** — `events.list` `{"name":"documents.create","auditLog":true}` filtered by `actorId`/`documentId`/`collectionId`. (→ `revisions-templates-events.md`)
4. **Paginate** — walk `{"limit":100,"offset":0}`, then `offset:100`, … until a short page returns, or follow `pagination.nextPath`.

When a call fails (400/401/403/404/429), switch to the `troubleshoot` skill.
