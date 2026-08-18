# Jira Dashboards & Filters

Saved JQL filters and the dashboards/gadgets built on them. Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`.

## Filters (saved JQL)

| Method | Purpose & key fields |
|--------|----------------------|
| `POST /filter` | Create a filter (`createFilter`). Body `{"name","jql":"project = PROJ AND statusCategory != Done","description":"…","favourite":true}`. |
| `GET /filter/search` | Paginated filter search (`getFiltersPaginated`). `?filterName=&accountId=&orderBy=name&expand=jql,owner,sharePermissions`. |
| `GET /filter/my` · `GET /filter/favourite` | The current user's filters / favourites. |
| `GET /filter/{id}` · `PUT /filter/{id}` · `DELETE /filter/{id}` | Get / update / delete a filter. |
| `PUT /filter/{id}/favourite` · `DELETE …/favourite` | Add / remove from favourites. |
| `GET/PUT/DELETE /filter/{id}/columns` | The filter's result columns. |
| `PUT /filter/{id}/owner` | Transfer ownership (`changeFilterOwner`). Body `{"accountId":"…"}`. |

## Filter sharing

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /filter/{id}/permission` | List share permissions (`getSharePermissions`). |
| `POST /filter/{id}/permission` | Add a share (`addSharePermission`). Body `{"type":"group"|"project"|"global","groupname"?,"projectId"?}`. |
| `DELETE /filter/{id}/permission/{permissionId}` | Remove a share. |
| `GET/PUT /filter/defaultShareScope` | Default scope for new filters (`GLOBAL`|`AUTHENTICATED`|`PRIVATE`). |

## Dashboards

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /dashboard` | List dashboards (`getAllDashboards`). |
| `GET /dashboard/search` | Paginated search (`getDashboardsPaginated`). `?dashboardName=&orderBy=name`. |
| `POST /dashboard` | Create a dashboard (`createDashboard`). Body `{"name","sharePermissions":[…],"editPermissions":[…]}`. |
| `GET /dashboard/{id}` · `PUT /dashboard/{id}` · `DELETE /dashboard/{id}` | Get / update / delete. |
| `POST /dashboard/{id}/copy` | Duplicate a dashboard (`copyDashboard`). |
| `GET /dashboard/gadgets` | Gadget types available to add (`getAllAvailableDashboardGadgets`). |
| `GET /dashboard/{dashboardId}/gadget` · `POST …/gadget` | List / add gadgets. |
| `PUT /dashboard/{dashboardId}/gadget/{gadgetId}` · `DELETE …` | Move/resize / remove a gadget. |
| `GET/PUT/DELETE /dashboard/{dashboardId}/items/{itemId}/properties/{propertyKey}` | Gadget config key/value store. |

## Notes
- A dashboard gadget usually points at a **filter** — create the filter first, then add a gadget referencing its id via gadget properties.
- Share/edit permissions use the same holder shapes as elsewhere (`group`, `project`, `global`, `authenticated`).
- For exact schemas: `grep -n '"operationId": "createFilter"' ../jira-openapi-v3.json`.
