---
name: setup
description: This skill should be used when the user wants to "connect to Jira", "connect to Confluence", "authenticate with Atlassian", "set up Jira/Confluence access", "use my Atlassian API token", or before running any Jira or Confluence REST API call. Establishes Atlassian Cloud Basic auth (email + API token) and the global conventions both APIs share (base paths, headers, Jira startAt/maxResults vs Confluence cursor pagination, ADF/storage body formats, accountId).
---

# Atlassian Setup & Authentication

Establish access to an Atlassian Cloud site and learn the conventions every other call depends on. Do this once per session before any Jira or Confluence operation. One API token authenticates **both** products on the same site.

## Environment variables

The user sets these in their shell or repo `.env`. Read them — never hardcode or print the token.

| Variable | Required | Meaning |
|----------|----------|---------|
| `ATLASSIAN_SITE_URL` | yes | Cloud site root, e.g. `https://your-domain.atlassian.net`. **No trailing path** — do not append `/rest` or `/wiki` here. |
| `ATLASSIAN_EMAIL` | yes | Atlassian account email. Used as the **username** half of HTTP Basic auth. |
| `ATLASSIAN_API_TOKEN` | yes | API token minted at `https://id.atlassian.com/manage-profile/security/api-tokens`. Used as the **password** half. Treat it like a password — never echo or commit it. |

If `ATLASSIAN_SITE_URL` is missing, ask the user for it. Normalize the trailing slash with `${ATLASSIAN_SITE_URL%/}` and build the two product bases from it:

```bash
JIRA="${ATLASSIAN_SITE_URL%/}/rest/api/3"      # Jira Cloud platform REST v3
CONF="${ATLASSIAN_SITE_URL%/}/wiki/api/v2"     # Confluence Cloud REST v2 (note the /wiki prefix)
```

## Step 1 — Verify access (one call per product)

```bash
# Jira: who am I (confirms the token works on Jira)
curl -s -u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json" \
  "${ATLASSIAN_SITE_URL%/}/rest/api/3/myself" | jq '{accountId, displayName, emailAddress}'

# Confluence: list one space (confirms the /wiki/api/v2 base + token)
curl -s -u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json" \
  "${ATLASSIAN_SITE_URL%/}/wiki/api/v2/spaces?limit=1" | jq '.results[0] | {id, key, name}'
```

A `200` with your account on `/myself` confirms the Jira token; a space object confirms Confluence. A `401` means a bad email/token. A `404` on the Confluence call almost always means the base path is missing the `/wiki` prefix.

## Global conventions (apply to every call)

Internalize these once so individual operations stay short.

- **Auth — HTTP Basic.** Send `-u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}"` on every request (`curl` base64-encodes it). Always add `-H "Accept: application/json"`; add `-H "Content-Type: application/json"` whenever you send a JSON body (POST/PUT). The password is the **API token**, never the account password.
- **REST by noun, real verbs.** Unlike RPC-style APIs, these use HTTP methods and path params: `GET` to read, `POST` to create, `PUT` to update, `DELETE` to remove. The resource id lives in the path (e.g. `/issue/PROJ-123`, `/pages/12345`).
- **Jira rich text is ADF (JSON), not markdown.** `description`, comment `body`, and other rich-text fields on Jira v3 are **Atlassian Document Format** documents, not plain strings. The minimal paragraph:
  ```json
  {"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"Hello from the API"}]}]}
  ```
  A plain string in those fields returns `400`.
- **Confluence bodies carry a `representation`.** Use `storage` (XHTML storage format) or `atlas_doc_format` (ADF). On **update**, you must send the **next `version.number`** (current + 1) — Confluence uses optimistic locking, so fetch the current version first.
- **Pagination differs by product.**
  - **Jira** — offset style: `startAt` + `maxResults` in the query; responses carry `{startAt, maxResults, total, isLast}` and an array (`issues`, `values`, …). Walk by incrementing `startAt`. (Newer issue search uses a `nextPageToken` — see `search-jql.md`.)
  - **Confluence v2** — cursor style: `limit` + `cursor` in the query; responses carry `{results, _links.next}` (and a `Link` header). Follow `_links.next`/the cursor; do **not** compute offsets.
- **Jira identifies users by `accountId`** (GDPR — not username or email). Resolve a person with `GET /rest/api/3/user/search?query=<name|email>` and keep the `accountId`.
- **Errors.** `400` validation (malformed body / missing field / plain-string-where-ADF-expected), `401` auth, `403` permission (lacks project/space rights or admin), `404` not found or wrong base path, `409` version conflict (Confluence), `429` rate limited (honor the `Retry-After` header).
- **Boards & sprints are a separate API.** Scrum/Kanban **boards, sprints, and backlog** live in the Jira Software Agile REST API at `${ATLASSIAN_SITE_URL%/}/rest/agile/1.0/…` — **not** in the bundled platform spec. The platform spec (`/rest/api/3`) covers issues, projects, workflows, fields, schemes, and Advanced Roadmaps "Plans".

## Next steps

- Everyday Jira work (create issue, JQL search, transition, comment, assign, report) → use the `jira-operations` skill.
- Everyday Confluence work (create/update pages, spaces, comments, labels) → use the `confluence-operations` skill.
- The full endpoint catalog of every resource → load the `api-reference` skill and open the relevant `references/jira/*.md` or `references/confluence/*.md` file (or grep the bundled `*-openapi-*.json` specs).
- When a call fails → use the `troubleshoot` skill.
