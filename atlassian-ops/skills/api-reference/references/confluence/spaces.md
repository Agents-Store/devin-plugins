# Confluence Spaces

Spaces are the top-level containers for pages and blog posts. Base `${ATLASSIAN_SITE_URL%/}/wiki/api/v2`. A space has a numeric `id` and a human `key` (e.g. `PROJ`).

## Spaces

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /spaces` | List spaces (`getSpaces`). `?ids=&keys=PROJ&type=global&status=current&labels=&sort=name&limit=25&cursor=`. Use `?keys=PROJ` to resolve a key → numeric `id`. |
| `POST /spaces` | Create a space (`createSpace`). Body `{"key":"PROJ","name":"…","description":{"plain":{"value":"…","representation":"plain"}}?,"roleAssignments":…?}`. |
| `GET /spaces/{id}` | Get a space (`getSpaceById`). `?description-format=plain&include-icon=`. |

## Space properties (key/value metadata)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /spaces/{space-id}/properties` | List properties (`getSpaceProperties`). |
| `POST /spaces/{space-id}/properties` | Create a property (`createSpaceProperty`). Body `{"key":"…","value":<any JSON>}`. |
| `GET/PUT/DELETE /spaces/{space-id}/properties/{property-id}` | Get / update / delete a property. |

## Space permissions

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /space-permissions` | All available space-permission types (`getAvailableSpacePermissions`). |
| `GET /spaces/{id}/permissions` | Permission assignments in a space (`getSpacePermissionsAssignments`), paginated. |

## Space roles (newer RBAC model)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /space-roles` | Available space roles (`getAvailableSpaceRoles`). |
| `GET /space-role-mode` | Whether the site uses the roles model (`getSpaceRoleMode`). |
| `POST /space-roles` · `GET/PUT/DELETE /space-roles/{id}` | Manage custom space roles. |
| `GET /spaces/{id}/role-assignments` | Who has which role in a space (`getSpaceRoleAssignments`). |
| `POST /spaces/{id}/role-assignments` | Assign roles to principals (`setSpaceRoleAssignments`). |

## Notes
- **Resolve key → id once**: `GET /spaces?keys=PROJ` → `.results[0].id`, then use that numeric `id` for `spaceId` when creating pages.
- `type` is `global` or `personal`; `status` is `current` or `archived`.
- Space permission *mutation* is limited in v2 — some changes still go through v1 / the UI; assignments here are mostly read + the roles model.
- **Cursor pagination** — follow `_links.next`.
- For exact schemas: `grep -n '"operationId": "createSpace"' ../confluence-openapi-v2.json`.
