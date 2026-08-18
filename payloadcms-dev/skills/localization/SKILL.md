---
name: localization
description: This skill should be used when the user asks to "add localization to Payload", "translate content into multiple languages", "configure locales", "make a field localized", "set a fallback locale", "internationalize the admin UI", "query a specific locale", or "add a language to the admin panel" in PayloadCMS v3.
---

# PayloadCMS — Localization & i18n

Payload separates two concerns that are easy to confuse. **Localization** is about your *content* — storing the same document in many languages (`title` in English, Spanish, German). **i18n** is about the *admin panel UI* — the labels, buttons, and messages editors see while working. Configure them independently: `localization` and `i18n` are sibling keys in `payload.config.ts`.

## Enabling Localization

Add the `localization` object to your config. The simplest form lists locale codes as strings:

```ts
// src/payload.config.ts
import { buildConfig } from 'payload'

export default buildConfig({
  localization: {
    locales: ['en', 'es', 'de'],
    defaultLocale: 'en',
    fallback: true,
  },
  // ...collections, db, etc.
})
```

For richer control — display labels in the locale selector and right-to-left scripts — use the object form:

```ts
// src/payload.config.ts
localization: {
  locales: [
    { label: 'English', code: 'en' },
    { label: 'Español', code: 'es' },
    { label: 'العربية', code: 'ar', rtl: true },
  ],
  defaultLocale: 'en',
  fallback: true,
},
```

### Localization Config Reference

| Option | Type | Purpose |
| --- | --- | --- |
| `locales` | `string[]` \| `LocaleObject[]` | Supported languages. Strings are shorthand; objects unlock `label` and `rtl`. |
| `defaultLocale` | `string` | **Required.** Code returned when no `locale` is specified on a request. Must match a code in `locales`. |
| `fallback` | `boolean` | Default `true`. When a field has no value in the requested locale, fall back to `defaultLocale`. |
| `filterAvailableLocales` | `function` | Filter which locales appear in the admin selector per request (e.g. by user role). |

### Locale Object Properties

| Property | Type | Purpose |
| --- | --- | --- |
| `code` | `string` | **Required.** Unique identifier (`'en'`, `'es'`, `'pt-BR'`). |
| `label` | `string` | Display name shown in the admin locale selector. |
| `rtl` | `boolean` | Render the admin UI right-to-left for this locale. |
| `fallbackLocale` | `string \| string[]` | Per-locale fallback override, instead of the global `defaultLocale`. |

## Marking Fields Localized

Localization is opt-in **per field**. Add `localized: true` to any field that should hold a separate value per locale:

```ts
fields: [
  { name: 'title', type: 'text', localized: true },
  { name: 'slug', type: 'text', unique: true },   // shared across all locales
  { name: 'content', type: 'richText', localized: true },
]
```

Fields *without* `localized: true` store one value shared by every locale — keep IDs, slugs, and toggles non-localized unless they genuinely differ by language.

For container fields — `group`, `array`, `blocks`, and `tabs` — setting `localized: true` on the **parent** creates a localized set of *all* nested fields at once. Alternatively, leave the parent non-localized and mark only specific children:

```ts
{
  name: 'meta',
  type: 'group',
  localized: true,        // every nested field becomes per-locale
  fields: [
    { name: 'metaTitle', type: 'text' },
    { name: 'metaDescription', type: 'textarea' },
  ],
}
```

> **Warning:** Toggling `localized` on an existing field changes the stored data shape and will lose existing data. Plan this before populating content, or write a migration — see the `cms-migration` skill.

### Localized Relationships & Uploads

`relationship` and `upload` fields can be localized too. With `localized: true`, each locale points to its own related document(s) or media item — useful when the Spanish article links a Spanish-language reference or a translated hero image. Without it, the relationship is shared across locales. When you query, the related documents are themselves resolved in the requested locale (locale arguments propagate down through nested relationships unless overridden).

## Querying Localized Content

Pass `locale` and `fallbackLocale` to control which language comes back. They work the same way across Local, REST, and GraphQL APIs.

**Local API:**
```ts
const posts = await payload.find({
  collection: 'posts',
  locale: 'es',
  fallbackLocale: false,   // return null instead of the English value
})
```

**REST API** (note the hyphenated query param):
```
GET /api/posts?locale=es&fallback-locale=none
```

**GraphQL** (locale codes with dashes/spaces become underscores, e.g. `pt-BR` → `pt_BR`):
```graphql
query {
  Posts(locale: de, fallbackLocale: none) {
    docs { title }
  }
}
```

`fallbackLocale` accepts a valid locale code, or `'null'` / `'false'` / `'none'` (and `false` in the Local API) to disable fallback so empty fields return `null`.

### `locale: 'all'`

To retrieve every translation in one request — ideal for building a translation editor or exporting content — pass `locale: 'all'`:

```ts
const posts = await payload.find({ collection: 'posts', locale: 'all' })
// localized fields come back as objects keyed by locale:
// { title: { en: 'Hello', es: 'Hola', de: 'Hallo' } }
```

The same works in REST: `GET /api/posts?locale=all`. Each localized field is returned as an object keyed by locale code rather than a single resolved string.

## Localization with Versions & Drafts

Localized fields participate in version history normally — each saved version captures all locale values. By default the `_status` field is a single string reflecting the latest status across all locales. To publish languages independently (publish `en` while `es` stays draft), opt into the experimental flag:

```ts
// src/payload.config.ts
export default buildConfig({
  experimental: { localizeStatus: true },
})
```

```ts
// then per collection
export const Posts: CollectionConfig = {
  slug: 'posts',
  versions: { drafts: { localizeStatus: true } },
  fields: [/* ... */],
}
```

Status is then stored per locale: `{ en: 'published', es: 'draft' }`. See the `collections` skill for general drafts/versions setup.

## Admin UI Internationalization (i18n)

The admin panel ships with 30+ languages and auto-detects the editor's language from the `accept-language` header. Restrict or extend the set via the `i18n` key. Install the translations package first:

```bash
pnpm install @payloadcms/translations
```

```ts
// src/payload.config.ts
import { en } from '@payloadcms/translations/languages/en'
import { de } from '@payloadcms/translations/languages/de'

export default buildConfig({
  i18n: {
    fallbackLanguage: 'en',
    supportedLanguages: { en, de },
  },
})
```

| Option | Purpose |
| --- | --- |
| `fallbackLanguage` | Language used when the editor's preferred one isn't supported. Default `'en'`. |
| `supportedLanguages` | Map of language code → imported translation object from `@payloadcms/translations/languages/*`. |
| `translations` | Custom strings that extend or override the built-in translations, keyed by language code. |

> Admin **i18n** (UI language) is distinct from content **localization** (which locale's data you edit). An editor can view the panel in German while editing the Spanish version of a document.

### Custom & Project Translations

Override built-in strings or add your own namespaced keys, with `{{variable}}` interpolation:

```ts
// src/payload.config.ts
i18n: {
  translations: {
    en: {
      general: { dashboard: 'Home' },           // override a built-in label
      custom: { welcome: 'Welcome, {{name}}!' }, // your own namespaced key
    },
  },
},
```

Collection, global, and field labels accept language-keyed objects so the admin renders the right label per UI language:

```ts
export const Articles: CollectionConfig = {
  slug: 'articles',
  labels: {
    singular: { en: 'Article', es: 'Artículo' },
    plural: { en: 'Articles', es: 'Artículos' },
  },
  fields: [
    { name: 'title', type: 'text', label: { en: 'Title', es: 'Título' } },
  ],
}
```

### Translating in Code

In backend hooks, access functions, and endpoints, translate via `req.i18n` / `req.t`:

```ts
hooks: {
  beforeValidate: [({ req }) => {
    if (!req.user) throw new Error(req.t('error:unauthorized'))
  }],
}
```

In custom React admin components, use the `useTranslation` hook:

```tsx
'use client'
import { useTranslation } from '@payloadcms/ui'

export const Banner = () => {
  const { t, i18n } = useTranslation()
  return <div dir={i18n.dir}>{t('general:dashboard')}</div>
}
```

<example>
**User**: "Make my Posts collection localized in English, Spanish, and Arabic, with Arabic right-to-left and titles falling back to English when empty."

**Solution**:
```ts
// src/payload.config.ts
localization: {
  locales: [
    { label: 'English', code: 'en' },
    { label: 'Español', code: 'es' },
    { label: 'العربية', code: 'ar', rtl: true },
  ],
  defaultLocale: 'en',
  fallback: true,
},
```
```ts
// src/collections/Posts.ts
export const Posts: CollectionConfig = {
  slug: 'posts',
  fields: [
    { name: 'title', type: 'text', localized: true, required: true },
    { name: 'slug', type: 'text', unique: true },        // shared
    { name: 'content', type: 'richText', localized: true },
  ],
}
```
With `fallback: true`, an empty Spanish `title` resolves to the English value automatically.
</example>

<example>
**User**: "I need to fetch all translations of a post at once to build a side-by-side translation view."

**Solution**:
```ts
const post = await payload.findByID({
  collection: 'posts',
  id,
  locale: 'all',
})
// post.title === { en: 'Hello', es: 'Hola', ar: 'مرحبا' }
// render each locale value in its own column
```
</example>

## What this skill does NOT cover

- **Defining the collections and fields themselves** — see `collections` and `fields`. This skill only covers the `localized` flag and locale labels.
- **General query syntax, `where`, `depth`, pagination** — see `queries`. This skill covers only the `locale` / `fallbackLocale` parameters.
- **Initial project + `payload.config.ts` bootstrapping** — see `setup`.
- **Wiring locale-aware routes in the Next.js App Router** (`[locale]` segments, `generateStaticParams`, passing `locale` from the URL to `payload.find`) — see `nextjs-integration`.
- **Storage adapters for localized upload fields** (S3, R2, Vercel Blob) — see `adapters`.
- **Migrating data when toggling `localized` on existing fields** — see `cms-migration`.
