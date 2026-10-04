---
name: setup
description: >
  Set up shadcn/ui and shadcn studio in a Next.js project. This skill should be used when the user asks to
  "set up shadcn", "install shadcn/ui", "initialize shadcn", "configure shadcn studio", "add shadcn to my
  project", "set up component library", "init shadcn in next.js", or needs to initialize a Next.js project
  for shadcn/ui component development.
---

## Prerequisites Check

Before initializing shadcn/ui, verify the project meets these requirements:

| Requirement | Check | Minimum |
|-------------|-------|---------|
| Node.js | `node --version` | 20+ |
| Next.js | `package.json` → `next` | 13+ with App Router (15/16 recommended) |
| React | `package.json` → `react` | 18+ |
| TypeScript | `tsconfig.json` exists | Recommended |
| Tailwind CSS | `package.json` → `tailwindcss` | 3.x or 4.x |

If Tailwind CSS is not installed:

```bash
# For new projects, create-next-app includes Tailwind by default:
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir

# For existing projects without Tailwind:
npm install -D tailwindcss @tailwindcss/postcss postcss
```

## Step 1: Initialize shadcn/ui

Run the init command in the project root:

```bash
npx shadcn@latest init
```

The CLI v4 `init` command (alias `create`) supports:
- `-t next|start|vite|react-router|laravel|astro` -- project template
- `-b base|radix|aria` -- component base (**Base UI is the default since July 2026**; Radix and React Aria remain fully supported)
- `-p <preset>` -- style preset
- `-d` -- accept defaults (equivalent to `--template=next --preset=base-nova`)
- `-n <name>`, `-y` -- project name and skip prompts (`npx shadcn@latest init -t next -d -n my-app --no-monorepo -y` scaffolds and initializes a Next.js app non-interactively)
- `--css-variables` (default true), `--rtl`, `--pointer` (adds `cursor: pointer` CSS for buttons), `--monorepo`

Base colors are now **neutral | stone | zinc | mauve | olive | mist | taupe**. Visual styles are the 8 official presets — **Vega** (classic look), **Nova** (compact, default), **Maia** (rounded), **Lyra** (sharp/mono), **Mira** (dense), **Luma**, **Rhea**, **Sera** — chosen via preset or the visual builder at https://ui.shadcn.com/create (`npx shadcn create`). Apply a preset to an existing project with `shadcn apply <preset-code> [--only theme|font]` (`--only` re-applies just the theme or just the font). Inspect presets with `npx shadcn@latest preset decode <code>`, `preset resolve` (the preset of the current project), `preset url <code>` and `preset open <code>`.

This creates:
- `components.json` -- Configuration file for the shadcn CLI
- `lib/utils.ts` (or `src/lib/utils.ts`) -- the `cn()` class merge utility, a one-line re-export from the `cn` package (CLI 4.21+)
- Updates `globals.css` with CSS variables for the chosen theme (plus the `tailwindcss`, `tw-animate-css` and `shadcn/tailwind.css` imports)
- Installs dependencies: `cn`, `class-variance-authority`, `tw-animate-css`, `lucide-react` (or the chosen icon library) and the base package (`@base-ui/react`, or `radix-ui` for `-b radix`)

## Step 2: Verify Base Installation

Check these files exist and are correct:

1. **`components.json`** -- Should look like this (this is what CLI 4.21 writes for `init -d` on a Next.js app; the `style` value is `<base>-<preset>`: `base-nova` for Base UI, `radix-nova` for Radix). For Tailwind v4, `tailwind.config` is left blank:
   ```json
   {
     "$schema": "https://ui.shadcn.com/schema.json",
     "style": "base-nova",
     "rsc": true,
     "tsx": true,
     "tailwind": {
       "config": "",
       "css": "app/globals.css",
       "baseColor": "neutral",
       "cssVariables": true,
       "prefix": ""
     },
     "iconLibrary": "lucide",
     "rtl": false,
     "aliases": {
       "components": "@/components",
       "utils": "@/lib/utils",
       "ui": "@/components/ui",
       "lib": "@/lib",
       "hooks": "@/hooks"
     },
     "menuColor": "default",
     "menuAccent": "subtle",
     "registries": {}
   }
   ```
   (Tailwind v3 projects keep `"config": "tailwind.config.ts"`; with a `src/` directory `css` is `src/app/globals.css`.) **Do not hand-edit `style` back to `new-york`**: it is the legacy pre-nova value, the shadcn studio URL templates are built for `base-nova` / `radix-nova` (a raw `new-york` studio URL returns 404, and the CLI falls back to the old Radix build of the item), and the `components-json` docs page still shows the old value.

2. **`lib/utils.ts`** -- Should be a one-line re-export of the `cn()` helper from the `cn` package:
   ```typescript
   export { cn } from "cn"
   ```
   `package.json` then lists `cn` (`^0.4.0`) instead of `clsx` + `tailwind-merge`, and registry components import `cn` from `"cn"`.

   **If the project was created before CLI 4.21** its `lib/utils.ts` still defines `cn()` itself by combining `clsx` with `tailwind-merge`. That keeps working. To move to the new scheme on Tailwind v4, run:
   ```bash
   npx shadcn@latest migrate cn          # whole project; installs `cn`, removes clsx/tailwind-merge when nothing else uses them
   npx shadcn@latest migrate cn src/lib/utils.ts   # or one file / a glob (keeps the old packages installed)
   ```
   The migration rewrites `lib/utils.ts` to the re-export above and rewrites other `clsx` / `tailwind-merge` imports. It reports unsupported shapes for manual review. **Tailwind v3 projects stay on `tailwind-merge` v2** — the `cn` merge engine supports Tailwind v4 only.

3. **`globals.css`** -- Should start with three imports and contain `:root` and `.dark` CSS variable blocks:
   ```css
   @import "tailwindcss";
   @import "tw-animate-css";
   @import "shadcn/tailwind.css";
   ```
   `shadcn/tailwind.css` provides the shared Tailwind v4 utilities — the `data-open:` / `data-closed:` variants and the accordion animations. `npx shadcn@latest eject` inlines it into your CSS and drops the `shadcn` dependency (irreversible).

4. **Font variable check** -- `init` wires a font in two places that must agree. In the generated app, `layout.tsx` declares the font with a CSS variable and `globals.css` maps it inside `@theme inline`:
   ```typescript
   // app/layout.tsx
   import { Geist } from "next/font/google"
   const geist = Geist({ subsets: ["latin"], variable: "--font-sans" })
   // ... className={cn("font-sans", geist.variable)} on the <html> element
   ```
   ```css
   /* app/globals.css */
   @theme inline {
     --font-sans: var(--font-sans);
   }
   ```
   This exact pair is what CLI 4.21 generates and it renders the font correctly — do not "fix" it. The check is that the variable name in `layout.tsx` (`variable: "--font-sans"`) is the name `@theme inline` refers to, and that the font's `variable` class is applied to `<html>` or `<body>`. If you use a differently named variable (`--font-geist-sans`), map it explicitly: `--font-sans: var(--font-geist-sans);`.

## Step 3: Configure shadcn studio Registries

To access shadcn studio components, blocks, pages, and themes, add the studio registries to `components.json`:

```json
{
  "registries": {
    "@shadcn-studio": "https://shadcnstudio.com/r/{style}/{name}.json",
    "@ss-components": "https://shadcnstudio.com/r/components/{style}/{name}.json",
    "@ss-blocks": "https://shadcnstudio.com/r/blocks/{style}/{name}.json",
    "@ss-pages": "https://shadcnstudio.com/r/pages/{style}/{name}.json",
    "@ss-themes": "https://shadcnstudio.com/r/themes/{name}.json"
  }
}
```

Or use the native one-liner instead of hand-editing:

```bash
npx shadcn registry add @shadcn-studio=https://shadcnstudio.com/r/{style}/{name}.json @ss-components=https://shadcnstudio.com/r/components/{style}/{name}.json @ss-blocks=https://shadcnstudio.com/r/blocks/{style}/{name}.json @ss-pages=https://shadcnstudio.com/r/pages/{style}/{name}.json @ss-themes=https://shadcnstudio.com/r/themes/{name}.json
```

This enables five namespace registries:
- `@shadcn-studio` -- Free studio content (new namespace)
- `@ss-components` -- Component variants (buttons, cards, inputs, etc.)
- `@ss-blocks` -- Pre-built UI blocks (hero sections, dashboards, forms, etc.)
- `@ss-pages` -- Full pre-built pages (new namespace)
- `@ss-themes` -- Theme presets (color schemes, typography, etc.)

## Step 4: Configure Premium Access (Optional)

For premium shadcn studio content, create a `.env` file in the project root:

```bash
EMAIL=your-email@example.com
LICENSE_KEY=your-license-key
```

Add `.env` to `.gitignore` if not already present:

```bash
echo ".env" >> .gitignore
```

Premium access requires converting the registry entries in `components.json` to objects with `params` — the CLI expands `${EMAIL}` and `${LICENSE_KEY}` from the environment:

```jsonc
"@ss-components": {
  "url": "https://shadcnstudio.com/r/components/{style}/{name}.json",
  "params": { "email": "${EMAIL}", "license_key": "${LICENSE_KEY}" }
}
```

Free components and blocks work without credentials. Premium content requires a shadcn studio license (Basic $99, Pro $199, Team $449, Enterprise $849 one-time; launch prices on https://shadcnstudio.com/pricing as of 2026-10-02 — check the page before quoting).

## Step 5: Test Component Installation

Verify the setup works by installing a test component:

```bash
# Standard shadcn/ui component:
npx shadcn@latest add button

# shadcn studio component (if registries configured) — namespaced address:
npx shadcn@latest add @ss-components/button-01
```

The `--registry` flag no longer exists in CLI v4 — installation from any registry uses namespaced addresses (`@namespace/item`).

Check that:
- Component file created at `components/ui/button.tsx` (or `src/components/ui/button.tsx`)
- No import errors when building: `npm run build`
- Component renders correctly in the browser

## Step 6: Configure Community Registries (Optional)

The official shadcn MCP only searches registries listed in `components.json`. To make every registry visible to the MCP, populate them from the official endpoint (418 entries on 2026-10-02):

```bash
curl -s https://ui.shadcn.com/r/registries.json
```

This returns a JSON array with `name`, `url`, `homepage`, `description`, `health` and `ranking` for every registry. `health.status` is `healthy`, `degraded`, `unavailable` or `observing`, and `health.hidden` marks entries the directory hides — skip `unavailable` and hidden ones. The CLI itself resolves `@registry/item` for any directory entry without further configuration; the bulk step below only matters for MCP search. Add entries with the native command:

```bash
npx shadcn registry add @magicui=https://magicui.design/r/{name} @aceternity=https://ui.aceternity.com/registry/{name}.json
```

Or add them to the `"registries"` field in `components.json` directly:

```json
{
  "registries": {
    "@magicui": "https://magicui.design/r/{name}",
    "@aceternity": "https://ui.aceternity.com/registry/{name}.json"
  }
}
```

Use the `/add-registries` command to do this in bulk automatically — it fetches the endpoint, drops `unavailable` and hidden entries, and merges the rest into `components.json`. Registries can also be declared in `package.json#registries` (CLI 4.18+; merged with `components.json`) — `/add-registries` only writes `components.json`.

### Install the Official shadcn Skill

The official shadcn skill reads `components.json` and enables Claude to discover components from configured registries:

```bash
pnpm dlx skills add shadcn/ui
```

This creates skill files that Claude Code loads automatically when `components.json` is detected. The skill runs `shadcn info --json` to read the project's resolved configuration.

## Tailwind v3 vs v4 Notes

| Aspect | Tailwind v3 | Tailwind v4 |
|--------|-------------|-------------|
| Config file | `tailwind.config.ts` | CSS-based (`@import "tailwindcss"`) |
| Content paths | In config `content: [...]` | Auto-detected |
| CSS variables | `@layer base { :root {...} }` | Same pattern, new import syntax |
| Button cursor | `cursor-pointer` default | Opt-in: use `shadcn init --pointer` (or add the `@layer base` rule manually) |

If using Tailwind v4, ensure `postcss.config.mjs` uses `@tailwindcss/postcss`:

```javascript
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

## What This Skill Does NOT Cover

- Development patterns (App Router, Server Components) -- see `nextjs-dev` plugin
- MCP server configuration -- see `mcp-tools` skill
- Theme customization beyond initial setup -- see `theme-configuration` skill
- Browsing and installing specific components -- see `component-registry` skill
- Searching and installing from community registries -- see `component-search` skill
