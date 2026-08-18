---
name: admin-customization
description: This skill should be used when the user asks to "customize the Payload admin panel", "swap in a custom React component", "build a custom field component", "create a custom admin view", "add a dashboard widget", "use useField/useForm", "change the admin logo or nav", "enable document locking", or "customize admin CSS" in PayloadCMS v3.
---

# PayloadCMS — Admin Panel Customization

The Payload v3 admin panel is a Next.js App Router application built on **React Server Components**. Almost every part of it — the nav, logo, dashboard, login screen, every view, and every field — is a swappable React component. Custom components default to Server Components (direct Local API access); add `'use client'` to opt into hooks and interactivity.

## How components are wired: the importMap

You never `import` a custom component into `payload.config.ts`. Instead you reference it by **string path**, and Payload resolves it through a generated import map. This keeps the config Node-safe and free of client code.

```ts
// payload.config.ts
admin: {
  components: {
    graphics: { Logo: '@/components/Logo' },     // default export
    Nav: '@/components/Nav#MyNav',               // named export via #
    beforeDashboard: ['@/components/Welcome'],   // array slots take a list
  },
}
```

- Default export → bare path. Named export → `path#ExportName`.
- Or use an object: `{ path: '@/components/Logo', exportName: 'Logo', clientProps: {...} }`.
- After adding/renaming a component, regenerate: `payload generate:importmap`. It also regenerates on dev startup and on HMR. **Never hand-edit `importMap.js`** — it is overwritten. (See the `setup` / `cli-recipes` skills for the command details.)

## Server vs Client Components

```tsx
// src/components/Welcome.tsx — Server Component (default)
import type { PayloadServerReactComponent } from 'payload'
import type { ServerProps } from 'payload'

const Welcome: PayloadServerReactComponent<React.FC<ServerProps>> = async ({ payload, user }) => {
  const { totalDocs } = await payload.count({ collection: 'posts' })
  return <div>Welcome, {user?.email}. You have {totalDocs} posts.</div>
}
export default Welcome
```

```tsx
// src/components/CounterWidget.tsx — Client Component
'use client'
import React, { useState } from 'react'

export default function CounterWidget() {
  const [n, setN] = useState(0)
  return <button onClick={() => setN(n + 1)}>Clicked {n}×</button>
}
```

Every component receives `payload` and `i18n` as default props. Pass your own with `clientProps` (serialized to the browser) or `serverProps` (server only). Payload strips non-serializable props before rendering Client Components.

## Three levels of swapping

**1 — Root** (`config.admin.components`): `Nav`, `graphics.Logo`, `graphics.Icon`, `logout.Button`, `header`, `actions`, `beforeDashboard`/`afterDashboard`, `beforeLogin`/`afterLogin`, `beforeNavLinks`/`afterNavLinks`, `settingsMenu`, `providers`, `views`. The account `avatar` lives at `config.admin.avatar`.

**2 — Collection / Global** (`collection.admin.components`): edit-view controls under `edit.*` (`SaveButton`, `PublishButton`, `PreviewButton`, `beforeDocumentControls`, `editMenuItems`, …), list-view slots (`beforeListTable`, `afterList`, …), and a shared `Description`. Globals use `admin.components.elements` for the same controls.

**3 — Field** (`field.admin.components`): `Field`, `Cell`, `Label`, `Description`, `Error`, `Filter`, `beforeInput`, `afterInput`, plus `RowLabel` on array fields.

The complete slot-by-slot catalog (with the props each receives) is in **`references/component-slots.md`**.

## Dashboard Widgets

The dashboard is modular: register widgets — data/analytics cards — via `admin.dashboard`:

```ts
admin: {
  dashboard: {
    widgets: [
      { Component: '@/widgets/OrdersToday' },   // + optional widget sizing per docs
    ],
    // defaultLayout: [...]  — omit to keep the built-in collections widget auto-included
  },
}
```

The built-in **collections widget** renders the collection/global cards and is auto-included whenever no `defaultLayout` is defined. `beforeDashboard` / `afterDashboard` still work for simple content injection around the dashboard. Regenerate the import map (`payload generate:importmap`) after adding widget components. Source: https://payloadcms.com/docs/custom-components/dashboard

## Custom Views and nav links

Register a key under `admin.components.views` to add a brand-new route, then add a nav link via `afterNavLinks`:

```ts
admin: {
  components: {
    views: {
      reports: { Component: '@/views/Reports', path: '/reports', exact: true, meta: { title: 'Reports' } },
    },
    afterNavLinks: ['@/components/ReportsNavLink'],
  },
}
```

Root views receive `AdminViewServerProps` (`req`, `payload`, `permissions`, …). You can also **override built-in document views** — `views.edit.default`, `views.edit.versions`, `views.edit.api` — or add a custom document **tab** (`tab: { label, href }`). List views can be fully replaced via `views.list` and wrap `DefaultListView` from `@payloadcms/ui` to keep the table.

## Custom Context providers

Wrap the whole panel with your own React context:

```ts
admin: { components: { providers: ['@/providers/TenantProvider'] } }
```

The provider component must render `children`. See `references/component-slots.md` for a full example.

## Admin React hooks

Client Components reach panel state through hooks from `@payloadcms/ui`. The essentials:

- `useField({ path })` — read/write a single field's value (the core of any custom `Field`).
- `useFormFields(selector)` / `useAllFormFields()` — reactively read other fields or dispatch updates.
- `useForm()` — programmatic `submit`, `validateForm`, `reset`, `setModified`.
- `useDocumentInfo()` — the active `id`, `collectionSlug`, `apiURL`, `docPermissions`.
- `usePayloadAPI(url)` — fetch REST data inside a view.
- `useConfig()`, `useAuth()`, `useLocale()`, `useTheme()`, `useTranslation()` — config, user, locale, theme, i18n.

Full return shapes and import examples are in **`references/react-hooks.md`**.

## Document locking

Payload locks a document while someone edits it, blocking concurrent updates/deletes on both the Local and REST APIs. It is **on by default** (5-minute idle expiry). Tune or disable per collection/global:

```ts
export const Posts: CollectionConfig = {
  slug: 'posts',
  lockDocuments: { duration: 600 },   // seconds of inactivity before the lock expires
  // lockDocuments: false,            // disable locking entirely
  fields: [/* … */],
}
```

`update`/`delete` accept `overrideLock` (defaults to `true`, ignoring locks) — pass `overrideLock: false` to respect an active lock.

## Page metadata

`admin.meta` controls panel-wide titles, descriptions, favicons, and Open Graph. Override per collection/global (`collection.admin.meta`) or per view (`meta` inside a view config):

```ts
admin: {
  meta: {
    title: 'Acme CMS',
    titleSuffix: ' — Acme',
    description: 'Acme content management',
    icons: [{ rel: 'icon', type: 'image/png', url: '/favicon.png' }],
    openGraph: { siteName: 'Acme', images: [{ url: '/og.png', width: 1200, height: 630 }] },
  },
}
```

## Customizing CSS

Point `admin.css` at a global stylesheet and override Payload's CSS variables. The admin UI uses BEM class names and CSS layers; custom CSS gets highest specificity by default.

```ts
admin: { css: path.resolve(dirname, 'styles/custom.scss') }
```

```scss
// styles/custom.scss
@layer payload-default {
  :root {
    --theme-elevation-0: #fafafa;
    --theme-success-500: #16a34a;
  }
  html[data-theme='dark'] {
    --theme-bg: #0b0b0c;
  }
}
.dashboard { padding-top: 2rem; } // target via BEM class names
```

Import Payload's SCSS to reuse its variables: `@import '~@payloadcms/ui/scss';`. When overriding colors, check both light and dark themes — Payload inverts elevation/status shades in dark mode.

<example>
**User**: "Show the order status as a colored badge in the Orders list view."

**Solution** — a custom `Cell` on the `status` field:
```tsx
// src/fields/StatusCell.tsx
'use client'
import type { DefaultCellComponentProps } from 'payload'

const COLORS: Record<string, string> = { paid: '#16a34a', pending: '#d97706', cancelled: '#dc2626' }

export default function StatusCell({ cellData }: DefaultCellComponentProps) {
  const status = String(cellData ?? 'unknown')
  return (
    <span style={{ background: COLORS[status] ?? '#888', color: '#fff', padding: '2px 8px', borderRadius: 12 }}>
      {status}
    </span>
  )
}
```
```ts
// On the Orders status field
{ name: 'status', type: 'select', options: ['paid', 'pending', 'cancelled'],
  admin: { components: { Cell: '@/fields/StatusCell' } } }
```
Then run `payload generate:importmap`.
</example>

<example>
**User**: "Add a 'Reports' page to the admin sidebar."

**Solution** — register a root view plus a nav link:
```tsx
// src/views/Reports.tsx — Server Component
import type { AdminViewServerProps } from 'payload'

export default async function Reports({ payload }: AdminViewServerProps) {
  const { totalDocs } = await payload.count({ collection: 'orders' })
  return <div style={{ padding: 24 }}><h1>Reports</h1><p>{totalDocs} orders</p></div>
}
```
```tsx
// src/components/ReportsNavLink.tsx
'use client'
import { Link } from '@payloadcms/ui'
export default function ReportsNavLink() { return <Link href="/admin/reports">Reports</Link> }
```
```ts
admin: { components: {
  views: { reports: { Component: '@/views/Reports', path: '/reports', exact: true } },
  afterNavLinks: ['@/components/ReportsNavLink'],
}}
```
</example>

## What this skill does NOT cover

- `setup` — installing Payload, the `payload generate:importmap` / `generate:types` workflow, and project bootstrapping.
- `collections` — the `admin` options recap on a CollectionConfig (`useAsTitle`, `defaultColumns`, `group`, live preview).
- `fields` — field types and their non-UI options.
- `lexical-editor` — building custom rich-text features and toolbar buttons.
- `cli-recipes` — the full CLI command reference.
