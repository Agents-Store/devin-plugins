---
name: mcp-tools
description: Next.js DevTools MCP server tools and integration patterns. This skill should be used when the user asks about "next-devtools-mcp", "Next.js MCP tools", "MCP server for Next.js", "runtime diagnostics", "Next.js dev server MCP", or needs to set up or use the official Next.js MCP toolchain for AI-assisted development.
---

# Next.js DevTools MCP

`next-devtools-mcp` (current version 0.4.0) is Vercel's official MCP server for Next.js development. It is a **thin connector**: it discovers running Next.js 16+ dev servers and proxies their built-in MCP endpoint at `/_next/mcp`, plus provides two gateways — one to version-matched documentation, one to browser automation. As of 0.4.0 the server exposes exactly four tools: `nextjs_index`, `nextjs_call`, `nextjs_docs`, and `browser_eval`.

## Setup

Add to project `.mcp.json`:

```json
{
  "mcpServers": {
    "next-devtools": {
      "command": "npx",
      "args": ["-y", "next-devtools-mcp@latest"]
    }
  }
}
```

Or install via CLI:

```bash
# Universal (writes the right config for your detected client)
npx add-mcp next-devtools-mcp@latest

# Claude Code
claude mcp add next-devtools npx next-devtools-mcp@latest

# Cursor
# Go to Settings → MCP → New MCP Server

# VS Code
code --add-mcp '{"name":"next-devtools","command":"npx","args":["-y","next-devtools-mcp@latest"]}'
```

Requirements:
- Node.js v20.19+
- For runtime tools (`nextjs_index`, `nextjs_call`): Next.js 16+ with dev server running

> **Removed in 0.4.0:** the `init`, `upgrade_nextjs_16`, and `enable_cache_components` tools no longer exist. Upgrade and Cache Components workflows now live in the upgrade codemod (`npx @next/codemod@canary upgrade latest`, or the `next upgrade` command in 16.1+) and the migration guide at `/docs/app/guides/migrating-to-cache-components`.

## Tools Reference

### `nextjs_index`

Discover all running Next.js 16+ dev servers and list their available MCP tools.

No parameters required. Returns JSON with discovered servers (port, PID, URL) and available tools.

Typical runtime tools per server (the exact set varies by Next.js version):
- `get_errors` — Current build, runtime, and type errors
- `get_logs` — Path to development log file
- `get_page_metadata` — Route and component metadata
- `get_project_metadata` — Project structure and config
- `get_routes` — All filesystem routes grouped by router type (added in 16.1)
- `get_server_action_by_id` — Look up Server Actions by ID
- `get_compilation_issues` — Compilation issues from the bundler (16.3+, Turbopack only)
- `compile_route` — Compile a route on demand; accepts a route specifier like `/blog/[slug]` or a path like `/blog/hello` (16.3+, Turbopack only)

### `nextjs_call`

Execute a specific tool on a running Next.js dev server.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `port` | number | Yes | Dev server port (from `nextjs_index`) |
| `toolName` | string | Yes | Tool name to invoke |
| `args` | object | No | Arguments for the tool |

### `nextjs_docs`

A **gateway** to version-accurate Next.js documentation. It no longer takes search/get parameters — instead it points the agent at the docs bundled with the installed Next.js version at `node_modules/next/dist/docs/`, which the agent then reads directly as files.

Since Next.js 16.3, `next dev` also auto-writes a version-matched AGENTS.md block pointing at these bundled docs (see `/docs/app/guides/ai-agents`), so agents get correct documentation with zero setup.

### `browser_eval`

A **gateway** to the [`agent-browser`](https://github.com/vercel-labs/agent-browser) CLI. It is not a Playwright action proxy — instead of taking `start`/`navigate`/`click` actions, it tells the agent how to install and run the `agent-browser` CLI for browser automation.

Use for:
- Verifying pages after changes
- Detecting hydration errors visually
- Taking screenshots for comparison
- Capturing browser console errors

## Typical Workflow

1. **Start dev server** — `npm run dev`
2. **Discover servers** — Call `nextjs_index` to find running instances
3. **Check errors** — Call `nextjs_call` with `get_errors`
4. **Read docs** — Use the `nextjs_docs` gateway to locate the bundled docs, then read the files directly
5. **Verify changes** — Use the `browser_eval` gateway to drive `agent-browser` for screenshots and testing

## Architecture

```
Coding Agent
      ↓
  next-devtools-mcp
      ↓
      ├─→ Next.js Dev Server (/_next/mcp) — Runtime diagnostics
      ├─→ agent-browser CLI (gateway) — Browser automation
      └─→ node_modules/next/dist/docs/ (gateway) — Version-matched docs
```

The MCP server bridges the agent to three systems: the running Next.js app, the `agent-browser` CLI, and the documentation bundled with the installed Next.js version.

## Zero-Setup Docs Tip

Since Next.js 16.3, running `next dev` automatically maintains an AGENTS.md block in your project that points coding agents at the version-matched docs in `node_modules/next/dist/docs/`. No manual CLAUDE.md instructions are needed — the framework keeps agents aligned with the exact installed version.
