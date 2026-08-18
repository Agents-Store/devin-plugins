# Jira Issues

The core of Jira. Issues are addressed by **`issueIdOrKey`** (numeric id or the human key like `PROJ-123`). All calls use Basic auth and the base `${ATLASSIAN_SITE_URL%/}/rest/api/3` (paths below are relative to it). **Rich-text fields (`description`, comment `body`, textarea custom fields) are Atlassian Document Format (ADF) JSON — not markdown.**

## ADF in one snippet

A minimal paragraph for any rich-text field:
```json
{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"Hello from the API"}]}]}
```

## Create, read, edit, delete

| Method | Purpose & key fields |
|--------|----------------------|
| `POST /issue` | Create an issue. Body `{"fields":{"project":{"key":"PROJ"},"issuetype":{"name":"Task"},"summary":"…","description":<ADF>,"assignee":{"accountId":"…"},"labels":[…],"priority":{"name":"High"}}}`. `project` + `issuetype` + `summary` required. Optional `?updateHistory=true`. Returns `{id,key,self}`. |
| `POST /issue/bulk` | Create many issues at once (`createIssues`). Body `{"issueUpdates":[{"fields":{…}}, …]}`. |
| `GET /issue/{issueIdOrKey}` | Fetch one issue. Query `fields=summary,status` to trim, `expand=changelog,renderedFields,transitions`, `?properties=…`. |
| `PUT /issue/{issueIdOrKey}` | Edit fields. Body `{"fields":{…}}` (overwrite) and/or `{"update":{"labels":[{"add":"x"}]}}` (add/remove ops). `?notifyUsers=false` to suppress mail. `204` on success. |
| `DELETE /issue/{issueIdOrKey}` | Delete. `?deleteSubtasks=true` if it has subtasks. **Confirm first.** |
| `PUT /issue/{issueIdOrKey}/assignee` | Assign (`assignIssue`). Body `{"accountId":"…"}`; `null` unassigns, `"-1"` sets project default. |

## Transitions (status changes)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issue/{issueIdOrKey}/transitions` | List transitions available **from the current status** (`getTransitions`). Ids are workflow-specific. `?expand=transitions.fields` to see required fields. |
| `POST /issue/{issueIdOrKey}/transitions` | Move the issue (`doTransition`). Body `{"transition":{"id":"31"},"fields":{…}?,"update":{"comment":[{"add":{"body":<ADF>}}]}?}`. Use a transition id from the GET above. `204` on success. |

## Metadata helpers

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issue/createmeta/{projectIdOrKey}/issuetypes` | Issue types creatable in a project (`getCreateIssueMetaIssueTypes`). |
| `GET /issue/createmeta/{projectIdOrKey}/issuetypes/{issueTypeId}` | Fields available/required for create (`getCreateIssueMetaIssueTypeId`). |
| `GET /issue/{issueIdOrKey}/editmeta` | Fields editable on an existing issue (`getEditIssueMeta`). |
| `GET /issue/{issueIdOrKey}/changelog` | Paginated change history (`getChangeLogs`). |
| `POST /issue/{issueIdOrKey}/notify` | Email a notification about the issue (`notify`). Body `{"subject","textBody","htmlBody","to":{…}}`. |

## Archive (Premium)

| Method | Purpose & key fields |
|--------|----------------------|
| `PUT /issue/archive` | Archive up to 1000 issues by key (`archiveIssues`). Body `{"issueIdsOrKeys":[…]}`. |
| `POST /issue/archive` | Archive by JQL, async (`archiveIssuesAsync`). Body `{"jql":"…"}`. |
| `PUT /issue/unarchive` | Restore archived issues (`unarchiveIssues`). |

## Bulk operations

All under `/bulk/issues/*`, return a task id you poll with `GET /bulk/queue/{taskId}` (`getBulkOperationProgress`).

| Method | Purpose & key fields |
|--------|----------------------|
| `POST /bulk/issues/fields` | Bulk edit fields (`submitBulkEdit`). `GET /bulk/issues/fields` lists editable fields first. |
| `POST /bulk/issues/move` | Bulk move to another project (`submitBulkMove`). |
| `POST /bulk/issues/transition` | Bulk transition (`submitBulkTransition`). `GET /bulk/issues/transition` lists available transitions. |
| `POST /bulk/issues/delete` | Bulk delete (`submitBulkDelete`). **Confirm first.** |
| `POST /bulk/issues/watch` · `/unwatch` | Bulk add/remove watchers. |

## Notes
- **ADF, not markdown** — a plain string in `description`/`body` returns `400`. Build the ADF doc shown above.
- **`accountId`, not username** — `assignee`/`reporter` take `{"accountId":"…"}`. Resolve via `GET /user/search?query=…` (see `users-groups.md`).
- Transition ids are per-workflow — always `GET …/transitions` first; never hardcode `31`.
- Editing a field requires it to be on the issue's edit screen — if a `PUT /issue` silently ignores a field, check `editmeta`.
- For the full request/response schema of any operation, grep the bundled spec: `grep -n '"operationId": "createIssue"' ../jira-openapi-v3.json`.
