---
name: data-management
description: This skill should be used when the user asks to "enable soft delete in Payload", "trash and restore documents", "recover a deleted record", "set up query presets", "save and share list filters", "organize documents in folders", "group documents by a field", "use admin.groupBy", or wants the recent v3 data-management features (Trash, Query Presets, Folders, Group By).
---

# PayloadCMS — Trash, Query Presets, Folders & Group By

Four data-management features shipped during Payload v3 (2025). Each is enabled by a single flag on a collection and, where it needs storage, auto-creates a managed collection. None require a custom UI.

## Feature Map

| Feature | Collection flag | Auto-created collection | Admin effect |
| --- | --- | --- | --- |
| Trash (soft delete) | `trash: true` | — (adds a `deletedAt` field) | Trash view + Restore / Permanently Delete actions |
| Query Presets | `enableQueryPresets: true` | `payload-query-presets` | Save/load/share named list-view configs |
| Folders | `folders: true` | `payload-folders` | "Browse by folder" view; folder field on docs |
| Group By | `admin.groupBy: true` | — | Grouped list view by a shared field |

> Each of these alters the database schema (a new column, table, or relationship). After enabling any of them in Postgres/SQLite, generate and run a migration — see the `cli-recipes` skill.

## Trash (Soft Delete)

Set `trash: true` to make deletes reversible. Payload injects a `deletedAt` timestamp field; "deleting" a document just stamps `deletedAt` instead of removing the row.

```ts
// src/collections/Posts.ts
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  trash: true, // defaults to false
  fields: [
    { name: 'title', type: 'text', required: true },
  ],
}
```

**Admin:** A new `/collections/:slug/trash` route lists soft-deleted docs with bulk **Restore**, **Delete** (permanent), and **Empty Trash** actions. The list view's delete modal gains a checkbox to bypass trash and delete permanently. A trashed document's edit view is read-only, offering **Restore** and **Permanently Delete**.

**Local API** — control which set you query with the `trash` param:

```ts
// All docs including trashed
await payload.find({ collection: 'posts', trash: true })

// Only trashed
await payload.find({
  collection: 'posts',
  trash: true,
  where: { deletedAt: { exists: true } },
})

// Only non-trashed (default behavior)
await payload.find({ collection: 'posts', trash: false })
```

Restore by clearing the timestamp; permanently delete by passing `trash: true` to `delete`:

```ts
// Restore — clear deletedAt
await payload.update({ collection: 'posts', id, data: { deletedAt: null }, req })

// Permanent delete (skip trash)
await payload.delete({ collection: 'posts', id, trash: true, req })
```

**REST** mirrors the param: `GET /api/posts?trash=true`, `GET /api/posts?trash=true&where[deletedAt][exists]=true`, `GET /api/posts?trash=false`.

**Access control:** all three operations (soft delete, restore, permanent delete) run through the collection's `delete` access function. Differentiate by inspecting the `data` argument — on a soft-delete `data.deletedAt` is set; on a permanent delete `data` is `undefined`:

```ts
// src/collections/Posts.ts
access: {
  delete: ({ req: { user }, data }) => {
    if (!user) return false
    if (user.roles?.includes('admin')) return true
    if (data?.deletedAt) return true   // allow trashing
    return false                       // deny permanent delete to non-admins
  },
}
```

When versions are enabled, a trashed document's versions cannot be restored until the document itself is restored, but version history stays visible in its edit view.

## Query Presets

Set `enableQueryPresets: true` so users can save a List View's **filters**, **columns**, and **sort order** as a named preset and reload it later. Presets are stored in the auto-created `payload-query-presets` collection, so users can define as many as they like.

```ts
// src/collections/Orders.ts
export const Orders: CollectionConfig = {
  slug: 'orders',
  enableQueryPresets: true,
  fields: [/* ... */],
}
```

**Sharing & access** is configured under the root `queryPresets` key in `payload.config.ts`:

```ts
// src/payload.config.ts
import { buildConfig } from 'payload'

export default buildConfig({
  collections: [Orders /* ... */],
  queryPresets: {
    // Static, config-level rules — NOT user-editable
    access: {
      read: ({ req: { user } }) => Boolean(user),
      update: ({ req: { user } }) => user?.roles?.includes('admin'),
    },
    // Constraint options users pick from in the UI when sharing a preset
    constraints: {
      read: [
        { label: 'Specific Roles', value: 'specificRoles' /* + custom fields/where */ },
      ],
    },
    // Dynamically filter which constraint options a user sees
    filterConstraints: ({ req, options }) => options,
    // Relabel the presets collection in the admin UI
    labels: { singular: 'Saved View', plural: 'Saved Views' },
  },
})
```

Out of the box each preset can be shared as **Only Me**, **Everyone**, or **Specific Users**; `queryPresets.constraints` extends this with role-based or custom sharing rules, while `queryPresets.access` defines static rules the user cannot override. Read presets via the Local API like any collection:

```ts
const { docs } = await payload.find({ collection: 'payload-query-presets' })
```

## Folders

Set `folders: true` to let editors organize documents into a folder tree. Payload adds a hidden relationship field on the document pointing to its parent folder (or `null`), and manages the tree in the auto-created `payload-folders` collection — which itself has a self-referencing folder field, allowing nested folders.

```ts
// src/collections/Media.ts
export const Media: CollectionConfig = {
  slug: 'media',
  folders: true, // defaults to false
  upload: true,
  fields: [{ name: 'alt', type: 'text' }],
}
```

**Admin:** enabling folders surfaces a **Browse by Folder** view (the global `browseByFolder` option, on by default). Editors drag documents between folders there.

Folders are configured globally under the `folders` key in `payload.config.ts`:

```ts
// src/payload.config.ts
export default buildConfig({
  folders: {
    browseByFolder: true,   // default true — show the folder browser
    fieldName: 'folder',    // default 'folder' — name of the doc→folder field
    slug: 'payload-folders',// default — the folder collection slug
    debug: false,           // default — reveal hidden folder fields
    collectionOverrides: [  // async functions that modify the auto-created folder collection
      async ({ collection }) => collection,
    ],
  },
})
```

Per-collection, `folders` may also be an object instead of `true` — e.g. `folders: { browseByFolder: false }` to keep the collection out of the global folder browser.

Because folders are built on relationship fields, you can scope a query to a folder with a normal `where` on the folder field (default name `folder`):

```ts
const { docs } = await payload.find({
  collection: 'media',
  where: { folder: { equals: folderId } },
})
```

Folders are marked **beta** in the docs and may change.

## Group By

Set `admin.groupBy: true` to add a grouped List View — results are bucketed by a shared field (e.g. counting items per category, grouping entries by status). The feature is marked **beta**.

```ts
// src/collections/Tickets.ts
export const Tickets: CollectionConfig = {
  slug: 'tickets',
  admin: {
    groupBy: true, // beta — enable grouping in the list view
    defaultColumns: ['title', 'status', 'priority'],
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'status', type: 'select', options: ['open', 'pending', 'closed'] },
    { name: 'priority', type: 'select', options: ['low', 'high'] },
  ],
}
```

**In the admin**, the list view gains a control to pick which field to group on and renders results in collapsible groups with per-group counts.

**Note on the option shape:** the boolean form `admin.groupBy: true` is confirmed in the docs and release notes. The collections config reference also describes it as "grouping by a field," implying a field name may be accepted; richer object forms (e.g. `{ default, options }`) are an open community proposal, **not** confirmed in stable docs. Use the boolean unless you verify the string/object form against your installed version. For aggregate reads in code, prefer the Local API with explicit grouping/counting rather than relying on the list-view UI.

<example>
**User**: "Make Articles soft-deletable, but only admins can permanently delete."

```ts
// src/collections/Articles.ts
export const Articles: CollectionConfig = {
  slug: 'articles',
  trash: true,
  access: {
    delete: ({ req: { user }, data }) => {
      if (!user) return false
      if (user.roles?.includes('admin')) return true
      return Boolean(data?.deletedAt) // non-admins may trash, not purge
    },
  },
  fields: [{ name: 'title', type: 'text', required: true }],
}
```
Editors trash via the normal delete; recover from `/collections/articles/trash`. Query live docs with `trash: false`, recoverable ones with `trash: true` + `where: { deletedAt: { exists: true } }`.
</example>

<example>
**User**: "Let the support team save and share their favorite ticket filters, and organize tickets into folders."

```ts
// src/collections/Tickets.ts
export const Tickets: CollectionConfig = {
  slug: 'tickets',
  enableQueryPresets: true, // save/share list-view filters, columns, sort
  folders: true,            // organize tickets into folders
  fields: [/* ... */],
}
```
Presets land in `payload-query-presets`; sharing options (Only Me / Everyone / Specific Users) come from `queryPresets.constraints`. Folder assignments live in `payload-folders`; query a folder with `where: { folder: { equals: folderId } }`.
</example>

## What this skill does NOT cover

- `collections` — the full `CollectionConfig` surface (auth, upload, versions, drafts, indexes, custom endpoints).
- `queries` — the complete `where` operator set, `depth`, `select`, pagination, REST/GraphQL query syntax used by all four features here.
- `access-control` — how `access.delete` / `overrideAccess` / `req.user` evaluate (Trash leans on `delete`; presets define their own `queryPresets.access`).
- `cli-recipes` — generating and running the migration each of these flags requires when they add a column, table, or relationship in Postgres/SQLite.
