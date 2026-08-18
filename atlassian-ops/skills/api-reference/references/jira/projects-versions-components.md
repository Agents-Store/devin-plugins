# Jira Projects, Versions & Components

Project containers and the release/component structure inside them. Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`. A project is addressed by `projectIdOrKey` (numeric id or the key like `PROJ`).

## Projects

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /project` | All visible projects (`getAllProjects`, non-paginated, legacy). |
| `GET /project/search` | **Paginated** project search (`searchProjects`). `?query=&startAt=&maxResults=&orderBy=name&typeKey=software`. |
| `POST /project` | Create a project (`createProject`). Body `{"key":"PROJ","name":"…","projectTypeKey":"software","leadAccountId":"…","projectTemplateKey":"…"?,"assigneeType":"PROJECT_LEAD"}`. |
| `GET /project/{projectIdOrKey}` | Get a project (`getProject`). `?expand=description,lead,issueTypes,url,projectKeys`. |
| `PUT /project/{projectIdOrKey}` | Update a project (`updateProject`). |
| `DELETE /project/{projectIdOrKey}` | Delete immediately (`deleteProject`). **Confirm first.** Prefer the async/restore flow below. |
| `POST /project/{projectIdOrKey}/delete` · `/archive` · `/restore` | Async delete to trash, archive, and restore (`deleteProjectAsynchronously`, `archiveProject`, `restore`). |
| `GET /project/{projectIdOrKey}/statuses` | Statuses by issue type for the project (`getAllStatuses`). |
| `GET /project/recent` | Recently viewed projects (`getRecent`). |

## Versions (releases)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /project/{projectIdOrKey}/version` | Paginated versions (`getProjectVersionsPaginated`). `?orderBy=releaseDate&status=unreleased`. |
| `POST /version` | Create a version (`createVersion`). Body `{"projectId":10000,"name":"1.2.0","releaseDate":"2026-06-01","description":"…"}`. |
| `GET /version/{id}` · `PUT /version/{id}` · `DELETE /version/{id}` | Get / update / delete a version. |
| `POST /version/{id}/move` · `PUT /version/{id}/mergeto/{moveIssuesTo}` | Reorder / merge versions (`moveVersion`, `mergeVersions`). |
| `POST /version/{id}/removeAndSwap` | Delete and reassign issues' fixVersion/affectsVersion (`deleteAndReplaceVersion`). |
| `GET /version/{id}/relatedIssueCounts` · `/unresolvedIssueCount` | Issue counts for release readiness. |

## Components

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /project/{projectIdOrKey}/component` | Paginated components (`getProjectComponentsPaginated`). |
| `POST /component` | Create a component (`createComponent`). Body `{"project":"PROJ","name":"API","leadAccountId":"…","assigneeType":"COMPONENT_LEAD"}`. |
| `GET /component/{id}` · `PUT /component/{id}` · `DELETE /component/{id}` | Get / update / delete (delete takes `?moveIssuesTo=`). |
| `GET /component/{id}/relatedIssueCounts` | Issues referencing the component. |

## Roles, actors, categories, features, templates

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /project/{projectIdOrKey}/role` | Project roles + member URLs (`getProjectRoles`). |
| `POST /project/{projectIdOrKey}/role/{id}` | Add actors to a project role (`addActorUsers`). Body `{"user":["<accountId>"]}` or `{"group":["…"]}`. |
| `PUT /project/{projectIdOrKey}/role/{id}` · `DELETE …/role/{id}` | Set / remove actors (`setActors`, `deleteActor`). |
| `GET /project/{projectIdOrKey}/features` · `PUT …/features/{featureKey}` | List / toggle project features (`getFeaturesForProject`, `toggleFeatureForProject`). |
| `GET /projectCategory` · `POST /projectCategory` | List / create project categories. |
| `POST /project-template` | Create a project from a custom template (`createProjectWithCustomTemplate`). |

## Notes
- **`leadAccountId`** (not username) sets the project/component lead.
- Deleting a version with issues attached needs `removeAndSwap` or the issues keep a dangling reference — prefer it over plain `DELETE`.
- Project keys are uppercase and immutable-ish; renaming the key has wide side effects.
- For exact schemas: `grep -n '"operationId": "createProject"' ../jira-openapi-v3.json`.
