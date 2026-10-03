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

1. **Snapshot the schema.** `mcp__plugin_nocodb-dev_nocodb__getTableSchema` (or `getBaseSchema`) — confirm the field / view / hook is actually present. `listBaseAudits` / `listRecordAudits` (category `audits`, Cloud/licensed) show who changed what and when.
2. **Check token scope.** A 403 from a Meta endpoint usually means the token lacks edit rights on the base, not a bug.
3. **Verify NocoDB version.** Instance versions are calendar-based now (`2026.MM.N`; older builds were `0.30x.y`). Run `curl -sS "${NOCODB_URL}/api/v1/health"` and check `version`. MCP schema tools need a Cloud / licensed instance recent enough to offer them (`listTools`).

## Auth & Permissions

| Code | Symptom | Fix |
|------|---------|-----|
| 401 | Token invalid | Regenerate at NocoDB → Team & Settings → API Tokens |
| 403 on POST `.../fields` | Token has read-only role on this base | Switch to a token with editor/creator role |
| 403 on PATCH `/tables/{id}` | Token can edit data but not schema | Use a higher-privilege token |
| Token works in nocodb-ops but not nocodb-dev | Wrong env var | Confirm `NOCODB_TOKEN` (REST) is set, not just `NOCODB_MCP_TOKEN` |

## Field-Type Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 on field create | Missing required option for that type, or a key outside `options` | Check `field-types.md` for the required keys; type-specific keys live inside `options` |
| 422 "type X requires field Y" | Lookup / Rollup / Barcode / QR missing a referenced field ID (`related_field_id`, `related_table_lookup_field_id`, `related_table_rollup_field_id`, `barcode_value_field_id`, `qrcode_value_field_id`) | Provide the referenced field ID inside `options` |
| 400 "related_field_id not found" | Lookup created before the link field exists | Create the `LinkToAnotherRecord` (or `Links`) field first |
| Type change rejected (422) | Incompatible existing values | Audit and clean values; or recreate the field with the desired type and migrate data |
| `MultiSelect → SingleSelect` rejected | At least one record has multiple values | Reduce records to one value each before changing |
| `LongText → Number` rejected | Non-numeric existing values | Set those values to null or numeric first |
| New SingleSelect option not visible | UI cache | Hard-refresh; the API call succeeded |

## Relation Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Inverse link missing on the other table | Link created but inverse not generated | Re-run with `type: "LinkToAnotherRecord"` and an explicit `options.relation_type` / `related_table_id` pair |
| Lookup column shows nothing | Underlying link has no records linked | Verify with `GET /api/v3/data/.../links/{linkFieldId}/{recordId}` |
| Rollup returns 0 / null | `rollup_function` mismatched type (e.g. `sum` on text) | Switch to `count` or `countDistinct`, or roll up a numeric field |
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
| Gallery cards bare | No cover image set or attachments missing | Set `options.cover_field_id`; upload attachments |
| Form submit error 422 | Required field missing in payload | NocoDB form validation lives client-side; for API submits, check field-level constraints |
| View create rejected | The view APIs are not in this plan (cloud Enterprise or licensed self-hosted) | Confirm the plan; on Community Edition create views in the UI |
| View create rejected with an unknown-key error | Option keys from older tooling (or another view type's key) | Use the v3 keys in **view-management** (`stack_by`, `cover_field_id`, `date_ranges`, `geo_data_field_id`, …) |

## Hook (Webhook) Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hook never fires | `active: false`, wrong `event`/`operation`, or `trigger_fields` excludes the changed field | Toggle active; verify event/operation; check `trigger_fields` |
| Hook fires but destination 401 | Auth header missing or wrong | Add `Authorization` to `payload.headers` |
| `{{record.X}}` rendered literally | Wrong column title | Match exact case-sensitive column title |
| Hook fires twice on bulk-update | Both `insert` and `update` configured on the same hook | Remove the unused operation from the `operation` array |
| Email hook never sends | NocoDB SMTP not configured | Configure SMTP plugin in NocoDB admin |

## Schema Cache & Sync

| Symptom | Cause | Fix |
|---------|-------|-----|
| `getTableSchema` returns stale shape after a write | Browser-side or MCP cache | Wait ~30s; hard-refresh; re-call `getBaseInfo` first |
| A deleted table, field or view needs to come back | Deleted on a NocoDB-managed source (Cloud / licensed) | `listTrash` → `restoreFromTrash(trashId)` before `cleanup_due_at`; not possible on an external source |
| Two clients see different schemas | Active replication lag (self-hosted) | Confirm replica is up-to-date; pin reads to primary |
| MCP sees a deleted field | MCP server cache | Restart MCP, or wait for TTL expiry |
| Field reorder not visible | Per-view field order overrides table order | `PATCH` the view with the complete ordered `fields` list |

## Version Compatibility

NocoDB versions are calendar-based (`2026.MM.N`) since 2026; the table below uses the older `0.30x` numbering for features that predate it.

| Feature | Notes |
|---------|-------|
| `Links` field type, Map view, HookV3, nested filter groups (3 levels), `display_field_id`, `Geometry` | Present since v0.200 |
| MCP schema / view / hook / workflow tools (`listTools` → `callTool`) | 2026.09.0 and later, Cloud and licensed self-hosted only |
| Gantt, Timeline and List views, `POST`/`DELETE …/fields/{fieldId}/options`, Docs API | Current Meta API v3 spec (bundled) |

Older instances may need the legacy hook v2 schema, and may lack the newer view types or the select-options endpoints — read the `version` from `/api/v1/health` and compare with the bundled spec before assuming an endpoint exists.

## Diagnostic Checklist

When reporting a schema bug:

1. NocoDB instance URL and version (`/api/v1/health`)
2. Edition and plan tier (Community Edition / licensed self-hosted / Cloud plan)
3. The exact MCP tool call or `curl` request (with token redacted)
4. The full HTTP response body (status + JSON error)
5. Output of `mcp__plugin_nocodb-dev_nocodb__getTableSchema` for the affected table
6. Whether the same operation works in the NocoDB web UI
7. Whether the issue is consistent or intermittent
