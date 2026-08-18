---
name: mcp-tools
description: >
  Set up and use shadcn MCP servers for AI-assisted component discovery and installation. This skill should
  be used when the user asks about "shadcn MCP", "shadcn MCP server", "set up shadcn MCP for Claude",
  "component MCP tools", "Jpisnice shadcn MCP", "shadcn-ui-mcp-server", "AI component installation",
  or needs to configure MCP servers for shadcn/ui component work.
---

Two MCP servers enable AI-assisted shadcn/ui component discovery and installation: the official shadcn MCP and the Jpisnice community MCP server.

## Official shadcn MCP

The official MCP is built into the shadcn CLI (v3.0+, current v4).

### Setup

```bash
pnpm dlx shadcn@latest mcp init --client claude
```

This generates the MCP configuration for Claude Code automatically. For other clients:

```bash
# Cursor
pnpm dlx shadcn@latest mcp init --client cursor

# VS Code
pnpm dlx shadcn@latest mcp init --client vscode

# Codex
pnpm dlx shadcn@latest mcp init --client codex

# opencode
pnpm dlx shadcn@latest mcp init --client opencode
```

### What It Enables

- Component resolution from any shadcn-compatible registry
- Theme management and preview
- Component search and installation
- Works with custom registries configured in `components.json`

## Jpisnice Community MCP Server

The `@jpisnice/shadcn-ui-mcp-server` (v2.0.0) provides more granular tools for component discovery.

### Setup for Claude Code

```bash
claude mcp add shadcn -- bunx -y @jpisnice/shadcn-ui-mcp-server
```

With a GitHub token for higher API rate limits (5000/hour vs 60/hour):

```bash
claude mcp add shadcn -- bunx -y @jpisnice/shadcn-ui-mcp-server --github-api-key ghp_YOUR_TOKEN
```

### Setup for Other Editors

Add to the project's `.mcp.json` or editor settings:

```json
{
  "mcpServers": {
    "shadcn": {
      "command": "bunx",
      "args": ["-y", "@jpisnice/shadcn-ui-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN"
      }
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `list_components` | Browse all available components in the registry |
| `get_component` | Get the source code for a component |
| `get_component_demo` | Get usage examples/demo code for a component |
| `get_component_metadata` | Get dependencies and metadata for a component |
| `list_blocks` | Browse pre-built templates (dashboards, forms, etc.) |
| `get_block` | Get source code for a block implementation |
| `get_directory_structure` | Browse the shadcn/ui repository structure |
| `list_themes` | Browse available tweakcn themes |
| `get_theme` | Get CSS variables and config for a tweakcn theme |
| `apply_theme` | Write a tweakcn theme's CSS/config files into the project (creates a backup; supports `dryRun`) |

The server has **no component-install tools** — component installation happens via the shadcn CLI (`npx shadcn@latest add ...`) after discovery. Note that `apply_theme` does write files: it applies tweakcn theme CSS/config to the project (use `dryRun` to preview).

### Framework Selection

The Jpisnice server supports multiple frameworks:

```bash
# React (default)
bunx -y @jpisnice/shadcn-ui-mcp-server

# Svelte
bunx -y @jpisnice/shadcn-ui-mcp-server --framework svelte

# Vue
bunx -y @jpisnice/shadcn-ui-mcp-server --framework vue

# React Native
bunx -y @jpisnice/shadcn-ui-mcp-server --framework react-native
```

### React UI Library Selection

For React, choose between Radix UI (default) or Base UI primitives:

```bash
bunx -y @jpisnice/shadcn-ui-mcp-server --ui-library base
```

### Transport Modes

Transport is selected with the `--mode` and `--port` flags (the `MCP_TRANSPORT_MODE`/`MCP_PORT` env vars still work):

| Mode | Use Case | Command |
|------|----------|---------|
| stdio (default) | CLI, Claude Code | `bunx -y @jpisnice/shadcn-ui-mcp-server` |
| SSE | HTTP-based clients, remote servers | `--mode sse --port 7423` |
| dual | Both stdio and SSE simultaneously | `--mode dual` |

SSE mode configuration and client attach:

```bash
bunx -y @jpisnice/shadcn-ui-mcp-server --mode sse --port 7423

# Attach Claude Code to the running SSE server:
claude mcp add --scope user --transport sse shadcn-mcp-server http://localhost:7423/sse
```

## Which MCP Server to Use

| Scenario | Recommendation |
|----------|----------------|
| Quick setup, standard shadcn/ui | Official MCP |
| Detailed component exploration | Jpisnice MCP |
| Custom/private registries | Official MCP |
| Multi-framework projects | Jpisnice MCP |
| shadcn studio premium components | Official MCP (works with the namespaced registries in components.json) |
| Multi-registry search (260+ registries) | Both (Official reads components.json registries; Jpisnice searches GitHub) |

Both servers can coexist. The official MCP integrates with `components.json` registries (including shadcn studio), while the Jpisnice server provides richer browsing tools from GitHub source.

## Workflow: AI-Assisted Component Installation

```
1. User describes UI need ("I need a login form")
     ↓
2. AI uses list_components/list_blocks to find relevant components
     ↓
3. AI uses get_component/get_component_demo/get_component_metadata to review options and dependencies
     ↓
4. AI composes the CLI command (npx shadcn@latest add ...)
     ↓
5. User runs the command (or AI runs via Bash)
     ↓
6. AI customizes the installed component for the user's needs
```

## Multi-Registry Search with MCP

When community registries are configured in `components.json`, the official shadcn MCP automatically discovers and searches them. This enables a combined workflow:

1. **Official MCP** resolves components from all configured registries (standard shadcn/ui + shadcn studio + 260+ community registries)
2. **Jpisnice MCP** provides deeper GitHub-based search across the shadcn ecosystem — component source code, demos, and block implementations

### Recommended Dual Setup for User Projects

```bash
# Official MCP (reads registries from components.json)
pnpm dlx shadcn@latest mcp init --client claude

# Community MCP (GitHub-based search, richer browsing)
claude mcp add shadcn-community -- npx -y @jpisnice/shadcn-ui-mcp-server
```

For a ready-to-use `.mcp.json` template with both servers, see the `component-search` skill's `references/mcp-config-template.json`.

### Adding Community Registries for MCP Search

The official MCP only searches registries listed in `components.json`. To unlock search across 260+ community registries:

1. Add registries to `components.json` (see `component-search` skill for the full list)
2. Or use the `/setup-registries --all` command to add all registries at once

## Rate Limiting

The Jpisnice MCP server uses GitHub's public API. Without a token, you get 60 requests/hour. With a GitHub Personal Access Token, you get 5000 requests/hour.

To create a token:
1. Go to GitHub Settings > Developer settings > Personal access tokens > Fine-grained tokens
2. Create a token with no special permissions (public repo access only)
3. Pass it via `--github-api-key` flag or `GITHUB_PERSONAL_ACCESS_TOKEN` env var

## What This Skill Does NOT Cover

- General Next.js MCP devtools -- see `nextjs-dev` plugin's `mcp-tools` skill
- Component installation details -- see `component-registry` skill
- shadcn/ui initialization -- see `setup` skill
- Community registry search and catalog -- see `component-search` skill
