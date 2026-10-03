---
name: overview
description: "Use when the user asks anything about NocoBase v2 — \"build app on NocoBase v2\", \"manage NocoBase\", \"how do I X in NocoBase\", \"NocoBase API or CLI\". Establishes the cardinal rule (REST API or `nb` CLI — pick whichever is convenient) and routes to the right specialist skill among the 20 upstream `nocobase-*` skills and the 4 custom skills in this plugin (UI authoring always enters through `nocobase-portal-manage`)."
---

# NocoBase v2 — overview and skill router

This plugin documents NocoBase v2 development and operations. Two surfaces are supported: the **HTTP REST API** under `/api/` and the **`nb` CLI**. They are interchangeable for most tasks. A third, agent-facing surface — the built-in MCP server at `/api/mcp` — is covered at the end.

## Cardinal rule

For any task, pick the surface that's more convenient — do not mix when one suffices.

- **CLI** (`nb …`) is best when the user is on a terminal and has an `nb` env configured: install, lifecycle (`nb app …`), plugins (`nb plugin …`), backup/restore (`nb backup …`), and the declarative `nb api …` calls.
- **REST API** (`/api/…`) is best when calling NocoBase from another service, a script, or a workflow runner: CRUD on collections, running workflows, reading executions, working with arbitrary data.

If both work, prefer **CLI** when the agent is already running locally with `nb` available, and **REST API** when the call originates from a different host or process.

## Authentication (always required)

Every call needs credentials. Three ways to obtain them:

1. **CLI env** — `nb env add <name> --api-base-url <https://host/api> --auth-type oauth|token|basic`, then `nb env auth [name]`. This is the native way: the CLI stores the credential, and every `nb api …` command picks it up (`-e <env>` to choose another env).
2. **API Key** — the built-in `API keys` plugin (enabled by default); create a key in `Settings → API keys`. Recommended for service-to-service REST calls (`Authorization: Bearer <key>`).
3. **OAuth via IdP: OAuth** — the built-in `IdP: OAuth` plugin (`@nocobase/plugin-idp-oauth`, OAuth 2.1 / OIDC) makes NocoBase act as an identity provider for **tools** — `nb env auth --auth-type oauth` and MCP clients sign in through it. It is **not** the SSO login with Google/Keycloak/Entra; that is the separate, commercial **Auth: OIDC** plugin.

→ See the `auth` skill for the full setup, curl and Node samples, and the IdP: OAuth versus Auth: OIDC split.

## Routing — which skill handles what

| User task | Skill to load |
|---|---|
| "Install NocoBase / set up `nb` / start, stop, upgrade the app / add an env" | `cli-recipes`, then `nocobase-env-manage` |
| "Find an HTTP endpoint / read the OpenAPI spec" | `api-reference` (loads on demand) |
| "Authenticate / create API key / set up OAuth" | `auth` |
| "Show me an end-to-end example mixing API + CLI" | `examples` |
| **"Build / edit pages, menus, blocks, fields, actions, dashboards, charts" (any UI authoring request)** | **`nocobase-portal-manage`** — the primary entry. It resolves exactly one enabled Portal, then hands off to `nocobase-ui-builder` (no-code Portal, or a runtime without Portals) or `nocobase-ai-builder` (AI Portal). Never start at `nocobase-ui-builder` |
| "Build the app from an HTML / image / link prototype", "page does not match the prototype" | `nocobase-prototype-repro` |
| "Create / change / list collections, fields, relations, view-backed collections" | `nocobase-data-modeling` |
| "Create / edit / diagnose workflows" | `nocobase-workflow-manage` |
| "Roles, permissions, role mode, which roles may enter a Portal" | `nocobase-acl-manage` |
| "List / enable / disable plugins via `nb plugin`" | `nocobase-plugin-manage` |
| "Backup, restore, migrate between environments" | `nocobase-publish-manage` |
| "Develop a NocoBase plugin (server + client code)" | `nocobase-plugin-development` |
| "LLM providers, saved LLM services, model discovery, AI prerequisites" | `nocobase-ai-manager` |
| "Create / maintain an AI employee" | `nocobase-ai-employee` (binding it to a UI surface is then done by the UI skills) |
| "Knowledge base, vector database, documents, retrieval tests" | `nocobase-ai-knowledge-base-manager` (Professional+) |
| "File storage engines, file collections, attachments" | `nocobase-file-manager` |
| "Notification channels (in-app, SMTP email), send logs" | `nocobase-notification-manage` |
| "Save a finished milestone as a restorable revision" | `nocobase-revision` |
| "YAML-DSL build path (committed spec files, `cli push`)" | `nocobase-dsl-reconciler` (opt-in only) |
| "Query business data — counts, breakdowns, summaries" | `nocobase-data-analysis` |
| "Evaluators, expressions, formula syntax, filter operators, UID" | `nocobase-utils` |

When a request spans several of these, load the most specific skill first; the upstream skills cross-reference each other automatically.

`nb portal` (Portal list, create, pull, push, deploy) ships **only in the `@alpha` channel** of `@nocobase/cli` (2.4.0-alpha.9 on 2026-10-02) — it is absent from the stable `latest` (2.2.20) and `beta` (2.3.0-beta.13). On a stable CLI, `nocobase-portal-manage` falls back to the legacy `nocobase-ui-builder` lane for ordinary UI authoring when the runtime reports `capabilities.multiPortal: false`, and stops for Portal lifecycle actions with a "missing `nb portal`" report. Install `@nocobase/cli@alpha` only when the user needs Portals.

## CLI quick install

```bash
npm install -g @nocobase/cli      # stable channel (`latest`); Node.js >= 22
nb --version
nb init --ui                      # browser-based first-time setup (new app or connect an existing one)
nb app start                      # later runs
```

Detailed steps and constraints (timeouts, sandboxed-environment behaviour, never auto-fill the install form) live in `nocobase-env-manage`. Connecting an agent to an existing NocoBase requires NocoBase **2.1.0 or newer**.

## REST API quick start

```bash
curl -H "Authorization: Bearer ${NB_TOKEN}" \
     "${NB_URL}/api/collections:list"
```

Endpoint conventions: `GET /api/{resource}:{action}` for reads, `POST /api/{resource}:{action}` for writes. The full spec sits at `${CLAUDE_PLUGIN_ROOT}/references/openapi/nocobase.json` — see the `api-reference` skill for navigation.

## Built-in MCP server

NocoBase ships its own MCP endpoint — plugin `@nocobase/plugin-mcp-server` (built-in): `https://<host>:<port>/api/mcp` for the main app (streamable HTTP), `…/api/__app/<app_name>/mcp` for a sub-application. Authenticate with an API key (`Authorization: Bearer`) or OAuth (needs IdP: OAuth; choose the role with the `x-role` header). By default only the generic `resource_*` tools are exposed; widen the surface with the `x-mcp-packages` header (for example `@nocobase/plugin-workflow,plugin-users`). `nocobase-data-analysis` works through this endpoint. The older standalone MCP package names are retired — do not look for them.

## What this plugin does NOT do

- It does not bundle an MCP server configuration for NocoBase — the endpoint above is per instance (host and credential), so the user adds it to their own MCP client. The plugin works without one.
- It replaces the retired `nocobase` plugin (the marketplace `renames` map moves installed copies to `nocobase-dev`); there is nothing to load alongside it.
