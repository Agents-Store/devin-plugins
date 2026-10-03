# Comments, Reactions, Pins, Subscriptions, Notifications, Stars & Views

User-facing engagement on documents. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header.

## Comments

A comment is attached to a document — either to the document as a whole, to a selection of text (inline, via `anchorText`), or as a reply to another comment (via `parentCommentId`).

| Method | Purpose & key fields |
|--------|----------------------|
| `comments.create` | Add a comment or reply. `{"documentId"(required)}` + either `{"text"}` (markdown, ≤10000 chars) or `{"data"}` (editor JSON). Optional `{"id","parentCommentId"(reply),"anchorText","anchorPrefix","anchorSuffix"}`. `anchorText` pins the comment to the first matching substring; `anchorPrefix`/`anchorSuffix` disambiguate multiple occurrences. |
| `comments.info` | Retrieve a comment. `{"id","includeAnchorText"?}`. |
| `comments.update` | Edit a comment's body. `{"id"}` + **either** `{"text"}` (markdown, ≤10000 chars) **or** `{"data"}` (editor JSON) — one of the two is required, same as `comments.create`. |
| `comments.delete` | Delete a comment. `{"id"}`. Deleting a top-level comment removes its replies too. |
| `comments.list` | List comments. Pagination + sorting + `{"documentId"?,"collectionId"?,"includeAnchorText"?}`. |
| `comments.resolve` | Mark a comment thread resolved (hidden from the document by default). `{"id"}` → the comment. |
| `comments.unresolve` | Re-open a resolved thread so it shows on the document again. `{"id"}` → the comment. |
| `comments.add_reaction` | React to a comment as the current user. `{"id","emoji"(required, a native emoji such as `👍`)}`. |
| `comments.remove_reaction` | Remove the current user's own reaction. `{"id","emoji"(required)}`. |

Edit a comment with plain markdown (no ProseMirror JSON needed):

```bash
curl -s -X POST "${OUTLINE_API_URL%/}/comments.update" \
  -H "Authorization: Bearer ${OUTLINE_API_KEY}" -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"id":"<commentId>","text":"Updated: **fixed** in the next release."}' | jq '.data | {id, data}'
```

### Reactions

| Method | Purpose & key fields |
|--------|----------------------|
| `reactions.list` | List the emoji reactions on one comment. `{"commentId"(required)}` + pagination. |

## Pins

A pin keeps a document at the top of a collection or on the workspace home screen. Pins are **visible to every workspace member**, not just the pinner.

| Method | Purpose & key fields |
|--------|----------------------|
| `pins.create` | Pin a document. `{"documentId"(required),"collectionId"?(omit or `null` = home screen),"index"?(fractional index for position)}`. |
| `pins.info` | Retrieve the pin of a document. `{"documentId"(required),"collectionId"?(omit for the home-screen pin)}`. |
| `pins.list` | List pins of one collection, or home-screen pins when `collectionId` is omitted. `{"collectionId"?}` + pagination. |
| `pins.update` | Reorder a pin. `{"id","index"(required)}`. |
| `pins.delete` | Un-pin; the document itself is untouched. `{"id"}`. |

## Subscriptions

A subscription makes the **current user** receive notifications when a document or collection changes.

| Method | Purpose & key fields |
|--------|----------------------|
| `subscriptions.create` | Subscribe. `{"event":"documents"(required)}` + **exactly one** of `{"documentId"}` / `{"collectionId"}`. |
| `subscriptions.info` | Retrieve the current user's subscription for a target. `{"event":"documents"}` + exactly one of `{"documentId"}` / `{"collectionId"}`. |
| `subscriptions.list` | List the current user's subscriptions for a target. `{"event":"documents"}` + exactly one of `{"documentId"}` / `{"collectionId"}` + pagination. |
| `subscriptions.delete` | Unsubscribe by subscription id. `{"id"}`. |

## Notifications

In-app notifications of the current user, and which notification types they receive.

| Method | Purpose & key fields |
|--------|----------------------|
| `notifications.list` | List the current user's notifications, newest first. Pagination + `{"eventType"?,"archived"?(true = only archived)}`. |
| `notifications.update` | Mark one notification viewed or archived by setting a timestamp. `{"id"}` + `{"viewedAt"?(ISO date-time, `null` = unviewed),"archivedAt"?(ISO date-time, `null` = unarchive)}`. |
| `notifications.update_all` | Same, for **all** of the user's notifications at once (e.g. mark everything viewed). `{"viewedAt"?,"archivedAt"?}`. |
| `users.notificationsSubscribe` | Turn one notification type on for the current user. `{"eventType"}`. |
| `users.notificationsUnsubscribe` | Turn one notification type off. `{"eventType"}`. |

`eventType` values: `documents.publish`, `documents.update`, `documents.add_user`, `collections.add_user`, `revisions.create`, `collections.create`, `comments.create`, `comments.resolve`, `reactions.create`, `documents.mentioned`, `comments.mentioned`, `documents.group_mentioned`, `comments.group_mentioned`, `emails.invite_accepted`, `emails.onboarding`, `emails.features`, `emails.export_completed`, `access_requests.create`.

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

## Notes

- `comments.create` and `comments.update` both accept **either** editor `data` (a ProseMirror JSON object) **or** plain `text` (markdown, ≤10000 chars); at least one of the two is required. Prefer `text` unless you already hold editor JSON.
- `views.create` ("record a view") is **not** in the current published spec — upstream removed it and Outline v1.10.1 tightened its authentication, so API keys may be rejected. Don't call it; views are recorded by the UI. Read counts with `views.list`.
- A resolved comment thread is hidden from the document by default (`comments.unresolve` makes it visible again); resolving does not delete anything.
- `stars.index` is a fractional-index string used purely for sidebar ordering.
- For exact schemas, search `operationId: comments…` / `stars…` / `views…` in `outline-openapi.yml`.
