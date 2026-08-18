# Epics — API Reference

All paths under `${TAIGA_API_URL%/}/api/v1`, header `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`. Edits (`PATCH`/`PUT`) require the epic's current `version` (GET first).

## Epics

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/epics?project=<id>` | List epics (filters `?assigned_to=`, `?status=`, `?tags=`) | — |
| POST | `/epics` | Create an epic | `project`, `subject`, `description?`, `status?`, `assigned_to?`, `color?`, `tags?`, `is_blocked?` |
| GET | `/epics/{id}` | Get an epic | — |
| GET | `/epics/by_ref?ref=<n>&project=<id>` | Get by reference number | — |
| PATCH | `/epics/{id}` | Edit (partial) | `version` + changed fields |
| PUT | `/epics/{id}` | Replace | full object + `version` |
| DELETE | `/epics/{id}` | Delete | — |
| POST | `/epics/bulk_create` | Create many | `project`, `bulk_epics` (newline subjects or array) |
| GET | `/epics/filters_data?project=<id>` | Filter metadata (statuses, assigned, tags) | — |
| POST | `/epics/{id}/upvote` | Vote | — |
| POST | `/epics/{id}/downvote` | Remove vote | — |
| GET | `/epics/{id}/voters` | List voters | — |
| POST | `/epics/{id}/watch` | Watch | — |
| POST | `/epics/{id}/unwatch` | Unwatch | — |
| GET | `/epics/{id}/watchers` | List watchers | — |

```bash
curl -s -X POST -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d '{"project":7,"subject":"Billing revamp","color":"#e44057"}' \
  "${TAIGA_API_URL%/}/api/v1/epics" | jq '{id, ref, subject}'
```

## Related user stories

Link user stories under an epic.

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/epics/{epicId}/related_userstories` | List linked stories | — |
| POST | `/epics/{epicId}/related_userstories` | Link a story | `epic`, `user_story` |
| GET | `/epics/{epicId}/related_userstories/{usId}` | Get a link | — |
| PATCH | `/epics/{epicId}/related_userstories/{usId}` | Edit link (order) | `version`, `order` |
| DELETE | `/epics/{epicId}/related_userstories/{usId}` | Unlink | — |
| POST | `/epics/{epicId}/related_userstories/bulk_create` | Link many | `bulk_userstories[]` |

## Epic statuses

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/epic-statuses?project=<id>` | List | — |
| POST | `/epic-statuses` | Create | `project`, `name`, `color`, `is_closed?`, `order?` |
| GET | `/epic-statuses/{id}` | Get | — |
| PATCH | `/epic-statuses/{id}` | Edit | `version` + fields |
| DELETE | `/epic-statuses/{id}` | Delete | — |
| POST | `/epic-statuses/bulk_update_order` | Reorder | `project`, `bulk_epic_statuses:[[id, order]]` |

## Epic custom attributes

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/epic-custom-attributes?project=<id>` | List | — |
| POST | `/epic-custom-attributes` | Create | `project`, `name`, `type` (`text`/`multiline`/`richtext`/`date`/`url`/`dropdown`/`checkbox`/`number`), `description?`, `order?` |
| GET | `/epic-custom-attributes/{id}` | Get | — |
| PATCH | `/epic-custom-attributes/{id}` | Edit | `version` + fields |
| DELETE | `/epic-custom-attributes/{id}` | Delete | — |
| POST | `/epic-custom-attributes/bulk_update_order` | Reorder | `project`, `bulk_epic_custom_attributes:[[id, order]]` |

### Custom attribute values (per epic)

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/epics/custom-attributes-values/{epicId}` | Get all values | — |
| PATCH | `/epics/custom-attributes-values/{epicId}` | Update values (partial) | `version`, `attributes_values:{<attrId>: value}` |
| PUT | `/epics/custom-attributes-values/{epicId}` | Replace all values | `version`, `attributes_values` |

## Epic attachments

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/epics/attachments?project=<id>&object_id=<epicId>` | List | — |
| POST | `/epics/attachments` | Upload (multipart) | `project`, `object_id` (epic id), `attached_file` |
| GET | `/epics/attachments/{id}` | Get | — |
| PATCH | `/epics/attachments/{id}` | Edit metadata | `version`, `description?`, `is_deprecated?` |
| DELETE | `/epics/attachments/{id}` | Delete | — |
