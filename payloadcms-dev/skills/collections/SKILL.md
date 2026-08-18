---
name: collections
description: This skill should be used when the user asks to "create a Payload collection", "define a CollectionConfig", "set up an auth collection", "build an upload collection", "add drafts/versions", "configure admin panel for a collection", "enable live preview", "set defaultColumns", or needs to model any content type in PayloadCMS v3.
---

# PayloadCMS — Collections

Collections are the building blocks of every Payload app. Each collection is a typed document store, a REST/GraphQL endpoint, an admin panel page, and an auto-generated TypeScript type — all from one config object.

## Minimal Collection

```ts
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'author', 'status', 'updatedAt'],
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text', unique: true, index: true },
    { name: 'content', type: 'richText' },
    { name: 'author', type: 'relationship', relationTo: 'users' },
  ],
  timestamps: true,
}
```

Register it in `payload.config.ts`:
```ts
collections: [Posts, Users, Media],
```

Re-run `pnpm generate:types` after every collection change.

## CollectionConfig Reference

| Property | Type | Purpose |
| --- | --- | --- |
| `slug` | `string` | Unique key. Becomes `/api/<slug>`, the table/collection name, and the type name (`Post` for slug `posts`). Use kebab-case plural. |
| `labels` | `{ singular, plural }` | Override singular/plural labels in the admin UI. Defaults to inflected slug. |
| `fields` | `Field[]` | Document schema. See the `fields` skill. |
| `timestamps` | `boolean` | Default `true`. Adds `createdAt` / `updatedAt`. |
| `defaultSort` | `string` | Initial sort for list view, e.g. `'-createdAt'`. |
| `admin` | `object` | Admin panel behavior (see below). |
| `access` | `object` | Permission rules. See the `access-control` skill. |
| `hooks` | `object` | Lifecycle callbacks. See the `hooks` skill. |
| `auth` | `boolean \| AuthConfig` | Turn this collection into a login source. |
| `upload` | `boolean \| UploadConfig` | Turn this collection into a file store. |
| `versions` | `boolean \| VersionsConfig` | Enable version history / drafts. |
| `endpoints` | `Endpoint[]` | Custom API routes scoped to this collection. |
| `indexes` | `object[]` | Compound indexes across multiple fields. |
| `disableDuplicate` | `boolean` | Hide the "Duplicate" admin action. |
| `disableBulkDelete` | `boolean` | Hide/disable bulk delete in the list view (3.86+). |

## `admin` Options

```ts
admin: {
  useAsTitle: 'title',                  // Field shown as document label everywhere
  defaultColumns: ['title', 'author'],  // Columns in list view
  group: 'Content',                     // Sidebar grouping
  description: 'Blog posts and articles',
  listSearchableFields: ['title', 'excerpt'],
  pagination: { defaultLimit: 25, limits: [10, 25, 50, 100] },
  preview: (doc, { req }) =>            // "Preview" button URL
    `${process.env.NEXT_PUBLIC_SITE_URL}/preview?slug=${doc.slug}&secret=${process.env.PREVIEW_SECRET}`,
  livePreview: {
    url: ({ data }) =>
      `${process.env.NEXT_PUBLIC_SITE_URL}/posts/${data.slug}?draft=true`,
    openByDefault: true,                // open the live-preview panel automatically (3.86+)
    breakpoints: [
      { name: 'mobile', width: 375, height: 667, label: 'Mobile' },
      { name: 'tablet', width: 768, height: 1024, label: 'Tablet' },
      { name: 'desktop', width: 1440, height: 900, label: 'Desktop' },
    ],
  },
  components: {                         // Custom React components (path strings)
    views: { Edit: { Default: '@/components/CustomEditView' } },
    BeforeDashboard: ['@/components/Banner'],
  },
}
```

## Auth Collections

Setting `auth: true` enables login on the collection. The most common is `Users`:

```ts
export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    tokenExpiration: 7200,          // 2h JWT
    verify: true,                   // Email verification flow
    maxLoginAttempts: 5,
    lockTime: 600 * 1000,           // 10 min lockout
    cookies: { secure: true, sameSite: 'Strict' },
    useAPIKey: false,
  },
  admin: { useAsTitle: 'email' },
  fields: [
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      saveToJWT: true,              // Include in JWT so access fns can read it
      options: [
        { label: 'Admin', value: 'admin' },
        { label: 'Editor', value: 'editor' },
        { label: 'User', value: 'user' },
      ],
      defaultValue: ['user'],
      required: true,
    },
    { name: 'fullName', type: 'text' },
  ],
}
```

Payload auto-generates `email`, `password`, `resetPasswordToken`, `loginAttempts`, `lockUntil`, etc. Set `admin.user: 'users'` in `payload.config.ts` so the admin panel signs in against this collection.

## Upload Collections

Setting `upload: true` (or a config object) makes the collection store files:

```ts
export const Media: CollectionConfig = {
  slug: 'media',
  upload: {
    staticDir: path.resolve(dirname, '../media'),  // Local FS (dev only)
    mimeTypes: ['image/*', 'application/pdf'],
    imageSizes: [
      { name: 'thumbnail', width: 400, height: 300, position: 'centre' },
      { name: 'card', width: 768, height: 1024, position: 'centre' },
      { name: 'hero', width: 1920 },              // Height auto
    ],
    adminThumbnail: 'thumbnail',
    focalPoint: true,
    crop: true,
  },
  fields: [
    { name: 'alt', type: 'text', required: true },
    { name: 'caption', type: 'text' },
  ],
}
```

Payload auto-adds `filename`, `mimeType`, `filesize`, `width`, `height`, `url`, and per-size variants. For production, swap `staticDir` for a storage adapter (S3, R2, Vercel Blob) — see the `adapters` skill.

## Versions & Drafts

```ts
export const Pages: CollectionConfig = {
  slug: 'pages',
  versions: {
    drafts: {
      autosave: { interval: 100 },   // ms between autosaves
      schedulePublish: true,          // Allow scheduling future publish
      validate: true,
    },
    maxPerDoc: 50,                   // Keep last 50 versions
  },
  fields: [/* ... */],
}
```

**`schedulePublish` requires a jobs runner.** Scheduled publish/unpublish runs through the Jobs Queue — the app must be processing jobs (autoRun, `payload jobs:run`, or the run endpoint) or scheduled events never execute. See the `jobs-queue` skill.

A `_status` field (`'draft' | 'published'`) is added automatically. Querying drafts requires `draft: true`:
```ts
const drafts = await payload.find({ collection: 'pages', draft: true, where: { _status: { equals: 'draft' } } })
```

## Custom Endpoints

Add bespoke routes scoped to the collection:
```ts
endpoints: [
  {
    path: '/popular',
    method: 'get',
    handler: async (req) => {
      const posts = await req.payload.find({
        collection: 'posts',
        sort: '-views',
        limit: 5,
        depth: 1,
      })
      return Response.json(posts)
    },
  },
],
```
Mounted at `/api/posts/popular`.

## Compound Indexes

```ts
indexes: [
  { fields: ['author', 'status'], unique: false },
  { fields: ['slug', 'locale'], unique: true },
],
```

Improves query performance for multi-field `where` clauses.

## Project Structure

```txt
src/
├── collections/
│   ├── Users.ts        # Auth collection
│   ├── Media.ts        # Upload collection
│   ├── Posts.ts        # Content with versions+drafts
│   └── index.ts        # Optional barrel re-export
├── payload.config.ts
```

Keep each collection in its own file. Group related access functions, hooks, and helpers in sibling files like `Posts.access.ts`, `Posts.hooks.ts`.

<example>
**User**: "I need a Tutorials collection with drafts, autosave, live preview, and admin grouping under 'Learning'."

**Solution**:
```ts
export const Tutorials: CollectionConfig = {
  slug: 'tutorials',
  admin: {
    group: 'Learning',
    useAsTitle: 'title',
    defaultColumns: ['title', 'difficulty', 'updatedAt', '_status'],
    livePreview: {
      url: ({ data }) => `${process.env.NEXT_PUBLIC_SITE_URL}/tutorials/${data.slug}?draft=true`,
    },
  },
  versions: { drafts: { autosave: { interval: 800 }, schedulePublish: true } },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'slug', type: 'text', unique: true, index: true },
    { name: 'difficulty', type: 'select', options: ['beginner', 'intermediate', 'advanced'] },
    { name: 'body', type: 'richText' },
  ],
}
```
</example>

After your collections are defined, the next likely topics are `fields` (full field reference), `access-control` (who can do what), and `hooks` (lifecycle automation).
