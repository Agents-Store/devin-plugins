---
name: troubleshoot
description: |
  Diagnose schema-side NocoDB errors — read-only fields, type-change rejections, broken Lookups, formula errors, view config validation, version mismatches. Use when:
  - "field type change rejected"
  - "Lookup not working"
  - "formula returns ERR"
  - "cannot delete table"
  - "Kanban not grouping"
  - "schema cache stale"
  - "NocoDB version too old"
---

# NocoDB Schema Troubleshooting

Diagnostics for the dev surface — schema modifications, relations, formulas, views, hooks. For data-side issues see `nocodb-ops/skills/troubleshoot`.

## Quick Diagnostics

1. **Snapshot the schema.** `mcp__nocodb__getTableSchema` — confirm the field / view / hook is actually present.
2. **Check token scope.** A 403 from a Meta endpoint usually means the token lacks edit rights on the base, not a bug.
3. **Verify NocoDB version.** Some endpoints (`Links` field, Map view, HookV3) are v0.200+. Run `curl -sS "$NOCODB_URL/api/v1/health"` and check `version`.

## Auth & Permissions

| Code | Symptom | Fix |
|------|---------|-----|
| 401 | Token invalid | Regenerate at NocoDB → Account Settings → API Tokens |
| 403 on POST `/columns` | Token has read-only role on this base | Switch to a token with editor/creator role |
| 403 on PATCH `/tables/{id}` | Token can edit data but not schema | Use a higher-privilege token |
| Token works in nocodb-ops but not nocodb-dev | Wrong env var | Confirm `NOCODB_API_TOKEN` (CLI/API) is set, not just `NOCODB_MCP_TOKEN` |

## Field-Type Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 on field create | Missing required option for that type | Check `field-types.md` for the required keys |
| 422 "type X requires field Y" | Lookup / Rollup / Barcode / QR missing `fk_*_column_id` | Provide the referenced column ID |
| 400 "fk_relation_column_id not found" | Lookup created before the link field exists | Create the `Links` / `LinkToAnotherRecord` field first |
| Type change rejected (422) | Incompatible existing values | Audit and clean values; or recreate the field with the desired type and migrate data |
| `MultiSelect → SingleSelect` rejected | At least one record has multiple values | Reduce records to one value each before changing |
| `LongText → Number` rejected | Non-numeric existing values | Set those values to null or numeric first |
| New SingleSelect option not visible | UI cache | Hard-refresh; the API call succeeded |

## Relation Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Inverse link missing on the other table | `Links` create succeeded but inverse not generated | Some older NocoDB versions require explicit `LinkToAnotherRecord` (classic) — re-run with the classic field |
| Lookup column shows nothing | Underlying link has no records linked | Verify with `GET /api/v3/data/.../links/{linkFieldId}/{recordId}` |
| Rollup returns 0 / null | `rollup_function` mismatched type (e.g. `sum` on text) | Switch to `count` or `countNotEmpty`, or rollup a numeric column |
| Cannot delete table | Another table has a link pointing here | Delete that link field first |
| Cycle detected | Two links forming a self-loop with the same column | Re-create one side; NocoDB v3 normally allows cycles on different columns |
| Display field of linked table changed | Display field on the parent was deleted | Set a new `display_field_id` on the parent table |

## Formula Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ERR` for some rows | Null operand or type mismatch | Wrap with `IF(ISBLANK({Field}), default, expr)` |
| `ERR` for all rows | Syntax error | Test the formula on one row in NocoDB UI; common mistakes: smart quotes, missing braces, unsupported function |
| Formula references a renamed field | NocoDB stores by ID, but visible string uses old name | Re-edit the Formula; the display refreshes |
| Date arithmetic returns 0 | Time component truncated | Use `DATETIME_DIFF(NOW(), {Field}, "days")`, not naive subtraction |
| String concat wrong | NocoDB uses `&` or `CONCAT()` not `+` for strings | Use `CONCAT({A}, " ", {B})` |

## View Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Kanban shows everything in "Uncategorized" | Records have null group value | Backfill the SingleSelect column |
| Calendar shows nothing | Date field null, or filter excludes records | Inspect view filters; check date population |
| Map renders empty | Geometry field empty | Populate `Geometry` values (POINT format) |
| Gallery cards bare | No cover image set or attachments missing | Set `fk_cover_image_col_id`; upload attachments |
| Form submit error 422 | Required field missing in payload | NocoDB form validation lives client-side; for API submits, check field-level constraints |
| View create rejected | View management requires Enterprise on this instance | Confirm plan; downgrade to Free-plan operations |

## Hook (Webhook) Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hook never fires | `active: false`, wrong event, or condition false | Toggle active; verify event/operation; relax condition |
| Hook fires but destination 401 | Auth header missing or wrong | Add `Authorization` to `payload.headers` |
| `{{record.X}}` rendered literally | Wrong column title | Match exact case-sensitive column title |
| Hook fires twice on bulk-update | Both `insert` and `update` configured on the same hook | Remove the unused operation from the `operation` array |
| Email hook never sends | NocoDB SMTP not configured | Configure SMTP plugin in NocoDB admin |

## Schema Cache & Sync

| Symptom | Cause | Fix |
|---------|-------|-----|
| `getTableSchema` returns stale shape after a write | Browser-side or MCP cache | Wait ~30s; hard-refresh; re-call `getBaseInfo` first |
| Two clients see different schemas | Active replication lag (self-hosted) | Confirm replica is up-to-date; pin reads to primary |
| MCP sees a deleted field | MCP server cache | Restart MCP, or wait for TTL expiry |
| Field reorder not visible | Per-view column order overrides table order | Use `view:column:update` to reorder per view |

## Version Compatibility

| Feature | Min version |
|---------|-------------|
| `Links` field type (modern) | v0.200 |
| Map view | v0.200 |
| HookV3 | v0.200 |
| Per-view filter groups level 3 | v0.200 |
| `display_field_id` on TableUpdate | v0.200 |
| `Geometry` field type | v0.200 |

Older instances may need `LinkToAnotherRecord` instead of `Links`, and the legacy hook v2 schema.

## Diagnostic Checklist

When reporting a schema bug:

1. NocoDB instance URL and version (`/api/v1/health`)
2. Plan tier (Free / Self-hosted Enterprise / Cloud Enterprise)
3. The exact CLI or API call (with token redacted)
4. The full HTTP response body (status + JSON error)
5. Output of `mcp__nocodb__getTableSchema` for the affected table
6. Whether the same operation works in the NocoDB web UI
7. Whether the issue is consistent or intermittent
