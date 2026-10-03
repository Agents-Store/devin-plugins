---
name: component-search
description: >
  Search and install UI components from the 400+ registries in the official shadcn directory. This skill should be used when
  the user asks to "search for shadcn components", "find a calendar component", "browse community registries",
  "install from magicui", "what shadcn registries are available", "add animated components", "search for a
  date picker", "find UI blocks for landing page", "install from aceternity", "what community components
  exist", or needs to discover and install components from community registries beyond the standard shadcn/ui
  and shadcn studio registries.
---

## How Community Registries Work

shadcn v4 supports custom registries via the `"registries"` field in `components.json`. Any registry that implements the shadcn registry protocol can be added. The official registry directory at `https://ui.shadcn.com/r/registries.json` held 418 registries on 2026-10-02 (380 not hidden; 326 healthy, 41 degraded, 39 unavailable, 12 observing) — always fetch it instead of trusting a number.

The CLI can install from any registry without configuration:

```bash
npx shadcn@latest add @magicui/shimmer-button
```

The CLI also installs straight from public GitHub repos — no build step, just a `registry.json` at the repo root:

```bash
npx shadcn@latest add <user>/<repo>/<item>
```

GitHub registries work with `list`, `search`, `view`, and `add`, and — since CLI 4.19 — also with **private** repositories: if the repo is not publicly readable the CLI reads it through `gh` (`gh auth login`, nothing else to configure), or through `GH_TOKEN` / `GITHUB_TOKEN` where `gh` is not installed (use a fine-grained token with read-only Contents access). Public repos are always tried anonymously first. Registries additionally support server-side dynamic search (`GET /r/registry.json?q=&limit=&offset=`), which powers `shadcn search`.

Registries can be declared in `components.json` or, since CLI 4.18, in `package.json#registries` (the two are merged).

The **official shadcn MCP server** only searches registries listed in the project's `components.json`. To enable MCP-assisted search across the directory, populate them from the official endpoint.

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
- `health` — `status` (`healthy` | `degraded` | `unavailable` | `observing`), `hidden`, `score`, `statusReason`, availability figures
- `ranking` — `score` and `itemCount` (missing for registries that are not ranked yet)

Always fetch this endpoint instead of using a hardcoded list — it's maintained by the shadcn team and always current.

**Filter by health before recommending or bulk-adding.** Skip `health.status == "unavailable"` and `health.hidden == true` (39 entries on 2026-10-02: all `unavailable`, 38 of them hidden — they would not install). Say so when you recommend a `degraded` registry (e.g. sampled items failing validation); prefer `healthy` ones with a high `ranking.score`:

```bash
curl -s https://ui.shadcn.com/r/registries.json | python3 -c '
import json, sys
for r in json.load(sys.stdin):
    h = r.get("health", {})
    if h.get("status") in ("healthy", "observing") and not h.get("hidden"):
        print(r["name"], r["url"])'
```

## Search Workflow

```
1. User describes what they need ("animated button", "pricing section", "chat component")
     ↓
2. Fetch https://ui.shadcn.com/r/registries.json — scan descriptions for matches
     ↓
3. Consult references/community-registries.md for category-based recommendations
     ↓
4. Check user's components.json — are registries configured?
   If not → run /add-registries to populate the available registries
   (the CLI can already install @registry/item for any directory entry
   without it — the bulk step only matters for MCP search)
     ↓
5. Use MCP tools to search, or install directly via CLI
     ↓
6. Install: npx shadcn@latest add @[registry]/[component]
     ↓
7. Verify the component renders correctly
```

## Adding Registries to components.json

### Add all registries (recommended)

Use the `/add-registries` command to fetch the registries from the official endpoint, skip the `unavailable` and hidden ones, and add the rest to `components.json` automatically.

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
       "@aceternity": "https://ui.aceternity.com/registry/{name}.json"
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

This plugin's `.mcp.json` declares one MCP server: the official `shadcn` server (`npx shadcn@latest mcp`). It searches the registries listed in the project's `components.json` — add community registries there to expand its scope. Through this plugin its tools are named `mcp__plugin_nextjs-provision_shadcn__<tool>`:

| Tool | Use |
|------|-----|
| `get_project_registries` | Which registries `components.json` configures |
| `search_items_in_registries` | Fuzzy search across (selected) registries |
| `list_items_in_registries` | Page through a registry's items (`types`, `limit`, `offset`) |
| `view_items_in_registries` | Item details and file contents — `@registry/item` |
| `get_item_examples_from_registries` | Demos and usage code (`calendar-demo`, `example-hero`, ...) |
| `get_add_command_for_items` | The `npx shadcn@latest add ...` command for given `@registry/item` addresses |
| `get_audit_checklist` | Post-install checklist after adding components |

Known quirks (shadcn 4.21.1): `search_items_in_registries` prints `Add command: [object Promise]` — build the command yourself (`npx shadcn@latest add @registry/item`) or call `get_add_command_for_items`. A registry that is not in `components.json` (for example `@magicui` in a fresh project) returns `NOT_CONFIGURED` from the MCP even though the CLI installs from it — configure it first (`/add-registries` or `npx shadcn registry add`).

The community MCP server `@jpisnice/shadcn-ui-mcp-server` is no longer shipped with this plugin: its `get_component` returns the Radix variant even with `--ui-library base`, and `get_component_metadata` answers "not found" for common components. For component source and demos use `npx shadcn@latest view @registry/item`, `npx shadcn@latest docs <component>`, or the tools above.

Without the MCP, the CLI covers the same ground: `npx shadcn@latest search @registry -q "<term>"`, `npx shadcn@latest view @registry/item`, `npx shadcn@latest add @registry/item --dry-run`.

To use the server in a user project (not through this plugin), run `npx shadcn@latest mcp init --client claude` — see the `mcp-tools` skill, and `references/mcp-config-template.json` for a ready `.mcp.json`.

## Registry Categories

| Category | Registries | Component Types |
|----------|-----------|-----------------|
| Animation & Motion | @magicui, @aceternity (degraded), @animate-ui, @cult-ui, @motion-primitives | Animated buttons, scroll effects, parallax, globe, beams |
| Extended UI | @coss (ex-Origin UI), @diceui, @basecn, @8bitcn, @boldkit, @8starlabs-ui, @cardcn | Extra components, retro/pixel style, card variants, dice rolls |
| Blocks & Sections | @bundui, @blocks-so, @efferd (degraded) | Landing page sections, marketing blocks, dashboards |
| E-Commerce | @commercn | Product cards, cart, checkout, reviews |
| AI Components | @ai-elements, @assistant-ui, @tool-ui | Chat bubbles, prompt inputs, AI response streams, LLM UIs |
| File Upload | @better-upload | Upload components, drag-and-drop, progress indicators |
| Editors & misc | @plate, @shadcn-editor, @kibo-ui, @kokonutui, @reui, @intentui, @tailark (degraded), @retroui, @smoothui, @skiper-ui, @paceui (degraded), @clerk, @supabase | Rich text editors, design-system kits, auth/backend UIs |
| Other | @arc, @abui (degraded), @aevr, @unlumen-ui (degraded), @einui, @billingsdk | Specialized UI, billing forms, misc |

Also `degraded` on 2026-10-02: @shadcnblocks. `unavailable` (do not recommend): @chamaac, @doras-ui, @creative-tim, @ai-blocks, @hextaui, @neobrutalism. Re-check `health` in the live directory before relying on this table.

See `references/community-registries.md` for the full list with URLs and descriptions.

Full directory (418 registries on 2026-10-02): https://ui.shadcn.com/docs/directory

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
