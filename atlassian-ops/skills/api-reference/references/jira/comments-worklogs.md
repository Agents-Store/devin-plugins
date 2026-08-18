# Jira Comments, Worklogs & Properties

Discussion, time tracking, and key/value metadata on issues. Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`. **Comment and worklog bodies are ADF JSON** (see `issues.md`).

## Issue comments

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issue/{issueIdOrKey}/comment` | List comments (`getComments`). `?startAt=&maxResults=&orderBy=created&expand=renderedBody`. |
| `POST /issue/{issueIdOrKey}/comment` | Add a comment (`addComment`). Body `{"body":<ADF>,"visibility":{"type":"role","value":"Administrators"}?}`. |
| `GET /issue/{issueIdOrKey}/comment/{id}` | Get one comment (`getComment`). |
| `PUT /issue/{issueIdOrKey}/comment/{id}` | Update a comment (`updateComment`). Body `{"body":<ADF>}`. |
| `DELETE /issue/{issueIdOrKey}/comment/{id}` | Delete a comment (`deleteComment`). **Confirm first.** |
| `POST /comment/list` | Fetch comments by id across issues (`getCommentsByIds`). Body `{"ids":[1,2,3]}`. |

## Issue worklogs (time tracking)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issue/{issueIdOrKey}/worklog` | List worklogs on an issue (`getIssueWorklog`). |
| `POST /issue/{issueIdOrKey}/worklog` | Log work (`addWorklog`). Body `{"timeSpent":"3h 30m" | "timeSpentSeconds":12600,"started":"2026-05-29T09:00:00.000+0000","comment":<ADF>?}`. `?adjustEstimate=new|leave|manual|auto`. |
| `GET /issue/{issueIdOrKey}/worklog/{id}` | Get one worklog (`getWorklog`). |
| `PUT /issue/{issueIdOrKey}/worklog/{id}` | Update a worklog (`updateWorklog`). |
| `DELETE /issue/{issueIdOrKey}/worklog/{id}` | Delete a worklog (`deleteWorklog`). `?adjustEstimate=…`. |
| `POST /issue/{issueIdOrKey}/worklog/move` | Move worklogs to another issue (`bulkMoveWorklogs`). |
| `GET /worklog/updated` · `GET /worklog/deleted` | Ids of worklogs changed/deleted since a timestamp (`?since=`), for sync. |
| `POST /worklog/list` | Fetch worklogs by id in bulk (`getWorklogsForIds`). Body `{"ids":[…]}`. |

## Issue properties (key/value app data)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /issue/{issueIdOrKey}/properties` | List property keys on an issue (`getIssuePropertyKeys`). |
| `GET /issue/{issueIdOrKey}/properties/{propertyKey}` | Get a property value (`getIssueProperty`). |
| `PUT /issue/{issueIdOrKey}/properties/{propertyKey}` | Set a property (`setIssueProperty`). Body is arbitrary JSON. |
| `DELETE /issue/{issueIdOrKey}/properties/{propertyKey}` | Delete a property (`deleteIssueProperty`). |
| `PUT /issue/properties/{propertyKey}` | Bulk-set one property across issues by filter (`bulkSetIssueProperty`). |

## Notes
- **`timeSpent` vs `timeSpentSeconds`** — send exactly one. `timeSpent` uses Jira duration syntax (`"1w 2d 3h 30m"`).
- `started` is ISO 8601 with milliseconds and offset (`yyyy-MM-dd'T'HH:mm:ss.SSSZ`).
- Worklog/estimate side effects depend on `adjustEstimate`; default `auto` subtracts from the remaining estimate.
- For exact schemas: `grep -n '"operationId": "addWorklog"' ../jira-openapi-v3.json`.
