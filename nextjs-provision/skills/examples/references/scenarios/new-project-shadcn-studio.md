# Scenario: New Project with shadcn studio

Complete walkthrough: setting up a fresh Next.js project with shadcn/ui, shadcn studio registries, a theme, core components, and MCP server.

## Prerequisites

- Node.js 20+ installed
- Package manager: pnpm (recommended), npm, yarn, or bun
- Optional: shadcn studio license for premium content
- Optional: GitHub token for MCP server rate limits

## Step 1: Create Next.js Project

```bash
npx create-next-app@latest my-dashboard --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd my-dashboard
```

Expected output:
```
Creating a new Next.js app in /path/to/my-dashboard.
Installing dependencies: react, react-dom, next
Installing devDependencies: typescript, @types/node, @types/react, @types/react-dom, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, postcss
```

## Step 2: Initialize shadcn/ui

```bash
npx shadcn@latest init
```

The v4 flow prompts for template, base, and preset:
- Template: **next** (`-t next`)
- Base: **base** (Base UI, the default; `-b radix` or `-b aria` to switch)
- Preset: **base-nova** (the default; pick another of the 8 styles or a code from https://ui.shadcn.com/create)

Pass `-d` to accept the defaults (`--template=next --preset=base-nova`) without prompts.

Verify:
```bash
# Should show components.json
cat components.json

# Should show cn() helper
cat src/lib/utils.ts
```

## Step 3: Configure shadcn studio Registries

Edit `components.json` to add studio registries:

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

For premium access, create `.env`:
```bash
echo "EMAIL=your-email@example.com" > .env
echo "LICENSE_KEY=your-license-key" >> .env
echo ".env" >> .gitignore
```

Then convert the premium registry entries to objects with `params`:

```json
"@ss-components": {
  "url": "https://shadcnstudio.com/r/components/{style}/{name}.json",
  "params": { "email": "${EMAIL}", "license_key": "${LICENSE_KEY}" }
}
```

## Step 4: Install a Theme

Option A: Use a studio theme (free themes install via init from the theme URL; premium themes via `@ss-themes` with `params` configured)
```bash
npx shadcn@latest init "https://shadcnstudio.com/r/themes/art-deco.json"
```

Option B: Use the default (already configured from init)

Option C: Use the Theme Generator at https://shadcnstudio.com

## Step 5: Set Up Dark Mode

```bash
npm install next-themes
```

Create the theme provider:

```typescript
// src/components/theme-provider.tsx
"use client"

import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({ children, ...props }: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

Update the root layout:

```typescript
// src/app/layout.tsx
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import "./globals.css"

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" })

export const metadata: Metadata = {
  title: "My Dashboard",
  description: "Dashboard built with shadcn/ui",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

## Step 6: Install Core Components

```bash
# Navigation and layout
npx shadcn@latest add sidebar sheet dropdown-menu avatar separator breadcrumb

# Data display
npx shadcn@latest add card table badge skeleton

# Forms
npx shadcn@latest add button input form label select checkbox

# Feedback
npx shadcn@latest add dialog alert-dialog sonner tooltip

# Utility
npx shadcn@latest add tabs command scroll-area
```

Verify all components installed:
```bash
ls src/components/ui/
```

Expected: ~20+ component files.

## Step 7: Install shadcn studio Blocks (Optional)

```bash
# Dashboard blocks (namespaced addresses — CLI v4 has no --registry flag)
npx shadcn@latest add @ss-blocks/dashboard-shell-01
npx shadcn@latest add @ss-blocks/stat-card-01

# Move to components directory
mv src/components/shadcn-studio/blocks/* src/components/blocks/ 2>/dev/null
```

## Step 8: Build a Sample Dashboard Page

```typescript
// src/app/page.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

const stats = [
  { title: "Total Revenue", value: "$45,231.89", change: "+20.1%", trend: "up" },
  { title: "Subscriptions", value: "+2,350", change: "+180.1%", trend: "up" },
  { title: "Sales", value: "+12,234", change: "+19%", trend: "up" },
  { title: "Active Now", value: "+573", change: "+201", trend: "up" },
]

export default function Dashboard() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <Button>Download Report</Button>
        </div>
      </header>
      <main className="flex-1 p-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <Badge variant="secondary">{stat.change}</Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <CardDescription>from last month</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  )
}
```

## Step 9: Set Up MCP Server (Optional)

For AI-assisted component discovery:

```bash
# Official shadcn MCP
pnpm dlx shadcn@latest mcp init --client claude

# OR Jpisnice community MCP (more browsing tools)
claude mcp add shadcn -- bunx -y @jpisnice/shadcn-ui-mcp-server
```

## Step 10: Verify Everything Works

```bash
# Build should succeed with no errors
npm run build

# Start dev server
npm run dev
```

Open http://localhost:3000 and verify:
- Dashboard page renders with stat cards
- Dark mode toggle works (if added)
- No console errors
- Components are styled correctly

## Final Project Structure

```
my-dashboard/
├── src/
│   ├── app/
│   │   ├── globals.css          # Theme CSS variables
│   │   ├── layout.tsx           # Root layout with theme provider
│   │   └── page.tsx             # Dashboard home
│   ├── components/
│   │   ├── ui/                  # ~20 shadcn/ui components
│   │   ├── blocks/              # Studio blocks (if installed)
│   │   └── theme-provider.tsx   # Dark mode provider
│   └── lib/
│       └── utils.ts             # cn() helper
├── components.json              # shadcn/ui + studio config ("config": "" for v4)
├── tsconfig.json                # TypeScript config with @/ alias
└── package.json
```

(Tailwind v4 is CSS-configured — there is no `tailwind.config.ts` in the tree.)

## Next Steps

- Add more pages with route groups: `(dashboard)`, `(auth)`, `(marketing)`
- Install more components as needed from the component registry
- Customize the theme with your brand colors
- Set up a sidebar layout for multi-page dashboards
- Add data tables with `@tanstack/react-table`
