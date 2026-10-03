---
name: troubleshoot
description: This skill should be used when a Jira or Confluence REST API call fails or behaves unexpectedly — "Jira/Confluence returns 401 / 403 / 404 / 400 / 409 / 429", "Atlassian API token not working / expired", "scoped API token 401", "JQL search returns 400 unbounded", "ADF error / body must be ADF", "page won't update / version conflict / approval space", "can't find the page/issue", "wrong base URL", "CQL not working in v2", "boards/sprints endpoint not found", or any Atlassian error response. Maps symptoms to causes and fixes.
---

# Atlassian Troubleshooting

Match the symptom, apply the fix. Most failures come from a wrong base path (or a scoped token on the wrong host), Basic auth set up incorrectly, an expired token, an unbounded JQL, a plain string where ADF/storage is required, a stale Confluence version, or a name used where an id is required.

## 401 Unauthorized

**Cause:** bad Basic auth — wrong email, wrong/revoked/**expired** token, password used instead of an API token, or a **scoped token sent to the site URL**.

- The credential is `email:API_TOKEN`, **not** `email:account_password`. Mint a token at `https://id.atlassian.com/manage-profile/security/api-tokens`.
- **Tokens expire** (1–365 days, 1 year by default). Tokens created before 2024-12-15 were given a one-year life and lapsed between 2026-03-14 and 2026-05-12, so a script that worked for years may suddenly `401` — reissue the token.
- **Scoped token?** (created with *Create API token with scopes*) It only works through the gateway: `https://api.atlassian.com/ex/jira/{cloudId}/…` and `https://api.atlassian.com/ex/confluence/{cloudId}/…`. On `https://your-domain.atlassian.net` it returns `401`/`403`. Set `ATLASSIAN_CLOUD_ID` (`curl -s "${ATLASSIAN_SITE_URL%/}/_edge/tenant_info" | jq -r .cloudId`) and use the bases from the `setup` skill.
- Confirm the vars are set without printing them: `[ -n "$ATLASSIAN_EMAIL" ] && [ -n "$ATLASSIAN_API_TOKEN" ] && echo set || echo MISSING`.
- Re-run the `setup` check: `GET ${JIRA}/myself`. A `200` there means auth is fine and the problem is elsewhere.

## 403 Forbidden (permission)

**Cause:** authenticated, but the token user lacks the rights for this action/object.

- **Jira:** run `GET /rest/api/3/mypermissions?projectKey=PROJ&permissions=CREATE_ISSUES,EDIT_ISSUES` — it shows exactly which permission is missing. Scheme/admin endpoints (workflows, fields, permission schemes) need Jira admin.
- **Confluence:** check `GET /wiki/api/v2/pages/{id}/operations` (or `/spaces/{id}/operations`) for what the user may do; space-restricted content needs space permission.
- Premium/Enterprise features (Advanced Roadmaps Plans, classification levels, data policies) return `403`/`404` when the plan doesn't include them.
- **Scoped token missing a scope** → `403` even for an allowed user. Compare the endpoint with the token's scopes (Jira: `read:jira-work`, `write:jira-work`, `read:jira-user`, …; Confluence: `read:confluence-content.all`, `write:confluence-content`, `read:confluence-space.summary`, …) and issue a token with the extra scope.
- A `403` is a real boundary — report it, don't try to route around it.

## 404 / "Not found"

**Cause:** wrong base path, or a name/wrong id used where a real id is required, or the object is archived/deleted.

- **Base paths:** Jira is `${ATLASSIAN_SITE_URL%/}/rest/api/3`; Confluence v2 is `${ATLASSIAN_SITE_URL%/}/wiki/api/v2`. A Confluence `404` on every call usually means the `/wiki` prefix is missing. With a scoped token the bases are `https://api.atlassian.com/ex/jira/{cloudId}/rest/api/3` and `https://api.atlassian.com/ex/confluence/{cloudId}/wiki/api/v2`.
- `ATLASSIAN_SITE_URL` must be the site root (`https://your-domain.atlassian.net`) with **no** trailing `/rest` or `/wiki`.
- **Confluence `spaceId` is numeric**, not the space key — resolve via `GET /wiki/api/v2/spaces?keys=PROJ`.
- **Jira** addresses issues by `issueIdOrKey` (`PROJ-123`) — resolve a summary to a key with JQL first.

## 400 Validation error

**Cause (Jira):** malformed body, missing required field, or a plain string where ADF is expected.

- **ADF, not markdown** — `description` and comment `body` must be an ADF doc: `{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"…"}]}]}`. A plain string returns `400`.
- Required field missing — run `GET /rest/api/3/issue/createmeta/PROJ/issuetypes/{issueTypeId}` to see what's required for that type.
- Setting a field the screen doesn't include is ignored or rejected — check `GET /issue/{key}/editmeta`.
- Send `-H "Content-Type: application/json"` and valid JSON on every write.

**Cause (Jira search):** `POST/GET /search/jql` with an **unbounded JQL** — one that is only an `ORDER BY` (for example `order by created DESC`) with no restriction. Add a search restriction: `created >= -30d ORDER BY created DESC`, `project = PROJ ORDER BY created DESC`, or `assignee = currentUser() ORDER BY key`. Also: the `ORDER BY` clause may name at most 7 fields, and `POST /issue/bulkfetch` rejects more than 100 issues (1000 only for an explicit `fields` list without multi-value fields) — see `search-jql.md` / `issues.md`.

**Cause (Confluence):** body missing its `representation`, or `spaceId` sent as a key.

- Body must be `{"representation":"storage"|"atlas_doc_format","value":"…"}`.

## 409 Conflict (Confluence)

**Cause 1 — stale version:** the `version.number` you sent isn't `current + 1` — someone (or your own earlier call) changed the page.

- Re-read the page: `GET ${CONF}/pages/{id}` → take `.version.number` → `PUT` with that number `+ 1`. Always read-then-write.

**Cause 2 — approval space (CHANGE-3432, announced 2026-09-28, rollout pending):** the space requires approval before publishing. Once the change is enabled, a direct `PUT /pages/{id}`, `PUT /pages/{id}/title` (or v1 `PUT /wiki/rest/api/content/{id}`) on a published page returns `409` **even with the correct `version.number`**.

- A version bump will not fix it and retries will not help. Atlassian announced this on 2026-09-28 and will publish the rollout date; it applies only to regular pages in approval-enabled spaces.
- Atlassian's guidance: save the change as a draft, complete the approval, publish the approved draft. **No REST draft→approval→publish flow is documented yet** — use the Confluence UI or ask a Confluence admin; ask a space admin whether approvals are on if a `409` survives a correct version.

## 429 Too Many Requests

**Cause:** rate limited.

- Honor the `Retry-After` response header (seconds). Inspect with `curl -s -D - …`; also read `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` and `RateLimit-Reason` (for example `jira-burst-based`).
- **API-token traffic is only under per-endpoint burst limits.** The points-based hourly quotas enforced since 2026-03-02 apply to Forge, Connect and OAuth 2.0 (3LO) apps, not to API tokens — so a token script that is rate limited needs slower pacing, not a quota increase.
- Pace bulk fan-outs (mass create, bulk edit, broadcasts); add small sleeps between requests, and prefer `POST /issue/bulkfetch` over one `GET /issue/{key}` per issue.

## "CQL / full-text search doesn't work in v2"

**Cause:** Confluence v2 list endpoints filter by `space-id`/`title`/`status` only — they are not full-text search.

- Use the **v1** search endpoint: `GET ${CONF_ROOT}/wiki/rest/api/search?cql=space=PROJ%20AND%20text~%22term%22`.

## "Label add / attachment upload returns 404/405 in v2"

**Cause:** those writes aren't in the Confluence v2 spec.

- Labels: `POST ${CONF_ROOT}/wiki/rest/api/content/{id}/label` (v1).
- Attachment upload: `POST ${CONF_ROOT}/wiki/rest/api/content/{id}/child/attachment` (v1, multipart, header `X-Atlassian-Token: nocheck`).

## "Boards / sprints / backlog endpoint not found"

**Cause:** those aren't in the Jira platform API.

- They live in the **Jira Software Agile REST API**: `${JIRA_ROOT}/rest/agile/1.0/board`, `/sprint`, `/backlog`. The bundled `jira-openapi-v3.json` does not cover them.

## Multipart upload rejected (Jira attachments)

**Cause:** missing the XSRF-bypass header or sending JSON.

- Use `-F "file=@path"` (not `-d`) **and** `-H "X-Atlassian-Token: no-check"`. Do not send `Content-Type: application/json` for uploads.
