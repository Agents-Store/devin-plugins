# Confluence Comments, Attachments, Versions & More

Discussion, files, version history, likes, and tasks on Confluence content. Base `${ATLASSIAN_SITE_URL%/}/wiki/api/v2`. Comment bodies follow the same `{representation, value}` shape as pages (see `pages-blogposts.md`).

## Footer comments (page/blog discussion)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /pages/{id}/footer-comments` · `GET /blogposts/{id}/footer-comments` | List footer comments on a page/blog (`getPageFooterComments`). |
| `POST /footer-comments` | Create a footer comment (`createFooterComment`). Body `{"pageId":"<id>"|"blogPostId":"<id>","body":{"representation":"storage","value":"<p>…</p>"},"parentCommentId":"<id>"?}`. |
| `GET /footer-comments/{comment-id}` · `PUT …` · `DELETE …` | Get / update (version bump) / delete a footer comment. |
| `GET /footer-comments/{id}/children` | Threaded replies (`getFooterCommentChildren`). |

## Inline comments (anchored to text)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /pages/{id}/inline-comments` | List inline comments on a page (`getPageInlineComments`). |
| `POST /inline-comments` | Create an inline comment (`createInlineComment`). Body adds `inlineCommentProperties:{"textSelection":"…","textSelectionMatchCount":N,"textSelectionMatchIndex":I}`. |
| `GET/PUT/DELETE /inline-comments/{comment-id}` | Get / update / delete. |

## Attachments

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /pages/{id}/attachments` · `GET /blogposts/{id}/attachments` | List attachments on content (`getPageAttachments`). |
| `GET /attachments/{id}` | Attachment metadata (`getAttachmentById`). |
| `GET /attachments/{id}/thumbnail/download` | Download a thumbnail. |
| `DELETE /attachments/{id}` | Delete an attachment (`deleteAttachment`). `?purge=true`. **Confirm first.** |

> **Uploading** an attachment is not in the v2 spec — use the v1 endpoint `POST ${ATLASSIAN_SITE_URL%/}/wiki/rest/api/content/{id}/child/attachment` (multipart `-F file=@…`, header `-H "X-Atlassian-Token: nocheck"`).

## Versions (history)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /pages/{id}/versions` | Version list for a page (`getPageVersions`). |
| `GET /pages/{page-id}/versions/{version-number}` | One version's detail (`getPageVersionDetails`). |
| `GET /blogposts/{id}/versions`, `…/attachments/{id}/versions`, `…/footer-comments/{id}/versions` | Same for other content types. |

## Likes, tasks, operations

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /pages/{id}/likes/count` · `/likes/users` | Like count / who liked (`getPageLikeCount`, `getPageLikeUsers`). |
| `GET /tasks` · `GET /tasks/{id}` · `PUT /tasks/{id}` | List / get / update inline action items (`getTasks`, `updateTask`). Filter `?space-id=&assigned-to=&status=`. |
| `GET /pages/{id}/operations` | Permitted operations for the current user on that content (`getPageOperations`) — useful to predict a `403`. |

## Notes
- **Comments are versioned too** — updating a comment requires the next `version.number`, same as pages.
- Attachment **upload/download bytes** live on the v1 API; v2 covers metadata, versions, and delete.
- `GET …/operations` tells you what the token user may do on an object before you try a write.
- **Cursor pagination** throughout — follow `_links.next`.
- For exact schemas: `grep -n '"operationId": "createFooterComment"' ../confluence-openapi-v2.json`.
