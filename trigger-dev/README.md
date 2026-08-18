# trigger-dev (Devin plugin)

Trigger.dev dev plugin for Agents Store. Comprehensive development knowledge for building background tasks, AI agent workflows, and durable execution on self-hosted Trigger.dev v4.4.4 — SDK patterns, CLI recipes, deployment, full 33-tool MCP reference, TRQL queries and dashboards, managed prompts, dev-server control, realtime API, and troubleshooting.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (12)

- `ai-agent-patterns` — Build AI agent workflows on Trigger.dev — prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, and human-in-the-loop. Use when the user asks to "build an AI agent with trigger.dev", "chain LLM calls", "parallelize AI tasks", "create an orchestrator", "add human approval to workflow", or needs patterns for LLM-powered durable execution.
- `cli-recipes` — Trigger.dev CLI commands for development, deployment, MCP setup, and project management. Use when the user asks about "trigger.dev CLI", "npx trigger.dev", "trigger.dev dev server", "trigger.dev deploy command", "trigger.dev mcp install", "trigger.dev profiles", or needs ready-to-use CLI commands.
- `config-and-build` — Configure Trigger.dev projects with trigger.config.ts, add build extensions for Prisma, Playwright, FFmpeg, Python, or customize deployment settings. Use when the user asks to "configure trigger.config.ts", "add Prisma to trigger.dev", "set up build extensions", "add FFmpeg to tasks", "configure Python in trigger.dev", or needs to customize project configuration.
- `deployment` — Deploy Trigger.dev tasks to staging, production, or preview environments. Use when the user asks to "deploy trigger.dev tasks", "set up CI/CD for trigger.dev", "deploy to production", "deploy self-hosted trigger", "manage environments", or needs deployment workflows and self-hosted infrastructure guidance.
- `examples` — Trigger.dev code examples, end-to-end workflow templates, MCP tool usage patterns, and scenario walkthroughs. Use when the user asks for "trigger.dev examples", "task templates", "MCP tool patterns", "trigger.dev workflow examples", or needs reference implementations.
- `managed-prompts` — Version and override Trigger.dev managed prompts via MCP — list, inspect, promote code versions, create dashboard overrides, hotfix, and revert. Use when the user asks about "trigger.dev prompt", "managed prompts", "prompt version", "prompt override", "hotfix prompt", "promote prompt version", "list prompts", or "revert prompt override".
- `mcp-patterns` — Trigger.dev MCP tools reference — all 33 tools, parameters, usage patterns, and common workflows as of v4.4.4. Use when the user asks about "trigger.dev MCP tools", "which trigger.dev tools are available", "how to use trigger.dev MCP", "trigger task via MCP", "list runs MCP", "profile switching", "TRQL queries from MCP", "dev server control", or "managed prompts overrides".
- `observability` — Query Trigger.dev data with TRQL, build dashboards, and inspect automatically-tracked LLM metrics. Use when the user asks about "trigger.dev query", "TRQL", "trigger.dev dashboards", "LLM metrics", "llm_metrics table", "how many runs failed this week", "cost per task", "query runs table", "span details", or "metrics table".
- `realtime` — Subscribe to Trigger.dev task runs in real-time from frontend and backend. Use when the user asks to "show task progress in UI", "stream AI responses", "use trigger.dev React hooks", "subscribe to runs", "build a progress indicator", "use useRealtimeRun", or needs live task status in a React application.
- `setup` — Set up Trigger.dev in a project, connect to a self-hosted instance, verify MCP connection, authenticate the CLI, or configure dev/staging/production environments. Use when the user asks to "set up trigger.dev", "init trigger project", "connect to self-hosted trigger", "verify trigger connection", "install trigger.dev", or "configure trigger environments".
- `task-development` — Write Trigger.dev tasks, configure retries, queues, concurrency, waits, metadata, tags, debouncing, idempotency, and use the @trigger.dev/sdk. Use when the user asks to "write a trigger.dev task", "create a background job", "add retries to task", "set up a task queue", "use triggerAndWait", "schedule a cron job", or needs SDK code patterns for Trigger.dev.
- `troubleshoot` — Diagnose and fix Trigger.dev errors, failed runs, deployment issues, and self-hosted problems. Use when the user encounters "trigger.dev not working", "task keeps failing", "deploy failed", "runs stuck", "self-hosted issues", "trigger.dev connection error", or needs to debug Trigger.dev v4.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 4 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/trigger-dev
