---
name: queries
description: This skill should be used when the user asks about "Payload Local API", "payload.find", "payload.findByID", "where query", "Payload query operators", "depth and populate", "filter Payload by relationship", "sort and paginate Payload results", "Payload REST API query string", "GraphQL queries", or needs to read or write data with Payload.
---

# PayloadCMS — Queries

Three ways to read/write data, all share the same `where` syntax:

1. **Local API** (`payload.find`, `payload.create`, …) — server-side, in-process, fastest, default.
2. **REST API** (`GET /api/posts?where[...]=...`) — for browser fetch, third-party clients.
3. **GraphQL API** (`/api/graphql`) — for typed introspection and frontend codegen.

## Local API — the Core Methods

```ts
import { getPayload } from 'payload'
import config from '@payload-config'

const payload = await getPayload({ config })

// Find many
const { docs, totalDocs, totalPages, page, hasNextPage } = await payload.find({
  collection: 'posts',
  where: { status: { equals: 'published' } },
  sort: '-publishedAt',
  limit: 20,
  page: 1,
  depth: 2,
  locale: 'en',
  user: req.user,
  overrideAccess: false,           // see access-control skill
})

// Find one by ID
const post = await payload.findByID({
  collection: 'posts',
  id: '675…',
  depth: 2,
})

// Count
const { totalDocs } = await payload.count({
  collection: 'posts',
  where: { author: { equals: userId } },
})

// Create
const post = await payload.create({
  collection: 'posts',
  data: { title: 'Hello', author: userId },
  user: req.user,
  overrideAccess: false,
  req,                              // KEEP TRANSACTION ATOMIC inside a hook
})

// Update one
await payload.update({
  collection: 'posts',
  id: postId,
  data: { status: 'published' },
  req,
})

// Update many
await payload.update({
  collection: 'posts',
  where: { author: { equals: userId } },
  data: { archived: true },
  req,
})

// Delete one / many
await payload.delete({ collection: 'posts', id: postId, req })
await payload.delete({ collection: 'posts', where: { archived: { equals: true } }, req })
```

Globals use the same methods on `payload.findGlobal / updateGlobal`:
```ts
const header = await payload.findGlobal({ slug: 'header' })
await payload.updateGlobal({ slug: 'header', data: { logo: mediaId }, req })
```

## Where Operators

Every operator is `{ field: { operator: value } }`:

| Operator | Meaning | Example |
| --- | --- | --- |
| `equals` | Exact match | `{ status: { equals: 'published' } }` |
| `not_equals` | Inverse | `{ status: { not_equals: 'archived' } }` |
| `greater_than` | `>` | `{ price: { greater_than: 100 } }` |
| `greater_than_equal` | `>=` | `{ price: { greater_than_equal: 100 } }` |
| `less_than` | `<` | `{ stock: { less_than: 5 } }` |
| `less_than_equal` | `<=` | — |
| `like` | Case-insensitive substring | `{ title: { like: 'payload' } }` |
| `contains` | Substring (case-sensitive) | `{ title: { contains: 'CMS' } }` |
| `in` | Value is one of | `{ status: { in: ['draft', 'review'] } }` |
| `not_in` | Value is none of | `{ tag: { not_in: ['nsfw'] } }` |
| `all` | hasMany must contain all | `{ tags: { all: ['ai', 'cms'] } }` |
| `exists` | Field present / absent | `{ deletedAt: { exists: false } }` |
| `near` | Geospatial: near point | `{ location: { near: [-73.9, 40.7, 5000] } }` — last param: meters |
| `within` | Geospatial: within polygon | `{ location: { within: { type: 'Polygon', coordinates: [[...]] } } }` |
| `intersects` | Geospatial: intersects shape | analogous |

### AND / OR

Combine multiple clauses:

```ts
where: {
  and: [
    { status: { equals: 'published' } },
    {
      or: [
        { author: { equals: userId } },
        { visibility: { equals: 'public' } },
      ],
    },
  ],
}
```

Top-level `where` defaults to AND across its keys, but use explicit `and:` when nesting OR.

### Nested Property Queries

Query through relationships using dot notation:

```ts
where: { 'author.name': { contains: 'john' } }
where: { 'team.members.email': { contains: '@example.com' } }
```

These compile to SQL joins (Postgres/SQLite) or Mongo aggregation lookups.

## Depth & Population

`depth` controls how deep to populate relationships. Default is **2**.

```ts
// depth: 0 — relationships return IDs only
await payload.findByID({ collection: 'posts', id, depth: 0 })
// → { author: 'user_123', tags: ['tag_1', 'tag_2'] }

// depth: 1 — populate one level
await payload.findByID({ collection: 'posts', id, depth: 1 })
// → { author: { id, name, email }, tags: [{ id, label }, ...] }

// depth: 2 — populate two levels (default)
// → { author: { id, name, organization: { id, name } } }
```

Higher depth = more DB calls. Cap with `maxDepth` on the relationship field.

## Select & Pagination

`select` returns only specified fields — saves bandwidth and avoids unnecessary `afterRead` hooks:

```ts
await payload.find({
  collection: 'posts',
  select: { title: true, slug: true, author: true },
  limit: 100,
})
```

Pagination:
- `limit` — page size (default 10).
- `page` — 1-based page index.
- `sort` — field name, prefix with `-` for descending, comma-separated for multi-sort: `'priority,-createdAt'`.
- `pagination: false` — disables totals/page counts on huge result sets (faster).

## Drafts & Locales

Query drafts:
```ts
await payload.find({
  collection: 'pages',
  draft: true,
  where: { _status: { equals: 'draft' } },
})
```

Query a specific locale:
```ts
await payload.find({
  collection: 'posts',
  locale: 'es',
  fallbackLocale: 'en',
})
```

## REST API

Every collection auto-mounts at `/api/<slug>`. The where syntax is JSON-stringified into the query string:

```bash
# List
curl 'https://app.example.com/api/posts?where[status][equals]=published&limit=20&sort=-publishedAt&depth=2' \
  -H "Authorization: JWT $TOKEN"

# Get by ID
curl 'https://app.example.com/api/posts/675abc?depth=1'

# Create
curl -X POST 'https://app.example.com/api/posts' \
  -H "Authorization: JWT $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Hello","status":"draft"}'

# Update
curl -X PATCH 'https://app.example.com/api/posts/675abc' \
  -H "Authorization: JWT $TOKEN" \
  -d '{"status":"published"}'

# Delete
curl -X DELETE 'https://app.example.com/api/posts/675abc' \
  -H "Authorization: JWT $TOKEN"
```

The library `qs-esm` (Payload-maintained ESM fork of `qs`) makes browser calls easy:
```ts
import { stringify } from 'qs-esm'

const query = stringify({
  where: { status: { equals: 'published' } },
  sort: '-publishedAt',
  depth: 2,
}, { addQueryPrefix: true })

const res = await fetch(`/api/posts${query}`).then(r => r.json())
```

## GraphQL API

Endpoint: `POST /api/graphql`. Schema is auto-generated from your collections.

```graphql
query Posts {
  Posts(
    where: { status: { equals: published } }
    sort: "-publishedAt"
    limit: 20
  ) {
    docs {
      id
      title
      slug
      author { id name }
    }
    totalDocs
  }
}
```

Generate typed clients with `graphql-codegen` against `/api/graphql` for a frontend-friendly typed query layer.

## Server Components — `getPayload`

Inside a Next.js Server Component or Route Handler:

```ts
// app/posts/[slug]/page.tsx
import { getPayload } from 'payload'
import config from '@payload-config'

export default async function PostPage({ params }: { params: { slug: string } }) {
  const payload = await getPayload({ config })
  const { docs } = await payload.find({
    collection: 'posts',
    where: { slug: { equals: params.slug } },
    limit: 1,
    depth: 2,
  })
  const post = docs[0]
  if (!post) return <div>Not found</div>
  return <article>{post.title}</article>
}
```

See the `nextjs-integration` skill for cache, ISR, and server-action patterns.

## Performance Tips

- `select` only the fields you'll render.
- Use the lowest `depth` that satisfies your UI. Each level adds joins.
- Index every field used in `where` / `sort`. Add the collection-level `indexes` for compound clauses.
- For pagination over huge collections (>10M rows), set `pagination: false` and use cursor-style `where.id.greater_than` instead.
- Cache server-component reads with Next.js `cache()` or `unstable_cache` — Payload doesn't add a caching layer by default.

<example>
**User**: "Give me the top 5 most-viewed published posts in English, with author populated."

```ts
const popular = await payload.find({
  collection: 'posts',
  where: {
    _status: { equals: 'published' },
  },
  locale: 'en',
  sort: '-viewCount',
  limit: 5,
  depth: 1,
  select: { title: true, slug: true, viewCount: true, author: true },
})
```
</example>

See also: `access-control` for `overrideAccess` semantics, `hooks` for `req` threading, `api-reference` for endpoint-by-endpoint specs.
