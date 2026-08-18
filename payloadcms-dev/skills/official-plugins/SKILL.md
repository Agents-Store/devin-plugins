---
name: official-plugins
description: This skill should be used when the user asks to "add the SEO plugin", "use plugin-form-builder", "set up multi-tenant", "add full-text search", "integrate Stripe", "add redirects", "configure the Payload Sentry plugin", "import/export data", "use the Payload MCP plugin", or "which official Payload plugin should I use" — installing and configuring the official @payloadcms/plugin-* packages in PayloadCMS v3.
---

# PayloadCMS — Official Plugins

Payload ships a family of first-party plugins (`@payloadcms/plugin-*`) that add common CMS features — SEO, forms, search, redirects, multi-tenancy, Stripe billing, and more — without hand-writing the collections, fields, and hooks yourself. This skill covers **installing and wiring them up**. To author your own plugin from scratch, use the `plugin-development` skill instead.

## How Plugins Compose

A Payload plugin is a curried function: `plugin(options)` returns a config transformer `(config) => config`.

```ts
type Plugin = (incomingConfig: Config) => Config
// official factories are: (options) => Plugin
```

You wire the **result** of calling the factory into the `plugins` array:

```ts
// src/payload.config.ts
import { buildConfig } from 'payload'
import { seoPlugin } from '@payloadcms/plugin-seo'
import { redirectsPlugin } from '@payloadcms/plugin-redirects'

export default buildConfig({
  // collections, db, etc.
  plugins: [
    seoPlugin({ collections: ['pages'] }),
    redirectsPlugin({ collections: ['pages'] }),
  ],
})
```

Three things to keep in mind:

- **Order matters.** Plugins run top-to-bottom, each receiving the config the previous one produced. Put a plugin that consumes another's output later in the array.
- **Timing.** Plugins execute *after* the incoming config is validated but *before* it is sanitized and defaults are merged — so they see your raw collections.
- **They mutate the schema.** Plugins add collections (`forms`, `search`, `redirects`…), inject fields (`meta`, `parent`, `breadcrumbs`, `stripeID`…), and append hooks. That means **you must re-run type generation after installing or reconfiguring one**.

## Installing

Same for every package — just swap the name:

```bash
pnpm add @payloadcms/plugin-seo
# then, every time you add or change a plugin:
pnpm generate:types
```

On SQL adapters (Postgres/SQLite), a new collection or field also needs a migration: `pnpm payload migrate:create`. See the `adapters` skill for DB specifics.

## The Plugins at a Glance

| Plugin | Package | What it adds | Use when |
| --- | --- | --- | --- |
| SEO | `@payloadcms/plugin-seo` | Meta group (title/description/image) + Google-snippet preview + auto-gen hooks | You need editable, previewable SEO metadata on pages/posts |
| Form Builder | `@payloadcms/plugin-form-builder` | `forms` + `form-submissions` collections, email actions, redirects | Editors must build contact/lead forms without code |
| Nested Docs | `@payloadcms/plugin-nested-docs` | `parent` relationship + computed `breadcrumbs` | You need parent/child page trees and nested URLs |
| Search | `@payloadcms/plugin-search` | Indexed `search` collection synced via hooks | You want fast native search with no third-party service |
| Stripe | `@payloadcms/plugin-stripe` | Two-way sync, `stripeID` field, webhook + REST proxy routes | Stripe handles billing; Payload owns content/logic |
| Multi-Tenant | `@payloadcms/plugin-multi-tenant` | `tenants` collection + tenant field/selector + scoped access | One admin panel serves many isolated tenants |
| Redirects | `@payloadcms/plugin-redirects` | `redirects` collection (`from`/`to`/type) | Editors manage 301/302 redirects after a URL restructure |
| Sentry | `@payloadcms/plugin-sentry` | Error + performance reporting into Sentry | You run on Next.js and want server-side error tracking |
| Import/Export | `@payloadcms/plugin-import-export` | Export/Import buttons + exports collection (CSV/JSON) | Bulk data ops, migrations, spreadsheet workflows |
| MCP | `@payloadcms/plugin-mcp` | `/api/mcp` endpoint + API-keys collection + auto CRUD tools | You want AI agents (Claude/Cursor) to read/write content |
| Ecommerce | `@payloadcms/plugin-ecommerce` | Products/variants, carts, orders, transactions, payment adapters | You need a storefront backend, not just billing |

The most common three or four are shown inline below; the rest (plus full option tables and longer snippets) live in `references/plugin-catalog.md`.

## SEO — `@payloadcms/plugin-seo`

```ts
// src/payload.config.ts
import { seoPlugin } from '@payloadcms/plugin-seo'

export default buildConfig({
  plugins: [
    seoPlugin({
      collections: ['pages', 'posts'],
      uploadsCollection: 'media',          // upload collection for the meta image
      tabbedUI: true,                       // add an "SEO" tab
      generateTitle: ({ doc }) => `Acme — ${doc.title}`,
      generateDescription: ({ doc }) => doc.excerpt,
      generateURL: ({ doc }) =>
        `${process.env.NEXT_PUBLIC_SITE_URL}/${doc.slug}`,
    }),
  ],
})
```

Key options: `collections`, `globals`, `uploadsCollection`, `tabbedUI`, `fields`, the four `generate*` functions, and `interfaceName`. Full table in the catalog.

## Form Builder — `@payloadcms/plugin-form-builder`

```ts
// src/payload.config.ts
import { formBuilderPlugin } from '@payloadcms/plugin-form-builder'

export default buildConfig({
  plugins: [
    formBuilderPlugin({
      fields: { text: true, textarea: true, email: true, select: true },
      redirectRelationships: ['pages'],   // collections offered in the redirect field
      defaultToEmail: 'leads@acme.com',
    }),
  ],
})
```

Adds the `forms` and `form-submissions` collections. Toggle field types with `fields`, transform outgoing mail with `beforeEmail`, and reshape the generated collections with `formOverrides` / `formSubmissionOverrides`.

## Search — `@payloadcms/plugin-search`

```ts
// src/payload.config.ts
import { searchPlugin } from '@payloadcms/plugin-search'

export default buildConfig({
  plugins: [
    searchPlugin({
      collections: ['pages', 'posts'],
      defaultPriorities: { pages: 10, posts: 20 },   // ranking weights
    }),
  ],
})
```

Creates one indexed `search` collection and keeps it in sync via hooks. Use `beforeSync` to denormalize extra fields into the index and `searchOverrides` to extend the search collection. Query it at `/api/search`.

## Redirects — `@payloadcms/plugin-redirects`

```ts
// src/payload.config.ts
import { redirectsPlugin } from '@payloadcms/plugin-redirects'

export default buildConfig({
  plugins: [
    redirectsPlugin({
      collections: ['pages', 'posts'],   // selectable as redirect targets
      redirectTypes: ['301', '302'],
    }),
  ],
})
```

Adds a `redirects` collection with `from`, `to` (relationship or custom URL), and a status type. Consume it in Next.js middleware by querying `/api/redirects`.

## Everything Else

Stripe, Multi-Tenant, Nested Docs, Sentry, Import/Export, MCP, and Ecommerce follow the identical pattern — install the package, call the factory in `plugins`, regenerate types. Their package names, minimal snippets, and full option tables are in `references/plugin-catalog.md`. Quick reminders:

- **Stripe** needs `STRIPE_SECRET_KEY` + `STRIPE_WEBHOOKS_ENDPOINT_SECRET` env vars and a webhook endpoint (`/api/stripe/webhooks`) registered in the Stripe dashboard.
- **Sentry** requires the `@sentry/nextjs` peer dependency and an initialized `Sentry` instance passed as `{ Sentry }`.
- **Multi-Tenant** takes a `collections` *map* (`{ pages: {} }`), not an array.
- **Import/Export** takes `collections` as `{ slug }[]` objects, and async jobs need a running jobs queue.
- **MCP** exposes `/api/mcp` and needs a Bearer API key created in the `MCP → API Keys` admin collection.

## Choosing a Plugin

- "Editors need to manage X without code" → there's probably a plugin (forms, redirects, SEO, import/export).
- "I need a thing synced to an external service" → Stripe (billing), Search (internal index), Sentry (errors), MCP (agents).
- "I need site structure" → Nested Docs (hierarchy), Multi-Tenant (isolation).
- Storefront (cart/checkout/orders) → Ecommerce; billing only → Stripe.
- If no official plugin fits, author your own with the `plugin-development` skill.

Plugins also stack cleanly: a typical content site runs SEO + Redirects + Search + Form Builder together, and a SaaS adds Stripe (or Ecommerce) + Multi-Tenant on top. Because each one only transforms the config, combining them is just more entries in the `plugins` array — order them so any consumer (e.g. Search indexing SEO-managed fields) comes after its producer, then regenerate types once at the end.

## Common Gotchas

- **Forgot `pnpm generate:types`** — TypeScript won't know about `meta`, `breadcrumbs`, `stripeID`, or the new `forms`/`search`/`redirects` collections until you regenerate. On SQL adapters, also `pnpm payload migrate:create`.
- **Calling the plugin without invoking the factory** — write `seoPlugin({ ... })`, not `seoPlugin`. The array holds the *result* of the call, not the factory itself.
- **`collections` shape varies** — it's an array of slugs for SEO/Search/Redirects/Nested Docs, a `{ slug }[]` for Import/Export, and a *map* (`{ pages: {} }`) for Multi-Tenant and MCP. Match each plugin's expected shape.
- **Slug collisions** — these plugins add fixed collection slugs (`forms`, `search`, `redirects`, `tenants`…). If you already have a collection by that name, rename yours or use the plugin's `*Overrides` / `*Slug` option.

<example>
**User**: "On our marketing site I want SEO fields on pages and posts, plus editor-managed 301 redirects."

**Solution**:
```ts
// src/payload.config.ts
import { buildConfig } from 'payload'
import { seoPlugin } from '@payloadcms/plugin-seo'
import { redirectsPlugin } from '@payloadcms/plugin-redirects'

export default buildConfig({
  plugins: [
    seoPlugin({
      collections: ['pages', 'posts'],
      uploadsCollection: 'media',
      tabbedUI: true,
      generateTitle: ({ doc }) => `Acme — ${doc.title}`,
    }),
    redirectsPlugin({
      collections: ['pages', 'posts'],
      redirectTypes: ['301', '302'],
      overrides: { admin: { group: 'SEO' } },
    }),
  ],
})
```
Then `pnpm add @payloadcms/plugin-seo @payloadcms/plugin-redirects` and `pnpm generate:types`. Read redirects from Next.js middleware via `/api/redirects`.
</example>

<example>
**User**: "Add full-text search to my docs and posts, but skip drafts."

**Solution**:
```ts
// src/payload.config.ts
import { searchPlugin } from '@payloadcms/plugin-search'

export default buildConfig({
  plugins: [
    searchPlugin({
      collections: ['docs', 'posts'],
      syncDrafts: false,
      defaultPriorities: { docs: 20, posts: 10 },
    }),
  ],
})
```
After `pnpm generate:types`, hit `/api/search?where[title][like]=onboarding` from your frontend search bar.
</example>

## What this skill does NOT cover

- **`plugin-development`** — authoring your *own* reusable Payload plugin (the curried factory, package layout, publishing).
- **`access-control`** — rolling your own multi-tenancy or row-level rules when the Multi-Tenant plugin's config-driven model isn't enough.
- **`fields`** — the field types these plugins inject and how to extend them via `fields`/`searchOverrides`.
- **`adapters`** — the database, storage, and email env/webhook wiring Stripe, Import/Export, and Search sit alongside.
