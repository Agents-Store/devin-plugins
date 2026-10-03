---
name: api-reference
description: "Reference-only skill (loaded on demand) that maps the NocoBase v2 REST API surface — base URL, authentication, action-style endpoint convention, and pointers into the bundled OpenAPI 3.0.3 specification. Loaded by the model when it needs an exact endpoint path or schema; not auto-triggered."
disable-model-invocation: true
---

# NocoBase v2 — REST API reference

This is a **reference-only** skill. It is not auto-triggered; load it manually when you need an exact endpoint or schema. The single source of truth is the bundled OpenAPI spec.

## Spec location

```
${CLAUDE_PLUGIN_ROOT}/references/openapi/nocobase.json
```

- OpenAPI version: `3.0.3`
- API version: `2.1.0-beta.29` — a **snapshot** from a 2.1.0-beta.29 stand; the stable line is 2.2.x (2.2.20 on 2026-10-02) and publishes more groups (AI employees, LLM services, knowledge bases, …) that this snapshot lacks. Refresh from a ≥ 2.2.x stand is pending.
- Endpoints: 272 operations on 272 paths, 56 distinct tags (the 19 in the top-level `tags[]` are only the curated headline groups) plus 4 untagged operations (`systemSettings`, `backupSettings`)
- Server: `/api/` (relative to NocoBase host)

**The snapshot may not contain a group your instance serves.** For the live schema of the connected app, `GET ${NB_URL}/api/swagger:getUrls` lists its schema URLs (needs the API documentation plugin), or ask the CLI — `nb api --help` and `nb api <group> --help` list what the connected app exposes, because `nb` builds those commands from the app's own OpenAPI schema (`nb env update` refreshes them). Treat this file as a map, the live app as the truth.

## Base URL and auth

```
${NB_URL}/api/{resource}:{action}
Authorization: Bearer <token>
```

Get the token via `POST ${NB_URL}/api/auth:signIn` with `NB_USER` + `NB_PASSWORD` (primary), or use a long-lived `NB_TOKEN` from the API Keys plugin — see the `auth` skill.

## Endpoint convention

NocoBase exposes a **resource-action** style API rather than CRUD over verbs:

| Convention | Example | HTTP method |
|---|---|---|
| Read collection of items | `GET /api/{name}:list` | GET |
| Read one item | `GET /api/{name}:get?filterByTk=…` | GET |
| Create | `POST /api/{name}:create` | POST |
| Update | `POST /api/{name}:update?filterByTk=…` | POST |
| Delete | `POST /api/{name}:destroy?filterByTk=…` | POST |
| Move (reorder) | `POST /api/{name}:move` | POST |
| Custom action | `POST /api/{name}:<action>` | POST |

Both reads and writes accept a **`filter`** query/body parameter using the JSON filter language (`$eq`, `$in`, `$and`, `$or`, etc.). The `nocobase-data-modeling` skill has the full grammar.

### Association resources

For relations, the path nests the parent record:

```
GET  /api/{collection}/{recordKey}/{associationField}:list
POST /api/{collection}/{recordKey}/{associationField}:add
POST /api/{collection}/{recordKey}/{associationField}:set
POST /api/{collection}/{recordKey}/{associationField}:remove
POST /api/{collection}/{recordKey}/{associationField}:toggle  // m2m only
```

`recordKey` is normally the primary key (often `id`).

## Tag groups (where to look first)

Top groups by operation count — see `references/tags-overview.md` for the full listing:

| Tag | Ops | What it covers |
|---|---:|---|
| `flowSurfaces` | 46 | UI authoring: pages, blocks, popups, tabs, layout, linkage, blueprints |
| `$collection*` (data + 4 relation types) | 41 | CRUD on user-defined collections + relation actions |
| `collections`, `collections.fields`, `collectionCategories`, `fields`, `dbViews` | 25 | Data modelling surface (schema admin) |
| `pm` | 9 | Plugin manager (`/api/pm:enable`, `:disable`, `:list`, …) |
| `backups`, `migration`, `migrationLogs`, `migrationRules`, `migrationRule` | 21 | Server-side backups (`/backup:*`) and migration files, rules and logs (`/migration:*`, `/migrationRules:*`, `/migrationLog:*`) |
| `roles*`, `dataSources.roles*` | 28 | ACL — roles, role resources, scopes, user-role membership |
| `workflows`, `flow_nodes`, `executions`, `jobs`, `userWorkflowTasks`, `workflows.nodes` | 24 | Workflow CRUD, manual run (`/workflows:execute`) + execution monitoring |
| `users`, `users.roles`, `apiKeys`, `Auth`, `Authenticator`, `OIDC`, `SAML`, `Basic auth`, `verifications*` | ~30 | Identity, auth, MFA |
| `app` | 5 | Lifecycle — `getInfo`, `getLang`, `getPlugins`, `restart`, `clearCache` |
| `uiSchemas` | 9 | Lower-level UI schema CRUD (used by ui-builder) |
| `storages`, `themeConfig`, `localization*`, `map-configuration`, … | many | Settings & utilities |

## How to look up an endpoint

When you need an endpoint path, schema, or parameter list, do not guess — query the OpenAPI file directly.

```bash
SPEC="${CLAUDE_PLUGIN_ROOT}/references/openapi/nocobase.json"

# 1. List every path containing a keyword
jq -r '.paths | keys[] | select(test("workflow"; "i"))' "$SPEC"

# 2. Show methods + summary for a path
jq '.paths["/workflows:create"]' "$SPEC"

# 3. List all operations in a tag
jq -r '.paths | to_entries[]
       | .key as $p
       | .value | to_entries[]
       | select(.value.tags[0]? == "flowSurfaces")
       | "\(.key | ascii_upcase) \($p)"' "$SPEC"

# 4. Resolve a schema reference
jq '.components.schemas.WorkflowDto' "$SPEC"
```

Always feed the path you derived back to the user as `${NB_URL}/api{path}` — the OpenAPI server is `/api/`, so paths in the spec are relative to that.

## Distilled summaries

- `references/tags-overview.md` — every tag, one line each, with the matching skill in this plugin.
- `references/common-endpoints.md` — copy-paste curl recipes for the highest-traffic operations, plus a section on calling the API from n8n or another service.

## Notes and gotchas

- **`POST` for non-creates is normal.** Most write actions (`:update`, `:destroy`, `:move`, `:set`, `:remove`) use `POST` even when conceptually they're updates or deletes — this is intentional, do not retry as `PUT`/`DELETE`.
- **`filterByTk` vs `filter`.** `filterByTk` selects exactly one record by primary key; `filter` is the general-purpose JSON filter language. Read endpoints accept both.
- **Pagination.** `page` (1-indexed) and `pageSize` (default 20) on any `:list`. The response wraps results in `{ data, meta: { count, page, pageSize, totalPage } }`.
- **`appends`.** Pass `appends=relName` (repeat for each relation) on `:list` / `:get` to eager-load relations; otherwise relations are not embedded.
- **Errors.** 4xx/5xx return `{ errors: [{ message, code? }] }`. 401 is auth (see `auth` skill); 403 is ACL (see `nocobase-acl-manage`).
- **Manual workflow run.** `POST /api/workflows:execute?filterByTk=<integer workflow id>` (optional `autoRevision=1`). The **whole JSON body is the trigger context** — no `values` or other envelope around it; its shape depends on the trigger (a collection-event trigger reads `data` — the record — a schedule trigger reads `date`). Response: `{ execution: { id, status }, newVersionId? }` — the object may arrive under a `data` key, so read both. The key of a workflow is not accepted as `filterByTk`. A different action, `:trigger`, exists only for custom-action triggers — see `nocobase-workflow-manage`.
- **OpenAPI completeness.** The spec covers core + bundled plugins shipping with NocoBase v2.1.0-beta.29. Newer core releases and custom plugins add routes that are not in this file — use the live schema (above), and load `nocobase-plugin-development` to learn how plugins register routes.
