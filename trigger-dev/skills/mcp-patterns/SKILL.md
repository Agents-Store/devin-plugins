---
name: mcp-patterns
description: Trigger.dev MCP tools reference — all 33 tools, parameters, usage patterns, and common workflows as of v4.4.4. Use when the user asks about "trigger.dev MCP tools", "which trigger.dev tools are available", "how to use trigger.dev MCP", "trigger task via MCP", "list runs MCP", "profile switching", "TRQL queries from MCP", "dev server control", or "managed prompts overrides".
---

# Trigger.dev MCP Tool Patterns

Reference for every MCP tool provided by the official Trigger.dev MCP server (v4.4.4 — 33 tools across 9 categories).

> **Note:** This plugin provides MCP **knowledge**, not the MCP connection. Install the MCP server via `npx trigger.dev@latest install-mcp` or configure it manually in your project.

## Install the MCP Server

```bash
# Interactive installer (detects installed clients)
npx trigger.dev@latest install-mcp

# Target a specific client
npx trigger.dev@latest install-mcp --client claude-code

# Install across all supported clients
npx trigger.dev@latest install-mcp --yolo
```

### Install Flags

| Flag | Purpose |
|------|---------|
| `--client <name...>` | Install for specific client(s) — claude-code, cursor, windsurf, vscode, zed, cline, gemini-cli, amp, openai-codex, crush, opencode, ruler |
| `--scope <scope>` | `user`, `project`, or `local` config file |
| `--dev-only` | Restrict tools to the dev environment only (hides `deploy`, `list_preview_branches`) |
| `--readonly` | Hide write tools (`deploy`, `trigger_task`, `cancel_run`) — agent cannot make changes |
| `--project-ref <ref>` | Scope MCP to a single project (proj_xxx) |
| `--tag <tag>` | Pin CLI package version |
| `-a, --api-url <url>` | Self-hosted API URL |
| `--log-file <path>` | Write MCP server logs to file |
| `--log-level <level>` | debug / info / log / warn / error / none |
| `--yolo` | Install into every supported client |

### Manual Config Example

```json
{
  "mcpServers": {
    "trigger": {
      "command": "npx",
      "args": ["trigger.dev@latest", "mcp", "--dev-only", "--project-ref", "proj_abc123"]
    }
  }
}
```

> **Tool annotations:** every tool carries `readOnlyHint` / `destructiveHint` metadata so MCP clients can gate write operations. `--readonly` enforces it server-side.

## Shared Parameters

Most tools accept these optional parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `projectRef` | Project ref (proj_xxx) | Auto-detected from trigger.config.ts |
| `configPath` | Path to trigger.config.ts | Auto |
| `environment` | dev, staging, prod, preview | dev |
| `branch` | Branch name (required with preview) | — |

## Documentation & Search

| Tool | Description |
|------|-------------|
| `search_docs` | Search Trigger.dev documentation |

## Project & Organization

| Tool | Description |
|------|-------------|
| `list_orgs` | List your organizations |
| `list_projects` | List your projects |
| `create_project_in_org` | Create a new project in an org |
| `initialize_project` | Init Trigger.dev in a directory |

## Task Management

| Tool | Description |
|------|-------------|
| `get_current_worker` | Worker version, SDK version, task list, machine presets (**no longer inlines payload schemas** in v4.4.4) |
| `get_task_schema` | Fetch the payload schema for a specific task (replaces the inlined schemas that used to live on `get_current_worker`) |
| `trigger_task` | Trigger a task with payload and options |

## Run Monitoring

| Tool | Description |
|------|-------------|
| `list_runs` | List and filter runs by status, task, tag, period |
| `get_run_details` | Run trace, logs, output — **trace output is paginated with a cursor** since v4.4.4 |
| `get_span_details` | Inspect a single span inside a run — attributes, events, AI enrichment (model, tokens, cost), child runs. Span IDs now appear in `get_run_details` output. |
| `wait_for_run_to_complete` | Wait for a run to finish |
| `cancel_run` | Cancel a running/queued run |

## Deployment

| Tool | Description |
|------|-------------|
| `deploy` | Deploy to staging/production/preview |
| `list_deploys` | List deployments with filters |
| `list_preview_branches` | List preview branches (not available with `--dev-only`) |

## Profile

| Tool | Description |
|------|-------------|
| `whoami` | Show current profile, user, and API URL |
| `list_profiles` | List all configured CLI profiles and the active one |
| `switch_profile` | Change the active profile for this MCP session (affects all subsequent tool calls) |

## Query & Analytics

Powered by TRQL (Trigger.dev Query Language — SQL over ClickHouse). See the **observability** skill for TRQL syntax and examples.

| Tool | Description |
|------|-------------|
| `get_query_schema` | Get columns, types, and descriptions for one TRQL table (now requires a `table` name — `runs`, `metrics`, or `llm_metrics`) |
| `query` | Execute a TRQL query. Results returned as text tables (~50% fewer tokens than JSON) |
| `list_dashboards` | List built-in dashboards and their widget IDs |
| `run_dashboard_query` | Execute a single widget query from a built-in dashboard |

## Dev Server

| Tool | Description |
|------|-------------|
| `start_dev_server` | Start `trigger dev` in the background (waits up to 30s for the worker to be ready) |
| `stop_dev_server` | Stop the running dev server |
| `dev_server_status` | Show status (`stopped` / `starting` / `ready` / `error`) and recent log lines (`lines` default 50) |

## Managed Prompts

Trigger.dev Managed Prompts — versioned prompts with dashboard overrides. See the **managed-prompts** skill for the full workflow.

| Tool | Description |
|------|-------------|
| `list_prompts` | List managed prompts — slug, current version, override status, version count |
| `get_prompt_versions` | List versions for one prompt — labels (`current`/`override`/`latest`), source (`code`/`dashboard`), model, content |
| `promote_prompt_version` | Promote a code-sourced version to current (dashboard overrides use override tools) |
| `create_prompt_override` | Create a dashboard override (takes precedence over the current code version) |
| `update_prompt_override` | Update the active dashboard override |
| `remove_prompt_override` | Remove the override — revert to the current code version |
| `reactivate_prompt_override` | Reactivate a prior dashboard-sourced version as the active override |

## Common Patterns

### Trigger and Monitor

```
1. get_current_worker(environment="dev") → task list
2. get_task_schema(taskIdentifier="process-order") → payload schema
3. trigger_task(taskId, payload) → run ID
4. wait_for_run_to_complete(runId) → result
```

### Debug a Failed Run with AI Enrichment

```
1. list_runs(status="FAILED", period="1d")
2. get_run_details(runId) → error trace + span IDs
3. get_span_details(runId, spanId) → llm model, tokens, cost per AI call
4. search_docs(query="<error topic>")
```

### Deploy Flow

```
1. deploy(environment="staging")
2. trigger_task(environment="staging") → verify
3. deploy(environment="prod")
4. list_deploys(environment="prod", limit=1) → confirm
```

### Initialize Project

```
1. list_orgs() → pick org
2. initialize_project(orgParam, projectName, cwd)
3. get_current_worker(environment="dev") → verify
```

### Dev Server Lifecycle (agent-controlled)

```
1. start_dev_server(configPath?) → launches `trigger dev` in background
2. dev_server_status(lines=50) → poll until status="ready"
3. trigger_task(...) → test against the dev worker
4. stop_dev_server() → tear down when done
```

### Query Analytics (TRQL)

```
1. get_query_schema(table="runs") → column list
2. query({
     query: "SELECT status, count() FROM runs GROUP BY status",
     period: "7d"
   }) → text table
```

### Dashboard Metrics

```
1. list_dashboards() → { dashboardId, widgets: [{ widgetId, title }] }
2. run_dashboard_query(dashboardId, widgetId, period="30d") → widget data
```

### Switch Profile Mid-Session

```
1. whoami() → current profile + API URL
2. list_profiles() → available profiles
3. switch_profile("self-hosted-prod") → all subsequent tool calls use the new profile
```

### Prompt Override Hotfix

```
1. list_prompts(environment="prod") → find slug
2. get_prompt_versions(slug="customer-reply") → see current/override state
3. create_prompt_override(slug, textContent="...revised copy...", commitMessage="Fix tone issue")
4. (iterate) update_prompt_override(slug, textContent="...")
5. remove_prompt_override(slug) → revert to code version when code is redeployed
```

## Best Practices

- **Prefer `get_task_schema` before `trigger_task`** — `get_current_worker` no longer ships schemas inline.
- Use `limit` and `period` to avoid fetching too many runs.
- Use `idempotencyKey` in trigger options to prevent duplicate runs.
- Default to the dev environment for safety; switch explicitly with `switch_profile` or `environment=`.
- For monorepos, always pass `configPath`.
- For production-facing MCP setups, install with `--readonly` to hide `deploy`, `trigger_task`, and `cancel_run`.
- Before a TRQL `query`, always call `get_query_schema(table)` — it's cached server-side since v4.4.4, so there's no penalty.
- Respect the query 10k-row cap — add `LIMIT` and time filters.
- For Managed Prompts, prefer `promote_prompt_version` over long-lived overrides when iteration should flow through code; use overrides for hotfixes.

## Deeper Reference

- @references/mcp-tools-reference.md — complete parameter documentation + REST API
- Sibling skills: **observability** (TRQL + dashboards), **managed-prompts** (prompt versioning workflow)
