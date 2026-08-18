---
name: troubleshoot
description: This skill should be used when a Jira or Confluence REST API call fails or behaves unexpectedly — "Jira/Confluence returns 401 / 403 / 404 / 400 / 409 / 429", "Atlassian API token not working", "ADF error / body must be ADF", "page won't update / version conflict", "can't find the page/issue", "wrong base URL", "CQL not working in v2", "boards/sprints endpoint not found", or any Atlassian error response. Maps symptoms to causes and fixes.
---

# Atlassian Troubleshooting

Match the symptom, apply the fix. Most failures come from a wrong base path, Basic auth set up incorrectly, a plain string where ADF/storage is required, a stale Confluence version, or a name used where an id is required.

## 401 Unauthorized

**Cause:** bad Basic auth — wrong email, wrong/revoked token, or password used instead of an API token.

- The credential is `email:API_TOKEN`, **not** `email:account_password`. Mint a token at `https://id.atlassian.com/manage-profile/security/api-tokens`.
- Confirm both vars are set: `[ -n "$ATLASSIAN_EMAIL" ] && [ -n "$ATLASSIAN_API_TOKEN" ] && echo set || echo MISSING`.
- Re-run the `setup` check: `GET /rest/api/3/myself`. A `200` there means auth is fine and the problem is elsewhere.
- A revoked or expired token always `401`s — reissue it.

## 403 Forbidden (permission)

**Cause:** authenticated, but the token user lacks the rights for this action/object.

- **Jira:** run `GET /rest/api/3/mypermissions?projectKey=PROJ&permissions=CREATE_ISSUES,EDIT_ISSUES` — it shows exactly which permission is missing. Scheme/admin endpoints (workflows, fields, permission schemes) need Jira admin.
- **Confluence:** check `GET /wiki/api/v2/pages/{id}/operations` (or `/spaces/{id}/operations`) for what the user may do; space-restricted content needs space permission.
- Premium/Enterprise features (Advanced Roadmaps Plans, classification levels, data policies) return `403`/`404` when the plan doesn't include them.
- A `403` is a real boundary — report it, don't try to route around it.

## 404 / "Not found"

**Cause:** wrong base path, or a name/wrong id used where a real id is required, or the object is archived/deleted.

- **Base paths:** Jira is `${ATLASSIAN_SITE_URL%/}/rest/api/3`; Confluence v2 is `${ATLASSIAN_SITE_URL%/}/wiki/api/v2`. A Confluence `404` on every call usually means the `/wiki` prefix is missing.
- `ATLASSIAN_SITE_URL` must be the site root (`https://your-domain.atlassian.net`) with **no** trailing `/rest` or `/wiki`.
- **Confluence `spaceId` is numeric**, not the space key — resolve via `GET /wiki/api/v2/spaces?keys=PROJ`.
- **Jira** addresses issues by `issueIdOrKey` (`PROJ-123`) — resolve a summary to a key with JQL first.

## 400 Validation error

**Cause (Jira):** malformed body, missing required field, or a plain string where ADF is expected.

- **ADF, not markdown** — `description` and comment `body` must be an ADF doc: `{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"…"}]}]}`. A plain string returns `400`.
- Required field missing — run `GET /rest/api/3/issue/createmeta/PROJ/issuetypes/{issueTypeId}` to see what's required for that type.
- Setting a field the screen doesn't include is ignored or rejected — check `GET /issue/{key}/editmeta`.
- Send `-H "Content-Type: application/json"` and valid JSON on every write.

**Cause (Confluence):** body missing its `representation`, or `spaceId` sent as a key.

- Body must be `{"representation":"storage"|"atlas_doc_format","value":"…"}`.

## 409 Conflict (Confluence version)

**Cause:** the `version.number` you sent isn't `current + 1` — someone (or your own earlier call) changed the page.

- Re-read the page: `GET /wiki/api/v2/pages/{id}` → take `.version.number` → `PUT` with that number `+ 1`. Always read-then-write.

## 429 Too Many Requests

**Cause:** rate limited.

- Honor the `Retry-After` response header (seconds). Inspect with `curl -s -D - …`.
- Pace bulk fan-outs (mass create, bulk edit, broadcasts); add small sleeps between requests.

## "CQL / full-text search doesn't work in v2"

**Cause:** Confluence v2 list endpoints filter by `space-id`/`title`/`status` only — they are not full-text search.

- Use the **v1** search endpoint: `GET ${ATLASSIAN_SITE_URL%/}/wiki/rest/api/search?cql=space=PROJ%20AND%20text~%22term%22`.

## "Label add / attachment upload returns 404/405 in v2"

**Cause:** those writes aren't in the Confluence v2 spec.

- Labels: `POST ${ATLASSIAN_SITE_URL%/}/wiki/rest/api/content/{id}/label` (v1).
- Attachment upload: `POST ${ATLASSIAN_SITE_URL%/}/wiki/rest/api/content/{id}/child/attachment` (v1, multipart, header `X-Atlassian-Token: nocheck`).

## "Boards / sprints / backlog endpoint not found"

**Cause:** those aren't in the Jira platform API.

- They live in the **Jira Software Agile REST API**: `${ATLASSIAN_SITE_URL%/}/rest/agile/1.0/board`, `/sprint`, `/backlog`. The bundled `jira-openapi-v3.json` does not cover them.

## Multipart upload rejected (Jira attachments)

**Cause:** missing the XSRF-bypass header or sending JSON.

- Use `-F "file=@path"` (not `-d`) **and** `-H "X-Atlassian-Token: no-check"`. Do not send `Content-Type: application/json` for uploads.
