# Jira Search & JQL

Find issues with JQL (Jira Query Language). Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`. The current search endpoint is `/search/jql`; the older `/search` is deprecated.

## Search

| Method | Purpose & key fields |
|--------|----------------------|
| `POST /search/jql` | **Current** issue search (`searchAndReconsileIssuesUsingJqlPost`). Body `{"jql":"…","fields":["summary","status","assignee"],"maxResults":50,"nextPageToken":"…"?,"expand":"…"?}`. Returns `{issues, nextPageToken, isLast}`. Cursor pagination — pass the returned `nextPageToken` to get the next page. |
| `GET /search/jql` | Same via query string (`searchAndReconsileIssuesUsingJql`): `?jql=…&fields=summary,status&maxResults=50&nextPageToken=…`. |
| `POST /search/approximate-count` | Fast approximate issue count for a JQL (`countIssues`). Body `{"jql":"…"}`. Cheaper than fetching for totals. |
| `GET /search` · `POST /search` | **Deprecated** offset search (`searchForIssuesUsingJql[Post]`, `startAt`/`maxResults`/`total`). Prefer `/search/jql`. |
| `GET /issue/picker` | Issue picker suggestions for autocomplete (`getIssuePickerResource`). `?query=…&currentJQL=…`. |
| `POST /jql/match` | Check whether given issues match given JQL queries (`matchIssues`). Body `{"jqls":[…],"issueIds":[…]}`. |

## JQL tooling

| Method | Purpose & key fields |
|--------|----------------------|
| `POST /jql/parse` | Validate/parse JQL strings (`parseJqlQueries`). Body `{"queries":["project = PROJ"]}`. Returns structure + errors. |
| `GET /jql/autocompletedata` | Reference data (visible fields, functions, operators) for building JQL (`getAutoComplete`). |
| `GET /jql/autocompletedata/suggestions` | Value suggestions for a field while typing (`getFieldAutoCompleteForQueryString`). `?fieldName=…&fieldValue=…`. |
| `POST /jql/sanitize` | Sanitize JQL for a given account (`sanitiseJqlQueries`). |

## JQL primer

A JQL string is `field operator value [AND|OR …] [ORDER BY field ASC|DESC]`. Common building blocks:
- `project = PROJ` · `project in (A, B)`
- `status = "In Progress"` · `statusCategory != Done` (categories: `"To Do"`, `"In Progress"`, `Done`)
- `assignee = currentUser()` · `assignee is EMPTY` · `assignee in (<accountId>)`
- `issuetype = Bug` · `priority >= High` · `labels = backend`
- `created >= -7d` · `updated >= startOfWeek()` · `due <= endOfMonth()`
- `fixVersion = "1.2.0"` · `sprint in openSprints()` · `parent = PROJ-100`
- `text ~ "login error"` (full-text) · `summary ~ "timeout*"`
- Order: `... ORDER BY priority DESC, created ASC`

## Notes
- **Pick fields explicitly** (`"fields":["summary","status"]`) to keep responses small; `"*all"` returns everything, `"*navigable"` the navigable set.
- **Pagination on `/search/jql` is token-based**, not `startAt` — loop while `isLast` is false, passing `nextPageToken`.
- Values with spaces must be quoted in JQL (`status = "In Progress"`). Reserved words/punctuation in names need quoting too.
- `expand=names,schema` annotates the result with field display names and types.
- For exact schemas: `grep -n '"operationId": "searchAndReconsileIssuesUsingJqlPost"' ../jira-openapi-v3.json`.
