# User Stories — API Reference

All paths under `${TAIGA_API_URL%/}/api/v1`, header `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`. Edits require the story's current `version` (GET first).

## User stories

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/userstories` | List (filters `?project=`, `?milestone=`, `?milestone__isnull=true` for backlog, `?status=`, `?assigned_to=`, `?epic=`, `?tags=`, `?status__is_closed=`) | — |
| POST | `/userstories` | Create a story | `project`, `subject`, `description?`, `status?`, `milestone?`, `assigned_to?`, `points?`, `tags?`, `is_blocked?` |
| GET | `/userstories/{id}` | Get a story | — |
| GET | `/userstories/by_ref?ref=<n>&project=<id>` | Get by reference number | — |
| PATCH | `/userstories/{id}` | Edit (partial) | `version` + changed fields |
| PUT | `/userstories/{id}` | Replace | full object + `version` |
| DELETE | `/userstories/{id}` | Delete | — |
| POST | `/userstories/bulk_create` | Create many | `project_id`, `status_id?`, `bulk_stories` (newline-separated subjects) |
| POST | `/userstories/bulk_update_backlog_order` | Reorder in backlog | `project_id`, `bulk_stories:[{us_id, order}]` |
| POST | `/userstories/bulk_update_sprint_order` | Reorder in sprint | `project_id`, `bulk_stories:[{us_id, order}]` |
| POST | `/userstories/bulk_update_kanban_order` | Reorder in kanban | `project_id`, `status_id`, `bulk_stories` |
| POST | `/userstories/bulk_update_milestone` | Move many to a sprint | `project_id`, `milestone_id`, `bulk_stories:[{us_id, order}]` |
| GET | `/userstories/filters_data?project=<id>` | Filter metadata | — |
| POST | `/userstories/{id}/upvote` / `/downvote` | Vote / unvote | — |
| GET | `/userstories/{id}/voters` | List voters | — |
| POST | `/userstories/{id}/watch` / `/unwatch` | Watch / unwatch | — |
| GET | `/userstories/{id}/watchers` | List watchers | — |

```bash
# Create a story directly into a sprint, then move it to "In progress"
US=$(curl -s -X POST -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d '{"project":7,"subject":"As a user I can reset my password","milestone":12}' \
  "${TAIGA_API_URL%/}/api/v1/userstories")
ID=$(echo "$US" | jq -r .id); VER=$(echo "$US" | jq -r .version)
curl -s -X PATCH -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"status\":456,\"version\":${VER}}" "${TAIGA_API_URL%/}/api/v1/userstories/${ID}" | jq '{id, status}'
```

## User story statuses

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/userstory-statuses?project=<id>` | List | — |
| POST | `/userstory-statuses` | Create | `project`, `name`, `color`, `is_closed?`, `is_archived?`, `wip_limit?`, `order?` |
| GET | `/userstory-statuses/{id}` | Get | — |
| PATCH | `/userstory-statuses/{id}` | Edit | `version` + fields |
| DELETE | `/userstory-statuses/{id}` | Delete | — |
| POST | `/userstory-statuses/bulk_update_order` | Reorder | `project`, `bulk_userstory_statuses:[[id, order]]` |

## Points (estimation values)

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/points?project=<id>` | List | — |
| POST | `/points` | Create | `project`, `name`, `value` (number or null), `order?` |
| GET | `/points/{id}` | Get | — |
| PATCH | `/points/{id}` | Edit | `version` + fields |
| DELETE | `/points/{id}` | Delete | — |
| POST | `/points/bulk_update_order` | Reorder | `project`, `bulk_points:[[id, order]]` |

## User story custom attributes

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/userstory-custom-attributes?project=<id>` | List | — |
| POST | `/userstory-custom-attributes` | Create | `project`, `name`, `type`, `description?`, `order?` |
| GET | `/userstory-custom-attributes/{id}` | Get | — |
| PATCH | `/userstory-custom-attributes/{id}` | Edit | `version` + fields |
| DELETE | `/userstory-custom-attributes/{id}` | Delete | — |
| POST | `/userstory-custom-attributes/bulk_update_order` | Reorder | `project`, `bulk_userstory_custom_attributes:[[id, order]]` |

### Custom attribute values (per story)

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/userstories/custom-attributes-values/{usId}` | Get all values | — |
| PATCH | `/userstories/custom-attributes-values/{usId}` | Update values | `version`, `attributes_values:{<attrId>: value}` |
| PUT | `/userstories/custom-attributes-values/{usId}` | Replace all values | `version`, `attributes_values` |

## Attachments

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/userstories/attachments?project=<id>&object_id=<usId>` | List | — |
| POST | `/userstories/attachments` | Upload (multipart) | `project`, `object_id` (us id), `attached_file` |
| GET | `/userstories/attachments/{id}` | Get | — |
| PATCH | `/userstories/attachments/{id}` | Edit metadata | `version`, `description?`, `is_deprecated?` |
| DELETE | `/userstories/attachments/{id}` | Delete | — |
