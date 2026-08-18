# Tasks — API Reference

All paths under `${TAIGA_API_URL%/}/api/v1`, header `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`. Edits require the task's current `version` (GET first). Tasks usually belong to a user story (`user_story`) and optionally a sprint (`milestone`).

## Tasks

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/tasks` | List (filters `?project=`, `?milestone=`, `?user_story=`, `?status=`, `?assigned_to=`, `?tags=`) | — |
| POST | `/tasks` | Create a task | `project`, `subject`, `user_story?`, `milestone?`, `status?`, `assigned_to?`, `description?`, `tags?`, `is_blocked?`, `is_iocaine?` |
| GET | `/tasks/{id}` | Get a task | — |
| GET | `/tasks/by_ref?ref=<n>&project=<id>` | Get by reference number | — |
| PATCH | `/tasks/{id}` | Edit (partial) | `version` + changed fields |
| PUT | `/tasks/{id}` | Replace | full object + `version` |
| DELETE | `/tasks/{id}` | Delete | — |
| POST | `/tasks/bulk_create` | Create many | `project_id`, `us_id?`, `milestone_id?`, `status_id?`, `bulk_tasks` (newline subjects) |
| POST | `/tasks/bulk_update_milestone` | Move many to a sprint | `project_id`, `milestone_id`, `bulk_tasks:[{task_id, order}]` |
| GET | `/tasks/filters_data?project=<id>` | Filter metadata | — |
| POST | `/tasks/{id}/upvote` / `/downvote` | Vote / unvote | — |
| GET | `/tasks/{id}/voters` | List voters | — |
| POST | `/tasks/{id}/watch` / `/unwatch` | Watch / unwatch | — |
| GET | `/tasks/{id}/watchers` | List watchers | — |

```bash
# Add a task to user story 1234 and assign it
curl -s -X POST -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d '{"project":7,"user_story":1234,"subject":"Write migration","assigned_to":15}' \
  "${TAIGA_API_URL%/}/api/v1/tasks" | jq '{id, ref, subject}'
```

## Task statuses

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/task-statuses?project=<id>` | List | — |
| POST | `/task-statuses` | Create | `project`, `name`, `color`, `is_closed?`, `order?` |
| GET | `/task-statuses/{id}` | Get | — |
| PATCH | `/task-statuses/{id}` | Edit | `version` + fields |
| DELETE | `/task-statuses/{id}` | Delete | — |
| POST | `/task-statuses/bulk_update_order` | Reorder | `project`, `bulk_task_statuses:[[id, order]]` |

## Task custom attributes

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/task-custom-attributes?project=<id>` | List | — |
| POST | `/task-custom-attributes` | Create | `project`, `name`, `type`, `description?`, `order?` |
| GET | `/task-custom-attributes/{id}` | Get | — |
| PATCH | `/task-custom-attributes/{id}` | Edit | `version` + fields |
| DELETE | `/task-custom-attributes/{id}` | Delete | — |
| POST | `/task-custom-attributes/bulk_update_order` | Reorder | `project`, `bulk_task_custom_attributes:[[id, order]]` |

### Custom attribute values (per task)

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/tasks/custom-attributes-values/{taskId}` | Get all values | — |
| PATCH | `/tasks/custom-attributes-values/{taskId}` | Update values | `version`, `attributes_values:{<attrId>: value}` |
| PUT | `/tasks/custom-attributes-values/{taskId}` | Replace all values | `version`, `attributes_values` |

## Attachments

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/tasks/attachments?project=<id>&object_id=<taskId>` | List | — |
| POST | `/tasks/attachments` | Upload (multipart) | `project`, `object_id` (task id), `attached_file` |
| GET | `/tasks/attachments/{id}` | Get | — |
| PATCH | `/tasks/attachments/{id}` | Edit metadata | `version`, `description?`, `is_deprecated?` |
| DELETE | `/tasks/attachments/{id}` | Delete | — |
