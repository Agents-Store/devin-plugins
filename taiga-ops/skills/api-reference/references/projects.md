# Projects, Templates, Memberships, Roles & Permissions — API Reference

All paths under `${TAIGA_API_URL%/}/api/v1`, header `Authorization: Bearer ${TAIGA_AUTH_TOKEN}`. Edits require the object's current `version`.

## Projects

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/projects` | List projects (filters `?member=<userId>`, `?members=`, `?is_backlog_activated=`, `?order_by=`) | — |
| POST | `/projects` | Create a project | `name`, `description`, `is_private`, `creation_template` (template id) |
| GET | `/projects/{id}` | Get a project | — |
| GET | `/projects/by_slug?slug=<slug>` | Get a project by slug | — |
| PATCH | `/projects/{id}` | Edit project (partial) | `version`, e.g. `name`, `description`, `is_private`, `is_backlog_activated`, `is_kanban_activated`, `is_issues_activated`, `is_wiki_activated` |
| PUT | `/projects/{id}` | Replace project | full object + `version` |
| DELETE | `/projects/{id}` | Delete a project | — |
| POST | `/projects/bulk_update_order` | Reorder the user's projects | `[{project_id, order}, ...]` |
| GET | `/projects/{id}/modules` | Get module (integration) config | — |
| PATCH | `/projects/{id}/modules` | Edit module config | module settings |
| GET | `/projects/{id}/stats` | Project statistics | — |
| GET | `/projects/{id}/issues_stats` | Issue statistics | — |
| POST | `/projects/{id}/like` | Like (favorite) | — |
| POST | `/projects/{id}/unlike` | Unlike | — |
| GET | `/projects/{id}/fans` | List fans (likers) | — |
| POST | `/projects/{id}/watch` | Watch project | `notify_level` |
| POST | `/projects/{id}/unwatch` | Unwatch | — |
| GET | `/projects/{id}/watchers` | List watchers | — |
| POST | `/projects/{id}/duplicate` | Duplicate project | `name`, `description`, `is_private`, `users` |
| POST | `/projects/{id}/leave` | Leave the project | — |
| POST | `/projects/{id}/change_logo` | Set logo (multipart) | `logo` (file) |
| POST | `/projects/{id}/remove_logo` | Remove logo | — |

### Tags

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/projects/{id}/tags_colors` | Map of tag → color | — |
| POST | `/projects/{id}/create_tag` | Create a tag | `tag`, `color` |
| POST | `/projects/{id}/edit_tag` | Rename / recolor a tag | `from_tag`, `to_tag?`, `color?` |
| POST | `/projects/{id}/delete_tag` | Delete a tag | `tag` |
| POST | `/projects/{id}/mix_tags` | Merge tags | `from_tags[]`, `to_tag` |

```bash
# Create a private project from a template
curl -s -X POST -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d '{"name":"Apollo","description":"Launch project","is_private":true}' \
  "${TAIGA_API_URL%/}/api/v1/projects" | jq '{id, slug, name}'
```

## Project templates

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/project-templates` | List templates | — |
| POST | `/project-templates` | Create a template | `name`, `slug`, `description`, `default_owner_role`, `roles`, `us_statuses`, `task_statuses`, `issue_statuses`, etc. |
| GET | `/project-templates/{id}` | Get a template | — |
| PATCH | `/project-templates/{id}` | Edit (partial) | changed fields |
| PUT | `/project-templates/{id}` | Replace | full object |
| DELETE | `/project-templates/{id}` | Delete | — |

## Memberships & invitations

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/memberships?project=<id>` | List members | — |
| POST | `/memberships` | Add a member by email | `project`, `role`, `username` (email) |
| POST | `/memberships/bulk_create` | Invite many | `project`, `bulk_memberships:[{role_id, username}]` |
| GET | `/memberships/{id}` | Get a membership | — |
| PATCH | `/memberships/{id}` | Change role (partial) | `version`, `role` |
| PUT | `/memberships/{id}` | Replace membership | full object + `version` |
| DELETE | `/memberships/{id}` | Remove a member | — |
| POST | `/memberships/{id}/resend_invitation` | Resend the invite email | — |
| GET | `/invitations/{uuid}` | Inspect an invitation by UUID (no auth) | — |

## Roles & permissions

| Method | Path | Purpose | Key fields |
|--------|------|---------|-----------|
| GET | `/roles?project=<id>` | List project roles | — |
| POST | `/roles` | Create a role | `project`, `name`, `permissions[]`, `computable` |
| GET | `/roles/{id}` | Get a role | — |
| PATCH | `/roles/{id}` | Edit role (partial) | `version`, `name`, `permissions[]` |
| PUT | `/roles/{id}` | Replace role | full object + `version` |
| DELETE | `/roles/{id}` | Delete a role | — |
| GET | `/permissions` | List all assignable permission codes | — |

Permission codes (subset) used in `permissions[]`: `view_project`, `add_milestone`, `modify_milestone`, `delete_milestone`, `view_milestones`, `add_us`, `modify_us`, `delete_us`, `view_us`, `add_task`, `modify_task`, `comment_task`, `delete_task`, `view_tasks`, `add_issue`, `modify_issue`, `comment_issue`, `delete_issue`, `view_issues`, `add_wiki_page`, `modify_wiki_page`, `delete_wiki_page`, `view_wiki_pages`, `add_wiki_link`, `view_wiki_links`. Fetch the live list with `GET /permissions`.

> Swimlanes are not documented in the official REST API reference; the Taiga UI manages them through Kanban configuration. Do not assume `/swimlanes` endpoints exist.
