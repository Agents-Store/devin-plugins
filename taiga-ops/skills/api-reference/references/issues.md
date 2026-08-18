# Issues — API Reference

All paths under `${TAIGA_API_URL%/}/api/v1`, header `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`. Edits require the issue's current `version` (GET first). Issues carry four classifiers: `status`, `type`, `priority`, `severity`.

## Issues

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/issues` | List (filters `?project=`, `?status=`, `?type=`, `?priority=`, `?severity=`, `?assigned_to=`, `?owner=`, `?tags=`, `?milestone=`) | — |
| POST | `/issues` | Create an issue | `project`, `subject`, `description?`, `status?`, `type?`, `priority?`, `severity?`, `assigned_to?`, `milestone?`, `tags?`, `is_blocked?` |
| GET | `/issues/{id}` | Get an issue | — |
| GET | `/issues/by_ref?ref=<n>&project=<id>` | Get by reference number | — |
| PATCH | `/issues/{id}` | Edit (partial) | `version` + changed fields |
| PUT | `/issues/{id}` | Replace | full object + `version` |
| DELETE | `/issues/{id}` | Delete | — |
| POST | `/issues/bulk_create` | Create many | `project_id`, `bulk_issues` (newline subjects) |
| GET | `/issues/filters_data?project=<id>` | Filter metadata (statuses, types, priorities, severities, assigned, tags) | — |
| POST | `/issues/{id}/upvote` / `/downvote` | Vote / unvote | — |
| GET | `/issues/{id}/voters` | List voters | — |
| POST | `/issues/{id}/watch` / `/unwatch` | Watch / unwatch | — |
| GET | `/issues/{id}/watchers` | List watchers | — |

```bash
# File a high-severity bug
curl -s -X POST -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d '{"project":7,"subject":"Checkout 500s on retry","type":1,"severity":5,"priority":4}' \
  "${TAIGA_API_URL%/}/api/v1/issues" | jq '{id, ref, subject}'
```

## Issue statuses

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/issue-statuses?project=<id>` | List | — |
| POST | `/issue-statuses` | Create | `project`, `name`, `color`, `is_closed?`, `order?` |
| GET / PATCH / DELETE | `/issue-statuses/{id}` | Get / edit (`version`) / delete | — |
| POST | `/issue-statuses/bulk_update_order` | Reorder | `project`, `bulk_issue_statuses:[[id, order]]` |

## Issue types

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/issue-types?project=<id>` | List | — |
| POST | `/issue-types` | Create | `project`, `name`, `color`, `order?` |
| GET / PATCH / DELETE | `/issue-types/{id}` | Get / edit (`version`) / delete | — |
| POST | `/issue-types/bulk_update_order` | Reorder | `project`, `bulk_issue_types:[[id, order]]` |

## Priorities

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/priorities?project=<id>` | List | — |
| POST | `/priorities` | Create | `project`, `name`, `color`, `order?` |
| GET / PATCH / DELETE | `/priorities/{id}` | Get / edit (`version`) / delete | — |
| POST | `/priorities/bulk_update_order` | Reorder | `project`, `bulk_priorities:[[id, order]]` |

## Severities

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/severities?project=<id>` | List | — |
| POST | `/severities` | Create | `project`, `name`, `color`, `order?` |
| GET / PATCH / DELETE | `/severities/{id}` | Get / edit (`version`) / delete | — |
| POST | `/severities/bulk_update_order` | Reorder | `project`, `bulk_severities:[[id, order]]` |

## Issue custom attributes

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/issue-custom-attributes?project=<id>` | List | — |
| POST | `/issue-custom-attributes` | Create | `project`, `name`, `type`, `description?`, `order?` |
| GET / PATCH / DELETE | `/issue-custom-attributes/{id}` | Get / edit (`version`) / delete | — |
| POST | `/issue-custom-attributes/bulk_update_order` | Reorder | `project`, `bulk_issue_custom_attributes:[[id, order]]` |

### Custom attribute values (per issue)

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/issues/custom-attributes-values/{issueId}` | Get all values | — |
| PATCH | `/issues/custom-attributes-values/{issueId}` | Update values | `version`, `attributes_values:{<attrId>: value}` |
| PUT | `/issues/custom-attributes-values/{issueId}` | Replace all values | `version`, `attributes_values` |

## Attachments

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/issues/attachments?project=<id>&object_id=<issueId>` | List | — |
| POST | `/issues/attachments` | Upload (multipart) | `project`, `object_id` (issue id), `attached_file` |
| GET | `/issues/attachments/{id}` | Get | — |
| PATCH | `/issues/attachments/{id}` | Edit metadata | `version`, `description?`, `is_deprecated?` |
| DELETE | `/issues/attachments/{id}` | Delete | — |
