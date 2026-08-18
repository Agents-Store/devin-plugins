# Jira Workflows, Issue Types & Statuses

How issues move (workflows) and how they're classified (types, statuses). Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`. Admin-level configuration.

## Statuses

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /statuses/search` | Paginated status search (`search`). `?searchString=&statusCategory=`. |
| `GET /statuses?id=…` | Get statuses by id (`getStatusesById`). |
| `POST /statuses` · `PUT /statuses` · `DELETE /statuses` | Create / update / delete custom statuses. Body `{"statuses":[{"name","statusCategory":"IN_PROGRESS"}],"scope":{…}}`. |
| `GET /status` · `GET /status/{idOrName}` | Legacy: all statuses / one status (`getStatuses`, `getStatus`). |
| `GET /statuses/{statusId}/workflowUsages` · `/projectUsages` | Where a status is used (before deleting). |

## Issue types

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issuetype` | All issue types (`getIssueAllTypes`). |
| `POST /issuetype` | Create an issue type (`createIssueType`). Body `{"name","description","type":"standard"|"subtask","hierarchyLevel":0}`. |
| `GET /issuetype/{id}` · `PUT /issuetype/{id}` · `DELETE /issuetype/{id}` | Get / update / delete (delete takes `?alternativeIssueTypeId=`). |
| `GET /issuetype/project?projectId=` | Issue types usable in a project (`getIssueTypesForProject`). |

## Issue type schemes

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issuetypescheme` · `POST /issuetypescheme` | List / create schemes (which issue types a project may use). |
| `PUT /issuetypescheme/project` | Assign a scheme to a project (`assignIssueTypeSchemeToProject`). |
| `PUT /issuetypescheme/{id}/issuetype` · `…/issuetype/move` · `DELETE …/issuetype/{issueTypeId}` | Add / reorder / remove issue types in a scheme. |

## Workflows

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /workflow/search` | Paginated workflow search (`getWorkflowsPaginated`). `?expand=transitions,statuses`. |
| `POST /workflows` | Read workflows by id/name with full detail (`readWorkflows`). |
| `POST /workflows/create` | Create workflows (`createWorkflows`); validate first with `POST /workflows/create/validation`. |
| `POST /workflows/update` | Update workflows (`updateWorkflows`); validate with `POST /workflows/update/validation`. |
| `GET /workflows/capabilities` | Editor capabilities/rule types available (`workflowCapabilities`). |
| `DELETE /workflow/{entityId}` | Delete an inactive workflow (`deleteInactiveWorkflow`). |

## Workflow schemes (+ drafts)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /workflowscheme` · `POST /workflowscheme` | List / create workflow schemes. |
| `GET /workflowscheme/{id}` · `PUT …` · `DELETE …` | Get / update / delete a scheme. |
| `PUT /workflowscheme/project` | Assign a scheme to a project (`assignSchemeToProject`). |
| `POST /workflowscheme/{id}/createdraft` · `POST …/draft/publish` | Edit an active scheme via a draft, then publish (`createWorkflowSchemeDraftFromParent`, `publishDraftWorkflowScheme`). |
| `PUT /workflowscheme/{id}/issuetype/{issueType}` | Map an issue type to a workflow within the scheme. |

## Notes
- **Active workflow schemes can't be edited directly** — create a draft, modify it, then publish. The API enforces this.
- Status `statusCategory` is one of `TODO`, `IN_PROGRESS`, `DONE` (drives the board columns and `statusCategory` JQL).
- To delete a status/issue type, first check its `*Usages` endpoints; in-use entities can't be removed.
- For exact schemas: `grep -n '"operationId": "createWorkflows"' ../jira-openapi-v3.json`.
