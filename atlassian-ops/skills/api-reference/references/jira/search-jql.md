# Jira Search & JQL

Find issues with JQL (Jira Query Language). Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`. The current search endpoint is `/search/jql`; the older `/search` is deprecated and being removed (CHANGE-2046) — do not use it.

**`/search/jql` only accepts a bounded JQL** — one with a search restriction (`project = PROJ`, `assignee = currentUser()`, `created >= -30d`, …). A bare `ORDER BY …` (no restriction) is unbounded and returns `400`. Unbounded: `order by key desc`. Bounded: `created >= -30d ORDER BY created DESC`.

## Search

| Method | Purpose & key fields |
|--------|----------------------|
| `POST /search/jql` | **Current** issue search (`searchAndReconsileIssuesUsingJqlPost`). Body `{"jql":"<bounded JQL>","fields":["summary","status","assignee"],"maxResults":50,"nextPageToken":"…"?,"expand":"…"?,"reconcileIssues":[10001,10002]?}`. Returns `{issues, nextPageToken, isLast}` (+ `names`/`schema` with `expand`). Cursor pagination — pass the returned `nextPageToken` to get the next page. |
| `GET /search/jql` | Same via query string (`searchAndReconsileIssuesUsingJql`): `?jql=…&fields=summary,status&maxResults=50&nextPageToken=…`. Use POST when the JQL is too long for a URL. |
| `POST /issue/bulkfetch` | Fetch issues by id/key, up to 100 per call — **1000** when the request is shaped for it (see `issues.md`). Use it after a search that returned only ids. |
| `POST /search/approximate-count` | Fast approximate issue count for a JQL (`countIssues`). Body `{"jql":"…"}`. Cheaper than fetching for totals. |
| `GET /search` · `POST /search` | **Deprecated, being removed** (CHANGE-2046) offset search (`searchForIssuesUsingJql[Post]`, `startAt`/`maxResults`/`total`). Use `/search/jql`. |
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
- **JQL must be bounded.** An unbounded query (only `ORDER BY …`) fails with `400`; add a restriction such as `project = PROJ` or `created >= -30d`. The `ORDER BY` clause may name at most 7 fields.
- **`fields` defaults to `id` only** — an omitted `fields` returns just issue ids, not the navigable set. Name the fields you need (`"fields":["summary","status"]`); `"*all"` returns everything, `"*navigable"` the navigable set, `-description` excludes one.
- **`maxResults` goes up to 5000 only when you ask for `id`/`key` alone**; with more fields the API may return fewer items per page.
- **Pagination on `/search/jql` is token-based**, not `startAt` — loop while `isLast` is false, passing `nextPageToken`. The last page carries no `nextPageToken`; a token expires after 7 days. There is **no `total` and no `startAt`** in the response — count with `POST /search/approximate-count`.
- **Read-after-write:** search results can lag behind a write. Pass `reconcileIssues` (up to 50 issue ids, the same list on every page) to make those issues consistent with the results; see https://developer.atlassian.com/cloud/jira/platform/search-and-reconcile/. `includeArchivedProjects=true` also returns issues from archived projects.
- Values with spaces must be quoted in JQL (`status = "In Progress"`). Reserved words/punctuation in names need quoting too.
- `expand=names,schema` annotates the result with field display names and types.
- For exact schemas: `grep -n '"operationId": "searchAndReconsileIssuesUsingJqlPost"' ../jira-openapi-v3.json`.
