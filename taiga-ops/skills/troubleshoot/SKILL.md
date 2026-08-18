---
name: troubleshoot
description: This skill should be used when a Taiga REST API call fails or behaves unexpectedly — "Taiga returns 401 / 403", "version conflict", "Taiga login fails", "can't find the object", "pagination missing results", "PATCH rejected", or any Taiga error response. Maps symptoms to causes and fixes.
---

# Taiga Troubleshooting

Match the symptom, apply the fix. Most Taiga API failures come from a missing `version`, an expired token, or using a slug where an ID is expected.

## 401 Unauthorized

**Cause:** missing, malformed, or expired `TAIGA_AUTH_TOKEN`.

- Confirm the header is exactly `Authorization: Bearer ${TAIGA_AUTH_TOKEN}` (Bearer, not `Token`/`JWT`). Application tokens instead use `Authorization: Application <token>`.
- If the token was valid earlier in the session, it expired — refresh it rather than re-logging in:
  ```bash
  export TAIGA_AUTH_TOKEN=$(curl -s -X POST "${TAIGA_API_URL%/}/api/v1/auth/refresh" \
    -H "Content-Type: application/json" -d "{\"refresh\":\"${TAIGA_REFRESH}\"}" | jq -r '.auth_token')
  ```
- If refresh also fails, re-run the `setup` login.

## Login itself fails (400/401 on `/auth`)

- The `type` field is **required**. The body must be `{"type":"normal","username":...,"password":...}`. Omitting `type` is the most common login error.
- `username` accepts either the username or the email — try the other if one fails.
- Verify `TAIGA_API_URL` points at the instance root (no `/api/v1` suffix, no trailing slash). The skill builds `${TAIGA_API_URL%/}/api/v1/auth`.

## 400 with a "version" / "stale" / conflict message

**Cause:** optimistic locking. The `version` you sent is not the object's current version (it was edited since your `GET`, or you omitted `version`).

Fix — re-read and retry with the fresh version:
```bash
OBJ=$(curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" "${TAIGA_API_URL%/}/api/v1/userstories/1234")
VER=$(echo "$OBJ" | jq -r .version)
curl -s -X PATCH -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json" \
  -d "{\"subject\":\"Updated\",\"version\":${VER}}" "${TAIGA_API_URL%/}/api/v1/userstories/1234"
```
Every `PATCH`/`PUT` on items, statuses, attachments, and custom-attribute values needs the current `version`.

## 403 Forbidden

**Cause:** authenticated but the role lacks the permission, or the object is in a private project you can't access.

- Check the user's role permissions: `GET /roles/{id}` and `GET /permissions`. (→ `api-reference` `projects.md`)
- Admin-only operations (e.g. `GET /stats/system`, deleting others' content) require a superuser/owner account — the `TAIGA_ADMIN_*` credentials should map to one.

## 404 / "object not found"

**Cause:** usually a slug or reference number used where a numeric ID is required.

- Refs like `#42` and project slugs are **not** IDs. Resolve first:
  ```bash
  curl -s -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
    "${TAIGA_API_URL%/}/api/v1/resolver?project=my-slug&us=42" | jq .
  ```
- Or use the dedicated `by_ref` endpoints: `GET /userstories/by_ref?ref=42&project=<id>` (same for tasks, issues, epics).

## A list seems to be missing rows

**Cause:** pagination. List endpoints return one page by default.

- Inspect headers: `curl -s -D - ... | grep -i x-pagination`. `x-pagination-count` is the true total.
- Walk pages with `?page=2`, `?page=3`, … or fetch everything in one go with header `x-disable-pagination: True` (use carefully on large projects).

## Creating an item rejects a `status` / `type` / `priority` / `severity`

**Cause:** those IDs are per-project. An ID valid in one project is invalid in another.

- Discover valid values: `GET /<resource>/filters_data?project=<id>` or `GET /<resource>-statuses?project=<id>`. Pick the ID for that project.

## Tags don't apply

Tags are arrays of `[name, color]` pairs, e.g. `"tags": [["urgent","#ff0000"],["backend",null]]` — not bare strings. Project-level tag management uses `/projects/{id}/create_tag` etc. (→ `projects.md`).

## Optional convenience MCP

If you'd rather call tools than curl for the ~33 most common operations, the community `greddy7574/taiga-mcp-server` (npx) and `talhaorak/pytaiga-mcp` exist. They cover a subset only — for full coverage use the REST endpoints in `api-reference`. These are not dependencies of this plugin.
