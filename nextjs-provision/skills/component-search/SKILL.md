---
name: component-search
description: >
  Search and install UI components from 260+ registries in the official shadcn directory. This skill should be used when
  the user asks to "search for shadcn components", "find a calendar component", "browse community registries",
  "install from magicui", "what shadcn registries are available", "add animated components", "search for a
  date picker", "find UI blocks for landing page", "install from aceternity", "what community components
  exist", or needs to discover and install components from community registries beyond the standard shadcn/ui
  and shadcn studio registries.
---

## How Community Registries Work

shadcn v4 supports custom registries via the `"registries"` field in `components.json`. Any registry that implements the shadcn registry protocol can be added. The official registry directory at `https://ui.shadcn.com/r/registries.json` contains 267 registries (Aug 2026) — always up to date.

The CLI can install from any registry without configuration:

```bash
npx shadcn@latest add @magicui/shimmer-button
```

The CLI also installs straight from public GitHub repos — no build step, just a `registry.json` at the repo root:

```bash
npx shadcn@latest add <user>/<repo>/<item>
```

GitHub registries work with `list`, `search`, `view`, and `add`. Registries additionally support server-side dynamic search (`?q=&limit=&offset=`), which powers `shadcn search`.

But the **official shadcn MCP server** only searches registries listed in `components.json`. To enable MCP-assisted search across all registries, populate them from the official endpoint.

## Dynamic Registry Source

The authoritative list of all shadcn-compatible registries:

```
https://ui.shadcn.com/r/registries.json
```

Returns a JSON array. Each entry has:
- `name` — Registry identifier (e.g., `"@magicui"`)
- `url` — Registry endpoint with `{name}` placeholder (e.g., `"https://magicui.design/r/{name}.json"`)
- `homepage` — Project website
- `description` — Brief description

Always fetch this endpoint instead of using a hardcoded list — it's maintained by the shadcn team and always current.

## Search Workflow

```
1. User describes what they need ("animated button", "pricing section", "chat component")
     ↓
2. Fetch https://ui.shadcn.com/r/registries.json — scan descriptions for matches
     ↓
3. Consult references/community-registries.md for category-based recommendations
     ↓
4. Check user's components.json — are registries configured?
   If not → run /add-registries to populate all registries
     ↓
5. Use MCP tools to search, or install directly via CLI
     ↓
6. Install: npx shadcn@latest add @[registry]/[component]
     ↓
7. Verify the component renders correctly
```

## Adding Registries to components.json

### Add all registries (recommended)

Use the `/add-registries` command to fetch all 260+ registries from the official endpoint and add them to `components.json` automatically.

### Add a handful natively

The CLI's native method (supersedes hand-editing):

```bash
npx shadcn registry add @magicui=https://magicui.design/r/{name} @coss=https://coss.com/ui/r/{name}.json
```

Registry authors can check their registry with `npx shadcn registry validate`.

Or manually:

1. Fetch the registry list:
   ```bash
   curl -s https://ui.shadcn.com/r/registries.json
   ```

2. For each entry, add to `components.json` `"registries"` field using the `name` as key and `url` as value:
   ```json
   {
     "registries": {
       "@magicui": "https://magicui.design/r/{name}.json",
       "@aceternity": "https://ui.aceternity.com/r/{name}.json"
     }
   }
   ```

3. Merge with existing registries — do not overwrite the `"registries"` object, add to it.

### Add a single registry

```json
{
  "registries": {
    "@registryname": "https://domain.com/r/{name}.json"
  }
}
```

## Installing from a Community Registry

```bash
# Install a single component
npx shadcn@latest add @magicui/shimmer-button

# Install multiple components from the same registry
npx shadcn@latest add @magicui/shimmer-button @magicui/animated-beam @magicui/globe

# Install from different registries in one command
npx shadcn@latest add @magicui/shimmer-button @aceternity/moving-border

# Force overwrite existing files
npx shadcn@latest add @magicui/shimmer-button --overwrite
```

The CLI auto-resolves registry URLs. Even without `components.json` configuration, the CLI can install from any known registry by name.

## MCP-Assisted Search

Two MCP servers are configured in this plugin's `.mcp.json`:

| Server | What It Searches | Best For |
|--------|-----------------|----------|
| `shadcn` (official) | All registries in `components.json` | Finding components across configured registries |
| `shadcn-community` (Jpisnice) | shadcn/ui GitHub repo via `list_components`, `get_component`, `get_component_demo`, `get_component_metadata`, `list_blocks`, `get_block`, `get_directory_structure`; plus tweakcn theme tools `list_themes`, `get_theme`, `apply_theme` (writes theme files, supports `dryRun`) | Browsing component source code, demos, block implementations; applying tweakcn themes |

### Dual search strategy

1. **Official MCP** searches all configured registries — add community registries to `components.json` to expand its scope
2. **Jpisnice MCP** searches the shadcn/ui GitHub repository for component source, demos, and blocks — useful for understanding how components work before installing

For projects that want both MCPs, copy the template from `references/mcp-config-template.json` to the project's `.mcp.json`.

### Jpisnice MCP rate limits

Without a GitHub token: 60 requests/hour. With a token: 5000/hour.

To add a token:

```bash
claude mcp add shadcn-community -- npx -y @jpisnice/shadcn-ui-mcp-server --github-api-key ghp_YOUR_TOKEN
```

Or set `GITHUB_PERSONAL_ACCESS_TOKEN` in the MCP server's env config. Create a fine-grained token with no special permissions (public repo access only).

## Registry Categories

| Category | Registries | Component Types |
|----------|-----------|-----------------|
| Animation & Motion | @magicui, @aceternity, @animate-ui, @cult-ui, @motion-primitives, @chamaac | Animated buttons, scroll effects, parallax, globe, beams |
| Extended UI | @coss (ex-Origin UI), @diceui, @basecn, @8bitcn, @boldkit, @8starlabs-ui, @cardcn | Extra components, retro/pixel style, card variants, dice rolls |
| Blocks & Sections | @bundui, @blocks-so, @efferd, @doras-ui, @creative-tim | Landing page sections, marketing blocks, dashboards |
| E-Commerce | @commercn | Product cards, cart, checkout, reviews |
| AI Components | @ai-elements, @assistant-ui, @tool-ui, @ai-blocks | Chat bubbles, prompt inputs, AI response streams, LLM UIs |
| File Upload | @better-upload | Upload components, drag-and-drop, progress indicators |
| Editors & misc | @plate, @shadcn-editor, @kibo-ui, @kokonutui, @reui, @intentui, @tailark, @retroui, @neobrutalism, @smoothui, @skiper-ui, @hextaui, @paceui, @clerk, @supabase | Rich text editors, design-system kits, auth/backend UIs |
| Other | @arc, @abui, @aevr, @unlumen-ui, @einui, @billingsdk | Specialized UI, billing forms, misc |

See `references/community-registries.md` for the full list with URLs and descriptions.

Full directory (267 registries): https://ui.shadcn.com/docs/directory

## CLAUDE.md Section for User Projects

When setting up a project with community registries, add the section from `references/claude-md-section.md` to the project's CLAUDE.md. This ensures Claude always searches registries before building components from scratch.

## Verifying a Registry Works

Test that a registry URL is correct by installing a known component:

```bash
# Install a component from the registry
npx shadcn@latest add @magicui/shimmer-button

# If the install succeeds, the registry URL is correct
# If it fails, check the registry's documentation for the correct URL pattern
```

The standard URL convention is `https://domain.com/r/{name}` but some registries may differ. The CLI auto-resolves known registry names — if `@registryname/component` works, the URL is valid.

## What This Skill Does NOT Cover

- Standard shadcn/ui and shadcn studio components — see `component-registry` skill
- Initial shadcn/ui project setup — see `setup` skill
- MCP server configuration details — see `mcp-tools` skill
- Theme customization — see `theme-configuration` skill
