---
name: permissions
description: Set NocoDB table and field permissions — who may see a table, add or delete records, download data, or edit one field — as grants on top of base roles, over MCP (listPermissions, setPermission, dropPermission) or REST (/bases/{baseId}/permissions). Use when access must be narrower than the base role for one table or field. Members, teams and base roles are not covered here.
---

# Table and Field Permissions

A base role (owner, creator, editor, commenter, viewer) decides what a person can do everywhere in a base. A **permission grant** narrows one table or one field: only tables and fields with an explicit grant appear in the list, everything else follows the base roles. Grants need Cloud-hosted **Business** and above or licensed self-hosted for `setPermission` / `dropPermission`; listing works on every plan, so a downgraded workspace can still see the grants in place. The caller needs the **Creator** or **Owner** role on the base (source: https://nocodb.com/docs/mcp/permissions, 2026-10-22; OpenAPI spec at tag 2026.10.2, tag `Permissions`).

Over MCP the tools are listed on `/mcp` (2026.10.1 and later); on `/mcp-discovery` or an older server reach them with `listTools category: "permissions"` → `callTool`. Community Edition has none of them (see **mcp-patterns**).

## The five permission keys

| `permission` | `entity` | What it controls |
|--------------|----------|------------------|
| `TABLE_VISIBILITY` | `table` | Who sees the table at all. Base owners only; needs a plan that includes it |
| `TABLE_RECORD_ADD` | `table` | Who may create records |
| `TABLE_RECORD_DELETE` | `table` | Who may delete records |
| `TABLE_DATA_DOWNLOAD` | `table` | Who may export CSV, Excel and JSON; with no grant every base member can |
| `RECORD_FIELD_EDIT` | `field` | Who may change the values of one field |

## One grant is one rule

| `granted_type` | Meaning | Extra keys |
|----------------|---------|------------|
| `role` | A minimum role | `granted_role`: `editor` or `creator` |
| `user` | Only the listed subjects | `subjects[]`: `{type: "user", id \| email}` or `{type: "team", id, hierarchy_scope?}`; `hierarchy_scope` is `self_only` or `self_and_descendants` (default) |
| `nobody` | No one | — |

`granted_role` is rejected unless `granted_type` is `role`, and `subjects` unless it is `user`. There is no owner-only role grant: to restrict to owners, use `granted_type: "user"` and name them. `enforce_for_automation` and `enforce_for_form` default to `true` — the grant also binds automations and form submissions; set `false` only when a workflow or a public form must keep writing.

## Workflow

```
1. getBaseSchema                      ← table and field ids
2. listPermissions  [tableId, entity] ← what is already granted
3. listBaseMembers                    ← the users and teams a grant can name (MCP)
4. setPermission                      ← one grant per call; replaces the grant for that key
5. listPermissions                    ← read it back
```

Show the user the table or field, the key and the rule before step 4. `setPermission` on an existing key **replaces** its grant.

MCP — editors and up may add records to a table:

```
setPermission
  entity: "table"
  entityId: "<tableId>"
  permission: "TABLE_RECORD_ADD"
  grantedType: "role"
  grantedRole: "editor"
```

Only two named people may edit a field (the tools use camelCase, REST uses snake_case):

```
setPermission
  entity: "field"
  entityId: "<fieldId>"
  permission: "RECORD_FIELD_EDIT"
  grantedType: "user"
  subjects: [ { type: "user", email: "ana@example.com" }, { type: "team", title: "Finance" } ]
```

REST:

```bash
# list (filters optional)
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/permissions?tableId=${TABLE_ID}"

# set
curl -sS -X PUT -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" \
  -d '{ "entity": "table", "entity_id": "<tableId>", "permission": "TABLE_DATA_DOWNLOAD", "granted_type": "nobody" }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/permissions"

# remove a grant by its id (from the list)
curl -sS -X DELETE -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/permissions/${PERMISSION_ID}"
```

A listed grant looks like `{id, entity, entity_id, permission, granted_type, granted_role, subjects, enforce_for_automation, enforce_for_form, created_by}`. `dropPermission` (MCP) takes `entity`, `entityId` and `permission` instead of the grant id. After a drop the table or field is back under plain base-role access — to open a table up to every role again, drop the grant rather than setting a lower role.

## Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| `403` on `setPermission` | Role below Creator, `TABLE_VISIBILITY` set by a non-owner, or the plan lacks table and field permissions | Ask an owner; check the plan — `listPermissions` still works |
| `400` on `setPermission` | `granted_role` or `subjects` does not match `granted_type`, or a required one is missing | One rule per grant: role + `granted_role`, or user + `subjects`, or `nobody` |
| Owner-only grant widened to editor | `granted_role` cannot express "owner" | Use `granted_type: "user"` with the owners as subjects |
| An automation still edits a locked field | `enforce_for_automation` was set to `false` | Leave it at the default `true` |

## What This Skill Does NOT Cover

- Base members, teams and base roles (`addBaseMembers`, `addBaseTeam` — Members & teams in the NocoDB UI, and the `/members` and `/teams` endpoints in **api-reference**).
- Row-level security policies (`createRlsPolicy` and related tools — Owner role and a plan with row-level security).
- API token scopes — see **api-reference** → API Tokens.

## See Also

- **api-reference** — `references/meta-api-endpoints.md` → Table and Field Permissions; `jq '.components.schemas.PermissionSet'` on the bundled meta spec
- **mcp-patterns** — the MCP contract and the `listTools` flow
