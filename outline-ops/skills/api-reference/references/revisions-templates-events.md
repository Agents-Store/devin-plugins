# Revisions, Templates & Events

Document version history, reusable document starting points, and the workspace audit trail. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header.

## Revisions

A revision is a snapshot of a document at a point in time. Restore a document to a revision via `documents.restore` `{"id","revisionId"}` (→ `documents.md`).

| Method | Purpose & key fields |
|--------|----------------------|
| `revisions.info` | Retrieve one revision. `{"id"}`. |
| `revisions.list` | List a document's revisions, newest activity first. `{"documentId"}` + pagination + sorting. |

## Templates

A template is a reusable document starting point, scoped to a collection or workspace-wide. (You can also turn an existing document into a template with `documents.templatize` — see `documents.md`.)

| Method | Purpose & key fields |
|--------|----------------------|
| `templates.create` | `{"title"(required),"data"(required, ProseMirror JSON body),"icon"?,"color"?(hex `^#[0-9A-Fa-f]{6}$`),"collectionId"?}`. Omit `collectionId` for a workspace-wide template. |
| `templates.list` | List accessible templates. Pagination + sorting + `{"collectionId"?}`. |
| `templates.info` | Retrieve one template. `{"id"}` (UUID or `urlId`). |
| `templates.update` | `{"id"}` + any of `{"title","data","icon","color","fullWidth","collectionId"}` (`collectionId:null` makes it workspace-wide). |
| `templates.delete` | Soft-delete (restorable). `{"id"}`. |
| `templates.restore` | Restore a soft-deleted template. `{"id"}`. |
| `templates.duplicate` | Copy a template. `{"id","title"?,"collectionId"?}`. |

## Events (audit trail / activity stream)

Events are an audit trail of important actions in the knowledge base. Event names use the `objects.verb` format (e.g. `documents.create`, `collections.update`).

| Method | Purpose & key fields |
|--------|----------------------|
| `events.list` | List events. Pagination + sorting + `{"name"?(e.g. "documents.create"),"actorId"?,"documentId"?,"collectionId"?,"auditLog"?}`. Set `auditLog:true` for detailed audit-grade events (includes the actor IP); without it, fewer/less-detailed event types are returned. |

## Notes

- `templates.create`/`update` take the body as `data` (ProseMirror JSON), unlike `documents` which take Markdown `text`.
- `events.list` with `auditLog:true` is the endpoint for compliance/activity reporting; filter by `actorId` for "what did this user do" and by `documentId`/`collectionId` for "what happened to this object".
- For exact schemas, search `operationId: revisions…` / `templates…` / `eventsList` in `outline-openapi.yml`.
