# All PayloadCMS Field Types — Long-Form Catalog

Exhaustive reference. The main `SKILL.md` covers the common patterns; this file covers every property of every type.

## Data Fields

### text

```ts
{
  name: 'title',
  type: 'text',
  required: true,
  unique: false,
  index: true,
  localized: false,
  minLength: 1,
  maxLength: 200,
  defaultValue: 'Untitled',
  hasMany: false,                       // Set true → array of strings
  validate: (value) => true,
  admin: { placeholder: 'Enter title…', autoComplete: 'off' },
}
```

### textarea

```ts
{ name: 'description', type: 'textarea', maxLength: 2000, admin: { rows: 6 } }
```

### email

```ts
{ name: 'email', type: 'email', required: true, unique: true, index: true }
```
Built-in email format validation.

### number

```ts
{
  name: 'price',
  type: 'number',
  required: true,
  min: 0,
  max: 1_000_000,
  hasMany: false,                       // true → array of numbers
  admin: { step: 0.01 },
}
```

### code

Syntax-highlighted text. The `admin.language` controls highlighting:
```ts
{
  name: 'snippet',
  type: 'code',
  admin: { language: 'typescript', editorOptions: { lineNumbers: 'on' } },
}
```

### json

Free-form JSON value:
```ts
{
  name: 'settings',
  type: 'json',
  defaultValue: { theme: 'auto' },
  jsonSchema: {                         // Optional: validate against schema
    uri: 'a://b/foo.json',
    fileMatch: ['*'],
    schema: { type: 'object', properties: { theme: { type: 'string' } } },
  },
}
```

### date

```ts
{
  name: 'publishedAt',
  type: 'date',
  defaultValue: () => new Date().toISOString(),
  admin: {
    date: {
      pickerAppearance: 'dayAndTime',  // 'dayOnly' | 'monthOnly' | 'timeOnly' | 'dayAndTime'
      displayFormat: 'd MMM yyy h:mm a',
      timeFormat: 'HH:mm',
      minDate: new Date('2020-01-01'),
      maxDate: new Date('2099-12-31'),
    },
  },
}
```

### checkbox

```ts
{ name: 'featured', type: 'checkbox', defaultValue: false }
```

### radio

```ts
{
  name: 'visibility',
  type: 'radio',
  options: [
    { label: 'Public', value: 'public' },
    { label: 'Private', value: 'private' },
  ],
  defaultValue: 'public',
  admin: { layout: 'horizontal' },
}
```

### select

```ts
{
  name: 'categories',
  type: 'select',
  hasMany: true,                        // Multi-select
  options: [
    'news',
    'announcements',
    { label: 'Engineering', value: 'engineering' },  // Custom label
  ],
  defaultValue: ['news'],
}
```

### relationship

```ts
{
  name: 'related',
  type: 'relationship',
  relationTo: 'posts',                  // Single collection
  // relationTo: ['posts', 'pages'],    // Polymorphic
  hasMany: true,
  required: false,
  min: 1,                                // hasMany only: min selections
  max: 10,
  maxDepth: 2,                          // Cap populate depth
  filterOptions: ({ data, user, siblingData, id, relationTo }) => ({
    _status: { equals: 'published' },
    author: { equals: user?.id },
  }),
  admin: { allowCreate: true, sortOptions: 'title' },
}
```

### upload

```ts
{
  name: 'image',
  type: 'upload',
  relationTo: 'media',
  required: true,
  filterOptions: () => ({ mimeType: { contains: 'image' } }),
  displayPreview: true,
}
```

### richText

Lexical editor. See the `lexical-editor` skill for full customization:
```ts
{
  name: 'content',
  type: 'richText',
  required: true,
  editor: lexicalEditor({
    features: ({ defaultFeatures, rootFeatures }) => [
      ...defaultFeatures,
      // Add custom features
    ],
  }),
}
```

### point — geolocation

```ts
{ name: 'location', type: 'point', required: true }
// Stored as [longitude, latitude] — order matches GeoJSON
```

Query examples:
```ts
// Near a point
where: { location: { near: [-73.97, 40.78, 5000 /* meters */] } }

// Within a bounding box
where: { location: { within: { type: 'Polygon', coordinates: [...] } } }
```

### join — reverse relationship

```ts
{
  name: 'orders',
  type: 'join',
  collection: 'orders',
  on: 'customer',                       // Field on `orders` that points back
  maxDepth: 1,
}
```

Queried like a relationship but read-only. Pagination controls available via `joinDefault`.

## Container Fields

### group

```ts
{
  name: 'seo',
  type: 'group',
  fields: [
    { name: 'metaTitle', type: 'text' },
    { name: 'metaDescription', type: 'textarea' },
    { name: 'ogImage', type: 'upload', relationTo: 'media' },
  ],
  admin: { hideGutter: false },
}
// Stored as: { seo: { metaTitle, metaDescription, ogImage } }
```

### array

```ts
{
  name: 'testimonials',
  type: 'array',
  required: false,
  minRows: 0,
  maxRows: 20,
  labels: { singular: 'Testimonial', plural: 'Testimonials' },
  fields: [
    { name: 'quote', type: 'textarea', required: true },
    { name: 'author', type: 'text', required: true },
    { name: 'avatar', type: 'upload', relationTo: 'media' },
  ],
  admin: { initCollapsed: true },
}
```

### blocks

```ts
const HeroBlock: Block = {
  slug: 'hero',
  labels: { singular: 'Hero', plural: 'Heroes' },
  imageURL: '/block-previews/hero.png',  // Admin preview thumbnail
  fields: [
    { name: 'heading', type: 'text', required: true },
    { name: 'background', type: 'upload', relationTo: 'media' },
  ],
}

{
  name: 'layout',
  type: 'blocks',
  minRows: 1,
  maxRows: 50,
  blocks: [HeroBlock, ContentBlock, MediaBlock],
}
```

Each saved entry has `blockType` and `id` automatically.

### tabs

```ts
{
  type: 'tabs',
  tabs: [
    {
      label: 'Content',
      description: 'Editorial content',
      fields: [{ name: 'title', type: 'text' }],
    },
    {
      label: 'SEO',
      name: 'seo',                       // With name → nests data
      fields: [{ name: 'metaTitle', type: 'text' }],
    },
  ],
}
```

### collapsible

```ts
{
  type: 'collapsible',
  label: ({ data }) => data?.title || 'Item',
  fields: [/* ... */],
  admin: { initCollapsed: true },
}
```

### row

Horizontal field layout. Set `admin.width` on children:
```ts
{
  type: 'row',
  fields: [
    { name: 'firstName', type: 'text', admin: { width: '50%' } },
    { name: 'lastName', type: 'text', admin: { width: '50%' } },
  ],
}
```

### ui

Custom React-only field (no data):
```ts
{
  name: 'warningCallout',
  type: 'ui',
  admin: {
    components: {
      Field: '@/components/WarningCallout',
      Cell: '@/components/EmptyCell',
    },
  },
}
```

## Special Behavior

### Virtual

Computed, not stored:
```ts
{
  name: 'wordCount',
  type: 'number',
  virtual: true,
  hooks: {
    afterRead: [({ siblingData }) => (siblingData.content || '').split(/\s+/).length],
  },
}
```

`virtual` also accepts a dot-notation string path through a relationship in the same collection — queryable, no hook required:
```ts
{ name: 'authorName', type: 'text', virtual: 'author.name' }
```

### Conditional

```ts
{
  name: 'shippingAddress',
  type: 'group',
  fields: [/* … */],
  admin: {
    condition: (data, siblingData) => data?.requiresShipping === true,
  },
}
```

### Localized

Per-locale values. Requires `localization` in payload.config.ts:
```ts
{ name: 'title', type: 'text', localized: true, required: true }
```

Queries:
```ts
const result = await payload.find({ collection: 'posts', locale: 'es' })
```

### Custom field components

```ts
{
  name: 'priority',
  type: 'number',
  admin: {
    components: {
      Field: '@/components/PrioritySlider',
      Cell: '@/components/PriorityBadge',
      Description: '@/components/PriorityHelp',
      Label: '@/components/PriorityLabel',
      Filter: '@/components/PriorityFilter',
    },
  },
}
```

Strings are import paths Payload resolves via the import map (`pnpm generate:importmap`).

## Field-Level Hooks

Subset of collection hooks, scoped to one field:
```ts
{
  name: 'slug',
  type: 'text',
  hooks: {
    beforeValidate: [({ data, value }) => value || slugify(data?.title || '')],
    afterRead: [({ value }) => value?.toLowerCase()],
  },
}
```

## Field-Level Access

```ts
{
  name: 'salary',
  type: 'number',
  access: {
    read: ({ req: { user } }) => user?.roles?.includes('admin'),
    update: ({ req: { user } }) => user?.roles?.includes('admin'),
  },
}
```

If `read` returns false, the field is stripped from the response. If `update` returns false, attempts to write the field are silently ignored.
