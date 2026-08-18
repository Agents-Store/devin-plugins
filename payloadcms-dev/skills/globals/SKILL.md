---
name: globals
description: This skill should be used when the user asks to "create a Payload global", "add site settings", "build a header/footer global", "define a GlobalConfig", "set global access control", "add hooks to a global", "fetch a global with the Local API", or needs to model any single-instance configuration (nav, homepage, announcement banner) in PayloadCMS v3.
---

# PayloadCMS — Globals

A Global is a **singleton** document — exactly one instance exists for its slug. Where a collection holds many rows, a Global holds one: site settings, the header, the footer, primary navigation, a homepage config, or an announcement banner. Like a collection, each Global is a typed document, a REST/GraphQL endpoint, an admin panel page, and an auto-generated TypeScript type — all from one config object.

## Global vs. single-doc collection

Reach for a **Global** when there is conceptually one and only one record, edited in place with no list view and no create/delete. Reach for a **collection** when you have (or might have) more than one — even "one per locale" or "one per tenant" is still a collection. If two Globals would share an identical field structure, model them as one collection instead.

## Minimal Global

```ts
// src/globals/Settings.ts
import type { GlobalConfig } from 'payload'

export const Settings: GlobalConfig = {
  slug: 'settings',
  label: 'Site Settings',
  fields: [
    { name: 'siteName', type: 'text', required: true },
    { name: 'siteDescription', type: 'textarea' },
  ],
}
```

Register it in `payload.config.ts`:
```ts
// src/payload.config.ts
import { Settings } from './globals/Settings'
import { Header } from './globals/Header'

export default buildConfig({
  globals: [Settings, Header],
})
```

Re-run `pnpm generate:types` after every global change. The slug `settings` produces a `Setting` (or `Settings`) interface in `payload-types.ts`.

## GlobalConfig Reference

| Property | Type | Purpose |
| --- | --- | --- |
| `slug` | `string` | **Required.** Unique key. Becomes `/api/globals/<slug>`, the DB table, and the type name. |
| `fields` | `Field[]` | **Required.** Document schema. See the `fields` skill. |
| `label` | `string` | Display name in the admin panel. Defaults to an inflected slug. |
| `description` | `string \| Component` | Helper text/React component shown under the header for editor context. |
| `access` | `object` | Permission rules — `read` / `update` only. See below. |
| `hooks` | `object` | Lifecycle callbacks. See below. |
| `versions` | `boolean \| object` | Enable version history / drafts. |
| `admin` | `object` | Admin panel behavior (group, description, preview, livePreview). |
| `endpoints` | `Endpoint[]` | Custom REST routes scoped to this global. |
| `graphQL` | `object \| false` | Customize (`name`, `disableQueries`, `disableMutations`) or disable GraphQL. |
| `typescript` | `{ interface: string }` | Override the generated TS interface name. |
| `custom` | `object` | Extension point for plugin metadata. |
| `dbName` | `string` | Custom DB table/collection name. |
| `lockDocuments` | `object \| false` | Document-locking behavior in the admin UI. |
| `forceSelect` | `object` | Fields always returned regardless of `select`. |

## `admin` Options

```ts
// src/globals/Header.ts
admin: {
  group: 'Configuration',                 // Sidebar grouping; `false` hides nav entry
  hidden: false,                          // or (user) => boolean — hides from nav, keeps routes
  description: 'Primary site navigation',
  preview: (doc, { req }) =>              // "Preview" button URL
    `${process.env.NEXT_PUBLIC_SITE_URL}/preview?secret=${process.env.PREVIEW_SECRET}`,
  livePreview: {
    url: ({ data, locale }) =>
      `${process.env.NEXT_PUBLIC_SITE_URL}?draft=true&locale=${locale?.code}`,
    breakpoints: [
      { name: 'mobile', width: 375, height: 667, label: 'Mobile' },
      { name: 'desktop', width: 1440, height: 900, label: 'Desktop' },
    ],
  },
}
```

## Access Control

Globals have **only two** access functions — `read` and `update`. There is no `create` or `delete` (a singleton is created on first save and never deleted). Versioned globals also accept `readVersions`.

```ts
// src/globals/Settings.ts
access: {
  read: () => true,                                   // Public read
  update: ({ req: { user } }) => user?.role === 'admin',
  readVersions: ({ req: { user } }) => Boolean(user), // Versioned globals only
}
```

Each function receives `{ req }` (with the authenticated `req.user`); `update` also receives `data` (the incoming update payload). Return a boolean, or a `where` query constraint to restrict access dynamically. See the `access-control` skill for the full pattern.

## Hooks

Globals expose six lifecycle hooks, each an array of sync or async functions:

| Hook | Fires | Common use |
| --- | --- | --- |
| `beforeOperation` | Before any operation begins | Mutate `args`, side-effects |
| `beforeValidate` | On `update`, before validation | Format/normalize incoming `data` |
| `beforeChange` | After validation, before save | Final data shaping (data is valid) |
| `afterChange` | After the global is saved | Purge caches, sync to CRM, revalidate |
| `beforeRead` | Before `findOne` output transform | Inspect all locales / hidden fields |
| `afterRead` | Last step before returning to client | Computed/derived fields |

```ts
// src/globals/Settings.ts
import type { GlobalConfig } from 'payload'

export const Settings: GlobalConfig = {
  slug: 'settings',
  hooks: {
    afterChange: [
      async ({ doc, previousDoc, req }) => {
        // Revalidate the front-end when settings change
        await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?tag=settings`)
        return doc
      },
    ],
  },
  fields: [/* ... */],
}
```

Mutating hooks (`beforeValidate`, `beforeChange`) return the (modified) `data`; read hooks return `doc`. See the `hooks` skill for full argument tables.

## Reading & Writing — Local API

```ts
// Read the global (server-side, fully typed)
const header = await payload.findGlobal({
  slug: 'header',
  depth: 2,          // Resolve relationships 2 levels deep
  locale: 'en',      // Localized field values for this locale
  fallbackLocale: false,
})

// Update the global (data is merged into the single instance)
const updated = await payload.updateGlobal({
  slug: 'settings',
  data: { siteName: 'Acme' },
  depth: 1,
  locale: 'en',
})
```

`findGlobal` also accepts `overrideAccess`, `user`, `showHiddenFields`; `updateGlobal` additionally accepts `overrideLock`. `depth` and `locale` work exactly as they do for collection queries — see the `queries` skill.

## Reading & Writing — REST & GraphQL

```http
GET   /api/globals/header?depth=2&locale=en
POST  /api/globals/settings        # body: JSON of fields to update (REST updates globals via POST)
```

GraphQL auto-generates a query and a mutation per global (e.g. `Header` and `updateHeader`). Customize the GraphQL type name or disable operations via `graphQL: { name, disableQueries, disableMutations }`, or turn it off entirely with `graphQL: false`.

## Versions, Drafts & Localization

Enable version history (and optional drafts) the same way collections do:

```ts
// src/globals/Homepage.ts
versions: {
  drafts: { autosave: { interval: 800 }, schedulePublish: true },
  max: 20,    // Keep the last 20 versions
}
```

A draft-enabled global gains a `_status` field; fetch the working draft with `payload.findGlobal({ slug: 'homepage', draft: true })`. Any field inside a global can be `localized: true`, in which case `findGlobal`/`updateGlobal` resolve values for the requested `locale`. See the `localization` skill for the localized-field model.

## Project Structure

```txt
src/
├── globals/
│   ├── Settings.ts     # Site-wide config
│   ├── Header.ts       # Localized nav
│   └── Footer.ts
├── payload.config.ts
```

Keep each global in its own file; co-locate access functions and hooks in sibling files (`Header.access.ts`, `Header.hooks.ts`) as globals grow.

<example>
**User**: "Build a Header global with localized nav items linking to pages, public read, and admin-only update, grouped under 'Configuration'."

**Solution**:
```ts
// src/globals/Header.ts
import type { GlobalConfig } from 'payload'

export const Header: GlobalConfig = {
  slug: 'header',
  label: 'Header',
  access: {
    read: () => true,
    update: ({ req: { user } }) => user?.role === 'admin',
  },
  admin: {
    group: 'Configuration',
    description: 'Primary site navigation',
  },
  fields: [
    {
      name: 'navItems',
      type: 'array',
      maxRows: 8,
      fields: [
        { name: 'label', type: 'text', required: true, localized: true },
        { name: 'page', type: 'relationship', relationTo: 'pages', required: true },
      ],
    },
  ],
}
```

Register `Header` in `globals: [...]`, then read it on the server:
```ts
const header = await payload.findGlobal({ slug: 'header', depth: 1, locale: 'en' })
```
</example>

<example>
**User**: "Add an afterChange hook to my Settings global that revalidates the cache."

**Solution**:
```ts
// src/globals/Settings.ts
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?tag=settings`)
      req.payload.logger.info('Settings updated — cache revalidated')
      return doc
    },
  ],
}
```
</example>

## What this skill does NOT cover

- **Field types** inside a global (`text`, `array`, `relationship`, `richText`, etc.) → `fields` skill.
- **Multi-document content types** and the full config → `collections` skill.
- **Access function signatures, `where` constraints, role logic** → `access-control` skill.
- **Hook argument tables and execution order** → `hooks` skill.
- **`depth`, `locale`, `where`, pagination, draft querying** → `queries` skill.
- **Localized fields, locale config, fallbacks** → `localization` skill.
