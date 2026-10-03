# Documents

The core of Outline. A document is a single Markdown page; the API always returns the latest version. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header. `id` accepts a UUID **or** the short `urlId`; `documents.info` also accepts a `shareId`.

## Read & list

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.info` | Retrieve one document. `{"id"}` (UUID, `urlId`, or `shareId` via `{"shareId"}`). |
| `documents.list` | List published + own drafts. Pagination + sorting + `{"filters"?}` (structured filter, see **Filters** below) + `{"backlinkDocumentId"?}`. The older `{"collectionId"?,"userId"?,"parentDocumentId"?,"statusFilter":["draft"|"archived"|"published"]}` still work but are **deprecated** and cannot be combined with `filters`. |
| `documents.documents` | The nested child tree of a document. `{"id"}` → `NavigationNode`. |
| `documents.drafts` | List the current user's drafts. Pagination + sorting + `{"collectionId"?,"dateFilter":"day"|"week"|"month"|"year"}`. |
| `documents.viewed` | List documents recently viewed by the current user. Pagination + sorting. |
| `documents.archived` | List archived documents. Pagination + sorting + `{"collectionId"?}`. |
| `documents.deleted` | List trashed documents. Pagination + sorting + `{"filters"?}` limited to `deletedAt` (date) and `deletedById` (user UUID; `eq`/`in`). |

## Search

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.search` | Full-text search. `{"query"}` + pagination + `{"filters"?,"shareId"?,"snippetMinWords"?,"snippetMaxWords"?,"sort":"relevance"|"createdAt"|"updatedAt"|"title","direction":"ASC"|"DESC"}`. The older `{"collectionId"?,"documentId"?,"userId"?,"statusFilter"?,"dateFilter"?}` still work but are **deprecated** in favour of `filters` (and cannot be combined with it). Returns `data[]` of `{context, ranking, document}`. |
| `documents.search_titles` | Title-only search (faster). `{"query"}` (required) + pagination + same `filters` / deprecated params. Returns `data[]` of documents. |
| `documents.answerQuestion` | **AI answers** (Business/Enterprise/Cloud; "AI answers" must be enabled). `{"query"}` + `{"userId"?,"collectionId"?,"documentId"?,"statusFilter"?,"dateFilter"?}`. Returns `{documents, search}` where `search.answer` holds the natural-language answer. |

## Create & import

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.create` | Create/publish. `{"title"(≤100),"text"(markdown, ≤1,536,000 chars),"collectionId"?,"parentDocumentId"?,"publish"?,"templateId"?,"icon"?,"color"?,"fullWidth"?,"createdAt"?,"dataAttributes"?,"preferences"?,"id"?}`. `preferences` sets display options, e.g. `{"headingPrefix":"none"|"numeric"|"alphanumeric"|"outline"}` (numbered headings). To **publish**, `collectionId` **or** `parentDocumentId` is required; omit `publish` for a draft. |
| `documents.import` | Create from an uploaded file (**multipart/form-data**, not JSON). Fields `file` (plain text, markdown, docx, csv, tsv, html), `collectionId` **or** `parentDocumentId` (one required), `publish`?. Use `-F file=@path -F collectionId=…`. |
| `documents.duplicate` | Copy a document. `{"id","title"?,"recursive"?(children),"publish"?,"collectionId"?,"parentDocumentId"?}`. |
| `documents.templatize` | Create a template from a document. `{"id","publish"(required),"collectionId"?}` → returns a `Template`. |

## Update

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.update` | Modify a document. `{"id"}` + any of `{"title","text","icon","color","fullWidth","collectionId","templateId","insightsEnabled","publish","dataAttributes","preferences","lastRevision","deprecatedReason"}`. **`editMode`** controls how `text` is applied: `append`, `prepend`, `replace` (default), or `patch`. For `patch`, also pass `findText` (the existing text to replace with `text`). **`lastRevision`** (int) turns on optimistic concurrency: if the document's current revision number (the `revision` field of `documents.info`) differs, the update is rejected with **`409`** — re-read the document (`documents.info`), merge, retry. **`preferences`** is merged field-by-field (`null` clears all of them). **`deprecatedReason`** (≤2000, nullable) can only be edited on an archived or deleted document. Note: `dataAttributes` sent here **replaces** the set — attributes you omit are removed. |
| `documents.unpublish` | Move a published doc back to draft. `{"id","detach"?}`. |
| `documents.move` | Relocate. `{"id","collectionId"?,"parentDocumentId"?,"index"?}` (no parent → collection root). Returns affected `{documents, collections}`. |

## Lifecycle (archive / trash)

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.archive` | Archive (hidden, still searchable). `{"id","reason"?(≤2000, nullable)}` — the reason is stored and returned as `deprecatedReason`. |
| `documents.restore` | Restore an archived/deleted doc, optionally to a prior revision. `{"id","collectionId"?,"revisionId"?}`. |
| `documents.delete` | Move to trash (recoverable ~30 days). `{"id","permanent"?,"reason"?(≤2000, stored as `deprecatedReason`)}`. `permanent:true` destroys it irreversibly — **confirm first**. |
| `documents.empty_trash` | Permanently delete everything in the trash (admin, irreversible). No body — **confirm first**. |

## Export & insights

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.export` | Export one document. `{"id","paperSize"?,"signedUrls"?,"includeChildDocuments"?}`. Output format follows the `Accept` header (`text/markdown`, `text/html`, `application/pdf`, or `application/x-textbundle` for TextBundle); `includeChildDocuments:true` returns a zip. `data` is the document content (e.g. Markdown string). |
| `documents.insights` | Activity rollups (views/comments/reactions/revisions/editors), Business/Enterprise; insights must be enabled on the doc. `{"id","startDate"?,"endDate"?}` (defaults to last 30 days). |

## Membership & permissions

`permission` is `read` or `read_write`.

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.users` | All users with access (direct or inherited). `{"id","query"?,"userId"?}`. |
| `documents.memberships` | Users with **direct** membership only. `{"id","query"?,"permission"?}` → `{users, memberships}`. |
| `documents.add_user` | Grant a user direct access. `{"id","userId","permission"?}`. |
| `documents.remove_user` | Revoke a user's direct access. `{"id","userId"}`. |
| `documents.add_group` | Grant a group access. `{"id","groupId","permission"?}`. |
| `documents.remove_group` | Revoke a group's access. `{"id","groupId"}`. |
| `documents.group_memberships` | List a document's group memberships. `{"id","query"?,"permission"?}` + pagination. |

## Filters (`documents.list`, `documents.search`, `documents.search_titles`)

`filters` is an array of nodes, ANDed together. A leaf is `{"field","operator","value"}`; a group is `{"operator":"AND"|"OR","filters":[…]}` and may nest.

- `field`: `createdAt`, `updatedAt`, `publishedAt`, `archivedAt`, `title`, `templateId`, `collectionId`, `userId`, `documentId`, `parentDocumentId` (`userId` and `documentId` accept only `eq` and `in`).
- `operator`: `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `contains`, `startsWith`, `endsWith`, `containsStrict`, `startsWithStrict`, `endsWithStrict`, `in`, `notIn`, `isNull`, `isNotNull`.
- `value`: string, number, boolean or an array (for `in`/`notIn`); date fields take an ISO 8601 date **or** an ISO 8601 duration (relative to now); omit for `isNull`/`isNotNull`.

```json
{"filters":[{"field":"collectionId","operator":"eq","value":"<collectionId>"},{"field":"archivedAt","operator":"isNull"}]}
```

## Notes

- **`text` is Markdown** in/out. Newlines in JSON must be escaped (`\n`).
- For shared or automated edits, read the document first and pass its `revision` number as `lastRevision` on `documents.update`; a `409` means someone changed it in between.
- Prefer `editMode:"append"`/`"prepend"`/`"patch"` over `replace` when you only mean to add or tweak — `replace` overwrites the whole body.
- For the full request/response schema of any method, see `outline-openapi.yml` (search `operationId: documents…`).
