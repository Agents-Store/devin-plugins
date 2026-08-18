---
name: cms-migration
description: This skill should be used when the user asks to "migrate WordPress to Payload", "move content from Contentful to Payload", "import Strapi data into Payload", "migrate Sanity to PayloadCMS", "Webflow CMS to Payload", "design Payload collections from CMS export", or needs a structured workflow for moving content from another CMS into Payload.
---

# PayloadCMS — CMS Migration

Config-first workflow for moving content from another CMS (WordPress, Contentful, Strapi, Sanity, Webflow, Ghost, custom DB) into PayloadCMS. Adapted from the official [payloadcms/skills](https://github.com/payloadcms/skills) (MIT) cms-migration skill.

**Core principle**: design the **data model** in Payload through conversation **before** importing a single row. Migration scripts are easy. Data shape decisions are forever.

## The 5-Phase Workflow

```
1. Analyze source data
2. Propose Payload collection configs
3. Iterate on edge cases with the user
4. Confirm related collections (media, users, taxonomies)
5. Plan the actual import (order, IDs, media, richText)
```

Don't write a single import script until Phases 1–4 are signed off.

## Phase 1 — Analyze the Source

Ask the user for a representative sample of the source data:
- WordPress: a JSON export from the REST API (`/wp-json/wp/v2/posts?per_page=10&_embed`).
- Contentful: a Space Export JSON (`contentful space export …`).
- Strapi: an export from the Admin → Content-Manager.
- Sanity: GROQ dump `sanity dataset export production`.
- Webflow: CSV export from each Collection.
- Custom DB: a `SELECT * LIMIT 10` per table.

For each row, identify:

| Question | Output |
| --- | --- |
| Which fields are text, number, date, boolean, JSON? | Field types |
| Which fields look like IDs or foreign keys? | Relationships |
| Which fields are repeated lists? | Arrays |
| Which fields contain rich HTML / Markdown? | richText (Lexical) |
| Which fields hold image URLs / file paths? | Uploads |
| Which fields are timestamps? | Date or built-in `timestamps: true` |
| What looks ambiguous? | Flag for Phase 3 |

Don't propose a collection yet. Surface findings as a table:

```
| Source Field        | Sample              | Suggested Payload Type |
|---------------------|---------------------|------------------------|
| title               | "Hello World"       | text, required         |
| slug                | "hello-world"       | text, unique, index    |
| content             | "<p>…</p>"          | richText (Lexical)     |
| categories          | [1, 2, 3]           | relationship → tags?   |
| featured_image_url  | "/wp-content/…"     | upload → media         |
| meta.seo_title      | "Hello | My Site"   | group { metaTitle }    |
```

## Phase 2 — Propose Collection Configs

Once analysis is shared, propose a TypeScript collection config with reasoning per field:

```ts
export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: { useAsTitle: 'title', defaultColumns: ['title', 'status', 'publishedAt'] },
  versions: { drafts: true },
  fields: [
    { name: 'title', type: 'text', required: true },   // direct map
    { name: 'slug',  type: 'text', unique: true, index: true },
    { name: 'content', type: 'richText' },             // HTML → Lexical (Phase 5)
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users',
      required: true,
      // WP "post_author" is a user ID → maps to Payload users
    },
    {
      name: 'categories',
      type: 'relationship',
      relationTo: 'categories',
      hasMany: true,
      // WP categories taxonomy → Categories collection
    },
    { name: 'tags', type: 'relationship', relationTo: 'tags', hasMany: true },
    { name: 'featuredImage', type: 'upload', relationTo: 'media' },
    {
      name: 'seo',
      type: 'group',
      fields: [
        { name: 'metaTitle', type: 'text' },
        { name: 'metaDescription', type: 'textarea' },
      ],
    },
    { name: 'publishedAt', type: 'date' },
  ],
  hooks: {
    beforeChange: [
      ({ data }) => {
        // Auto-slugify if missing
        return data
      },
    ],
  },
}
```

Explain every non-trivial decision:
- Why `tags` is a relationship and not a select.
- Why `seo` is a group, not separate top-level fields.
- Why `versions.drafts` is enabled (so the migration can stage drafts).

## Phase 3 — Iterate on Edge Cases

Run through ambiguities **with the user**, not by guessing. Common questions:

### Select vs Relationship

If the source has repeated string values (categories, tags, statuses), ask:
- "These look like categories. Will editors add new ones over time? If yes, make them a relationship to a `categories` collection (editable, queryable). If they're fixed forever (like `draft / published / archived`), a select field is simpler."

**Default to relationship** for anything content-like. Reserve `select` for true enums.

### Rich Text Conversion

WordPress / Contentful / Strapi store HTML. Sanity stores Portable Text. Payload uses Lexical JSON. Conversion choices:
- **HTML → Lexical**: use a parser (e.g. `unified` + `rehype` + `mdast-util-to-mdast` + a Lexical state builder). The official `@payloadcms/richtext-lexical/html` ships an HTML→Lexical converter for the common cases.
- **Portable Text → Lexical**: walk the Portable Text array and emit equivalent Lexical nodes.
- **Markdown → Lexical**: parse with `remark`, walk the AST.

Discuss what to preserve: headings, lists, links (internal vs external?), images (rehost to Payload media?), embeds (custom blocks?).

### IDs

External IDs from the source rarely line up with Payload's `id` (Mongo ObjectID / Postgres uuid). Solutions:
- Add a `legacyId` field on each migrated collection (`{ name: 'legacyId', type: 'text', unique: true, index: true }`). Use it to resolve relationships during import.
- After import, drop `legacyId` (or keep it for audit).

### Required vs Optional

Source schemas often have stray empty values. Decide per field:
- "Title was required in WordPress but ~3% of exports are empty. Should we backfill `'Untitled'` or skip those rows?"

### Localization

If the source is multi-language, decide whether each language is a separate document (WordPress with Polylang) or a localized field (Payload's `localized: true` + `locales` config). The latter is usually cleaner.

## Phase 4 — Confirm Related Collections

A blog post export rarely arrives alone. Ask:

- **Media** — every image URL or attachment → an `Upload` collection (`media`). Pre-create.
- **Users / Authors** — `post_author` → a `users` auth collection. Decide: full auth (let them log in) or just record (no password)?
- **Categories / Tags** — taxonomies → separate collections.
- **Comments** — separate collection or skip (use Disqus / Giscus instead)?
- **Menus / Globals** — site nav, footer links → Payload globals.
- **Forms / Submissions** — usually skip; replace with `@payloadcms/plugin-form-builder`.
- **Custom Post Types** — WordPress CPTs → Payload collections. Ask one-by-one.
- **Custom Fields (ACF / Pods)** — map each ACF field group to Payload fields (often a `group` or `tabs`).

Don't proceed until every content type has a planned Payload collection.

## Phase 5 — The Migration Plan

Only now talk about the import script. Order matters:

1. **Schema** — `pnpm migrate:create initial && pnpm migrate` (or `db.push` in dev).
2. **Users** — import users first; everything else references them.
3. **Media** — upload assets next so posts can reference uploaded `media.id`.
4. **Taxonomies** — categories, tags.
5. **Globals** — site settings, navigation.
6. **Content collections** — posts, pages, products, etc. In dependency order (e.g., articles after their `series` collection).
7. **Relationships** — resolve `legacyId` references to Payload IDs.
8. **Versions / drafts** — if source has draft/publish, set `_status` per row.

### Sample Import Script

```ts
// scripts/migrate-wordpress.ts
import { getPayload } from 'payload'
import config from '../src/payload.config'
import fs from 'node:fs/promises'
import { htmlToLexical } from './lib/htmlToLexical'

async function importMedia(payload, items) {
  for (const item of items) {
    const buffer = await fetch(item.url).then(r => r.arrayBuffer())
    const created = await payload.create({
      collection: 'media',
      data: { alt: item.alt || item.title || 'image', legacyId: String(item.id) },
      file: { data: Buffer.from(buffer), mimetype: item.mime, name: item.filename, size: buffer.byteLength },
    })
    console.log('Media:', item.filename, '→', created.id)
  }
}

async function run() {
  const payload = await getPayload({ config })
  const raw = JSON.parse(await fs.readFile('./wp-export.json', 'utf8'))

  await importMedia(payload, raw.media)
  // …users, categories, posts (each resolving legacyIds)
}

run().catch((e) => { console.error(e); process.exit(1) })
```

Run inside the project:
```bash
pnpm tsx scripts/migrate-wordpress.ts
```

### Resolving Legacy Relationships

```ts
const mediaIdByLegacy = new Map<string, string>()
const mediaDocs = await payload.find({ collection: 'media', limit: 10_000 })
for (const m of mediaDocs.docs) {
  if (m.legacyId) mediaIdByLegacy.set(m.legacyId, m.id)
}

// Now translate WordPress featured_media → Payload id
const featuredImage = mediaIdByLegacy.get(String(post.featured_media))
```

### Re-Run Safety

Make the script idempotent so partial failures can resume:
```ts
const existing = await payload.find({
  collection: 'posts',
  where: { legacyId: { equals: String(wpPost.id) } },
  limit: 1,
})
if (existing.docs.length > 0) {
  console.log('Skip — already migrated:', wpPost.id)
  continue
}
```

## Source-Specific Quick Notes

| Source | Quirk |
| --- | --- |
| **WordPress** | Rich text is HTML with WP-specific shortcodes (`[gallery]`, `[embed]`). Decide per shortcode: render to a Payload Block, strip, or convert. |
| **Contentful** | Rich text is Contentful's own JSON format (similar to Lexical). Walk and emit Lexical equivalents. |
| **Strapi** | Easy 1:1 — Strapi v4+ uses fields/components conceptually close to Payload. |
| **Sanity** | Portable Text. Custom blocks → Payload Blocks via `BlocksFeature`. |
| **Webflow** | CSV per Collection. Relations stored as comma-separated Item IDs. |
| **Ghost** | Mobiledoc format. Convert via `@tryghost/mobiledoc-renderer` then HTML → Lexical. |

## See Also

- The `collections` skill — designing the target shape.
- The `fields` skill — picking the right field type per source column.
- The `lexical-editor` skill — converting HTML/Portable Text to Lexical.
- The `cli-recipes` skill — running one-off `tsx` scripts via the Local API.
- The `adapters` skill — choosing the target DB (Postgres recommended for large migrations).
