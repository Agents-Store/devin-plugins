---
name: jira-operations
description: This skill should be used when the user wants to do Jira work — "create a Jira issue", "search Jira", "run a JQL query", "transition an issue", "move an issue to Done", "assign an issue", "comment on an issue", "log work / log time", "create a Jira project", "create a version/release", "add an attachment", or any everyday Jira operation. Provides plain-language playbooks that drive the Jira Cloud REST API v3.
---

# Jira Common Operations

Plain-language playbooks for everyday Jira work, each driving the REST API v3. For exact method signatures and every field, open the `api-reference` skill's matching `references/jira/*.md` file (named in each workflow).

## Before anything: ensure access

If `ATLASSIAN_*` aren't confirmed this session, run the `setup` skill first (one `GET /myself` call). Define these once for brevity:

```bash
# Classic token → site URL; scoped token (ATLASSIAN_CLOUD_ID set) → API gateway — see `setup`
JIRA_ROOT="${ATLASSIAN_CLOUD_ID:+https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}}"
JIRA_ROOT="${JIRA_ROOT:-${ATLASSIAN_SITE_URL%/}}"
JIRA="${JIRA_ROOT}/rest/api/3"
AUTH=(-u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json")
JSON=(-H "Content-Type: application/json")
```

## The golden rules (why workflows look the way they do)

1. **Real HTTP verbs + path ids.** `GET` read, `POST` create, `PUT` update, `DELETE` remove. The id is in the path (`/issue/PROJ-123`).
2. **Rich text is ADF JSON**, not markdown — `description` and comment `body` must be an ADF doc (see `references/jira/issues.md`). A plain string returns `400`.
3. **Users are `accountId`.** Resolve a name/email with `GET /user/search` before assigning.
4. **Transitions need a live lookup.** `GET …/transitions` returns ids valid from the current status; never hardcode them.
5. **Confirm destructive actions** — `DELETE /issue`, bulk delete, project delete — show what will change first.

## Workflow: search issues with JQL

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/search/jql" \
  -d '{"jql":"project = PROJ AND statusCategory != Done ORDER BY created DESC","fields":["summary","status","assignee"],"maxResults":50}' \
  | jq '.issues[] | {key, summary: .fields.summary, status: .fields.status.name}'
```
The JQL must be **bounded** — it needs a restriction such as `project = PROJ` or `created >= -30d` before `ORDER BY`; a bare `ORDER BY created DESC` returns `400`. List the `fields` you need (the default is `id` only). Page by passing the returned `nextPageToken` until `isLast` is true — there is no `total`; use `POST /search/approximate-count` for a count. (→ `search-jql.md`)

To pull many issues with full fields, search for ids and then `POST /issue/bulkfetch` (`{"issueIdsOrKeys":[…],"fields":["summary","status"]}`): up to 1000 issues per call when `fields` is an explicit list with no multi-value fields (`comment`, `worklog`, `attachment`), otherwise 100. (→ `issues.md`)

## Workflow: create an issue

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/issue" -d '{
  "fields": {
    "project": {"key": "PROJ"},
    "issuetype": {"name": "Task"},
    "summary": "Investigate login timeout",
    "description": {"type":"doc","version":1,"content":[
      {"type":"paragraph","content":[{"type":"text","text":"Reported on prod; intermittent."}]}]}
  }
}' | jq '{key, id}'
```
If unsure which fields/types are valid, check `GET /issue/createmeta/PROJ/issuetypes` first. (→ `issues.md`)

## Workflow: comment on an issue (ADF)

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/issue/PROJ-123/comment" -d '{
  "body": {"type":"doc","version":1,"content":[
    {"type":"paragraph","content":[{"type":"text","text":"Deployed the fix to staging."}]}]}
}' | jq '{id, created}'
```
(→ `comments-worklogs.md`)

## Workflow: transition an issue (e.g. to Done)

```bash
# 1. Discover the transition id from the current status
TID=$(curl -s "${AUTH[@]}" "${JIRA}/issue/PROJ-123/transitions" \
  | jq -r '.transitions[] | select(.name=="Done") | .id')
# 2. Apply it
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/issue/PROJ-123/transitions" \
  -d "{\"transition\":{\"id\":\"${TID}\"}}"
```
(→ `issues.md`)

## Workflow: assign an issue

```bash
# Resolve the person to an accountId
ACCT=$(curl -s "${AUTH[@]}" "${JIRA}/user/search?query=alice@acme.com" | jq -r '.[0].accountId')
curl -s "${AUTH[@]}" "${JSON[@]}" -X PUT "${JIRA}/issue/PROJ-123/assignee" -d "{\"accountId\":\"${ACCT}\"}"
```
`{"accountId":null}` unassigns. (→ `users-groups.md`, `issues.md`)

## Workflow: create a project, version, component

1. **Project** — `POST /project` `{"key":"PROJ","name":"…","projectTypeKey":"software","leadAccountId":"…"}`.
2. **Version (release)** — `POST /version` `{"projectId":10000,"name":"1.2.0","releaseDate":"2026-06-01"}`.
3. **Component** — `POST /component` `{"project":"PROJ","name":"API"}`. (→ `projects-versions-components.md`)

## Workflow: add an attachment (multipart)

```bash
curl -s -u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" \
  -H "X-Atlassian-Token: no-check" \
  -F "file=@./logs/error.txt" \
  "${JIRA}/issue/PROJ-123/attachments" | jq '.[].filename'
```
Note: no `Content-Type: application/json` here — it's multipart. (→ `attachments-links.md`)

## Workflow: link two issues

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/issueLink" -d '{
  "type":{"name":"Blocks"},
  "inwardIssue":{"key":"PROJ-124"},
  "outwardIssue":{"key":"PROJ-123"}
}'
```
`GET /issueLinkType` lists the available types and their direction labels. (→ `attachments-links.md`)

## Workflow: report (paginate a JQL)

Use `POST /search/jql` (bounded JQL) with `maxResults` and loop on `nextPageToken`; or `POST /search/approximate-count` `{"jql":"…"}` for a fast total. Build a saved filter with `POST /filter` to reuse the query. (→ `search-jql.md`, `dashboards-filters.md`)

Right after a write, a search can still miss the change; pass `"reconcileIssues":[<issueId>]` for read-after-write consistency. (→ `search-jql.md`)

When a call fails (400/401/403/404/429), switch to the `troubleshoot` skill.
