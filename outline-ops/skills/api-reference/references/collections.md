# Collections

Collections group documents into a nested hierarchy and are the level at which read/write permissions are granted to users or groups. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header. `id` accepts a UUID or the short `urlId`. `permission` is `read` or `read_write`.

## Read & list

| Method | Purpose & key fields |
|--------|----------------------|
| `collections.info` | Retrieve one collection. `{"id"}`. |
| `collections.documents` | The collection's document tree as `NavigationNode[]`. `{"id"}`. |
| `collections.list` | List accessible collections. Pagination + sorting + `{"filters"?}` (structured filter, see **Filters** below). The older `{"query"?(name filter),"statusFilter"?:["archived"]}` still work but are **deprecated** and cannot be combined with `filters`. |

## Create & update

| Method | Purpose & key fields |
|--------|----------------------|
| `collections.create` | `{"name"(required, ≤100),"description"?(markdown, ≤100000) **or** "data"?(ProseMirror JSON),"permission"?,"icon"?,"color"?(hex),"sharing"?}`. `permission` sets the default access for all members (omit for a private collection). Send **either** `description` **or** `data` — a request carrying both is rejected (Outline v1.9.0+). |
| `collections.update` | `{"id"}` + any of `{"name","description"|"data"(not both),"permission","icon","color","sharing","deprecatedReason"?}`. `deprecatedReason` (≤2000, nullable) can only be edited on an already-archived collection. |
| `collections.delete` | Delete the collection **and all its documents** — irreversible. `{"id","reason"?(≤2000, stored as `deprecatedReason`)}`. **Confirm first.** |

## Archive, restore, reorder, duplicate, import

| Method | Purpose & key fields |
|--------|----------------------|
| `collections.archive` | Hide the collection and all its documents from the sidebar and search; reversible. `{"id","reason"?(≤2000, nullable)}` — the reason is stored and returned as `deprecatedReason`. |
| `collections.restore` | Bring an archived collection (and its documents) back. `{"id"}`. |
| `collections.move` | Reposition the collection in the sidebar. `{"id","index"(required)}` — `index` is a fractional-index string; this reorders siblings, it does not nest the collection. |
| `collections.duplicate` | Copy a collection with its **published** documents (icon, color, permission, sharing and sorting are kept; drafts and archived documents are not copied). `{"id","name"?(≤100, defaults to the original name)}`. Document copying runs in the background, so the returned collection may fill up shortly after the response. |
| `collections.import` | Create a new collection from a previously uploaded file. `{"attachmentId"(required),"format"?:"outline-markdown"|"json"(default `outline-markdown`),"permission"?:"read"|"read_write"}` → `{fileOperation}`; poll `fileOperations.info`. Upload the file first with `attachments.create` (→ `attachments-fileops.md`). |

## Memberships — users

| Method | Purpose & key fields |
|--------|----------------------|
| `collections.add_user` | Add a user membership. `{"id","userId","permission"?}` → `{users, memberships}`. |
| `collections.remove_user` | Remove a user. `{"id","userId"}`. |
| `collections.memberships` | List **individual** user memberships (not group). `{"id","query"?,"permission"?}` + pagination → `{users, memberships}`. |

## Memberships — groups

| Method | Purpose & key fields |
|--------|----------------------|
| `collections.add_group` | Give a whole group access. `{"id","groupId","permission"?}` → `{collectionGroupMemberships}`. |
| `collections.remove_group` | Revoke a group's access (members may retain access via other groups). `{"id","groupId"}`. |
| `collections.group_memberships` | List the collection's group memberships. `{"id","query"?,"permission"?}` + pagination → `{groups, collectionGroupMemberships}`. |

## Export

| Method | Purpose & key fields |
|--------|----------------------|
| `collections.export` | Bulk-export one collection (markdown + attachments, nested as folders in a zip). `{"id","format":"outline-markdown"|"json"|"html"|"okf"}` (`okf` = Open Knowledge Format, Outline v1.10.1+). Returns a `FileOperation` — poll `fileOperations.info` and download with `fileOperations.redirect`. |
| `collections.export_all` | Export all collections. `{"format":"outline-markdown"|"json"|"html"|"okf","includeAttachments"?(default true),"includePrivate"?(default true)}`. Returns a `FileOperation`. |

## Filters (`collections.list`)

`filters` is an array of nodes, ANDed together. A leaf is `{"field","operator","value"}`; a group is `{"operator":"AND"|"OR","filters":[…]}` and may nest.

- `field`: `name`, `createdAt`, `updatedAt`, `archivedAt`, `createdById`, `permission`.
- `operator`: `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `contains`, `startsWith`, `endsWith`, `containsStrict`, `startsWithStrict`, `endsWithStrict`, `in`, `notIn`, `isNull`, `isNotNull` (`permission` accepts only `eq`, `neq`, `in`, `notIn`, `isNull`, `isNotNull`).
- `value`: string, boolean or an array (for `in`/`notIn`); date fields take an ISO 8601 date **or** an ISO 8601 duration (relative to now); omit for `isNull`/`isNotNull`.

```json
{"filters":[{"field":"archivedAt","operator":"isNull"},{"field":"name","operator":"contains","value":"Handbook"}]}
```

## Notes

- Exports are asynchronous: both export methods return a `FileOperation` whose `state` moves `creating → uploading → complete`; fetch the result via `fileOperations.redirect` (→ `attachments-fileops.md`).
- An archived collection is hidden, not deleted: use `collections.restore` to reverse it, `collections.delete` only when the content must go. Prefer archive over delete when unsure.
- A collection `color` is a hex string including the `#` (e.g. `#123123`); `icon` is an outline-icons name or an emoji.
- For exact request/response schemas, search `operationId: collections…` in `outline-openapi.yml`.
