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
- `--css-variables` (default true), `--rtl`, `--pointer` (adds `cursor: pointer` CSS for buttons), `--monorepo`

Base colors are now **neutral | stone | zinc | mauve | olive | mist | taupe**. Visual styles are the 8 official presets — **Vega** (classic look), **Nova** (compact, default), **Maia** (rounded), **Lyra** (sharp/mono), **Mira** (dense), **Luma**, **Rhea**, **Sera** — chosen via preset or the visual builder at https://ui.shadcn.com/create (`npx shadcn create`). Apply a preset to an existing project with `shadcn apply <preset-code> [--only theme|font]`.

This creates:
- `components.json` -- Configuration file for the shadcn CLI
- `lib/utils.ts` (or `src/lib/utils.ts`) -- The `cn()` class merge utility
- Updates `globals.css` with CSS variables for the chosen theme
- Installs dependencies: `clsx`, `tailwind-merge`, `class-variance-authority`

## Step 2: Verify Base Installation

Check these files exist and are correct:

1. **`components.json`** -- Should contain (`"style": "new-york"` is still the standard value; `"default"` is deprecated). For Tailwind v4, `tailwind.config` is left blank:
   ```json
   {
     "$schema": "https://ui.shadcn.com/schema.json",
     "style": "new-york",
     "rsc": true,
     "tsx": true,
     "tailwind": {
       "config": "",
       "css": "src/app/globals.css",
       "baseColor": "neutral",
       "cssVariables": true
     },
     "aliases": {
       "components": "@/components",
       "utils": "@/lib/utils"
     }
   }
   ```
   (Tailwind v3 projects keep `"config": "tailwind.config.ts"`.)

2. **`lib/utils.ts`** -- Should export the `cn()` helper:
   ```typescript
   import { type ClassValue, clsx } from "clsx"
   import { twMerge } from "tailwind-merge"

   export function cn(...inputs: ClassValue[]) {
     return twMerge(clsx(inputs))
   }
   ```

3. **`globals.css`** -- Should contain `:root` and `.dark` CSS variable blocks

4. **Font variable check** -- After init, verify `globals.css` does not contain circular font references:
   - `--font-sans: var(--font-sans)` — **wrong**, circular reference, browser falls back to system font
   - `--font-sans: var(--font-geist-sans)` — **correct**, maps to the CSS variable set by `next/font` in `layout.tsx`

   If the project uses Geist (Next.js default), ensure `layout.tsx` declares the font variable:
   ```typescript
   import { Geist } from "next/font/google"
   const geistSans = Geist({ subsets: ["latin"], variable: "--font-geist-sans" })
   ```
   And `globals.css` maps it (inside `@theme inline`):
   ```css
   --font-sans: var(--font-geist-sans);
   ```

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

```json
"@ss-components": {
  "url": "https://shadcnstudio.com/r/components/{style}/{name}.json",
  "params": { "email": "${EMAIL}", "license_key": "${LICENSE_KEY}" }
}
```

Free components and blocks work without credentials. Premium content requires a shadcn studio license (Basic $99, Pro $199, Team $449, Enterprise $849).

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

The official shadcn MCP only searches registries listed in `components.json`. To unlock search across all 260+ community registries (267 as of Aug 2026), populate them from the official endpoint:

```bash
curl -s https://ui.shadcn.com/r/registries.json
```

This returns a JSON array with `name`, `url`, `homepage`, `description` for every registry. Add entries with the native command:

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

Use the `/add-registries` command to do this in bulk automatically — it fetches the endpoint, parses all entries, and merges them into `components.json`.

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
