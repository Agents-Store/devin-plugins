---
name: init-project
description: This skill should be used when the user asks to "set up composable stack", "initialize project", "configure environment", "connect MCP services", or needs to set up all MCP connections and environment variables for the Composable Stack v1.
---

# Initialize Composable Stack v1

Set up environment variables, verify all MCP connections, and create project configuration for the Composable Stack.

## Architecture Overview

| Layer | Service | MCP Server | Transport |
|-------|---------|------------|-----------|
| Data | PostgreSQL + NocoDB | `nocodb` | HTTP |
| Data | PostgreSQL (direct) | `postgresql-mcp` | HTTP |
| Logic | n8n | `n8n-mcp-external` + `n8n-native-mcp` | stdio + HTTP |
| Logic | Trigger.dev | `trigger-dev` | stdio |
| Interface | NocoBase (prod) | — (via NocoBase API with `NOCOBASE_URL` + `NOCOBASE_API_KEY`) | — |
| Interface | NocoBase (dev sandbox) | `nocobase-dev` | HTTP |
| Interface | NocoDB | — (covered by the `nocodb` MCP above) | — |

## NocoBase: Two Instances

This stack uses **two NocoBase instances** for a safe develop-then-promote workflow:

| Instance | Env Vars | Purpose |
|----------|----------|---------|
| **Production** | `NOCOBASE_URL`, `NOCOBASE_API_KEY` | Stable collections, released UI, live data |
| **Development** | `NOCOBASE_DEV_URL`, `NOCOBASE_DEV_API_KEY` | Sandbox for building/testing new tables, UX elements, menus, pages, workflows; also used for test-app API and MCP calls |

**Rule of thumb:**
- Build new tables, fields, collections, menus, pages, blocks, and workflows on the **dev** instance first.
- Test API flows and test apps against the **dev** instance — safe to break.
- Promote validated schema and UI to **prod** via export/import or migration.

The `nocobase-dev` MCP server in this plugin points at `${NOCOBASE_DEV_URL}/api/mcp`, so the NocoBase MCP toolset (collections, fields, resources, workflows, flow-surfaces, RBAC, data sources — about 180 tools in October 2026; the number drifts between releases) is available for the dev instance out of the box. The `x-mcp-packages` header in `.mcp.json` limits which plugin groups the server exposes; keep it as small as the work needs.

## Step 1: Environment Variables

### Using Infisical (recommended)

Pull all secrets from Infisical in one command:

```bash
./scripts/setup.sh dev .env .claude/settings.local.json
```

This writes `.env` and injects variables into `.claude/settings.local.json` for MCP resolution.

### Manual Setup

Copy the template and fill in values:

```bash
cp templates/.env.example .env
```

Required variables:

| Variable | Service | Description |
|----------|---------|-------------|
| `TRIGGER_SECRET_KEY` | Trigger.dev | Dev environment secret key (`tr_dev_xxx`) |
| `TRIGGER_ACCESS_TOKEN` | Trigger.dev | Personal Access Token (`tr_pat_xxx`) — MCP server auth |
| `TRIGGER_API_URL` | Trigger.dev | Self-hosted instance URL |
| `N8N_API_URL` | n8n | Instance base URL |
| `N8N_API_KEY` | n8n | API authentication key |
| `N8N_NATIVE_MCP_URL` | n8n | Full native MCP URL (`{N8N_API_URL}/mcp-server/http`) |
| `N8N_MCP_TOKEN` | n8n | Native MCP bearer token |
| `NOCODB_MCP_URL` | NocoDB | MCP server URL (full URL with `/mcp` path) |
| `NOCODB_MCP_TOKEN` | NocoDB | MCP authentication token (`xc-mcp-token` header; not the REST API token `NOCODB_TOKEN`) |
| `POSTGRESQL_MCP_URL` | PostgreSQL MCP | MCP server URL (full URL with `/mcp` path) |
| `POSTGRESQL_MCP_TOKEN` | PostgreSQL MCP | MCP bearer token |
| `POSTGRESQL_API_URL` | PostgREST | PostgREST base URL (no trailing slash) |
| `POSTGRESQL_API_TOKEN` | PostgREST | PostgREST bearer token |
| `NOCOBASE_URL` | NocoBase (prod) | Production instance URL |
| `NOCOBASE_API_KEY` | NocoBase (prod) | API key for production NocoBase |
| `NOCOBASE_DEV_URL` | NocoBase (dev) | Dev-sandbox instance URL — used for building/testing tables, UX, menus, pages, workflows, and dev/test apps |
| `NOCOBASE_DEV_API_KEY` | NocoBase (dev) | API key for dev NocoBase (also auth for the `nocobase-dev` MCP server) |

## Step 2: Verify MCP Connections

Test each service connection in order.

### 2a. NocoDB (Data layer)

```
Tool: mcp__plugin_stack-composable-stack-v1_nocodb__getTablesList
```

Expected: returns a list of tables from the connected NocoDB base.

### 2b. n8n External MCP (Logic layer)

```
Tool: mcp__plugin_stack-composable-stack-v1_n8n-mcp-external__search_nodes
Input: { "query": "webhook", "limit": 5 }
```

Expected: returns matching n8n node types.

### 2c. n8n Native MCP (Logic layer)

```
Tool: mcp__plugin_stack-composable-stack-v1_n8n-native-mcp__search_workflows
Input: { "limit": 5 }
```

Expected: returns a preview of workflows from the n8n instance (an empty list on a fresh instance is a pass; a 401/403 is not).

### 2d. Trigger.dev (Logic layer)

```
Tool: mcp__plugin_stack-composable-stack-v1_trigger-dev__list_runs
Input: { "limit": 5 }
```

Expected: returns recent task runs of the `dev` environment (the tool's default; an empty list is a pass).

### 2e. PostgreSQL MCP (Data layer — direct)

```
Tool: mcp__plugin_stack-composable-stack-v1_postgresql-mcp__database_overview
```

Expected: returns PostgreSQL server version, uptime, connection counts, and replica status.

### 2f. PostgREST API (Data layer — REST)

Verify with a direct HTTP call:

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  "${POSTGRESQL_API_URL}/"
```

Expected: HTTP 200 with OpenAPI spec of available endpoints.

### 2g. NocoBase dev instance (Interface layer — sandbox)

The `nocobase-dev` MCP server in this plugin targets `${NOCOBASE_DEV_URL}/api/mcp`. Verify with any NocoBase MCP tool:

```
Tool: mcp__plugin_stack-composable-stack-v1_nocobase-dev__collections_list
```

Expected: returns the collections defined on the dev NocoBase instance.

Also verify HTTP API access:

```bash
curl -s -H "Authorization: Bearer ${NOCOBASE_DEV_API_KEY}" \
  "${NOCOBASE_DEV_URL}/api/collections:list" | head -c 500
```

Expected: HTTP 200 with a JSON list of collections.

### 2h. NocoBase production instance (Interface layer)

Production NocoBase is accessed via HTTP API only (no MCP transport in this plugin — keeps prod safe from accidental MCP mutations):

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer ${NOCOBASE_API_KEY}" \
  "${NOCOBASE_URL}/api/collections:list"
```

Expected: HTTP 200.

If you need MCP against production, the `nocobase-dev` technology plugin can be re-pointed at `NOCOBASE_URL` — but prefer to build on the dev instance and promote.

## Step 3: Create CLAUDE.md

Copy the template:

```bash
cp templates/CLAUDE.md.template CLAUDE.md
```

Replace `{{PROJECT_NAME}}` with your project name.

## Step 4: Verify Installed Plugins

This plugin declares its technology plugins as `dependencies`, so they install with it. Confirm they are enabled in `.claude/settings.json`:

- `trigger-dev@agents-store-claude-plugins`
- `n8n-dev@agents-store-claude-plugins`
- `nocodb-ops@agents-store-claude-plugins`
- `nocobase-dev@agents-store-claude-plugins`
- `postgresql-external-dev@agents-store-claude-plugins`

These provide tool-specific knowledge. The stack plugin provides the architecture and the integration patterns between services. `n8n-provision@agents-store-claude-plugins` is optional: it provisions an n8n instance and is not needed to build with the stack.

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| MCP connection refused | Service not running or wrong URL | Verify URL in `.env`, check service health |
| 401 on NocoDB | Invalid MCP token | Regenerate the MCP token in NocoDB and update `NOCODB_MCP_TOKEN` |
| 401 on n8n | Expired API key | Create new API key in n8n settings |
| Trigger.dev timeout | Wrong `TRIGGER_API_URL` | Verify the self-hosted instance URL |
| n8n native MCP 403 | Wrong MCP token | Generate new MCP token in n8n → Settings → API |
| 401 on PostgreSQL MCP | Invalid MCP token | Regenerate bearer token in MCP server settings |
| 401 on PostgREST | Invalid API token | Check PostgREST JWT secret and regenerate token |
