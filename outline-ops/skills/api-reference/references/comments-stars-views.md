# Comments, Stars & Views

User-facing engagement on documents. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header.

## Comments

A comment is attached to a document — either to the document as a whole, to a selection of text (inline, via `anchorText`), or as a reply to another comment (via `parentCommentId`).

| Method | Purpose & key fields |
|--------|----------------------|
| `comments.create` | Add a comment or reply. `{"documentId"(required)}` + either `{"text"}` (markdown) or `{"data"}` (editor JSON). Optional `{"id","parentCommentId"(reply),"anchorText","anchorPrefix","anchorSuffix"}`. `anchorText` pins the comment to the first matching substring; `anchorPrefix`/`anchorSuffix` disambiguate multiple occurrences. |
| `comments.info` | Retrieve a comment. `{"id","includeAnchorText"?}`. |
| `comments.update` | Edit a comment's body. `{"id","data"(required, editor JSON)}`. |
| `comments.delete` | Delete a comment. `{"id"}`. Deleting a top-level comment removes its replies too. |
| `comments.list` | List comments. Pagination + sorting + `{"documentId"?,"collectionId"?,"includeAnchorText"?}`. |

## Stars

A star bookmarks a document or collection into the user's sidebar. Each user has their own stars.

| Method | Purpose & key fields |
|--------|----------------------|
| `stars.create` | Star an item. One of `{"documentId"}` or `{"collectionId"}` (optional `index` for ordering). |
| `stars.list` | List the current user's stars. Pagination → `{stars, documents}`. |
| `stars.update` | Reorder a star in the sidebar. `{"id","index"(required)}`. |
| `stars.delete` | Remove a star. `{"id"}`. |

## Views

A view is a compressed record of a user's views of a document (first, last, and total count per user — individual views aren't recorded).

| Method | Purpose & key fields |
|--------|----------------------|
| `views.list` | List who viewed a document and the total count. `{"documentId"(required),"includeSuspended"?}`. |
| `views.create` | Record a view. `{"documentId"}`. Documented for completeness — Outline recommends **not** creating views from outside the UI. |

## Notes

- `comments.create`/`comments.update` accept editor `data` (a ProseMirror JSON object); `comments.create` also accepts plain `text` (markdown) as a simpler alternative.
- `stars.index` is a fractional-index string used purely for sidebar ordering.
- For exact schemas, search `operationId: comments…` / `stars…` / `views…` in `outline-openapi.yml`.
