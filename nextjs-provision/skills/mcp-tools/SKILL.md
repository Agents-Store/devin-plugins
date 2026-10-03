---
name: mcp-tools
description: >
  Set up and use the official shadcn MCP server for AI-assisted component discovery and installation. This skill
  should be used when the user asks about "shadcn MCP", "shadcn MCP server", "set up shadcn MCP for Claude",
  "component MCP tools", "shadcn mcp init", "Jpisnice shadcn MCP", "shadcn-ui-mcp-server", "AI component
  installation", or needs to configure MCP for shadcn/ui component work.
---

One MCP server enables AI-assisted shadcn/ui component discovery and installation: the **official shadcn MCP**, built into the shadcn CLI (`npx shadcn@latest mcp`). This plugin's `.mcp.json` declares exactly that server.

## Official shadcn MCP

### Through this plugin

With the plugin enabled, Claude Code starts the server itself (`npx shadcn@latest mcp`). Its tools are named `mcp__plugin_nextjs-provision_shadcn__<tool>`. The server reads the project's `components.json`, so run the `setup` skill first in a project that has none.

### In a user project (without the plugin)

```bash
pnpm dlx shadcn@latest mcp init --client claude
```

This generates the MCP configuration for Claude Code automatically. Supported `--client` values: `claude`, `cursor`, `vscode`, `codex`, `opencode`:

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

Or write the server into the project's `.mcp.json` yourself — see `component-search/references/mcp-config-template.json`:

```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

### Tools

The server exposes seven tools (shadcn 4.21.1):

| Tool | Description |
|------|-------------|
| `get_project_registries` | List the registries configured in `components.json` (requires that file — `init` creates it) |
| `list_items_in_registries` | Page through items of the given registries; filter with `types` (`ui`, `block`, `component`, `hook`, `page`, `theme`, `style`, `base`, `font`, ...), `limit`, `offset` |
| `search_items_in_registries` | Fuzzy search by name/description across the given or all configured registries |
| `view_items_in_registries` | Item details and file contents; items are written `@registry/item` |
| `get_item_examples_from_registries` | Usage examples and demos with full code (`accordion-demo`, `example-booking-form`, ...) |
| `get_add_command_for_items` | The `npx shadcn@latest add ...` command for a list of `@registry/item` addresses |
| `get_audit_checklist` | Checklist to run after adding components or generating code |

Registry and component search work across **every registry configured in `components.json`**, including shadcn studio (`@ss-*`) and any community registry you added.

### Known quirks (shadcn 4.21.1)

- `search_items_in_registries` prints `Add command: [object Promise]` for every hit. Do not copy it — build the command (`npx shadcn@latest add @registry/item`) or call `get_add_command_for_items`.
- A registry that is not listed in `components.json` returns `NOT_CONFIGURED` from the MCP tools (for example `@magicui` in a project with `"registries": {}`), although the CLI itself resolves `@registry/item` for any directory entry. Configure it first with `/add-registries` or `npx shadcn registry add`.

## The community server is no longer shipped

Earlier versions of this plugin also declared `@jpisnice/shadcn-ui-mcp-server`. It was removed in 1.3.0: its `get_component` returns the Radix variant (`asChild`, `Slot`) even with `--ui-library base`, `get_component_metadata` answers "Component metadata not found" for common components such as `button` and `accordion`, and its `list_components` lists outdated `form` / `sonner` entries. Use the official tools above, or the CLI:

| Need | Use |
|------|-----|
| Component source for your project's base | `npx shadcn@latest view @shadcn/button` or `view_items_in_registries` |
| Usage docs, API and examples | `npx shadcn@latest docs button` |
| Demo code | `get_item_examples_from_registries` |
| Themes and presets | `npx shadcn@latest apply <preset>`, https://ui.shadcn.com/create (see `theme-configuration`) |

## Workflow: AI-Assisted Component Installation

```
1. User describes UI need ("I need a login form")
     ↓
2. AI uses search_items_in_registries / list_items_in_registries to find components and blocks
     ↓
3. AI uses view_items_in_registries / get_item_examples_from_registries to review options and dependencies
     ↓
4. AI gets the command from get_add_command_for_items (npx shadcn@latest add ...)
     ↓
5. User runs the command (or AI runs it via Bash, `--dry-run` first)
     ↓
6. AI customizes the installed component, then runs get_audit_checklist
```

## Multi-Registry Search with MCP

The official MCP only searches registries listed in `components.json`. To search the community directory:

1. Add registries to `components.json` (`/add-registries` fetches the directory, skips `unavailable` and hidden entries, and merges the rest; see the `component-search` skill)
2. Or add a handful with `npx shadcn registry add @name=https://domain.com/r/{name}.json`

Registries can also be declared in `package.json#registries` (CLI 4.18+; merged with `components.json`).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| MCP server not connecting | Check `/mcp` or `claude mcp list`; the server is started with `npx shadcn@latest mcp` — run that command once by hand to see errors |
| `NOT_CONFIGURED` for a registry | Add the registry to `components.json` (see above) |
| Empty `get_project_registries` | No `components.json` or no `registries` in it yet — run `npx shadcn@latest init`, or add registries |

## What This Skill Does NOT Cover

- General Next.js MCP devtools -- see `nextjs-dev` plugin's `mcp-tools` skill
- Component installation details -- see `component-registry` skill
- shadcn/ui initialization -- see `setup` skill
- Community registry search and catalog -- see `component-search` skill
