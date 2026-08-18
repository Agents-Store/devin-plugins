---
name: theme-configuration
description: >
  Configure themes, CSS variables, colors, fonts, and dark mode for shadcn/ui and shadcn studio. This skill
  should be used when the user asks to "set up a theme", "customize shadcn colors", "add dark mode",
  "change shadcn theme", "use shadcn theme generator", "configure CSS variables for shadcn", "install a
  shadcn studio theme", "customize fonts", "brand colors for shadcn", or needs to design and apply visual
  themes to their shadcn/ui project.
---

## Theme System Overview

shadcn/ui themes are powered by CSS custom properties (variables) in **OKLCH format**. Variables are complete colors — e.g. `--primary: oklch(0.205 0 0)` — referenced directly as `var(--primary)`. A `@theme inline` block in `globals.css` exposes them to Tailwind utilities. All components reference these variables, so changing them updates the entire UI.

Theme variables are defined in `globals.css` inside `:root` (light) and `.dark` (dark mode) blocks. Legacy projects with HSL triples (`--primary: 240 5.9% 10%` + `hsl(var(--primary))`) still work, but new inits emit OKLCH.

The official theming fast-path: pick one of the 8 style presets (Vega, Nova, Maia, Lyra, Mira, Luma, Rhea, Sera) via the visual builder at https://ui.shadcn.com/create, then apply with `shadcn apply <preset-code> --only theme`.

## Installing Pre-Made Themes

### From shadcn studio

Free themes install via `init` with the theme URL:

```bash
npx shadcn@latest init "https://shadcnstudio.com/r/themes/art-deco.json"
```

Premium/user themes: append `?email={EMAIL}&license_key={LICENSE_KEY}` to the URL, or configure the `@ss-themes` registry with `params` (see `setup` skill) and use:

```bash
npx shadcn@latest add @ss-themes/[name]
```

Available themes include: Spotify, VS Code, Material Design, Pastel Dreams, GitHub, and 15+ more. The theme install updates `globals.css` with the theme's CSS variables.

### From the Theme Generator

1. Visit https://shadcnstudio.com (Theme Generator section)
2. Select a pre-made theme or create custom with AI
3. Preview changes in real-time
4. Click "Copy" to get the CLI command
5. Run the copied command in your project root
6. Manually import required fonts (see Fonts section below)

## CSS Variable Structure

All color variables are complete OKLCH colors, referenced directly via `var(--name)`:

```css
:root {
  --radius: 0.625rem;

  /* Background and text */
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);

  /* Cards and popovers */
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);

  /* Primary action color */
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);

  /* Secondary/muted elements */
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);

  /* Muted backgrounds and text */
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);

  /* Accent highlights */
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
}
```

The `.dark` block redefines the same names with dark values. A `@theme inline` block maps the variables to Tailwind utility tokens (`--color-background: var(--background)`, etc.) — the CLI generates it during init.

## Dark Mode Setup

### Step 1: Define Dark Theme Variables

Add a `.dark` block in `globals.css`:

```css
.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  /* ... all other variables with dark values */
}
```

### Step 2: Configure Tailwind

**Tailwind v3** -- add to `tailwind.config.ts`:
```typescript
export default {
  darkMode: "class",
  // ...
}
```

**Tailwind v4** -- add to `globals.css`:
```css
@custom-variant dark (&:is(.dark *));
```

### Step 3: Install next-themes

```bash
npm install next-themes
```

### Step 4: Create Theme Provider

```typescript
// components/theme-provider.tsx
"use client"

import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({ children, ...props }: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

### Step 5: Wrap App Layout

```typescript
// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

### Step 6: Add Theme Toggle

```bash
npx shadcn@latest add button dropdown-menu
```

With the default Base UI base, triggers compose via the `render` prop (`asChild` only exists on Radix-based projects initialized with `-b radix`):

```typescript
// components/theme-toggle.tsx
"use client"

import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Moon, Sun } from "lucide-react"

export function ThemeToggle() {
  const { setTheme } = useTheme()
  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<Button variant="outline" size="icon" />}>
        <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
        <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        <span className="sr-only">Toggle theme</span>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>Light</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>Dark</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>System</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

(Radix variant: `<DropdownMenuTrigger asChild><Button ...>...</Button></DropdownMenuTrigger>`.)

## Font Configuration

### Using next/font (Recommended)

```typescript
// app/layout.tsx
import { Inter } from "next/font/google"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  )
}
```

Map the font variable in `globals.css`:

```css
@layer base {
  body {
    font-family: var(--font-sans), system-ui, sans-serif;
  }
}
```

### Theme-Specific Fonts

When installing a shadcn studio theme, check the theme's font requirements. Fonts must be manually installed via `next/font`:

```typescript
import { Geist, Geist_Mono } from "next/font/google"

const geistSans = Geist({ subsets: ["latin"], variable: "--font-sans" })
const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" })
```

## Creating a Custom Brand Theme

### Step 1: Define Brand Colors in OKLCH

Convert your brand hex colors to OKLCH (use a converter such as https://oklch.com):
- `#1a1a2e` → `oklch(0.24 0.04 285)` (dark navy)
- `#e94560` → `oklch(0.65 0.2 20)` (coral accent)

### Step 2: Map to CSS Variables

```css
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.24 0.04 285);
  --primary: oklch(0.65 0.2 20);
  --primary-foreground: oklch(1 0 0);
  /* Map remaining variables following the pattern */
}

.dark {
  --background: oklch(0.17 0.03 285);
  --foreground: oklch(0.95 0 0);
  --primary: oklch(0.65 0.2 20);
  --primary-foreground: oklch(1 0 0);
}
```

### Step 3: Test Across Components

Install a few components and verify the theme looks correct:

```bash
npx shadcn@latest add button card badge alert dialog
```

Check that:
- Primary buttons use your brand color
- Cards have proper background/border contrast
- Destructive elements are clearly distinguishable
- Dark mode maintains readability

See `references/theme-variables.md` for the complete CSS variable reference and all token mappings.

## What This Skill Does NOT Cover

- Initial shadcn/ui setup -- see `setup` skill
- Component installation -- see `component-registry` skill
- Project structure decisions -- see `project-scaffolding` skill
