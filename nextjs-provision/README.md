# nextjs-provision (Devin plugin)

Next.js provisioning plugin. Set up shadcn/ui and shadcn studio — component installation, theme configuration, MCP server setup, project scaffolding, and multi-registry component search across the 400+ registries of the official directory.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (8)

- `component-registry` — Install and use shadcn/ui and shadcn studio components with the shadcn CLI v4 — add, view, --dry-run and --diff, the @shadcn-studio and @ss-* registries, compositions that are not registry items such as form and date picker, and Base UI specifics like the render prop instead of asChild. Use when adding or composing components. Searching community registries is component-search.
- `component-search` — Search and install components from the 400+ registries in the official shadcn directory — community registries such as magicui or aceternity, registries.json with its health status, adding registries to components.json, private GitHub registries. Use when looking for a component beyond the standard shadcn/ui and shadcn studio registries.
- `examples` — End-to-end scenario walkthroughs for setting up Next.js projects with shadcn/ui and shadcn studio. This skill should be used when the user asks for "shadcn setup walkthrough", "how to set up a project with shadcn from scratch", "add shadcn to existing project example", "full shadcn setup guide", "shadcn studio tutorial", "step-by-step shadcn setup", or needs a complete example of provisioning a Next.js project with shadcn components.

- `mcp-tools` — Set up and use the official shadcn MCP server (npx shadcn@latest mcp) — mcp init per client for Claude Code, Cursor, VS Code, Codex and opencode, its seven tools, how items are addressed as @registry/item, and why the community shadcn-ui-mcp-server is no longer shipped. Use when configuring or using MCP for shadcn component work.
- `project-scaffolding` — Scaffold and organise Next.js projects that use shadcn/ui — init with templates and the base choice (Base UI or Radix), shadcn studio templates, folder structure for ui, blocks and features, components.json aliases, the cn helper in lib/utils, and Turborepo monorepos with a shared ui package. Use when starting a project or deciding where components live.
- `setup` — Set up shadcn/ui and shadcn studio in a Next.js project. This skill should be used when the user asks to "set up shadcn", "install shadcn/ui", "initialize shadcn", "configure shadcn studio", "add shadcn to my project", "set up component library", "init shadcn in next.js", or needs to initialize a Next.js project for shadcn/ui component development.

- `theme-configuration` — Theme shadcn/ui and shadcn studio projects — OKLCH CSS variables with @theme inline, light and dark variants, next-themes setup, next/font fonts, brand colors, style presets applied with shadcn apply, and installing shadcn studio themes. Use when changing colors, fonts or dark mode of a shadcn project.
- `troubleshoot` — Diagnose shadcn/ui and shadcn studio problems — components.json errors, Tailwind v3 or v4 mismatches, a missing cn helper after CLI 4.21, unstyled components or unset CSS variables, studio registry 401 or 403, dependency conflicts with React 19, hydration issues with next-themes. Use when an install, init or render fails.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 3 command(s) — Devin plugins do not support commands
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/nextjs-provision
