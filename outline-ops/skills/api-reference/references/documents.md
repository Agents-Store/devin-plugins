# Documents

The core of Outline. A document is a single Markdown page; the API always returns the latest version. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header. `id` accepts a UUID **or** the short `urlId`; `documents.info` also accepts a `shareId`.

## Read & list

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.info` | Retrieve one document. `{"id"}` (UUID, `urlId`, or `shareId` via `{"shareId"}`). |
| `documents.list` | List published + own drafts. Pagination + sorting + filters `{"collectionId"?,"userId"?,"parentDocumentId"?,"backlinkDocumentId"?,"statusFilter":["draft"|"archived"|"published"]}`. |
| `documents.documents` | The nested child tree of a document. `{"id"}` → `NavigationNode`. |
| `documents.drafts` | List the current user's drafts. Pagination + sorting + `{"collectionId"?,"dateFilter":"day"|"week"|"month"|"year"}`. |
| `documents.viewed` | List documents recently viewed by the current user. Pagination + sorting. |
| `documents.archived` | List archived documents. Pagination + sorting + `{"collectionId"?}`. |
| `documents.deleted` | List trashed documents. Pagination + sorting. |

## Search

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.search` | Full-text search. `{"query"}` + pagination + `{"collectionId"?,"documentId"?,"userId"?,"statusFilter"?,"dateFilter"?,"shareId"?,"snippetMinWords"?,"snippetMaxWords"?,"sort":"relevance"|"createdAt"|"updatedAt"|"title","direction":"ASC"|"DESC"}`. Returns `data[]` of `{context, ranking, document}`. |
| `documents.search_titles` | Title-only search (faster). `{"query"}` (required) + pagination + same filters. Returns `data[]` of documents. |
| `documents.answerQuestion` | **AI answers** (Business/Enterprise/Cloud; "AI answers" must be enabled). `{"query"}` + `{"userId"?,"collectionId"?,"documentId"?,"statusFilter"?,"dateFilter"?}`. Returns `{documents, search}` where `search.answer` holds the natural-language answer. |

## Create & import

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.create` | Create/publish. `{"title","text"(markdown),"collectionId"?,"parentDocumentId"?,"publish"?,"templateId"?,"icon"?,"color"?,"fullWidth"?,"createdAt"?,"dataAttributes"?}`. To **publish**, `collectionId` **or** `parentDocumentId` is required; omit `publish` for a draft. |
| `documents.import` | Create from an uploaded file (**multipart/form-data**, not JSON). Fields `file` (plain text, markdown, docx, csv, tsv, html), `collectionId` **or** `parentDocumentId` (one required), `publish`?. Use `-F file=@path -F collectionId=…`. |
| `documents.duplicate` | Copy a document. `{"id","title"?,"recursive"?(children),"publish"?,"collectionId"?,"parentDocumentId"?}`. |
| `documents.templatize` | Create a template from a document. `{"id","publish"(required),"collectionId"?}` → returns a `Template`. |

## Update

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.update` | Modify a document. `{"id"}` + any of `{"title","text","icon","color","fullWidth","collectionId","templateId","insightsEnabled","publish","dataAttributes"}`. **`editMode`** controls how `text` is applied: `append`, `prepend`, `replace` (default), or `patch`. For `patch`, also pass `findText` (the existing text to replace with `text`). |
| `documents.unpublish` | Move a published doc back to draft. `{"id","detach"?}`. |
| `documents.move` | Relocate. `{"id","collectionId"?,"parentDocumentId"?,"index"?}` (no parent → collection root). Returns affected `{documents, collections}`. |

## Lifecycle (archive / trash)

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.archive` | Archive (hidden, still searchable). `{"id"}`. |
| `documents.restore` | Restore an archived/deleted doc, optionally to a prior revision. `{"id","collectionId"?,"revisionId"?}`. |
| `documents.delete` | Move to trash (recoverable ~30 days). `{"id","permanent"?}`. `permanent:true` destroys it irreversibly — **confirm first**. |
| `documents.empty_trash` | Permanently delete everything in the trash (admin, irreversible). No body — **confirm first**. |

## Export & insights

| Method | Purpose & key fields |
|--------|----------------------|
| `documents.export` | Export one document. `{"id","paperSize"?,"signedUrls"?,"includeChildDocuments"?}`. Output format follows the `Accept` header (Markdown/HTML/PDF); `includeChildDocuments:true` returns a zip. `data` is the document content (e.g. Markdown string). |
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

## Notes

- **`text` is Markdown** in/out. Newlines in JSON must be escaped (`\n`).
- Prefer `editMode:"append"`/`"prepend"`/`"patch"` over `replace` when you only mean to add or tweak — `replace` overwrites the whole body.
- For the full request/response schema of any method, see `outline-openapi.yml` (search `operationId: documents…`).
