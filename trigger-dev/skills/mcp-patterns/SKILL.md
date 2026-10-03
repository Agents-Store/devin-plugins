---
name: mcp-patterns
description: Trigger.dev MCP tools reference — all 41 tools, parameters, usage patterns, and common workflows (CLI 4.7.x). Use when the user asks about "trigger.dev MCP tools", "which trigger.dev tools are available", "how to use trigger.dev MCP", "trigger task via MCP", "list runs MCP", "profile switching", "TRQL queries from MCP", "dev server control", "agent chat via MCP", "mcp readonly", or "managed prompts overrides".
---

# Trigger.dev MCP Tool Patterns

Reference for every MCP tool provided by the official Trigger.dev MCP server (41 tools across 13 categories as of CLI 4.7.2). The set of tools is decided by the version of the `trigger.dev` CLI that runs the server, not by the Trigger.dev instance behind it; a self-hosted 4.4.4 server answers fewer of them usefully (see the notes marked "requires server" below).

> **Note:** This plugin provides MCP **knowledge**, not the MCP connection. The plugin ships no `.mcp.json`; the MCP server is configured by the user (`npx trigger.dev@latest install-mcp`, or by hand), so tool names are the bare `mcp__<server>__<tool>` form, where `<server>` is the name chosen in the user's MCP config (for example `trigger-dev` gives `mcp__trigger-dev__trigger_task`).

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
| `--scope <scope>` | `user`, `project` or `local` config file (support differs per client) |
| `--dev-only` | Restrict to the dev environment: `deploy`, `list_deploys`, `list_preview_branches` and every non-dev `environment` argument return an error |
| `--project-ref <ref>` | Scope MCP to a single project (proj_xxx) |
| `--tag <tag>` | Pin the CLI package version the MCP server runs |
| `-a, --api-url <url>` | Self-hosted API URL |
| `--log-file <path>` | Write MCP server logs to file |
| `--log-level <level>` | debug / info / log / warn / error / none |
| `--yolo` | Install into every supported client |

`install-mcp` has no read-only flag. Read-only mode belongs to the server command, see below.

### Manual Config Examples

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

Read-only (production-facing agents):

```json
{
  "mcpServers": {
    "trigger": {
      "command": "npx",
      "args": ["trigger.dev@latest", "mcp", "--readonly"]
    }
  }
}
```

`--readonly` is a flag of `trigger.dev mcp` only (the docs page for `install-mcp` attributes it to the installer, which rejects it). It hides 15 write tools server-side, so the model never sees them: `deploy`, `trigger_task`, `cancel_run`, `create_project_in_org`, `initialize_project`, the five prompt writers (`promote_prompt_version`, `create_prompt_override`, `update_prompt_override`, `remove_prompt_override`, `reactivate_prompt_override`), `start_agent_chat`, `send_agent_message`, `close_agent_chat`, `write_session_channel` and `submit_feedback`. It does **not** hide `start_dev_server`, `stop_dev_server` or `switch_profile`.

> **Tool annotations:** every tool carries `readOnlyHint` / `destructiveHint` metadata (write tools are `destructiveHint`) so MCP clients can gate write operations. `--readonly` enforces it server-side.

## Shared Parameters

Most tools accept these optional parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `projectRef` | Project ref (proj_xxx) | Auto-detected from trigger.config.ts |
| `configPath` | Path to trigger.config.ts | Auto |
| `environment` | dev, staging, prod, preview | dev (`prod` for `deploy` / `list_deploys`) |
| `branch` | Branch name (preview environments and branchable dev) | — |

## Documentation & Search

| Tool | Description |
|------|-------------|
| `search_docs` | Search Trigger.dev documentation |

## Feedback

| Tool | Description |
|------|-------------|
| `submit_feedback` | Report an MCP/SDK/docs problem to the Trigger.dev team. Write tool; hidden by `--readonly` and when telemetry is disabled. Never include secrets or user data, and tell the user what was sent |

## Project & Organization

| Tool | Description |
|------|-------------|
| `list_orgs` | List your organizations |
| `list_projects` | List your projects |
| `create_project_in_org` | Create a new project in an org (write) |
| `initialize_project` | Create/choose a project and return the manual-setup guide with its ref and dev key (write; writes no files) |

## Task Management

| Tool | Description |
|------|-------------|
| `get_current_worker` | Worker version, SDK version and registered task slugs (agents are marked `[agent]`). No payload schemas |
| `get_task_schema` | Payload schema for one task; parameter is `taskSlug` |
| `trigger_task` | Trigger a task with payload and options, including `region` (write) |

## Run Monitoring

| Tool | Description |
|------|-------------|
| `list_runs` | List and filter runs by status, task, tag, version, machine, region, period |
| `get_run_details` | Run details and trace — **trace is paginated**: `maxTraceLines` (default 200) and `cursor` |
| `get_span_details` | Inspect a single span inside a run — attributes, events, AI enrichment (model, tokens, cost), child runs. Span IDs appear in `get_run_details` output |
| `wait_for_run_to_complete` | Wait for a run to finish (`timeoutInSeconds`, default 60) |
| `cancel_run` | Cancel a running/queued run (write) |

## Deployment

| Tool | Description |
|------|-------------|
| `deploy` | Deploy to staging/prod/preview (write); `skipPromotion`, `skipSyncEnvVars`, `skipUpdateCheck` |
| `list_deploys` | List deployments with filters (not available with `--dev-only`) |
| `list_preview_branches` | List preview branches (not available with `--dev-only`) |

## Profile

| Tool | Description |
|------|-------------|
| `whoami` | Show current profile, user, and API URL |
| `list_profiles` | List all configured CLI profiles and the active one |
| `switch_profile` | Change the active profile for this MCP session (affects all subsequent tool calls) |

## Query & Analytics

Powered by TRQL (Trigger.dev Query Language — SQL over ClickHouse). See the **observability** skill for TRQL syntax and examples. On self-hosted, TRQL, dashboards and metrics need the bundled ClickHouse.

| Tool | Description |
|------|-------------|
| `get_query_schema` | Columns, types, and descriptions for one TRQL table (`table` is required: `runs`, `metrics`, or `llm_metrics`) |
| `query` | Execute a TRQL query (`query`, `scope`, `period` or `from`+`to`). Results returned as text tables; no `format` parameter |
| `list_dashboards` | List built-in dashboards (by key) and their widget IDs |
| `run_dashboard_query` | Execute a single widget query: `dashboardKey` + `widgetId` + `period` / `from` / `to` / `scope` |

## Reports

| Tool | Description |
|------|-------------|
| `get_report` | Interpreted health report (`key: "health"`) with verdict and sparklines: is work flowing, is it your code, is telemetry fresh. Same as `trigger report health` |

## Dev Server

| Tool | Description |
|------|-------------|
| `start_dev_server` | Start `trigger dev` in the background (waits up to 30s for the worker to be ready) |
| `stop_dev_server` | Stop the running dev server |
| `dev_server_status` | Show status (`stopped` / `starting` / `ready` / `error`) and recent log lines (`lines` default 50) |

## Managed Prompts

Trigger.dev Managed Prompts — versioned prompts with dashboard overrides. Declaring prompts in code (`prompts.define()`) requires SDK and server ≥ 4.5.0. See the **managed-prompts** skill for the full workflow.

| Tool | Description |
|------|-------------|
| `list_prompts` | List managed prompts — slug, current version, override status, version count |
| `get_prompt_versions` | List versions for one prompt — labels (`current`/`override`/`latest`), source (`code`/`dashboard`), model, content |
| `promote_prompt_version` | Promote a code-sourced version to current (dashboard overrides use override tools) |
| `create_prompt_override` | Create a dashboard override (takes precedence over the current code version) |
| `update_prompt_override` | Update the active dashboard override |
| `remove_prompt_override` | Remove the override — revert to the current code version |
| `reactivate_prompt_override` | Reactivate a prior dashboard-sourced version as the active override |

## Agent Chat

Chat with `chat.agent()` tasks (requires server ≥ 4.5.0; see the **ai-chat-agents** skill for the agents). Chats live in the MCP server process.

| Tool | Description |
|------|-------------|
| `list_agents` | List the chat agents of the current worker |
| `start_agent_chat` | Start a conversation: `agentId`, optional `chatId` (reuse to resume), `clientData`, `preload` (write) |
| `send_agent_message` | Send a message, get the agent's full response text back (write) |
| `close_agent_chat` | Close the conversation; the agent exits gracefully (write) |

## Session Channels

Raw access to a session's realtime streams (requires server ≥ 4.5.0).

| Tool | Description |
|------|-------------|
| `read_session_channel` | Read records from a named side channel (or the chat transcript when `channel` is omitted); `io` `out`/`in`, `afterEventId` cursor, `timeoutInSeconds` for a bounded tail |
| `write_session_channel` | Append one record to a channel's `in` stream to send control input to a running agent without triggering a run (write) |

## Common Patterns

### Trigger and Monitor

```
1. get_current_worker(environment="dev") → task slugs
2. get_task_schema(taskSlug="process-order") → payload schema
3. trigger_task(taskId, payload) → run ID
4. wait_for_run_to_complete(runId) → result
```

### Debug a Failed Run with AI Enrichment

```
1. list_runs(status="FAILED", period="1d")
2. get_run_details(runId) → error trace + span IDs (call again with `cursor` for more trace)
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
2. initialize_project(orgParam, projectName, cwd) → setup guide with project ref and dev key
3. Follow the guide (install the SDK, create trigger.config.ts with `maxDuration`, add a task)
4. get_current_worker(environment="dev") → verify
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
1. list_dashboards() → dashboards by key (overview, llm, ...) with widget IDs
2. run_dashboard_query(dashboardKey, widgetId, period="30d") → widget data
```

### Health Check

```
get_report(key="health", environment="prod", period="24h") → verdict + next action
```

### Chat With a Chat Agent

```
1. list_agents() → agent slugs
2. start_agent_chat(agentId="support-chat", clientData={ ... }) → chatId
3. send_agent_message(chatId, "message") → response text
4. close_agent_chat(chatId)
```

### Switch Profile Mid-Session

```
1. whoami() → current profile + API URL
2. list_profiles() → available profiles
3. switch_profile("<profile-name>") → all subsequent tool calls use the new profile
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

- **Call `get_task_schema` before `trigger_task`** — `get_current_worker` returns slugs only.
- Use `limit` and `period` to avoid fetching too many runs.
- Use `idempotencyKey` in trigger options to prevent duplicate runs.
- Default to the dev environment for safety; switch explicitly with `switch_profile` or `environment=`.
- For monorepos, always pass `configPath`.
- For production-facing MCP setups, run the server with `mcp --readonly` (15 write tools hidden); add `--dev-only` when the agent must never touch other environments.
- Before a TRQL `query`, always call `get_query_schema(table)` — it's cached server-side, so there's no penalty.
- Respect the query 10k-row cap — add `LIMIT` and time filters.
- For Managed Prompts, prefer `promote_prompt_version` over long-lived overrides when iteration should flow through code; use overrides for hotfixes.
- Keep the SDK, CLI and server on one version: `deploy` runs the CLI that matches the project's installed SDK.

## Deeper Reference

- @references/mcp-tools-reference.md — complete parameter documentation for all 41 tools + REST API
- Sibling skills: **observability** (TRQL + dashboards), **managed-prompts** (prompt versioning workflow), **ai-chat-agents** (chat agents behind the agent-chat tools)
