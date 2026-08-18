---
name: api-reference
description: This skill should be used when the user asks for "Jira API endpoints", "Confluence API endpoints", "Jira/Confluence REST API", "Atlassian curl examples", "the exact method/parameters" for any Jira or Confluence resource, or needs HTTP details for issues, JQL search, comments, worklogs, attachments, links, projects, versions, components, fields, screens, workflows, statuses, users, groups, permissions, schemes, dashboards, filters, plans; or Confluence pages, blog posts, spaces, comments, attachments, labels, content properties. Indexes the full per-domain endpoint catalog plus the bundled OpenAPI specs.
disable-model-invocation: true
---

# Atlassian REST API Reference (Jira v3 + Confluence v2)

Complete catalog for the Jira Cloud platform REST API v3 and the Confluence Cloud REST API v2, split by domain. Official docs: https://developer.atlassian.com/cloud/jira/platform/rest/v3/ and https://developer.atlassian.com/cloud/confluence/rest/v2/

The **exhaustive source of truth** is the two bundled OpenAPI specs:
- `references/jira-openapi-v3.json` — 420 paths, 99 tags (OpenAPI 3.0.1).
- `references/confluence-openapi-v2.json` — 147 paths, 29 tags (OpenAPI 3.0.3).

The curated `references/jira/*.md` and `references/confluence/*.md` files below cover the common operations in plain, copy-pasteable form.

Load the `setup` skill first for authentication and the global conventions (Basic auth, headers, ADF/storage bodies, Jira `startAt`/`maxResults` vs Confluence cursor pagination, `accountId`) — those rules apply to every method here and are not repeated in each file.

## Global recap

- **Jira** base: `${ATLASSIAN_SITE_URL%/}/rest/api/3`. **Confluence** base: `${ATLASSIAN_SITE_URL%/}/wiki/api/v2`.
- Auth: `-u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}"`, `-H "Accept: application/json"` (+ `-H "Content-Type: application/json"` on writes).
- **Jira rich text = ADF JSON** (`description`, comment `body`). **Confluence body** = `{representation, value}`; update needs the next `version.number`.
- **Jira users = `accountId`** (resolve via `GET /user/search`). Paths in the Jira files below are written **relative to the `/rest/api/3` base**; Confluence paths are relative to the `/wiki/api/v2` base.

## Jira domain index

| Domain | File | Covers |
|--------|------|--------|
| Issues | `references/jira/issues.md` | createIssue, getIssue, editIssue, deleteIssue, assignIssue, getTransitions/doTransition, createmeta/editmeta, notify, changelog, archive/unarchive, bulk create/edit/move/delete/transition/watch |
| Search & JQL | `references/jira/search-jql.md` | search/jql (GET+POST), search/approximate-count, jql/parse, jql/autocompletedata, jql/match, issue/picker, JQL syntax primer |
| Comments, worklogs & properties | `references/jira/comments-worklogs.md` | issue comments CRUD, worklogs CRUD + move + deleted/updated, issue properties |
| Attachments & links | `references/jira/attachments-links.md` | add/get/delete attachments (multipart), issue links + link types, remote links |
| Projects, versions & components | `references/jira/projects-versions-components.md` | projects CRUD + search + archive/restore, versions, components, roles & actors, categories, features, templates |
| Fields & screens | `references/jira/fields-screens.md` | issue fields, custom field contexts & options, field configurations (+schemes), screens, screen tabs, screen schemes, issue type screen schemes |
| Workflows, types & statuses | `references/jira/workflows-types-statuses.md` | workflows (read/create/update/search), workflow schemes (+drafts), statuses, issue types, issue type schemes, transition rules |
| Users & groups | `references/jira/users-groups.md` | users CRUD, user search (accountId), groups + members, myself + preferences, avatars |
| Permissions & schemes | `references/jira/permissions-schemes.md` | permission schemes + grants, my/all permissions, issue security schemes & levels, notification schemes, priorities + priority schemes, resolutions |
| Dashboards & filters | `references/jira/dashboards-filters.md` | dashboards + gadgets + item properties, filters CRUD + columns + favourite + owner, filter sharing |
| Plans & teams | `references/jira/plans-teams.md` | Advanced Roadmaps plans CRUD + archive/duplicate/trash, teams in plan (atlassian + plan-only) |

## Confluence domain index

| Domain | File | Covers |
|--------|------|--------|
| Pages & blog posts | `references/confluence/pages-blogposts.md` | pages CRUD (versioned), blog posts, body-format, ancestors/children/descendants, custom content, whiteboards, databases, folders, smart links |
| Spaces | `references/confluence/spaces.md` | spaces list/get/create, space properties, space permissions, space roles |
| Comments & attachments | `references/confluence/comments-attachments.md` | footer + inline comments CRUD, attachments, versions, likes, tasks, operations |
| Labels & content properties | `references/confluence/labels-content-properties.md` | labels, content properties, classification levels, data policies, redactions, admin key, app properties |

## How to use a reference file

Each file lists endpoints as `METHOD /path` (relative to the product base) with purpose and key fields. To run one, wrap it with auth and `jq`:

```bash
# Jira example
curl -s -u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json" \
  "${ATLASSIAN_SITE_URL%/}/rest/api/3/<path>" | jq '.'
# Confluence example
curl -s -u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json" \
  "${ATLASSIAN_SITE_URL%/}/wiki/api/v2/<path>" | jq '.'
```

For the full request/response schema of any operation, grep the bundled spec by `operationId`:

```bash
grep -n '"operationId": "createIssue"' references/jira-openapi-v3.json
grep -n '"operationId": "createPage"'  references/confluence-openapi-v2.json
```

## Examples

<example>
User: "What's the endpoint to create a Jira issue?"
→ Open `references/jira/issues.md`. `POST /issue` with `{"fields":{"project":{"key":"PROJ"},"issuetype":{"name":"Task"},"summary":"…","description":<ADF>}}`. `description` must be ADF JSON, not a string.
</example>

<example>
User: "How do I search issues with JQL?"
→ Open `references/jira/search-jql.md`. `POST /search/jql` with `{"jql":"project = PROJ ORDER BY created DESC","fields":["summary","status"],"maxResults":50}`. Page with the returned `nextPageToken`.
</example>

<example>
User: "Give me the curl to update a Confluence page."
→ Open `references/confluence/pages-blogposts.md`. `GET /pages/{id}?body-format=storage` to read the current `version.number`, then `PUT /pages/{id}` with `{"id","status":"current","title","version":{"number":<current+1>},"body":{"representation":"storage","value":"<p>…</p>"}}`.
</example>
