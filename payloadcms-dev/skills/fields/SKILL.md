---
name: fields
description: This skill should be used when the user asks about "Payload field types", "add a relationship field", "blocks field", "array field", "rich text field", "upload field", "virtual field", "conditional fields", "field validation", "join field", "point/geolocation field", "slug field helper", or needs to design any field inside a PayloadCMS collection or global.
---

# PayloadCMS — Fields

Every field is a JS object with a `type` discriminator. Fields go inside a collection or global's `fields: []` array. This skill is the field-type cheat sheet; see `references/all-field-types.md` for the long-form catalog and `references/field-type-guards.md` for runtime type narrowing.

## Common Field Properties

These apply to almost every field type:

| Property | Purpose |
| --- | --- |
| `name` | Field key (camelCase). Becomes a property on the document. |
| `type` | Discriminator (`text`, `relationship`, etc.). |
| `label` | Admin label override. Defaults to title-cased `name`. |
| `required` | Enforces non-empty on save. |
| `defaultValue` | Static value or `({ user, req }) => value` function. |
| `unique` | DB-level uniqueness. |
| `index` | Adds a single-column index. |
| `localized` | Stores per-locale values (requires `localization` config). |
| `saveToJWT` | Auth collections only — include this field in the JWT payload. |
| `validate` | Custom validator `(value, { req, siblingData }) => true \| string`. |
| `access` | Per-field read/create/update access functions. |
| `hooks` | Field-level `beforeChange` / `afterChange` / `afterRead` / `beforeValidate`. |
| `admin` | UI options (see below). |
| `virtual` | Don't persist; compute via `afterRead`. |

The `admin` object inside any field:
```ts
admin: {
  description: 'Tooltip text',
  position: 'sidebar',           // Move out of main column
  width: '50%',                  // For row layout
  condition: (data, siblingData) => data.published === true,
  readOnly: false,
  hidden: false,
  placeholder: 'Enter title…',
  disableBulkEdit: true,         // Hide from the bulk-edit field selector
  disableGroupBy: true,          // Hide from the list-view groupBy dropdown
  disableListColumn: true,       // Hide from list-view column options
  disableListFilter: true,       // Hide from list-view filter options
  components: { Field: '@/components/CustomField' },
}
```

## Data Fields

### text / textarea / email / number / code / json / date

```ts
{ name: 'title', type: 'text', required: true, minLength: 5, maxLength: 200 }
{ name: 'bio', type: 'textarea', maxLength: 5000 }
{ name: 'contact', type: 'email', required: true }
{ name: 'price', type: 'number', min: 0, max: 999999 }
{ name: 'config', type: 'code', admin: { language: 'json' } }
{ name: 'metadata', type: 'json' }
{ name: 'publishedAt', type: 'date', admin: { date: { pickerAppearance: 'dayAndTime' } } }
```

### checkbox / radio / select

```ts
{ name: 'featured', type: 'checkbox', defaultValue: false }
{
  name: 'priority',
  type: 'radio',
  options: [
    { label: 'Low', value: 'low' },
    { label: 'High', value: 'high' },
  ],
}
{
  name: 'status',
  type: 'select',
  options: ['draft', 'published', 'archived'],
  defaultValue: 'draft',
  hasMany: false,                       // Set true for multi-select
}
```

### relationship

The most important non-trivial type:

```ts
// One-to-one
{ name: 'author', type: 'relationship', relationTo: 'users', required: true }

// One-to-many
{ name: 'tags', type: 'relationship', relationTo: 'tags', hasMany: true }

// Polymorphic (can point to multiple collections)
{
  name: 'related',
  type: 'relationship',
  relationTo: ['posts', 'pages', 'products'],
  hasMany: true,
}

// Filter what's selectable
{
  name: 'editor',
  type: 'relationship',
  relationTo: 'users',
  filterOptions: ({ user }) => ({
    roles: { in: ['editor', 'admin'] },
  }),
}
```

Stored as IDs by default. Set `depth` in queries to populate.

### upload

Relationship to an upload-enabled collection:
```ts
{ name: 'featuredImage', type: 'upload', relationTo: 'media', required: true }
{ name: 'gallery', type: 'upload', relationTo: 'media', hasMany: true }
```

### richText

Lexical-backed editor. See the `lexical-editor` skill for customization:
```ts
{
  name: 'content',
  type: 'richText',
  editor: lexicalEditor({
    features: ({ defaultFeatures }) => [
      ...defaultFeatures,
      // Custom features here
    ],
  }),
}
```

### point — geolocation

Stored as `[longitude, latitude]`. Enables `near` / `within` queries:
```ts
{ name: 'location', type: 'point', required: true }
```

### join — reverse relationship (read-only)

Surface the inverse side of a `relationship` without storing extra data:
```ts
// Posts collection has { name: 'author', type: 'relationship', relationTo: 'users' }

// Inside Users collection:
{ name: 'posts', type: 'join', collection: 'posts', on: 'author' }
```

`users.posts` is computed at query time from posts where `author = user.id`.

## Container Fields

### group

Nested object — fields collapsed under a single key:
```ts
{
  name: 'seo',
  type: 'group',
  fields: [
    { name: 'title', type: 'text' },
    { name: 'description', type: 'textarea' },
  ],
}
// Stored as: { seo: { title, description } }
```

### array

List of repeating sub-records:
```ts
{
  name: 'slides',
  type: 'array',
  minRows: 1,
  maxRows: 10,
  fields: [
    { name: 'heading', type: 'text', required: true },
    { name: 'image', type: 'upload', relationTo: 'media' },
  ],
}
```

### blocks

Heterogeneous list of typed sub-records — the cornerstone of flexible page builders:

```ts
const HeroBlock: Block = {
  slug: 'hero',
  fields: [
    { name: 'heading', type: 'text', required: true },
    { name: 'cta', type: 'group', fields: [
      { name: 'label', type: 'text' },
      { name: 'href', type: 'text' },
    ]},
  ],
}

const ContentBlock: Block = {
  slug: 'content',
  fields: [{ name: 'body', type: 'richText' }],
}

// In a collection:
{ name: 'layout', type: 'blocks', blocks: [HeroBlock, ContentBlock] }
```

Each entry stores its `blockType` discriminator. Use TypeScript narrowing on `blockType` to render the right component.

### tabs

Group fields into admin tabs (UI only — data stored under each tab's key if `name` is given):
```ts
{
  type: 'tabs',
  tabs: [
    {
      label: 'Content',
      fields: [{ name: 'title', type: 'text' }],
    },
    {
      label: 'SEO',
      name: 'seo',                       // Optional: nests these fields under `seo`
      fields: [{ name: 'metaTitle', type: 'text' }],
    },
  ],
}
```

### collapsible / row / ui

Pure layout helpers — no data storage (`row`, `collapsible`) or arbitrary React render (`ui`):
```ts
{ type: 'row', fields: [
  { name: 'firstName', type: 'text', admin: { width: '50%' } },
  { name: 'lastName', type: 'text', admin: { width: '50%' } },
]}

{ type: 'collapsible', label: 'Advanced', fields: [/* … */], admin: { initCollapsed: true }}

{
  name: 'helpMessage',
  type: 'ui',
  admin: { components: { Field: '@/components/HelpCallout' } },
}
```

## Virtual Fields

Computed at read time, never stored:
```ts
{
  name: 'fullName',
  type: 'text',
  virtual: true,
  hooks: {
    afterRead: [({ siblingData }) => `${siblingData.firstName} ${siblingData.lastName}`],
  },
}
```

`virtual` also accepts a **dot-notation string path** that resolves through a relationship field in the same collection — no hook needed, and the field stays queryable:

```ts
// Virtual field linked through a relationship — queryable, no hook needed
{ name: 'authorName', type: 'text', virtual: 'author.name' }
```

The path walks `relationship` (or `upload`) fields to a subfield of the related document; `hasMany` relationships resolve to arrays. Source: https://payloadcms.com/docs/fields/overview

Useful for derived display values, slugs from titles (see the slug field pattern below), aggregate counts, formatted dates.

## Conditional Fields

Show/hide based on other fields:
```ts
{ name: 'enableNewsletter', type: 'checkbox' },
{
  name: 'newsletterFrequency',
  type: 'select',
  options: ['daily', 'weekly', 'monthly'],
  admin: {
    condition: (data, siblingData) => Boolean(data?.enableNewsletter),
  },
}
```

The `condition` runs in the browser — don't rely on it for security; use `access` for that.

## Custom Validation

```ts
{
  name: 'username',
  type: 'text',
  validate: async (value, { req, siblingData }) => {
    if (!value) return 'Username is required.'
    if (!/^[a-z0-9_]+$/.test(value)) return 'Only a-z, 0-9, _ allowed.'
    const taken = await req.payload.count({
      collection: 'users',
      where: { username: { equals: value } },
    })
    if (taken.totalDocs > 0) return 'Username is taken.'
    return true                          // Pass
  },
}
```

Return `true` for valid, a string error for invalid.

## Slug Field Pattern

Payload core **does** export an experimental `slugField` helper (`import { slugField } from 'payload'`, present since at least 3.80.0). It returns a `RowField` containing a slug text field plus a `generateSlug` checkbox, with options `name`, `useAsSlug`, `slugify`, `disableUnique`, `checkboxName`, and `overrides` — but it is JSDoc-tagged `@experimental` and undocumented in the v3 docs, so its API may change without notice.

The stable, documented alternative is the project-level convention from the official website template — a text field with a `beforeValidate` hook. Note that the local helper below shadows the core `slugField` export; rename one of them if you want both in scope:

```ts
// src/fields/slug.ts — the stable website-template pattern
// (shadows the experimental core `slugField` export — rename if you use both)
import type { Field } from 'payload'

export const slugField = (fieldToUse = 'title'): Field => ({
  name: 'slug',
  type: 'text',
  index: true,
  unique: true,
  admin: { position: 'sidebar' },
  hooks: {
    beforeValidate: [({ data, value }) =>
      value || String(data?.[fieldToUse] ?? '')
        .toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')],
  },
})
```

```ts
fields: [
  { name: 'title', type: 'text', required: true },
  slugField('title'),
],
```

It generates the slug from `title` on save, allows manual override in admin, and indexes the field. For a derived value that simply mirrors a related document's field, prefer a string-path virtual field (see Virtual Fields above).

## See Also

- `references/all-field-types.md` — exhaustive catalog with every property of every type.
- `references/field-type-guards.md` — type guards for runtime narrowing inside hooks and custom components.
- The `collections` skill — where fields live.
- The `access-control` skill — per-field read/create/update gates.
- The `hooks` skill — field-level beforeChange/afterRead patterns.
- The `lexical-editor` skill — customizing `richText` editors.

Run `pnpm generate:types` whenever you change fields — the typed `payload-types.ts` is what makes Local API calls type-safe.
