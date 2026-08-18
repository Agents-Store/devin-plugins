# History, Comments, Attachments, Webhooks & Notifications — API Reference

All paths under `${TAIGA_API_URL%/}/api/v1`, header `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`.

## History & comments

History records every change to an item, including comments. `{type}` is one of `epic`, `userstory`, `task`, `issue`, `wiki`. Comments are not a separate resource — you add one by `PATCH`-ing the item with a `comment` field; you manage existing comments through history.

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/history/{type}/{id}` | Full change + comment history of an item | — |
| GET | `/history/{type}/{id}/comment_versions?id=<commentId>` | All versions of one comment | — |
| POST | `/history/{type}/{id}/edit_comment?id=<commentId>` | Edit a comment | `comment` |
| POST | `/history/{type}/{id}/delete_comment?id=<commentId>` | Soft-delete a comment | — |
| POST | `/history/{type}/{id}/undelete_comment?id=<commentId>` | Restore a deleted comment | — |

```bash
# Add a comment to user story 1234 (comments ride on the item PATCH)
US=$(curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" "${TAIGA_API_URL%/}/api/v1/userstories/1234")
VER=$(echo "$US" | jq -r .version)
curl -s -X PATCH -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"comment\":\"Reviewed — ready for QA\",\"version\":${VER}}" \
  "${TAIGA_API_URL%/}/api/v1/userstories/1234" > /dev/null

# Read the history (comments included)
curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
  "${TAIGA_API_URL%/}/api/v1/history/userstory/1234" | jq '.[].comment // empty'
```

## Attachments (overview)

Every work item and wiki page uses the same attachment pattern. Detailed in each item's reference file.

- List / create: `GET|POST /api/v1/{resource}/attachments` (POST is multipart: `project`, `object_id`, `attached_file`).
- Get / edit / delete: `GET|PATCH|PUT|DELETE /api/v1/{resource}/attachments/{id}` (edits need `version`).
- `{resource}` ∈ `epics`, `userstories`, `tasks`, `issues`, `wiki`.

## Webhooks

Project-level callbacks fired on item events. Taiga signs each payload with HMAC-SHA1 using `key`.

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/webhooks?project=<id>` | List webhooks | — |
| POST | `/webhooks` | Create a webhook | `project`, `name`, `url`, `key` (signing secret) |
| GET | `/webhooks/{id}` | Get a webhook | — |
| PATCH | `/webhooks/{id}` | Edit (partial) | `name?`, `url?`, `key?` |
| PUT | `/webhooks/{id}` | Replace | full object |
| DELETE | `/webhooks/{id}` | Delete | — |
| POST | `/webhooks/{id}/test` | Send a test payload | — |

```bash
curl -s -X POST -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d '{"project":7,"name":"CI hook","url":"https://ci.example.com/taiga","key":"s3cr3t"}' \
  "${TAIGA_API_URL%/}/api/v1/webhooks" | jq '{id, name, url}'
```

## Webhook logs

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/webhooklogs?webhook=<id>` | List delivery logs for a webhook |
| GET | `/webhooklogs/{id}` | Get one delivery (request + response) |
| POST | `/webhooklogs/{id}/resend` | Re-deliver a failed payload |

## Notify policies

Per-user, per-project notification level. Levels: `1` = all, `2` = involved only, `3` = none.

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/notify-policies` | List the user's policies (one per project) | — |
| GET | `/notify-policies/{id}` | Get a policy | — |
| PATCH | `/notify-policies/{id}` | Set the level | `notify_level` |
| PUT | `/notify-policies/{id}` | Replace | `notify_level` |
| DELETE | `/notify-policies/{id}` | Reset to default | — |
