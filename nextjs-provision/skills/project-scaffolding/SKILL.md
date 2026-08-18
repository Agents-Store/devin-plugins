---
name: project-scaffolding
description: >
  Scaffold Next.js projects with shadcn/ui templates, starter kits, and component architecture patterns.
  This skill should be used when the user asks to "scaffold a project", "use a shadcn template",
  "project structure with shadcn", "component organization", "set up a dashboard template", "starter kit
  for shadcn", "how to organize shadcn components", or needs guidance on organizing a Next.js project with
  shadcn/ui component architecture.
---

## Quick Start: New Project from Scratch

```bash
# 1. Create Next.js project
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir

# 2. Initialize shadcn/ui (Base UI is the default base; -b radix|aria to switch;
#    default preset is base-nova)
cd my-app
npx shadcn@latest init

# Or one step — init scaffolds the Next.js app too:
npx shadcn@latest init -t next -n my-app

# 3. Install core components
npx shadcn@latest add button card input form dialog dropdown-menu toast tabs
```

## shadcn studio Templates

shadcn studio offers 20+ production-ready templates (requires Pro license). Official templates can also be scaffolded via `npx shadcn create` presets:

| Template | Includes |
|----------|----------|
| Dashboard | Sidebar, header, stat cards, charts, data tables |
| SaaS | Landing page, pricing, auth, dashboard |
| E-commerce | Product listing, cart, checkout, order management |
| Portfolio | Hero, project showcase, about, contact |
| Blog | Article listing, MDX rendering, categories, search |
| Admin Panel | Multi-page admin with forms, tables, settings |

### Using a Template

1. Download the template ZIP from shadcnstudio.com
2. Extract to your project directory
3. Install dependencies: `pnpm install`
4. Start dev server: `pnpm dev`

Templates come pre-configured with:
- Next.js App Router with TypeScript
- Tailwind CSS and shadcn/ui components
- Responsive layouts (mobile-first)
- Dark mode support
- Professional page structure

## Recommended Project Structure

```
src/
├── app/                        # App Router pages
│   ├── layout.tsx              # Root layout (theme provider, fonts)
│   ├── page.tsx                # Home page
│   ├── (auth)/                 # Auth route group
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (dashboard)/            # Dashboard route group
│   │   ├── layout.tsx          # Dashboard layout with sidebar
│   │   ├── page.tsx            # Dashboard home
│   │   └── settings/page.tsx
│   └── (marketing)/            # Marketing route group
│       ├── layout.tsx          # Marketing layout with navbar
│       └── page.tsx            # Landing page
├── components/
│   ├── ui/                     # shadcn/ui primitives (auto-generated)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── blocks/                 # shadcn studio blocks (moved from shadcn-studio/)
│   │   ├── hero-section.tsx
│   │   └── pricing-table.tsx
│   ├── forms/                  # Form compositions
│   │   ├── login-form.tsx
│   │   └── settings-form.tsx
│   ├── layout/                 # Layout components
│   │   ├── site-header.tsx
│   │   ├── site-footer.tsx
│   │   ├── sidebar-nav.tsx
│   │   └── mobile-nav.tsx
│   └── features/               # Feature-specific compositions
│       ├── user-profile-card.tsx
│       └── data-table.tsx
├── lib/
│   ├── utils.ts                # cn() helper (created by shadcn init)
│   └── validations.ts          # Zod schemas for forms
├── hooks/                      # Custom React hooks
│   └── use-media-query.ts
├── styles/
│   └── globals.css             # Theme CSS variables
└── types/                      # TypeScript type definitions
    └── index.ts
```

### Key Organization Rules

1. **`components/ui/`** -- Only auto-generated shadcn/ui files. Do not put custom components here
2. **`components/blocks/`** -- Moved studio blocks and your own larger UI sections
3. **`components/forms/`** -- Form compositions that combine shadcn form primitives
4. **`components/layout/`** -- Shared layout elements (header, footer, sidebar, navigation)
5. **`components/features/`** -- Domain-specific component compositions

## components.json Configuration

The `components.json` file controls where components are installed and how paths resolve:

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
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "registries": {
    "@shadcn-studio": "https://shadcnstudio.com/r/{style}/{name}.json",
    "@ss-components": "https://shadcnstudio.com/r/components/{style}/{name}.json",
    "@ss-blocks": "https://shadcnstudio.com/r/blocks/{style}/{name}.json",
    "@ss-pages": "https://shadcnstudio.com/r/pages/{style}/{name}.json",
    "@ss-themes": "https://shadcnstudio.com/r/themes/{name}.json"
  }
}
```

(`"config": ""` is correct for Tailwind v4 — v3 projects point it at `tailwind.config.ts`.) Run `npx shadcn@latest info` to print the project's resolved configuration.

### Key Fields

| Field | Purpose |
|-------|---------|
| `style` | `new-york` (default; `default` style deprecated). Visual styles now come from presets (Vega/Nova/Maia/Lyra/Mira/Luma/Rhea/Sera) |
| `rsc` | Enable React Server Components support |
| `tsx` | Use TypeScript (`.tsx`) files |
| `tailwind.config` | Path to Tailwind config (v3); blank for v4 |
| `tailwind.css` | Path to the CSS file with theme variables |
| `aliases.components` | Where components are installed |
| `aliases.ui` | Shorthand alias for `components/ui` |
| `registries` | Custom registries (shadcn studio, private, etc.) |

## Component Architecture Patterns

### Atomic Design Mapping

| Atomic Level | shadcn Equivalent | Examples |
|--------------|-------------------|----------|
| Atoms | `components/ui/` | Button, Input, Badge, Avatar |
| Molecules | `components/forms/`, `components/features/` | LoginForm, SearchBar, UserCard |
| Organisms | `components/blocks/`, `components/layout/` | SiteHeader, HeroSection, DataTable |
| Templates | `app/(group)/layout.tsx` | DashboardLayout, MarketingLayout |
| Pages | `app/(group)/page.tsx` | HomePage, SettingsPage |

### Server vs Client Component Split

```
Server Components (default):           Client Components ('use client'):
├── Layout shells                       ├── Interactive forms
├── Data display (cards, tables)        ├── Theme toggle
├── Static content blocks               ├── Dropdown menus
├── Navigation structure                ├── Dialogs/modals
└── Page-level data fetching            ├── Tabs with state
                                        ├── Toast notifications
                                        └── Any component using hooks
```

Rule: Keep components as Server Components until they need interactivity. Wrap only the interactive part in `'use client'`.

### Barrel Exports Pattern

Create index files for component groups:

```typescript
// components/layout/index.ts
export { SiteHeader } from "./site-header"
export { SiteFooter } from "./site-footer"
export { SidebarNav } from "./sidebar-nav"
export { MobileNav } from "./mobile-nav"
```

Usage:
```typescript
import { SiteHeader, SiteFooter } from "@/components/layout"
```

## Monorepo Setup (Turborepo)

For shared component libraries across multiple Next.js apps:

```
packages/
├── ui/                         # Shared shadcn/ui components
│   ├── src/components/ui/      # shadcn primitives
│   ├── src/lib/utils.ts        # cn() helper
│   ├── components.json         # shadcn config
│   ├── package.json
│   └── tsconfig.json
apps/
├── web/                        # Main Next.js app
│   └── components/             # App-specific compositions
└── admin/                      # Admin Next.js app
    └── components/             # Admin-specific compositions
```

The `ui` package exports shared shadcn/ui components. Each app imports them and adds app-specific compositions.

## What This Skill Does NOT Cover

- Installing specific components -- see `component-registry` skill
- Theme and color configuration -- see `theme-configuration` skill
- Initial shadcn/ui setup -- see `setup` skill
- Development patterns (routing, data fetching) -- see `nextjs-dev` plugin
