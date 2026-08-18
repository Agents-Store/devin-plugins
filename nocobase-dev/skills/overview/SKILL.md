---
name: overview
description: "Use when the user asks anything about NocoBase v2 — \"build app on NocoBase v2\", \"manage NocoBase\", \"how do I X in NocoBase\", \"NocoBase API or CLI\". Establishes the cardinal rule (REST API or `nb` CLI — pick whichever is convenient) and routes to the right specialist skill in this plugin."
---

# NocoBase v2 — overview and skill router

This plugin documents NocoBase v2 development and operations. Two surfaces are supported: the **HTTP REST API** under `/api/` and the **`nb` CLI**. They are interchangeable for most tasks.

## Cardinal rule

For any task, pick the surface that's more convenient — do not mix when one suffices.

- **CLI** (`nb …`) is best when the user is on a terminal in the NocoBase project directory: install, lifecycle, `pm enable`, backup/restore, migration, declarative `nb api …` calls.
- **REST API** (`/api/…`) is best when calling NocoBase from another service, a script, or a workflow runner: CRUD on collections, triggering workflows, reading executions, working with arbitrary data.

If both work, prefer **CLI** when the agent is already running locally with `nb` available, and **REST API** when the call originates from a different host or process.

## Authentication (always required)

All API calls need `Authorization: Bearer <token>`. Two ways to obtain one:

1. **API Key** — enable the `API Keys` plugin, create a key in `Settings → API keys`. Recommended for service-to-service.
2. **OAuth (IdP: OAuth)** — enable the `IdP: OAuth` plugin and configure a provider. Recommended for end-user-facing flows.

→ See `auth` skill for full setup with curl + Node samples.

## Routing — which skill handles what

| User task | Skill to load |
|---|---|
| "Install NocoBase / set up `nb` / start/stop the app" | `cli-recipes`, then `nocobase-env-manage` |
| "Find an HTTP endpoint / read the OpenAPI spec" | `api-reference` (loads on demand) |
| "Authenticate / create API key / set up OAuth" | `auth` |
| "Show me an end-to-end example mixing API + CLI" | `examples` |
| "Create / change / list collections, fields, relations" | `nocobase-data-modeling` |
| "Build / edit pages, blocks, popups, menus" | `nocobase-ui-builder` (default UI authoring entry) |
| "Create / edit / diagnose workflows" | `nocobase-workflow-manage` |
| "Roles, permissions, role mode, ACL" | `nocobase-acl-manage` |
| "Enable / disable / list plugins via `nb pm`" | `nocobase-plugin-manage` |
| "Backup, restore, migrate environments" | `nocobase-publish-manage` |
| "Develop a NocoBase plugin (server + client code)" | `nocobase-plugin-development` |
| "YAML-DSL build path (committed spec files, `cli push`)" | `nocobase-dsl-reconciler` (opt-in only) |
| "Query business data — counts, breakdowns, summaries" | `nocobase-data-analysis` |
| "Evaluators, expressions, formula syntax, UID" | `nocobase-utils` |

When a request spans several of these, load the most specific skill first; the upstream skills cross-reference each other automatically.

## CLI quick install

```bash
npm install -g @nocobase/cli@beta
nb init --ui            # browser-based first-time setup
nb start                # later runs
```

Detailed steps and constraints (timeouts, sandboxed-environment behaviour, never auto-fill the install form) live in `nocobase-env-manage`.

## REST API quick start

```bash
curl -H "Authorization: Bearer ${NB_TOKEN}" \
     "${NB_URL}/api/collections:list"
```

Endpoint conventions: `GET /api/{resource}:{action}` for reads, `POST /api/{resource}:{action}` for writes. The full spec sits at `${CLAUDE_PLUGIN_ROOT}/references/openapi/nocobase.json` — see the `api-reference` skill for navigation.

## What this plugin does NOT do

- It does not bundle an MCP server for NocoBase. If a NocoBase MCP server is configured separately (`nc-mcp` or similar), the upstream skills can use it; this plugin works without one.
- It does not duplicate or replace the legacy `nocobase-dev` plugin — load only one at a time.
