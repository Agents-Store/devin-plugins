# Jira Attachments & Links

File attachments, issue-to-issue links, and remote (external) links. Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`.

## Attachments

| Method | Purpose & key fields |
|--------|----------------------|
| `POST /issue/{issueIdOrKey}/attachments` | Upload a file (`addAttachment`). **Multipart**, not JSON — `-F "file=@/path/to/file"` and the header `-H "X-Atlassian-Token: no-check"`. Returns an array of attachment metadata. |
| `GET /attachment/{id}` | Attachment metadata (`getAttachment`). |
| `GET /attachment/content/{id}` | Download the file content (`getAttachmentContent`) — follows a redirect to storage. |
| `GET /attachment/thumbnail/{id}` | Thumbnail for image attachments (`getAttachmentThumbnail`). |
| `DELETE /attachment/{id}` | Delete an attachment (`removeAttachment`). **Confirm first.** |
| `GET /attachment/meta` | Global attachment settings — enabled + max upload size (`getAttachmentMeta`). |

## Issue links

| Method | Purpose & key fields |
|--------|----------------------|
| `POST /issueLink` | Link two issues (`linkIssues`). Body `{"type":{"name":"Blocks"},"inwardIssue":{"key":"PROJ-1"},"outwardIssue":{"key":"PROJ-2"},"comment":{"body":<ADF>}?}`. `204`. |
| `GET /issueLink/{linkId}` | Get a link (`getIssueLink`). |
| `DELETE /issueLink/{linkId}` | Remove a link (`deleteIssueLink`). |

## Issue link types

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issueLinkType` | List link types (`getIssueLinkTypes`) — `Blocks`, `Relates`, `Duplicate`, `Cloners`, … with inward/outward labels. |
| `POST /issueLinkType` | Create a link type (`createIssueLinkType`). Body `{"name","inward","outward"}`. |
| `PUT /issueLinkType/{issueLinkTypeId}` · `DELETE …` | Update / delete a link type. |

## Remote links (external URLs)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issue/{issueIdOrKey}/remotelink` | List remote links (`getRemoteIssueLinks`). |
| `POST /issue/{issueIdOrKey}/remotelink` | Create or update by globalId (`createOrUpdateRemoteIssueLink`). Body `{"globalId"?,"object":{"url":"https://…","title":"…","icon":{…}?}}`. |
| `GET /issue/{issueIdOrKey}/remotelink/{linkId}` · `PUT …` · `DELETE …` | Get / update / delete one remote link by id. |
| `DELETE /issue/{issueIdOrKey}/remotelink?globalId=…` | Delete by globalId (`deleteRemoteIssueLinkByGlobalId`). |

## Notes
- **Attachments are the one multipart endpoint** — never send JSON; always include `-H "X-Atlassian-Token: no-check"` or the upload is rejected as a possible XSRF.
- Link direction matters: `inwardIssue` "is blocked by" / `outwardIssue` "blocks" depends on the type's labels — check `GET /issueLinkType`.
- For exact schemas: `grep -n '"operationId": "linkIssues"' ../jira-openapi-v3.json`.
