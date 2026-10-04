---
name: n8n-api-reference
description: n8n REST API reference with all endpoints, authentication, and curl examples. Use when making direct API calls, writing scripts that interact with n8n API, or when MCP tools are unavailable. Reference-only skill.
disable-model-invocation: true
---

# n8n REST API Reference

## Overview

n8n Public API, OpenAPI 3.0. The bundled `references/n8n-api.json` is the **n8n 2.41.6 public API, bundled from the n8n repo at tag `n8n@2.41.6`**: **154 operations across 26 tags** (Audit, CommunityPackage, Credential, DataTable, Discover, Evaluation, Executions, Folders, Insights, LogStreaming, N8nPackage, NodeTypePolicy, Projects, Promotions, Role, RoleMappingRule, SecurityPolicy, SettingsLdap, SettingsOtel, SettingsSsoOidc, SettingsSsoSaml, SourceControl, Tags, User, Variables, Workflow). `info.version` reads `1.1.1`; n8n does not bump it.

The public API allows programmatic access to workflows, executions, credentials, tags, users, variables, projects, folders, data tables, source control, evaluations, roles and audit features, plus instance administration for enterprise setups.

Full OpenAPI spec available at: `references/n8n-api.json`.

> **Match the spec to your instance.** Routes are version-specific (the table notes say from which n8n version where it matters). For the exact surface of the instance you target, open its API playground (`/api/v1/docs`) or read `GET /api/v1/discover`, which lists what the calling key may do.

---

## Authentication

All API requests require an API key passed via the `X-N8N-API-KEY` header.

### Generating an API Key

1. Open your n8n instance
2. Go to **Settings** → **n8n API**
3. Click **Create an API key** and choose its scopes and expiry
4. Copy the generated key (it is shown once)

The key carries **scopes** (for example `workflow:read`, `workflow:update`, `workflow:activate`); a call outside the key's scopes answers `403`, and each operation below lists the scope it needs. Besides `X-N8N-API-KEY`, the spec allows `BearerAuth` (JWT) and `CookieAuth` — an API key is the right choice for scripts.

### Base URL

`N8N_API_URL` may hold the instance root or already end in `/api/v1` — `n8n-mcp` accepts both.
Derive the root once per shell, then build every path from `N8N_BASE`:

```bash
N8N_BASE="${N8N_API_URL%/}"; N8N_BASE="${N8N_BASE%/api/v1}"
```

Every endpoint below is `${N8N_BASE}/api/v1/...`.

### Header Format

```
X-N8N-API-KEY: <your-api-key>
```

### Quick Verification

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE/api/v1/workflows?limit=1"
```

If you get a 200 response with workflow data, authentication is working.

---

## Endpoint Reference by Tag

Every operation below comes from `references/n8n-api.json`. **Scope** is the API key scope the operation needs (`x-required-scope`); a key without it gets `403`. Paths are relative to `/api/v1`.

### Workflow (17 operations)

The spec also carries the deprecated `activate` and `deactivate` aliases of publish and unpublish; they are left out of the table. The deprecated version route is marked.

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/workflows` | Retrieve all workflows | `workflow:list` |
| `POST` | `/workflows` | Create a workflow | `workflow:create` |
| `GET` | `/workflows/{id}/{versionId}` | **Deprecated.** Get one version of a workflow. Use `/workflows/{workflowId}/versions/{workflowVersionId}` instead (deprecated since n8n 2.39). | `workflow:read` |
| `GET` | `/workflows/{workflowId}` | Retrieve a workflow | `workflow:read` |
| `PUT` | `/workflows/{workflowId}` | Update a workflow. A published workflow is re-published unless `publishIfActive=false`. | `workflow:update` |
| `DELETE` | `/workflows/{workflowId}` | Delete a workflow | `workflow:delete` |
| `POST` | `/workflows/{workflowId}/archive` | Archive (soft-delete) a workflow. Idempotent. | `workflow:delete` |
| `GET` | `/workflows/{workflowId}/history` | List the saved versions of a workflow. | `workflow:read` |
| `POST` | `/workflows/{workflowId}/publish` | Publish a workflow so it responds to triggers. Optional body `{versionId, name, description}`. | `workflow:activate` |
| `GET` | `/workflows/{workflowId}/tags` | Get workflow tags | `workflowTags:list` |
| `PUT` | `/workflows/{workflowId}/tags` | Update tags of a workflow | `workflowTags:update` |
| `PUT` | `/workflows/{workflowId}/transfer` | Transfer a workflow to another project | `workflow:move` |
| `POST` | `/workflows/{workflowId}/unarchive` | Restore an archived workflow. | `workflow:delete` |
| `POST` | `/workflows/{workflowId}/unpublish` | Unpublish a workflow. Stops trigger-based execution. | `workflow:deactivate` |
| `GET` | `/workflows/{workflowId}/versions/{workflowVersionId}` | Retrieve a workflow version | `workflow:read` |

**Query parameters for `GET /workflows`:**
- `limit` — number of results (default 100, max 250); `cursor` — pagination cursor from the previous response; `offset` — legacy offset
- `active` — filter by published status (`true`/`false`)
- `tags` — filter by tag name; `name` — filter by workflow name; `projectId` — filter by project
- `excludePinnedData` — leave pinned data out of the response (default `false`)

**Publish, unpublish, re-publish.** In n8n 2.x a workflow body is a *draft*; what runs in production is the *published version*. `POST /workflows/{id}/publish` (n8n 2.33+, scope `workflow:activate`) takes an optional `versionId` (without it the latest version is published) and answers **409** when an open workflow review blocks it (`reason`, `workflowReviewRequestId`) or the webhook path collides with another workflow. `PUT /workflows/{id}` on a published workflow **re-publishes the update** unless the query has `publishIfActive=false`; the re-publication needs the `workflow:activate` scope **and** the `workflow:publish` project permission, otherwise the new version is stored as a draft and the response is `403` naming the missing permission (the published version stays live).

### Executions (8 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/executions` | Retrieve all executions | `execution:list` |
| `POST` | `/executions/stop` | Stop multiple executions | `execution:stop` |
| `GET` | `/executions/{executionId}` | Retrieve an execution | `execution:read` |
| `DELETE` | `/executions/{executionId}` | Delete an execution | `execution:delete` |
| `POST` | `/executions/{executionId}/retry` | Retry an execution | `execution:retry` |
| `POST` | `/executions/{executionId}/stop` | Stop an execution | `execution:stop` |
| `GET` | `/executions/{executionId}/tags` | Get execution tags | `executionTags:list` |
| `PUT` | `/executions/{executionId}/tags` | Update tags of an execution | `executionTags:update` |

**Query parameters for `GET /executions`:**
- `workflowId`, `projectId` — filters
- `status` — `canceled`, `crashed`, `error`, `new`, `running`, `success`, `unknown`, `waiting`
- `limit` (default 100, max 250), `cursor`
- `includeData` (default `false`), `ignoreDataSizeLimit`, `redactExecutionData` — control the execution data in the response
- `startedAfter` / `startedBefore` — date range (ISO 8601)

### Credential (8 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/credentials` | List credentials | `credential:list` |
| `POST` | `/credentials` | Create a credential | `credential:create` |
| `GET` | `/credentials/schema/{credentialTypeName}` | Show credential data schema |  |
| `GET` | `/credentials/{credentialId}` | Get credential by ID | `credential:read` |
| `PATCH` | `/credentials/{credentialId}` | Update credential by ID | `credential:update` |
| `DELETE` | `/credentials/{credentialId}` | Delete credential by ID | `credential:delete` |
| `POST` | `/credentials/{credentialId}/test` | Test credential by ID | `credential:read` |
| `PUT` | `/credentials/{credentialId}/transfer` | Transfer a credential to another project. | `credential:move` |

**Important:** `GET /credentials` never returns secret data. Use the schema endpoint to learn the required fields before creating one. `POST /credentials/{id}/test` runs the credential's own test.

### DataTable (15 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/data-tables` | List all data tables | `dataTable:list` |
| `POST` | `/data-tables` | Create a new data table | `dataTable:create` |
| `GET` | `/data-tables/{dataTableId}` | Get a data table | `dataTable:read` |
| `PATCH` | `/data-tables/{dataTableId}` | Update a data table | `dataTable:update` |
| `DELETE` | `/data-tables/{dataTableId}` | Delete a data table | `dataTable:delete` |
| `GET` | `/data-tables/{dataTableId}/columns` | List columns of a data table | `dataTableColumn:read` |
| `POST` | `/data-tables/{dataTableId}/columns` | Add a column to a data table | `dataTableColumn:create` |
| `PATCH` | `/data-tables/{dataTableId}/columns/{columnId}` | Update a column | `dataTableColumn:update` |
| `DELETE` | `/data-tables/{dataTableId}/columns/{columnId}` | Delete a column | `dataTableColumn:delete` |
| `GET` | `/data-tables/{dataTableId}/rows` | Retrieve rows from a data table | `dataTableRow:read` |
| `POST` | `/data-tables/{dataTableId}/rows` | Insert rows into a data table | `dataTableRow:create` |
| `DELETE` | `/data-tables/{dataTableId}/rows/clear` | Clear all rows from a data table | `dataTableRow:delete` |
| `DELETE` | `/data-tables/{dataTableId}/rows/delete` | Delete rows from a data table | `dataTableRow:delete` |
| `PATCH` | `/data-tables/{dataTableId}/rows/update` | Update rows in a data table | `dataTableRow:update` |
| `POST` | `/data-tables/{dataTableId}/rows/upsert` | Upsert a row in a data table | `dataTableRow:upsert` |

`GET /data-tables/{id}/rows` takes `limit` (default 100, max 250), `cursor`, `filter`, `sortBy` and `search`. Deleting a column drops its values.

### Folders (5 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/projects/{projectId}/folders` | Retrieve folders | `folder:list` |
| `POST` | `/projects/{projectId}/folders` | Create a folder | `folder:create` |
| `GET` | `/projects/{projectId}/folders/{folderId}` | Get folder details | `folder:read` |
| `PATCH` | `/projects/{projectId}/folders/{folderId}` | Update a folder | `folder:update` |
| `DELETE` | `/projects/{projectId}/folders/{folderId}` | Delete a folder | `folder:delete` |

`GET /projects/{projectId}/folders` takes `filter`, `select`, `sortBy` (`name`, `createdAt` or `updatedAt`, `:asc` / `:desc`), `skip` and `take`.

### Projects (8 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/projects` | Retrieve projects | `project:list` |
| `POST` | `/projects` | Create a project | `project:create` |
| `PUT` | `/projects/{projectId}` | Update a project | `project:update` |
| `DELETE` | `/projects/{projectId}` | Delete a project | `project:delete` |
| `GET` | `/projects/{projectId}/users` | List project members | `user:list` |
| `POST` | `/projects/{projectId}/users` | Add one or more users to a project | `project:manageMembers` |
| `PATCH` | `/projects/{projectId}/users/{userId}` | Change a user's role in a project | `project:manageMembers` |
| `DELETE` | `/projects/{projectId}/users/{userId}` | Delete a user from a project | `project:manageMembers` |

Projects support member management — add and remove users with a project role. Deleting a project requires transferring its resources first.

### User (5 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/users` | Retrieve all users | `user:list` |
| `POST` | `/users` | Create multiple users | `user:create` |
| `GET` | `/users/{id}` | Get user by ID/Email | `user:read` |
| `DELETE` | `/users/{id}` | Delete a user | `user:delete` |
| `PATCH` | `/users/{id}/role` | Change a user's global role | `user:changeRole` |

**Roles:** `global:owner`, `global:admin`, `global:member` (custom roles: see Role). `GET /users` takes `limit`, `cursor`, `includeRole`, `projectId`.

### Tags (5 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/tags` | Retrieve all tags | `tag:list` |
| `POST` | `/tags` | Create a tag | `tag:create` |
| `GET` | `/tags/{tagId}` | Retrieves a tag | `tag:read` |
| `PUT` | `/tags/{tagId}` | Update a tag | `tag:update` |
| `DELETE` | `/tags/{tagId}` | Delete a tag | `tag:delete` |

### Variables (4 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/variables` | Retrieve variables | `variable:list` |
| `POST` | `/variables` | Create a variable | `variable:create` |
| `PUT` | `/variables/{id}` | Update a variable | `variable:update` |
| `DELETE` | `/variables/{id}` | Delete a variable | `variable:delete` |

Variables are accessible in workflows via `$vars.variableName`.

### Audit (1 operation)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `POST` | `/audit` | Generate an audit | `securityAudit:generate` |

**Body options:**
```json
{
  "additionalOptions": {
    "categories": ["credentials", "nodes", "database", "filesystem", "instance"],
    "daysAbandonedWorkflow": 90
  }
}
```

### SourceControl (3 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `POST` | `/source-control/pull` | Pull changes from the remote repository | `sourceControl:pull` |
| `POST` | `/source-control/push` | Push local source control changes | `sourceControl:push` |
| `GET` | `/source-control/status` | Preview pending source control changes | `sourceControl:read` |

`GET /source-control/status` takes `direction` (`push` or `pull`). `POST /source-control/push` takes `commitMessage`, `fileNames` and `force`; `POST /source-control/pull` takes `force` and `autoPublish`.

### Insights (1 operation)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/insights/summary` | Retrieve insights summary | `insights:read` |

Query parameters: `startDate`, `endDate`, `projectId`.

### Evaluation (5 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/workflows/{id}/test-runs` | Retrieve test runs | `testRun:list` |
| `POST` | `/workflows/{id}/test-runs` | Trigger a test run | `testRun:create` |
| `GET` | `/workflows/{id}/test-runs/{runId}` | Retrieve a test run | `testRun:read` |
| `POST` | `/workflows/{id}/test-runs/{runId}/cancel` | Cancel a test run | `testRun:cancel` |
| `GET` | `/workflows/{id}/test-runs/{runId}/test-cases` | Retrieve test run cases | `testRun:read` |

Evaluation test runs: read from n8n 2.30, trigger and cancel from 2.32.

### Discover (1 operation)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/discover` | Discover available API capabilities | none |

Returns the capability map for the **calling API key's scopes**. Query parameters: `include` (`schemas` inlines request body schemas), `resource`, `operation`. Use it to see what a key may do before building a script.

### Role (5 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/roles` | Retrieve all roles | `role:list` |
| `POST` | `/roles` | Create a custom role | `role:manage`, `role:manageProject` |
| `GET` | `/roles/{roleSlug}` | Retrieve a role | `role:read` |
| `PUT` | `/roles/{roleSlug}` | Update a custom role | `role:manage`, `role:manageProject` |
| `DELETE` | `/roles/{roleSlug}` | Delete a custom role | `role:manage`, `role:manageProject` |

### RoleMappingRule (5 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/role-mapping-rules` | Retrieve role-mapping rules | `roleMappingRule:list` |
| `POST` | `/role-mapping-rules` | Create a role-mapping rule | `roleMappingRule:create` |
| `PATCH` | `/role-mapping-rules/{roleMappingRuleId}` | Update a role-mapping rule | `roleMappingRule:update` |
| `DELETE` | `/role-mapping-rules/{roleMappingRuleId}` | Delete a role-mapping rule | `roleMappingRule:delete` |
| `POST` | `/role-mapping-rules/{roleMappingRuleId}/move` | Move a role-mapping rule | `roleMappingRule:update` |

### CommunityPackage (4 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/community-packages` | List installed community packages | `communityPackage:list` |
| `POST` | `/community-packages` | Install a community package | `communityPackage:install` |
| `PATCH` | `/community-packages/{name}` | Update a community package | `communityPackage:update` |
| `DELETE` | `/community-packages/{name}` | Uninstall a community package | `communityPackage:uninstall` |

### N8nPackage (2 operations, beta)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `POST` | `/n8n-packages/export` | Beta: Export workflows, folders, or projects as an n8n package | `project:export`, `workflow:export` |
| `POST` | `/n8n-packages/import` | Beta: Import an n8n package into a project | `workflow:import` |

### Instance administration and enterprise tags

These tags configure the instance itself (promotion between environments, node policies, log streaming, SSO, LDAP, telemetry, security policy). Each operation needs its own admin scope; read the spec for request bodies before calling them.

#### Promotions (22 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/promotions/connections` | List promotion connections | `gitConnection:list` |
| `POST` | `/promotions/connections` | Create a promotion connection | `gitConnection:create` |
| `GET` | `/promotions/connections/{promotionConnectionId}` | Retrieve a promotion connection | `gitConnection:read` |
| `PUT` | `/promotions/connections/{promotionConnectionId}` | Update a promotion connection | `gitConnection:update` |
| `DELETE` | `/promotions/connections/{promotionConnectionId}` | Delete a promotion connection | `gitConnection:delete` |
| `POST` | `/promotions/connections/{promotionConnectionId}/apply` | Apply a package to the instance | `gitConnection:pull` |
| `POST` | `/promotions/connections/{promotionConnectionId}/apply/continue` | Continue Apply after binding setup | `gitConnection:pull` |
| `PUT` | `/promotions/connections/{promotionConnectionId}/configs/apply` | Create or replace the Apply configuration | `gitConnection:update` |
| `PUT` | `/promotions/connections/{promotionConnectionId}/configs/promote` | Create or replace the Promote configuration | `gitConnection:update` |
| `DELETE` | `/promotions/connections/{promotionConnectionId}/configs/{direction}` | Remove one direction | `gitConnection:update` |
| `GET` | `/promotions/connections/{promotionConnectionId}/projects` | List projects linked to a promotion connection | `gitConnection:read` |
| `POST` | `/promotions/connections/{promotionConnectionId}/projects/{projectId}` | Link a project to a promotion connection | `gitConnection:manageProjects` |
| `DELETE` | `/promotions/connections/{promotionConnectionId}/projects/{projectId}` | Unlink a project from a promotion connection | `gitConnection:manageProjects` |
| `POST` | `/promotions/connections/{promotionConnectionId}/promote` | Promote all team projects | `gitConnection:push` |
| `POST` | `/promotions/connections/{promotionConnectionId}/{direction}/clone` | Clone one direction's repository | `gitConnection:clone` |
| `POST` | `/promotions/connections/{promotionConnectionId}/{direction}/disconnect` | Remove one direction's local checkout | `gitConnection:clone` |
| `GET` | `/promotions/projects/{projectId}/changes/{direction}` | List the changes of a project in one direction | `gitConnection:push`, `gitConnection:pull` |
| `GET` | `/promotions/providers` | List promotion providers | `gitConnection:list` |
| `POST` | `/promotions/providers` | Create a promotion provider | `gitConnection:create` |
| `GET` | `/promotions/providers/{promotionProviderId}` | Retrieve a promotion provider | `gitConnection:read` |
| `PUT` | `/promotions/providers/{promotionProviderId}` | Update a promotion provider | `gitConnection:update` |
| `DELETE` | `/promotions/providers/{promotionProviderId}` | Delete a promotion provider | `gitConnection:delete` |

#### NodeTypePolicy (10 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/node-type-policies/instance` | Retrieve the instance node type policy | `nodeTypePolicy:manage` |
| `PUT` | `/node-type-policies/instance` | Replace the instance node type policy | `nodeTypePolicy:manage` |
| `GET` | `/node-type-policies/policies` | List node type policy documents | `nodeTypePolicy:manage` |
| `POST` | `/node-type-policies/policies` | Create a node type policy document | `nodeTypePolicy:manage` |
| `GET` | `/node-type-policies/policies/{policyId}` | Retrieve a node type policy document | `nodeTypePolicy:manage` |
| `PUT` | `/node-type-policies/policies/{policyId}` | Replace the rules of a node type policy document | `nodeTypePolicy:manage` |
| `DELETE` | `/node-type-policies/policies/{policyId}` | Delete a node type policy document | `nodeTypePolicy:manage` |
| `GET` | `/node-type-policies/projects/{projectId}` | Retrieve a project's node type policy | `nodeTypePolicy:manage` |
| `PUT` | `/node-type-policies/projects/{projectId}` | Replace a project's node type policy | `nodeTypePolicy:manage` |
| `PUT` | `/node-type-policies/scopes/{scopeId}/attachments` | Replace a scope's attached policy documents | `nodeTypePolicy:manage` |

#### LogStreaming (7 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/settings/log-streaming/destinations` | List log streaming destinations | `eventBusDestination:list` |
| `POST` | `/settings/log-streaming/destinations` | Create a log streaming destination | `eventBusDestination:create` |
| `GET` | `/settings/log-streaming/destinations/{id}` | Retrieve a log streaming destination | `eventBusDestination:read` |
| `PUT` | `/settings/log-streaming/destinations/{id}` | Update a log streaming destination | `eventBusDestination:update` |
| `DELETE` | `/settings/log-streaming/destinations/{id}` | Delete a log streaming destination | `eventBusDestination:delete` |
| `POST` | `/settings/log-streaming/destinations/{id}/test` | Send a test message to a log streaming destination | `eventBusDestination:test` |
| `GET` | `/settings/log-streaming/event-types` | List streamable event types | `eventBusDestination:list` |

#### SecurityPolicy (2 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/settings/security-policy` | Retrieve the security policy | `securitySettings:manage` |
| `PUT` | `/settings/security-policy` | Set the security policy | `securitySettings:manage` |

#### SettingsLdap (4 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/settings/ldap` | Retrieve the LDAP configuration | `ldap:manage` |
| `PUT` | `/settings/ldap` | Set the LDAP configuration | `ldap:manage` |
| `GET` | `/settings/ldap/sync` | Retrieve LDAP synchronization history | `ldap:sync` |
| `POST` | `/settings/ldap/sync` | Trigger an LDAP synchronization | `ldap:sync` |

#### SettingsOtel (3 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/settings/otel` | Retrieve the OpenTelemetry configuration | `otel:manage` |
| `PUT` | `/settings/otel` | Set the OpenTelemetry configuration | `otel:manage` |
| `POST` | `/settings/otel/test-trace` | Test the connection to an OTLP collector | `otel:manage` |

#### SettingsSsoOidc (2 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/settings/sso/oidc` | Retrieve the OIDC SSO configuration | `oidc:manage` |
| `PUT` | `/settings/sso/oidc` | Set the OIDC SSO configuration | `oidc:manage` |

#### SettingsSsoSaml (2 operations)

| Method | Endpoint | Description | Scope |
|--------|----------|-------------|-------|
| `GET` | `/settings/sso/saml` | Retrieve the SAML SSO configuration | `saml:manage` |
| `PUT` | `/settings/sso/saml` | Set the SAML SSO configuration | `saml:manage` |

---

## Notes the spec does not spell out

- **What is bundled.** `references/n8n-api.json` is the n8n 2.41.6 public API, bundled from the n8n repository at tag `n8n@2.41.6` (`packages/cli/src/public-api/v1`): `openapi.yml` (57 operations) and `openapi.decorator-routes.generated.yml` (97 operations), each bundled with Redocly and merged into one document — 154 operations, 26 tags, no overlap. `info.version` stays `1.1.1` because n8n does not bump it.
- **Routes are version-specific.** Publish/unpublish routes exist from n8n 2.33 (older instances only have the deprecated activate/deactivate pair), the workflow-version route moved in 2.39, evaluations are readable from 2.30 and runnable from 2.32. A newer or older instance than 2.41.6 differs: open its playground (`/api/v1/docs`) or call `GET /api/v1/discover` for the exact surface your key can use.
- **Draft versus published.** Reading `GET /workflows/{id}` returns the draft; the published graph is what executes. See the publish notes under *Workflow*.
- **Not the Public API.** The editor talks to internal `/rest/...` routes. They are unversioned and unsupported for scripts.

---

## Common curl Patterns

### List Workflows

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE/api/v1/workflows"
```

### Get Workflow by ID

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE/api/v1/workflows/123"
```

### Create Workflow

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Workflow","nodes":[],"connections":{},"settings":{}}' \
  "$N8N_BASE/api/v1/workflows"
```

### Publish Workflow

Makes the workflow's triggers live. Publish only when the owner asks.

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"versionId":"<version-id>"}' \
  "$N8N_BASE/api/v1/workflows/123/publish"
```

The body is optional; without it the latest version is published. On an older n8n (before 2.33) use `/activate`.

### Unpublish Workflow

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE/api/v1/workflows/123/unpublish"
```

### Save a Draft Without Re-publishing

```bash
curl -X PUT \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @workflow.json \
  "$N8N_BASE/api/v1/workflows/123?publishIfActive=false"
```

### List Executions (filtered)

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE/api/v1/executions?workflowId=123&status=error&limit=10"
```

### Retry Failed Execution

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE/api/v1/executions/456/retry"
```

### Create Credential

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"My API Key","type":"httpHeaderAuth","data":{"name":"Authorization","value":"Bearer xxx"}}' \
  "$N8N_BASE/api/v1/credentials"
```

### Get Credential Schema

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE/api/v1/credentials/schema/httpHeaderAuth"
```

### Create Tag

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"production"}' \
  "$N8N_BASE/api/v1/tags"
```

### Tag a Workflow

```bash
curl -X PUT \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"id":"tag-id-here"}]' \
  "$N8N_BASE/api/v1/workflows/123/tags"
```

### List Variables

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE/api/v1/variables"
```

### Run Security Audit

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"additionalOptions":{"categories":["credentials","nodes","instance"]}}' \
  "$N8N_BASE/api/v1/audit"
```

### Get Data Table Rows

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE/api/v1/data-tables/dt-abc123/rows?limit=50"
```

---

## Pagination

The n8n API uses **cursor-based pagination**.

### How It Works

1. First request: `GET /workflows?limit=10`
2. Response includes `nextCursor` if more results exist
3. Next request: `GET /workflows?limit=10&cursor=<nextCursor-value>`
4. Repeat until `nextCursor` is absent

### Response Structure

```jsonc
{
  "data": [...],
  "nextCursor": "eyJsaW1pdCI6MTAsIm9mZnNldCI6MTB9"
}
```

When `nextCursor` is `null` or absent, you have reached the last page.

### Pagination Example (bash loop)

```bash
CURSOR=""
while true; do
  RESPONSE=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
    "$N8N_BASE/api/v1/workflows?limit=50${CURSOR:+&cursor=$CURSOR}")
  echo "$RESPONSE" | jq '.data[]'
  CURSOR=$(echo "$RESPONSE" | jq -r '.nextCursor // empty')
  [ -z "$CURSOR" ] && break
done
```

---

## Error Responses

| Status | Meaning | Common Cause |
|--------|---------|--------------|
| 400 | Bad Request | Invalid JSON body or missing required fields |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | The API key lacks the operation's scope, or the user lacks the project permission (for example `workflow:publish` when saving a published workflow) |
| 404 | Not Found | Resource doesn't exist or wrong endpoint URL |
| 409 | Conflict | Resource already exists (e.g., duplicate tag name), or publishing is blocked (open workflow review, webhook path collision) |
| 500 | Internal Server Error | Server-side issue, check n8n logs |

### Error Response Format

```json
{
  "code": 404,
  "message": "Workflow with ID \"999\" could not be found."
}
```

---

## Rate Limits and Best Practices

- No official rate limits documented, but self-hosted instances may have resource constraints
- Use pagination (`limit` + `cursor`) for large datasets instead of fetching all at once
- Cache credential schemas — they rarely change
- Use `status` and `workflowId` filters on executions to reduce response size
- Prefer `PATCH` over `PUT` for credentials to avoid overwriting unchanged fields
- When bulk-operating, add small delays between requests to avoid overloading the instance
