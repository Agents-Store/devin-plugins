---
name: troubleshoot
description: >
  Diagnose and fix common shadcn/ui and shadcn studio setup issues, dependency conflicts, and configuration
  problems. This skill should be used when the user encounters "shadcn install error", "components.json
  error", "tailwind not working with shadcn", "shadcn component not rendering", "CSS variables not applied",
  "shadcn studio registry error", "dependency conflict", "cn() not found", or needs to debug problems with
  their shadcn/ui setup.
---

## Quick Diagnostics

Run these checks first:

```bash
# 0. Project config as the CLI resolves it (first diagnostic)
npx shadcn@latest info

# 1. Node.js version (need 20+)
node --version

# 2. shadcn CLI version
npx shadcn@latest --version

# 3. components.json exists and is valid
cat components.json

# 4. Tailwind is installed (works for both v3 and v4 — the v4 CLI moved
#    to @tailwindcss/cli, so `npx tailwindcss --help` fails on v4)
node -e "console.log(require('tailwindcss/package.json').version)"

# 5. cn() helper exists
cat src/lib/utils.ts 2>/dev/null || cat lib/utils.ts 2>/dev/null || echo "NOT FOUND"

# 6. CSS variables defined
grep -c "\-\-background:" src/app/globals.css 2>/dev/null || grep -c "\-\-background:" app/globals.css 2>/dev/null

# 7. TypeScript compiles
npx tsc --noEmit
```

## Installation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `components.json not found` | shadcn/ui not initialized | Run `npx shadcn@latest init` |
| `Tailwind CSS not detected` | Tailwind not installed or misconfigured | Install tailwindcss and verify config |
| `Could not find tsconfig.json` | Not a TypeScript project | Add `tsconfig.json` or run `npx tsc --init` |
| `Cannot resolve @/components` | Path aliases not configured | Add `paths` to `tsconfig.json` |
| `EACCES permission denied` | npm permissions issue | Use `npx` prefix or fix npm permissions |
| `Module not found: clsx` | Dependencies not installed | Run `npm install` after shadcn init |

## Registry Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Registry not found: @ss-components` | Studio registries not configured | Add the `@`-prefixed studio registries to `components.json`, e.g. `"@ss-components": "https://shadcnstudio.com/r/components/{style}/{name}.json"` (see `setup` skill) |
| `401 Unauthorized` | Invalid or missing premium credentials | Credentials are injected via `params` in the registry entry (`${EMAIL}`, `${LICENSE_KEY}` expanded from env/`.env.local`) — check both the params config and the values |
| `403 Forbidden` | License expired or wrong tier | Verify license at shadcnstudio.com account; confirm `params` auth is configured for the registry |
| `Network timeout` | Registry unreachable | Check internet connection, try again |
| `Component not found in registry` | Typo or wrong registry | Check component name at shadcnstudio.com/components |
| CLI v2/v3 syntax with v4 | Using `--registry` flag or URL-based format | Use namespaced addresses: `npx shadcn@latest add @ss-components/button-01` |

## Tailwind CSS Issues

### v3 Specific

**Components unstyled / CSS not applied:**
```typescript
// tailwind.config.ts — ensure content includes components
export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  // ...
}
```

**Dark mode not working:**
```typescript
// tailwind.config.ts — add darkMode
export default {
  darkMode: "class",
  // ...
}
```

### v4 Specific

**Components unstyled (Tailwind v4):**
```css
/* globals.css — verify import syntax */
@import "tailwindcss";
```

**postcss.config not using v4 plugin:**
```javascript
// postcss.config.mjs
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

**Buttons show default cursor instead of pointer (v4 change):**

For new projects, `shadcn init --pointer` injects this automatically. For existing projects, add the official rule manually:

```css
/* globals.css — restore pointer cursor */
@layer base {
  button:not(:disabled),
  [role="button"]:not(:disabled) {
    cursor: pointer;
  }
}
```

### Both Versions

**CSS variables not taking effect:**
- Verify `:root` block exists in `globals.css`
- Verify `globals.css` is imported in `app/layout.tsx`
- Check for conflicting CSS that overrides variables
- Verify `cssVariables: true` in `components.json`

## Dependency Conflicts

Note: Base UI projects (the default since July 2026) depend on a single `@base-ui/react` package — the Radix rows below apply only to Radix-based projects (`init -b radix`).

| Conflict | Symptoms | Fix |
|----------|----------|-----|
| React 18 vs 19 | Peer dependency warnings | Pin React to 18.x or upgrade all Radix packages |
| Conflicting Radix versions | Type errors, runtime crashes | `npm ls @radix-ui/react-*` to find conflicts, then `npm dedupe` |
| Mixed radix packages | `@radix-ui/react-*` and unified `radix-ui` both installed | Run `npx shadcn@latest migrate radix` (Feb 2026 unified package replaces per-component installs) |
| CVA version mismatch | `cva is not a function` | `npm install class-variance-authority@latest` |
| Multiple tailwind-merge | Inconsistent class merging | `npm dedupe tailwind-merge` |

### Diagnosing Dependency Issues

```bash
# Check for duplicate packages
npm ls --all | grep -E "(radix|tailwind-merge|clsx|cva)"

# Deduplicate
npm dedupe

# Nuclear option: clean install
rm -rf node_modules package-lock.json
npm install
```

## Component Rendering Issues

### "use client" Errors

**Error: `useState`, `useEffect`, etc. in Server Component**

Interactive shadcn/ui components (Dialog, DropdownMenu, Tabs, etc.) require `'use client'`. If you get this error when importing a component:

1. The component itself already has `'use client'` -- check that it was installed correctly
2. If importing in a Server Component, wrap usage in a Client Component:

```typescript
// components/interactive-section.tsx
"use client"

import { Dialog, DialogTrigger, DialogContent } from "@/components/ui/dialog"

export function InteractiveSection() {
  return (
    <Dialog>
      <DialogTrigger>Open</DialogTrigger>
      <DialogContent>...</DialogContent>
    </Dialog>
  )
}
```

### Hydration Errors

**Error: `Hydration failed because the initial UI does not match`**

Common causes with shadcn/ui:
- Using `next-themes` without `suppressHydrationWarning` on `<html>`
- Date/time rendering without client-side detection
- Browser extensions modifying the DOM

Fix:
```typescript
<html lang="en" suppressHydrationWarning>
```

### TooltipProvider Missing

**Error: `useContext` returning undefined for Tooltip**

Current shadcn `tooltip.tsx` embeds its own `TooltipProvider` inside the `Tooltip` component, so no layout-level provider is needed. Check the installed `components/ui/tooltip.tsx` first: if it wraps `TooltipPrimitive.Root` in a provider, you are on the current copy.

A layout-level provider is only needed for **older copies** of the component, or to set a shared `delayDuration` across all tooltips:

```typescript
// app/layout.tsx — only for old tooltip.tsx copies or custom delayDuration
import { TooltipProvider } from "@/components/ui/tooltip"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <TooltipProvider delayDuration={200}>
          {children}
        </TooltipProvider>
      </body>
    </html>
  )
}
```

If the error persists on a current copy, re-install: `npx shadcn@latest add tooltip --overwrite`.

## Path Alias Issues

**Error: `Cannot find module '@/components/ui/button'`**

Check `tsconfig.json`:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

For projects without `src/` directory:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

Ensure `components.json` aliases match `tsconfig.json` paths.

## MCP Server Issues

| Issue | Fix |
|-------|-----|
| MCP server not connecting | Check `claude mcp list` output, verify server is installed |
| Rate limit exceeded (60/hour) | Add GitHub token via `--github-api-key` flag |
| Stale component data | MCP server caches GitHub API responses; restart the server |
| Wrong framework components | Pass `--framework react` explicitly (also: svelte, vue, react-native) |
| Wrong transport | Pass `--mode stdio|sse|dual` (and `--port` for SSE) explicitly |

## When to Escalate

- **Build fails after clean install** -- Likely a framework version incompatibility. Check Next.js and React versions
- **Components look correct locally but break in production** -- Check Tailwind purge/content configuration for production builds
- **Type errors in installed components** -- May indicate a shadcn/ui version mismatch. Update the CLI: `npm install -g shadcn@latest`
