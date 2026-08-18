# Jira Permissions & Schemes

Who can do what, and the configurable value lists (priorities, resolutions, security, notifications). Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`. Mostly admin-level.

## Permissions

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /mypermissions?projectKey=&permissions=` | What the current user may do (`getMyPermissions`). Pass a comma list of permission keys. |
| `GET /permissions` | All permission keys in the instance (`getAllPermissions`). |
| `POST /permissions/check` | Bulk-check global + project permissions (`getBulkPermissions`). Body `{"accountId","projectPermissions":[{"projects":[…],"permissions":[…]}]}`. |
| `POST /permissions/project` | Projects where the user has given permissions (`getPermittedProjects`). |

## Permission schemes

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /permissionscheme` · `POST /permissionscheme` | List / create permission schemes. |
| `GET /permissionscheme/{schemeId}` · `PUT …` · `DELETE …` | Get / update / delete a scheme. |
| `GET /permissionscheme/{schemeId}/permission` | List grants (`getPermissionSchemeGrants`). |
| `POST /permissionscheme/{schemeId}/permission` | Add a grant (`createPermissionGrant`). Body `{"holder":{"type":"group"|"user"|"projectRole","parameter":"…"},"permission":"BROWSE_PROJECTS"}`. |
| `DELETE /permissionscheme/{schemeId}/permission/{permissionId}` | Remove a grant. |

## Issue security schemes & levels

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issuesecurityschemes` · `POST /issuesecurityschemes` | List / create issue-security schemes. |
| `PUT /issuesecurityschemes/{schemeId}/level` · `…/level/{levelId}/member` | Add a level / add members to a level. |
| `PUT /issuesecurityschemes/project` | Associate schemes to projects (`associateSchemesToProjects`). |

## Notification schemes

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /notificationscheme` · `POST /notificationscheme` | List / create notification schemes. |
| `PUT /notificationscheme/{id}/notification` | Add notifications (events → recipients) (`addNotifications`). |
| `GET /notificationscheme/project` | Scheme↔project mappings. |

## Priorities & priority schemes

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /priority` · `GET /priority/search` | List / search priorities. |
| `POST /priority` · `PUT /priority/{id}` · `DELETE /priority/{id}` | Create / update / delete a priority. |
| `PUT /priority/default` · `PUT /priority/move` | Set default / reorder. |
| `GET /priorityscheme` · `POST /priorityscheme` | List / create priority schemes (Cloud). |

## Resolutions

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /resolution` · `GET /resolution/search` | List / search resolutions. |
| `POST /resolution` · `PUT /resolution/{id}` · `DELETE /resolution/{id}` | Create / update / delete. |
| `PUT /resolution/default` · `PUT /resolution/move` | Set default / reorder. |

## Notes
- **Grant holders** are `group` (by name/id), `user` (by accountId), `projectRole` (by role id), `applicationRole`, `assignee`, `reporter`, etc. — `parameter` carries the id.
- Use `GET /mypermissions` to debug a `403`: it shows exactly which permission the token user is missing.
- Changing schemes affects every project they're assigned to — confirm before editing shared schemes.
- For exact schemas: `grep -n '"operationId": "createPermissionGrant"' ../jira-openapi-v3.json`.
