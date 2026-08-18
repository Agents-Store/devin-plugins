# Collections

Collections group documents into a nested hierarchy and are the level at which read/write permissions are granted to users or groups. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header. `id` accepts a UUID or the short `urlId`. `permission` is `read` or `read_write`.

## Read & list

| Method | Purpose & key fields |
|--------|----------------------|
| `collections.info` | Retrieve one collection. `{"id"}`. |
| `collections.documents` | The collection's document tree as `NavigationNode[]`. `{"id"}`. |
| `collections.list` | List accessible collections. Pagination + sorting + `{"query"?(name filter),"statusFilter"?}`. |

## Create & update

| Method | Purpose & key fields |
|--------|----------------------|
| `collections.create` | `{"name"(required),"description"?(markdown),"permission"?,"icon"?,"color"?(hex),"sharing"?}`. `permission` sets the default access for all members (omit for a private collection). |
| `collections.update` | `{"id"}` + any of `{"name","description","permission","icon","color","sharing"}`. |
| `collections.delete` | Delete the collection **and all its documents** — irreversible. `{"id"}`. **Confirm first.** |

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
| `collections.export` | Bulk-export one collection (markdown + attachments, nested as folders in a zip). `{"id","format":"outline-markdown"|"json"|"html"}`. Returns a `FileOperation` — poll `fileOperations.info` and download with `fileOperations.redirect`. |
| `collections.export_all` | Export all collections. `{"format":"outline-markdown"|"json"|"html","includeAttachments"?(default true),"includePrivate"?(default true)}`. Returns a `FileOperation`. |

## Notes

- Exports are asynchronous: both export methods return a `FileOperation` whose `state` moves `creating → uploading → complete`; fetch the result via `fileOperations.redirect` (→ `attachments-fileops.md`).
- A collection `color` is a hex string including the `#` (e.g. `#123123`); `icon` is an outline-icons name or an emoji.
- For exact request/response schemas, search `operationId: collections…` in `outline-openapi.yml`.
