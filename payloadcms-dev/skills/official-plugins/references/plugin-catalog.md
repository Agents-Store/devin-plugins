# Official Payload Plugins — Full Catalog

Detailed config reference for every official `@payloadcms/plugin-*` package. Each plugin is a curried factory: `plugin(options)` returns a config transformer that runs **after** the incoming config is validated but **before** it is sanitized. Add the result to `plugins: [...]` in `payload.config.ts`. After installing or reconfiguring any plugin, run `pnpm generate:types` (and, on SQL adapters, `pnpm payload migrate:create`) because most plugins inject collections and/or fields.

Install pattern is the same for all: `pnpm add @payloadcms/plugin-<name>` (or `npm i` / `yarn add`).

---

## SEO — `@payloadcms/plugin-seo`

Adds a meta group (title, description, image) to collections/globals, an admin preview of the Google snippet, and auto-generation hooks.

```ts
// src/payload.config.ts
import { seoPlugin } from '@payloadcms/plugin-seo'

export default buildConfig({
  plugins: [
    seoPlugin({
      collections: ['pages', 'posts'],
      globals: ['home'],
      uploadsCollection: 'media',     // upload collection used for the meta image field
      tabbedUI: true,                 // append an "SEO" tab instead of a flat group
      interfaceName: 'SeoMeta',       // name of the generated TS/GraphQL interface
      generateTitle: ({ doc }) => `Acme — ${doc.title}`,
      generateDescription: ({ doc }) => doc.excerpt,
      generateImage: ({ doc }) => doc.heroImage,
      generateURL: ({ doc }) =>
        `${process.env.NEXT_PUBLIC_SITE_URL}/${doc.slug}`,
      fields: ({ defaultFields }) => [
        ...defaultFields,
        { name: 'canonicalURL', type: 'text' },
      ],
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `collections` | Collection slugs to add the SEO group to |
| `globals` | Global slugs to add the SEO group to |
| `uploadsCollection` | Upload collection slug for the meta-image relationship |
| `tabbedUI` | Append an SEO tab (default `false`) — needs all fields tab-wrapped |
| `fields` | `({ defaultFields }) => Field[]` — extend/replace the SEO fields |
| `generateTitle` / `generateDescription` / `generateImage` / `generateURL` | Auto-generation + preview functions, receive `{ doc, locale, req }` |
| `interfaceName` | Custom name for the generated TypeScript/GraphQL interface |

---

## Form Builder — `@payloadcms/plugin-form-builder`

Adds two collections — `forms` (admin-built form definitions) and `form-submissions` (captured entries) — plus confirmation messages, email actions, and redirects.

```ts
// src/payload.config.ts
import { formBuilderPlugin } from '@payloadcms/plugin-form-builder'

export default buildConfig({
  plugins: [
    formBuilderPlugin({
      fields: {
        text: true,
        textarea: true,
        select: true,
        email: true,
        checkbox: true,
        number: true,
        message: true,
        payment: false,
      },
      redirectRelationships: ['pages'],   // collections selectable in the redirect field
      defaultToEmail: 'leads@acme.com',
      beforeEmail: (emails) =>
        emails.map((e) => ({ ...e, html: wrapBrandTemplate(e.html) })),
      formOverrides: {
        slug: 'contact-forms',
        admin: { group: 'Forms' },
      },
      formSubmissionOverrides: {
        admin: { group: 'Forms' },
      },
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `fields` | Toggle which field types editors can add: `text`, `textarea`, `select`, `radio`, `email`, `state`, `country`, `checkbox`, `date`, `number`, `message`, `payment`, `upload` |
| `redirectRelationships` | Collection slugs offered in the post-submit redirect field |
| `defaultToEmail` | Fallback recipient when a form has no `to` set |
| `beforeEmail` | Transform the email array before send (branding, BCC, etc.) |
| `handlePayment` | Callback to charge when the `payment` field type is used |
| `formOverrides` | Partial `CollectionConfig` merged into the `forms` collection |
| `formSubmissionOverrides` | Partial `CollectionConfig` merged into `form-submissions` |

Since 3.86, the plugin's fields support translations (i18n of the form-builder field labels).

---

## Nested Docs — `@payloadcms/plugin-nested-docs`

Adds a self-referencing `parent` relationship and a computed `breadcrumbs` array to a collection so you can build parent/child page trees and nested URLs.

```ts
// src/payload.config.ts
import { nestedDocsPlugin } from '@payloadcms/plugin-nested-docs'

export default buildConfig({
  plugins: [
    nestedDocsPlugin({
      collections: ['pages', 'categories'],
      generateLabel: (_, doc) => String(doc.title),
      generateURL: (docs) =>
        docs.reduce((url, doc) => `${url}/${String(doc.slug)}`, ''),
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `collections` | Collection slugs to enable nesting on |
| `generateLabel` | `(docs, currentDoc) => string` — breadcrumb label per level |
| `generateURL` | `(docs, currentDoc) => string` — full URL built from ancestors |
| `parentFieldSlug` | Override the auto-added `parent` field name |
| `breadcrumbsFieldSlug` | Override the auto-added `breadcrumbs` field name |

---

## Search — `@payloadcms/plugin-search`

Creates a single indexed `search` collection and keeps it in sync with the source collections via hooks, giving you fast database-native full-text search with no external service.

```ts
// src/payload.config.ts
import { searchPlugin } from '@payloadcms/plugin-search'

export default buildConfig({
  plugins: [
    searchPlugin({
      collections: ['pages', 'posts'],
      defaultPriorities: { pages: 10, posts: 20 },
      syncDrafts: false,
      deleteDrafts: true,
      beforeSync: ({ originalDoc, searchDoc }) => ({
        ...searchDoc,
        excerpt: originalDoc.excerpt,   // copy extra fields into the index
      }),
      searchOverrides: {
        fields: ({ defaultFields }) => [
          ...defaultFields,
          { name: 'excerpt', type: 'text' },
        ],
      },
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `collections` | Source collection slugs to index |
| `defaultPriorities` | Per-collection ranking weight (number or function) |
| `beforeSync` | Reshape the search doc before write (denormalize fields) |
| `searchOverrides` | Override the generated `search` collection (extra fields, access) |
| `syncDrafts` | Index drafts too (default `false`) |
| `deleteDrafts` | Remove an entry when a doc becomes a draft (default `true`) |
| `localize` | Localize the search `title` field (default `true` if localization is on) |
| `reindexBatchSize` | Docs per batch during reindex (default `50`) |

Query the index from the frontend by hitting `/api/search?where[title][like]=...`.

---

## Stripe — `@payloadcms/plugin-stripe`

Two-way sync between Payload collections and Stripe resources. Adds a `/api/stripe/rest` proxy (dev), a `/api/stripe/webhooks` route, `stripeID` + `skipSync` fields on synced collections, and admin links to Stripe.

```ts
// src/payload.config.ts
import { stripePlugin } from '@payloadcms/plugin-stripe'

export default buildConfig({
  plugins: [
    stripePlugin({
      stripeSecretKey: process.env.STRIPE_SECRET_KEY,
      stripeWebhooksEndpointSecret: process.env.STRIPE_WEBHOOKS_ENDPOINT_SECRET,
      isTestKey: process.env.NODE_ENV !== 'production',
      rest: false,            // expose /api/stripe/rest proxy — dev only, keep off in prod
      logs: true,
      sync: [
        {
          collection: 'customers',
          stripeResourceType: 'customers',
          stripeResourceTypeSingular: 'customer',
          fields: [
            { fieldPath: 'name', stripeProperty: 'name' },
            { fieldPath: 'email', stripeProperty: 'email' },
          ],
        },
      ],
      webhooks: {
        'customer.subscription.updated': ({ event, payload }) => {
          /* react to Stripe events */
        },
      },
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `stripeSecretKey` * | Stripe secret key (required) |
| `stripeWebhooksEndpointSecret` | Signing secret for the webhook route |
| `isTestKey` | Flags the key as a test key |
| `rest` | Enable the `/api/stripe/rest` proxy (development only) |
| `webhooks` | Object/function of handlers keyed by Stripe event name |
| `sync` | Field-by-field two-way sync config between collections and Stripe |
| `logs` | Console-log sync activity |

Env vars: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOKS_ENDPOINT_SECRET`. The webhook route must be reachable by Stripe; configure the endpoint in the Stripe dashboard pointing at `/api/stripe/webhooks`. See the `adapters` skill for the email/storage env wiring this commonly sits alongside.

---

## Multi-Tenant — `@payloadcms/plugin-multi-tenant`

Adds a `tenant` relationship + tenant selector to chosen collections and a `tenants` collection, scoping data and access by tenant from inside one admin panel.

```ts
// src/payload.config.ts
import { multiTenantPlugin } from '@payloadcms/plugin-multi-tenant'
import type { Config } from './payload-types'

export default buildConfig({
  plugins: [
    multiTenantPlugin<Config>({
      collections: {
        pages: {},
        products: {},
      },
      tenantsSlug: 'tenants',
      userHasAccessToAllTenants: (user) =>
        Boolean(user?.roles?.includes('super-admin')),
      cleanupAfterTenantDelete: true,
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `collections` | Map of collection slug → per-collection tenant options |
| `tenantsSlug` | Slug of the tenants collection (default `'tenants'`) |
| `tenantField` | Override the injected tenant field config |
| `userHasAccessToAllTenants` | Predicate that marks a user a cross-tenant super-admin |
| `useTenantsCollectionAccess` | Apply tenant constraints to the tenants collection itself |
| `cleanupAfterTenantDelete` | Delete tenant-scoped docs when a tenant is removed (default `true`) |
| `basePath` | App base path (for tenant routing) |

This is config-driven tenancy. For bespoke rules (row-level checks, custom JWT claims), hand-roll it — see the `access-control` skill.

---

## Redirects — `@payloadcms/plugin-redirects`

Adds a `redirects` collection with `from`, `to` (a relationship to your chosen collections or a custom URL), and a redirect type (301/302), so editors manage URL redirects without code.

```ts
// src/payload.config.ts
import { redirectsPlugin } from '@payloadcms/plugin-redirects'

export default buildConfig({
  plugins: [
    redirectsPlugin({
      collections: ['pages', 'posts'],
      redirectTypes: ['301', '302'],
      overrides: {
        admin: { group: 'SEO' },
      },
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `collections` | Slugs offered as targets in the `to` relationship |
| `redirectTypes` | Allowed status codes (e.g. `['301', '302']`) |
| `overrides` | Partial `CollectionConfig` merged into the `redirects` collection |
| `redirectTypeFieldOverride` | Customize the redirect-type field |

Consume in Next.js middleware or `next.config` by querying `/api/redirects`.

---

## Sentry — `@payloadcms/plugin-sentry`

Wires Payload errors and performance data into Sentry. Requires the `@sentry/nextjs` peer dependency and an initialized `Sentry` instance.

```ts
// src/payload.config.ts
import { sentryPlugin } from '@payloadcms/plugin-sentry'
import * as Sentry from '@sentry/nextjs'

export default buildConfig({
  plugins: [
    sentryPlugin({
      Sentry,
      enabled: process.env.NODE_ENV === 'production',
      captureErrors: [400, 403, 404],   // status codes to capture beyond 500+
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `Sentry` * | Your initialized `@sentry/nextjs` instance (required) |
| `enabled` | Toggle the plugin (default `true`) |
| `captureErrors` | Extra HTTP status codes to report (500+ captured by default) |
| `context` | Function to attach extra contextual data to captured events |

Install: `pnpm add @payloadcms/plugin-sentry @sentry/nextjs`, then configure Sentry normally (`sentry.client/server.config.ts`, DSN env var).

---

## Import / Export — `@payloadcms/plugin-import-export`

Adds Export/Import buttons to collection list views and an exports collection that stores generated CSV/JSON files; large jobs run through the jobs queue.

```ts
// src/payload.config.ts
import { importExportPlugin } from '@payloadcms/plugin-import-export'

export default buildConfig({
  plugins: [
    importExportPlugin({
      collections: [{ slug: 'pages' }, { slug: 'users' }],
      disableJobsQueue: false,
      format: 'csv',
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `collections` | `{ slug }[]` of collections to enable import/export on |
| `exportLimit` / `importLimit` | Global document caps (`0` = unlimited) |
| `overrideExportCollection` / `overrideImportCollection` | Customize the generated exports/imports collections |
| `disableJobsQueue` | Run synchronously instead of queued |
| `disableDownload` / `disableSave` | Hide the download / save-to-collection buttons |
| `format` | Force `'csv'` or `'json'` |

CSV uses underscore notation for nested fields; JSON preserves structure. Async jobs need a running jobs queue.

---

## MCP — `@payloadcms/plugin-mcp`

Exposes your collections/globals to MCP clients (Claude, Cursor, VS Code) over an `/api/mcp` HTTP endpoint, auto-generating one tool per enabled CRUD operation and gating access with Bearer API keys.

```ts
// src/payload.config.ts
import { mcpPlugin } from '@payloadcms/plugin-mcp'

export default buildConfig({
  plugins: [
    mcpPlugin({
      collections: {
        posts: { enabled: true, description: 'Blog posts' },
        pages: { enabled: { find: true, update: true } },
      },
      globals: {
        home: { enabled: { find: true } },
      },
      userCollection: 'users',
    }),
  ],
})
```

| Option | Purpose |
| --- | --- |
| `collections[slug].enabled` | Toggle `find`/`create`/`update`/`delete` per collection (bool or per-op object) |
| `collections[slug].description` | Per-collection description surfaced to MCP clients |
| `collections[slug].overrideResponse` | Strip sensitive fields before models see them (per collection) |
| `globals[slug].enabled` | Toggle `find`/`update` per global |
| `mcp.tools` | Custom tools beyond CRUD |
| `mcp.prompts` / `mcp.resources` | MCP prompts and resources |
| `mcp.handlerOptions` | `{ verboseLogs, maxDuration, onEvent }` — MCP request-handler tuning |
| `mcp.serverOptions.serverInfo` | Server name/version reported to clients (default name "Payload MCP Server") |
| `userCollection` | Auth collection that owns the MCP API keys (defaults to `config.admin.user`) |
| `overrideApiKeyCollection` | Customize the auto-generated MCP API Keys collection |
| `overrideAuth` | Replace the built-in Bearer API-key auth |

What it adds: the `/api/mcp` endpoint, an `MCP → API Keys` admin collection, auto tools like `findPosts`/`createPosts`, and Bearer-token auth (`Authorization: Bearer <API-KEY>`). Create a key in the admin panel and grant per-key permissions before connecting a client.

---

## Ecommerce — `@payloadcms/plugin-ecommerce`

A full storefront backend — still **Beta** (breaking changes possible). Adds managed **Products** (with **Variants**), **Carts**, **Orders**, **Transactions**, and **Addresses** collections, plus a payment-adapter pattern and React frontend utilities exported from the same package.

```ts
// src/payload.config.ts
import { ecommercePlugin } from '@payloadcms/plugin-ecommerce'
import { stripeAdapter } from '@payloadcms/plugin-ecommerce/payments/stripe'

export default buildConfig({
  plugins: [
    ecommercePlugin({
      // Required: access functions the plugin's collections use
      access: {
        adminOnlyFieldAccess,
        adminOrPublishedStatus,
        isAdmin,
        isAuthenticated,
        isCustomer,
        isDocumentOwner,
      },
      // Required: which auth collection acts as customers
      customers: { slug: 'users' },
      // Payments via the adapter pattern — Stripe is the default adapter;
      // implement the PaymentAdapter interface for custom providers
      payments: { paymentMethods: [stripeAdapter({ /* keys, webhooks */ })] },
    }),
  ],
})
```

Use it when you need cart/checkout/orders rather than just billing — for billing-only SaaS, reach for the Stripe plugin instead. Shipping, taxes, and subscriptions are **not** natively handled. Docs: https://payloadcms.com/docs/ecommerce/overview
