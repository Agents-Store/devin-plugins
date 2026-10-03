---
name: setup
description: This skill should be used when the user wants to "connect to Jira", "connect to Confluence", "authenticate with Atlassian", "set up Jira/Confluence access", "use my Atlassian API token", "use a scoped API token", "find my cloudId", "use the Atlassian MCP / Rovo MCP", or before running any Jira or Confluence REST API call. Establishes Atlassian Cloud Basic auth (email + API token, classic or scoped), chooses between curl and the official Rovo MCP server, and states the global conventions both APIs share (base paths, headers, Jira startAt/maxResults vs Confluence cursor pagination, ADF/storage body formats, accountId).
---

# Atlassian Setup & Authentication

Establish access to an Atlassian Cloud site and learn the conventions every other call depends on. Do this once per session before any Jira or Confluence operation. One API token authenticates **both** products on the same site.

## Environment variables

The user sets these in their shell or repo `.env`. Read them — never hardcode or print the token.

| Variable | Required | Meaning |
|----------|----------|---------|
| `ATLASSIAN_SITE_URL` | yes | Cloud site root, e.g. `https://your-domain.atlassian.net`. **No trailing path** — do not append `/rest` or `/wiki` here. |
| `ATLASSIAN_EMAIL` | yes | Atlassian account email. Used as the **username** half of HTTP Basic auth. |
| `ATLASSIAN_API_TOKEN` | yes | API token minted at `https://id.atlassian.com/manage-profile/security/api-tokens`. Used as the **password** half. Treat it like a password — never echo or commit it. Tokens expire after 1–365 days (1 year by default) — a lapsed token returns `401`. |
| `ATLASSIAN_CLOUD_ID` | only for a **scoped** token | The site's `cloudId`. Set it **only** if the token was created with scopes; it moves every base URL to the `api.atlassian.com` gateway (below). Leave it unset for a classic token. |

If `ATLASSIAN_SITE_URL` is missing, ask the user for it. Normalize the trailing slash with `${ATLASSIAN_SITE_URL%/}` and build the two product bases from it:

```bash
if [ -n "${ATLASSIAN_CLOUD_ID:-}" ]; then      # scoped token → API gateway
  JIRA_ROOT="https://api.atlassian.com/ex/jira/${ATLASSIAN_CLOUD_ID}"
  CONF_ROOT="https://api.atlassian.com/ex/confluence/${ATLASSIAN_CLOUD_ID}"
else                                            # classic token → the site URL
  JIRA_ROOT="${ATLASSIAN_SITE_URL%/}"; CONF_ROOT="${ATLASSIAN_SITE_URL%/}"
fi
JIRA="${JIRA_ROOT}/rest/api/3"                  # Jira Cloud platform REST v3
CONF="${CONF_ROOT}/wiki/api/v2"                 # Confluence Cloud REST v2 (note the /wiki prefix)
# Confluence v1 (labels, attachment upload, CQL): ${CONF_ROOT}/wiki/rest/api/…
# Jira Software Agile API (boards, sprints):      ${JIRA_ROOT}/rest/agile/1.0/…
```

### Classic vs scoped API token

| | Classic token | Scoped token |
|---|---|---|
| Created with | **Create API token** | **Create API token with scopes** (pick the app and scopes, expiry 1–365 days) |
| Base URL | `${ATLASSIAN_SITE_URL}` (`https://your-domain.atlassian.net`) | `https://api.atlassian.com/ex/jira/{cloudId}` and `https://api.atlassian.com/ex/confluence/{cloudId}` |
| Auth | Basic `email:token` | Basic `email:token` (same) |
| Failure mode | `401` if expired/revoked | on the site URL → `401`/`403`; on the gateway with a missing scope → `403` |

Find the `cloudId` with the site's public tenant-info document (no auth needed):

```bash
export ATLASSIAN_CLOUD_ID="$(curl -s "${ATLASSIAN_SITE_URL%/}/_edge/tenant_info" | jq -r .cloudId)"
```

Prefer a scoped token with the narrowest scopes the task needs (for example `read:jira-work`, `write:jira-work`, `read:confluence-content.all`, `write:confluence-content`). The `cloudId` is not a secret; the token is — never echo it.

## REST (this plugin) vs the Atlassian Rovo MCP server

Atlassian also runs an official MCP server: **`https://mcp.atlassian.com/v2/mcp`** (streamable HTTP). Auth is OAuth 2.1 in the browser, or an API token (`Authorization: Basic base64(email:token)`) or a service-account key (`Authorization: Bearer …`) in a header; an organisation admin has to enable it and can disable it by policy. The v1 endpoint is switched to v2 on 2027-03-01 — always write the v2 URL, and re-authenticate once if a client cached v1 credentials.

- Its tool surface is "primary + discover/execute": `atlassianUserInfo`, `getAccessibleAtlassianResources` (call first — returns the `cloudId` every tool needs), `discover`, `executeRead` / `executeWrite` / `executeDestructive`, plus `getJiraIssue`, `searchJiraIssuesUsingJql`, `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`, `addOrEditJiraIssueComment`, `searchConfluence`, `getConfluenceContent`, `createConfluenceContent`, `updateConfluenceContent`. `?tools=all` returns a flat tool list for gateways. Your MCP client adds its own prefix to these names.
- **Prefer the MCP server** for quick interactive reads and edits (issues, JQL, pages) where OAuth is acceptable and no token should live in `.env`.
- **Prefer the REST recipes in this plugin** for everything outside that surface — workflows, fields and schemes, permission schemes, bulk operations, `bulkfetch`, Confluence v1 (labels, attachments, CQL) — and for scripts, CI and sites where the MCP server is disabled.
- This plugin does not ship an MCP configuration; connect the server in your client if you want it.

## Step 1 — Verify access (one call per product)

```bash
# Jira: who am I (confirms the token works on Jira)
curl -s -u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json" \
  "${JIRA}/myself" | jq '{accountId, displayName, emailAddress}'

# Confluence: list one space (confirms the /wiki/api/v2 base + token)
curl -s -u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json" \
  "${CONF}/spaces?limit=1" | jq '.results[0] | {id, key, name}'
```

A `200` with your account on `/myself` confirms the Jira token; a space object confirms Confluence. A `401` means a bad, expired or revoked email/token — or a scoped token sent to the site URL instead of the `api.atlassian.com/ex/…` gateway. A `404` on the Confluence call almost always means the base path is missing the `/wiki` prefix.

## Global conventions (apply to every call)

Internalize these once so individual operations stay short.

- **Auth — HTTP Basic.** Send `-u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}"` on every request (`curl` base64-encodes it). Always add `-H "Accept: application/json"`; add `-H "Content-Type: application/json"` whenever you send a JSON body (POST/PUT). The password is the **API token**, never the account password.
- **REST by noun, real verbs.** Unlike RPC-style APIs, these use HTTP methods and path params: `GET` to read, `POST` to create, `PUT` to update, `DELETE` to remove. The resource id lives in the path (e.g. `/issue/PROJ-123`, `/pages/12345`).
- **Jira rich text is ADF (JSON), not markdown.** `description`, comment `body`, and other rich-text fields on Jira v3 are **Atlassian Document Format** documents, not plain strings. The minimal paragraph:
  ```json
  {"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"Hello from the API"}]}]}
  ```
  A plain string in those fields returns `400`.
- **Confluence bodies carry a `representation`.** Use `storage` (XHTML storage format) or `atlas_doc_format` (ADF). On **update**, you must send the **next `version.number`** (current + 1) — Confluence uses optimistic locking, so fetch the current version first. In a space that requires approval before publishing, a direct update of a published page will return `409` regardless of the version number (announced 2026-09-28, rollout pending; no REST draft→approval→publish flow is documented yet — see `troubleshoot`).
- **Pagination differs by product.**
  - **Jira** — offset style: `startAt` + `maxResults` in the query; responses carry `{startAt, maxResults, total, isLast}` and an array (`values`, …). Walk by incrementing `startAt`. **Issue search (`/search/jql`) is the exception:** it uses `nextPageToken`, has no `total`/`startAt`, needs a **bounded** JQL (a bare `ORDER BY` returns `400`) and returns only `id` unless `fields` is set — see `search-jql.md`.
  - **Confluence v2** — cursor style: `limit` + `cursor` in the query; responses carry `{results, _links.next}` (and a `Link` header). Follow `_links.next`/the cursor; do **not** compute offsets.
- **Jira identifies users by `accountId`** (GDPR — not username or email). Resolve a person with `GET /rest/api/3/user/search?query=<name|email>` and keep the `accountId`.
- **Errors.** `400` validation (malformed body / missing field / plain-string-where-ADF-expected / unbounded JQL), `401` auth (bad, expired or revoked token; scoped token on the wrong base), `403` permission (lacks project/space rights, admin, or a token scope), `404` not found or wrong base path, `409` version conflict or, once rolled out, the approval-space publish rule (Confluence), `429` rate limited (honor the `Retry-After` header; API-token traffic is under burst limits only).
- **Boards & sprints are a separate API.** Scrum/Kanban **boards, sprints, and backlog** live in the Jira Software Agile REST API at `${JIRA_ROOT}/rest/agile/1.0/…` — **not** in the bundled platform spec. The platform spec (`/rest/api/3`) covers issues, projects, workflows, fields, schemes, and Advanced Roadmaps "Plans".

## Next steps

- Everyday Jira work (create issue, JQL search, transition, comment, assign, report) → use the `jira-operations` skill.
- Everyday Confluence work (create/update pages, spaces, comments, labels) → use the `confluence-operations` skill.
- The full endpoint catalog of every resource → load the `api-reference` skill and open the relevant `references/jira/*.md` or `references/confluence/*.md` file (or grep the bundled `*-openapi-*.json` specs).
- When a call fails → use the `troubleshoot` skill.
