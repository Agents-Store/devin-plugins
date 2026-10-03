---
name: component-registry
description: >
  Browse, search, install, and use shadcn/ui and shadcn studio components, blocks, and templates. This skill
  should be used when the user asks to "install a shadcn component", "add a button", "list shadcn blocks",
  "find a form block", "date picker", "add a form", "browse shadcn studio components", "add a card component", "install a navigation
  block", "what components are available", "write code with shadcn components", "use Button component",
  "render shadcn component as link", "Button as a link", "shadcn component patterns", or needs to discover,
  install, or use UI components from shadcn registries correctly.
---

## Registries Overview

Installation uses **namespaced addresses** (`@namespace/item`) — the `--registry` flag no longer exists in CLI v4.

| Registry | Install Syntax | Content | Auth Required |
|----------|----------------|---------|---------------|
| Standard shadcn/ui | `npx shadcn@latest add button` | Core components | No |
| `@shadcn-studio` | `npx shadcn@latest add @shadcn-studio/[name]` | Free studio content | No |
| `@ss-components` | `npx shadcn@latest add @ss-components/button-01` | 1000+ component variants | Free + Premium |
| `@ss-blocks` | `npx shadcn@latest add @ss-blocks/hero-section-01` | 1000+ pre-built UI blocks | Free + Premium |
| `@ss-pages` | `npx shadcn@latest add @ss-pages/feature-page-01` | 100+ full pre-built pages | Free + Premium |
| `@ss-themes` | `npx shadcn@latest add @ss-themes/[name]` | Theme presets | Free + Premium |

The `{style}` placeholder in the studio registry URLs is filled from `components.json` → `style`, which `init` writes as `<base>-<preset>` — `base-nova` (Base UI, default) or `radix-nova` (Radix). Both resolve on shadcnstudio.com. The legacy `new-york` style value does not: the raw URL `https://shadcnstudio.com/r/components/new-york/button-01.json` returns 404, and the CLI falls back to the old Radix New York build of the item (a dry run overwrote the Base UI `button.tsx`). Run `npx shadcn@latest info` and fix `style` before installing studio items.

## Installation Commands

### Standard shadcn/ui Components

```bash
# Single component
npx shadcn@latest add button

# Multiple components at once
npx shadcn@latest add button card input dialog

# Force overwrite existing files
npx shadcn@latest add button --overwrite
```

### shadcn studio Components

```bash
# Component variant
npx shadcn@latest add @ss-components/button-01

# Block
npx shadcn@latest add @ss-blocks/hero-section-01

# Theme — install via init from the theme URL, or the @ss-themes namespace
npx shadcn@latest init "https://shadcnstudio.com/r/themes/[name].json"
npx shadcn@latest add @ss-themes/[name]

# Skip confirmation prompts
npx shadcn@latest add @ss-components/button-01 --yes
```

### Inspect Before Installing

```bash
# View a registry item's contents without installing
npx shadcn@latest view @ss-blocks/hero-section-01

# See what an install would change, without writing files
npx shadcn@latest add button --dry-run

# Show how an installed component differs from the registry (replaces the deprecated `shadcn diff`)
npx shadcn@latest add button --diff

# Read a component's docs/API/examples in the terminal
npx shadcn@latest docs button

# Search a registry server-side
npx shadcn@latest search @shadcn -q "calendar"
```

## Core Component Categories

### Data Display

| Component | Use Case | Install |
|-----------|----------|---------|
| `card` | Content container with header/footer | `npx shadcn@latest add card` |
| `table` | Tabular data display | `npx shadcn@latest add table` |
| `badge` | Status labels, tags | `npx shadcn@latest add badge` |
| `avatar` | User profile images | `npx shadcn@latest add avatar` |
| `calendar` | Date display/selection | `npx shadcn@latest add calendar` |
| `carousel` | Image/content slider | `npx shadcn@latest add carousel` |
| `item` | Generic list/detail item | `npx shadcn@latest add item` |
| `kbd` | Keyboard shortcut display (Kbd + KbdGroup) | `npx shadcn@latest add kbd` |

### Form Inputs

| Component | Use Case | Install |
|-----------|----------|---------|
| `input` | Text input fields | `npx shadcn@latest add input` |
| `button` | Actions and submissions | `npx shadcn@latest add button` |
| `checkbox` | Multiple selections | `npx shadcn@latest add checkbox` |
| `radio-group` | Single selection | `npx shadcn@latest add radio-group` |
| `select` | Dropdown selection | `npx shadcn@latest add select` |
| `switch` | Toggle on/off | `npx shadcn@latest add switch` |
| `slider` | Range input | `npx shadcn@latest add slider` |
| `textarea` | Multi-line text | `npx shadcn@latest add textarea` |
| `field` | The form building block — Field/FieldGroup/FieldLabel/FieldDescription/FieldError; pair it with React Hook Form, TanStack Form or Formisch (see "Forms" below). Replaces the old `form` item | `npx shadcn@latest add field` |
| `input-group` | Grouped inputs with addons | `npx shadcn@latest add input-group` |
| `button-group` | Grouped/segmented buttons | `npx shadcn@latest add button-group` |
| `questionnaire` | Multi-question form flows | `npx shadcn@latest add questionnaire` |
| Date Picker (composition, no `date-picker` item) | Date selection — `Popover` + `Calendar` (see "Date Picker" below) | `npx shadcn@latest add popover calendar` |

### Date Picker

There is no `date-picker` registry item — asking the CLI for it fails with "The item ... was not found". A date picker is a composition of `Popover` and `Calendar` (`Popover` > `PopoverTrigger` + `PopoverContent` > `Calendar`). Install the two parts, then write the component:

```bash
npx shadcn@latest add popover calendar
```

```tsx
// components/date-picker.tsx
"use client"

import * as React from "react"
import { format } from "date-fns"
import { CalendarIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

export function DatePicker() {
  const [date, setDate] = React.useState<Date>()

  return (
    <Popover>
      <PopoverTrigger
        render={
          <Button
            variant="outline"
            data-empty={!date}
            className="w-[240px] justify-start text-left font-normal data-[empty=true]:text-muted-foreground"
          />
        }
      >
        <CalendarIcon />
        {date ? format(date, "PPP") : <span>Pick a date</span>}
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="single"
          selected={date}
          onSelect={setDate}
          defaultMonth={date}
        />
      </PopoverContent>
    </Popover>
  )
}
```

`calendar` brings `react-day-picker` and `date-fns` with it. On a Radix project (`radix-nova`) write `<PopoverTrigger asChild><Button ... /></PopoverTrigger>` instead of the `render` prop. For a date range use `mode="range"` with `selected`/`onSelect` typed as `DateRange`; docs and more variants: `npx shadcn@latest docs calendar`.

### Forms

There is no working `form` item either — asking the CLI for it writes no files (a `--dry-run` lists none: the registry item carries only a name and type). Forms are built from the `field` component plus a form library. For React Hook Form with Zod:

```bash
npx shadcn@latest add field input button
npm install react-hook-form @hookform/resolvers zod
```

```tsx
// components/forms/contact-form.tsx
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import * as z from "zod"

import { Button } from "@/components/ui/button"
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"

const contactSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters."),
  email: z.string().email("Invalid email address."),
})

type ContactValues = z.infer<typeof contactSchema>

export function ContactForm() {
  const form = useForm<ContactValues>({
    resolver: zodResolver(contactSchema),
    defaultValues: { name: "", email: "" },
  })

  function onSubmit(values: ContactValues) {
    console.log(values)
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <FieldGroup>
        <Controller
          name="name"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={field.name}>Name</FieldLabel>
              <Input {...field} id={field.name} aria-invalid={fieldState.invalid} />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Controller
          name="email"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={field.name}>Email</FieldLabel>
              <Input {...field} id={field.name} type="email" aria-invalid={fieldState.invalid} />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
        <Button type="submit">Submit</Button>
      </FieldGroup>
    </form>
  )
}
```

`Controller` and `fieldState` replace the removed `Form`/`FormField`/`FormItem`/`FormMessage` wrappers — do not import `@/components/ui/form`. TanStack Form and Formisch guides: https://ui.shadcn.com/docs/forms.

### Navigation & Layout

| Component | Use Case | Install |
|-----------|----------|---------|
| `tabs` | Content tabs | `npx shadcn@latest add tabs` |
| `navigation-menu` | Site navigation | `npx shadcn@latest add navigation-menu` |
| `breadcrumb` | Page hierarchy | `npx shadcn@latest add breadcrumb` |
| `sidebar` | Collapsible sidebar | `npx shadcn@latest add sidebar` |
| `pagination` | Page navigation | `npx shadcn@latest add pagination` |
| `separator` | Visual divider | `npx shadcn@latest add separator` |
| `sheet` | Slide-over panel | `npx shadcn@latest add sheet` |
| `resizable` | Resizable panels | `npx shadcn@latest add resizable` |

### Feedback & Overlay

| Component | Use Case | Install |
|-----------|----------|---------|
| `dialog` | Modal windows | `npx shadcn@latest add dialog` |
| `alert-dialog` | Confirmation dialogs | `npx shadcn@latest add alert-dialog` |
| `toast` | Native Toast for Base UI projects (sonner remains for Radix/legacy) | `npx shadcn@latest add toast` |
| `sonner` | Notification messages (Radix/legacy projects) | `npx shadcn@latest add sonner` |
| `tooltip` | Hover information | `npx shadcn@latest add tooltip` |
| `popover` | Floating panels | `npx shadcn@latest add popover` |
| `alert` | Inline messages | `npx shadcn@latest add alert` |
| `skeleton` | Loading placeholders | `npx shadcn@latest add skeleton` |
| `spinner` | Loading spinner | `npx shadcn@latest add spinner` |
| `empty` | Empty states | `npx shadcn@latest add empty` |
| `progress` | Progress indicators | `npx shadcn@latest add progress` |

### Data & Utility

| Component | Use Case | Install |
|-----------|----------|---------|
| `dropdown-menu` | Context menus | `npx shadcn@latest add dropdown-menu` |
| `command` | Command palette (search) | `npx shadcn@latest add command` |
| `accordion` | Collapsible sections | `npx shadcn@latest add accordion` |
| `collapsible` | Show/hide content | `npx shadcn@latest add collapsible` |
| `scroll-area` | Custom scrollbars | `npx shadcn@latest add scroll-area` |
| `aspect-ratio` | Fixed aspect containers | `npx shadcn@latest add aspect-ratio` |

### Chat (June 2026)

Chat interface suite plus `scroll-fade` and `shimmer` CSS utilities:

| Component | Use Case |
|-----------|----------|
| `message-scroller` | Auto-scrolling message container |
| `message` | Chat message layout |
| `bubble` | Message bubble styling |
| `attachment` | File/image attachments in chat |
| `marker` | Message markers (timestamps, dividers) |

```bash
npx shadcn@latest add message-scroller message bubble attachment marker
```

### Headless primitives and helpers

Newer official building blocks that components and docs may pull in:

- `@shadcn/react` — unstyled headless primitives (Questionnaire, Message Scroller); registry items depend on it, so `add` installs it
- `@shadcn/registry` — the registry engine package the CLI is built on (fetch, resolve and install registry items; 0.1.0)
- `@shadcn/helpers/ai-sdk` — `createChat()` scripts a mock AI SDK chat (tool calls, approvals, questions) that streams through the real `useChat` lifecycle
- Typeset — one `typeset.css` you own that styles HTML/markdown inside a `typeset` container; generate it at https://ui.shadcn.com/typeset and import it after Tailwind
- Package Imports — `package.json#imports` aliases (`#components/*`, `#lib/*`) usable instead of `tsconfig` `paths` (needs TypeScript 5, `moduleResolution: "bundler"`, `resolvePackageJsonImports: true`)

## shadcn studio Block Categories

| Category | Examples | Count |
|----------|----------|-------|
| Hero sections | Landing page heroes with CTAs, images, videos | 50+ |
| Feature sections | Feature grids, icon lists, comparison tables | 40+ |
| Pricing | Pricing cards, comparison tables, toggles | 30+ |
| Testimonials | Quote cards, carousels, social proof | 20+ |
| Navigation | Headers, navbars, mega menus, mobile nav | 30+ |
| Footers | Multi-column, newsletter signup, sitemap | 20+ |
| CTA sections | Call-to-action banners, signup forms | 20+ |
| Dashboard | Dashboard shells, stat cards, charts | 100+ |
| Forms | Multi-step forms, login/signup, contact | 40+ |
| eCommerce | Product cards, carts, checkout, reviews | 100+ |
| Data tables | Sortable tables, filters, pagination | 30+ |
| Authentication | Login, signup, forgot password, OTP | 20+ |

See `references/shadcn-studio-components.md` and `references/shadcn-studio-blocks.md` for detailed catalogs.

## Community Registries (400+)

Beyond the standard shadcn/ui and shadcn studio registries, the official directory (418 entries on 2026-10-02) lists registries with specialized components. Each entry carries `health.status` (`healthy`, `degraded`, `unavailable`, `observing`) and `health.hidden` — recommend only healthy ones, and mention it when a registry is degraded:

| Category | Example Registries | Component Types |
|----------|-------------------|-----------------|
| Animation & Motion | @magicui, @aceternity (degraded), @animate-ui, @cult-ui | Animated buttons, scroll effects, parallax, globe, beams |
| Extended Components | @coss (ex-Origin UI), @diceui, @basecn, @8bitcn, @boldkit | Multi-select, file upload, retro/pixel style, card variants |
| Blocks & Sections | @bundui, @blocks-so, @efferd (degraded) | Landing page sections, marketing blocks, dashboards |
| E-Commerce | @commercn | Product cards, cart, checkout, reviews |
| AI / Chat | @ai-elements, @assistant-ui, @tool-ui | Chat bubbles, prompt inputs, AI response streams |

Install from a community registry:

```bash
npx shadcn@latest add @magicui/shimmer-button
npx shadcn@latest add @aceternity/moving-border
npx shadcn@latest add @commercn/product-card-01
```

The CLI resolves `@registry/item` for any registry in the directory without extra configuration. See the `component-search` skill for the full registry reference with URLs, health filtering, setup instructions, and search workflow.

## Where Components Are Installed

```
src/
├── components/
│   └── ui/                    # ← shadcn/ui components go here
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       └── ...
├── components/
│   └── shadcn-studio/         # ← Studio blocks land here initially
│       └── blocks/
│           └── hero-section-01/
└── lib/
    └── utils.ts               # export { cn } from "cn"
```

After installing studio blocks, move them to your preferred location:

```bash
# Move from studio default to your blocks directory
mv src/components/shadcn-studio/blocks/hero-section-01 src/components/blocks/hero-section-01
```

## Common Installation Patterns

### Dashboard Setup

```bash
npx shadcn@latest add card table tabs sidebar sheet dropdown-menu avatar badge separator skeleton chart
```

### Form Setup

```bash
npx shadcn@latest add field input button select checkbox radio-group switch textarea label
npm install react-hook-form @hookform/resolvers zod
```

### Marketing Page Setup

```bash
npx shadcn@latest add button card badge separator navigation-menu
npx shadcn@latest add @ss-blocks/hero-section-01
npx shadcn@latest add @ss-blocks/features-section-01
npx shadcn@latest add @ss-blocks/pricing-component-01
```

### Authentication Setup

```bash
npx shadcn@latest add field input button label card
npx shadcn@latest add @ss-blocks/login-page-01
```

## Component Composition

shadcn/ui components are building blocks. Compose them into feature components:

```typescript
// components/user-profile-card.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"

export function UserProfileCard({ user }: { user: User }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-4">
          <Avatar>
            <AvatarImage src={user.avatar} />
            <AvatarFallback>{user.initials}</AvatarFallback>
          </Avatar>
          <div>
            <CardTitle>{user.name}</CardTitle>
            <Badge variant={user.active ? "default" : "secondary"}>
              {user.role}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>{user.bio}</CardContent>
    </Card>
  )
}
```

## shadcn v4: `render` Prop Instead of `asChild`

shadcn v4 uses `@base-ui/react` (Base UI) instead of Radix by default. The `asChild` prop **does not exist** on Base UI components — it will cause a TypeScript error. Use the `render` prop instead. This applies to **all** compound components (SheetTrigger, DialogTrigger, DropdownMenuTrigger, etc.). Radix-based projects (`init -b radix`) still use `asChild`.

### Button as Link

The official Base UI Button docs explicitly warn: **do NOT use `<Button render={<a />} nativeButton={false} />` for links** — Base UI's Button always applies `role="button"`, which overrides link semantics. Use `buttonVariants()` on a plain `<a>` instead:

```typescript
import { buttonVariants } from "@/components/ui/button"

// Correct — a real link with button styling
<a href="/dashboard" className={buttonVariants()}>Go to Dashboard</a>

// Wrong — role="button" breaks link semantics
// <Button nativeButton={false} render={<a href="/dashboard" />}>Go</Button>

// Wrong — asChild does NOT exist on Base UI components
// <Button asChild><a href="/dashboard">Go</a></Button>
```

### Trigger Components (SheetTrigger, DialogTrigger, etc.)

When wrapping a custom element as a trigger, use `render` to compose the trigger with your component — this Base UI pattern remains correct:

```typescript
import { Sheet, SheetTrigger, SheetContent } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"

// Correct — SheetTrigger renders as a Button
<SheetTrigger render={<Button variant="ghost" size="icon" />}>
  <Menu className="h-5 w-5" />
</SheetTrigger>

// Wrong — asChild does NOT exist on Base UI components
// <SheetTrigger asChild><Button>Open</Button></SheetTrigger>
```

## Updating Components

To update to the latest version of a component, re-run the add command with `--overwrite`:

```bash
npx shadcn@latest add button --overwrite
```

This replaces the component file entirely. If you customized the component, back up your changes first.

## What This Skill Does NOT Cover

- Initial shadcn/ui setup -- see `setup` skill
- MCP-based component discovery -- see `mcp-tools` skill
- Theme and color configuration -- see `theme-configuration` skill
- Project structure and architecture -- see `project-scaffolding` skill
- Community registry search and catalog -- see `component-search` skill
