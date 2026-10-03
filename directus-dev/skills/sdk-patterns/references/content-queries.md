# Reading Content: Relations, Singletons, Filters from the URL

Read patterns for pages that render Directus content, written for `@directus/sdk` 26 and checked with `tsc --strict`. The basic `readItems` / `readItem` calls, filters and `deep` are in `SKILL.md`; the server-side client module is in [ssr-client.md](ssr-client.md). The examples use a blog schema:

```typescript
// types/directus.ts
export interface Author { id: string; name: string; bio: string | null; avatar: string | null; slug: string }
export interface Category { id: string; name: string; slug: string }
export interface PostCategory { id: number; posts_id: string | Post; categories_id: string | Category }
export interface Post {
  id: string;
  status: 'draft' | 'published' | 'archived';
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  featured_image: string | null;
  author: string | Author;
  categories: number[] | PostCategory[];
  date_published: string;
  date_created: string;
}
export interface Global { id: number; site_title: string; tagline: string | null } // a singleton
export interface Schema {
  posts: Post[];
  authors: Author[];
  categories: Category[];
  posts_categories: PostCategory[];
  global: Global; // singleton: an object, not an array
}
```

Match the types to the real collections. A `decimal` field arrives as a string (`"19.99"`, checked on PostgreSQL): type it `string` and convert with `Number()` for display. Directus 12 gives new collections a boolean `archived` field instead of the string `status` above; existing `status` fields keep working. If your collection has `archived`, filter with `{ archived: { _eq: false } }`.

## Relations go in `fields` as objects

Dotted strings do not type-check in SDK 26 (`'author.name'` is TS2322). Nest an object instead:

```typescript
// lib/queries/relations.ts
import { readItems } from '@directus/sdk';
import directus from '@/lib/directus';

// many-to-one: the related fields you want
const posts = await directus.request(
  readItems('posts', {
    filter: { status: { _eq: 'published' } },
    sort: ['-date_published'],
    fields: ['id', 'title', 'slug', 'excerpt', 'featured_image', 'date_published', { author: ['name', 'slug'] }],
    limit: 20,
  }),
);

// many-to-many: go through the junction collection
const [post] = await directus.request(
  readItems('posts', {
    filter: { slug: { _eq: 'hello-world' } },
    fields: ['*', { author: ['name', 'bio', 'avatar'] }, { categories: [{ categories_id: ['name', 'slug'] }] }],
    limit: 1,
  }),
);
```

- The junction collection (`posts_categories`) must be in `Schema` for the nested object to type-check.
- A single item by slug is a filtered list with `limit: 1`; destructure the first entry and call `notFound()` (or your framework's equivalent) when it is `undefined`.
- Relation fields are unions (`author: string | Author`): a UUID when the field was not expanded, the object when it was. Narrow before use: `typeof post.author === 'object' ? post.author.name : 'Unknown'`.

## Independent reads in parallel

```typescript
// lib/queries/parallel.ts
import { readItems } from '@directus/sdk';
import directus from '@/lib/directus';

const [posts, categories] = await Promise.all([
  directus.request(readItems('posts', { limit: 10 })),
  directus.request(readItems('categories', { sort: ['name'] })),
]);
```

## Singletons

A singleton collection (site settings, a home page) holds one row and the API answers with an object, not an array. Type it as an object in `Schema` (`global: Global`, not `Global[]`) and read it with `readSingleton`; `readItems('global')` is then a compile error:

```typescript
// lib/queries/singleton.ts
import { readSingleton } from '@directus/sdk';
import directus from '@/lib/directus';

const settings = await directus.request(readSingleton('global', { fields: ['site_title', 'tagline'] }));
```

## Filters and search that come from the URL

Type the filter with the SDK's own `QueryFilter` so a typo in a field name fails the build, and compose conditions with `_and`:

```typescript
// lib/queries/filter.ts
import { readItems, type QueryFilter } from '@directus/sdk';
import directus from '@/lib/directus';
import type { Post, Schema } from '@/types/directus';

export function postFilter(authorSlug?: string): QueryFilter<Schema, Post> {
  const published: QueryFilter<Schema, Post> = { status: { _eq: 'published' } };
  return authorSlug ? { _and: [published, { author: { slug: { _eq: authorSlug } } }] } : published;
}

export async function searchPosts(authorSlug?: string, search?: string) {
  return directus.request(
    readItems('posts', { filter: postFilter(authorSlug), search, fields: ['id', 'title', 'slug'] }),
  );
}
```

Values from query strings are untrusted input: pass them as filter *values* (as above), never build `filter` keys from them. A `search` of `undefined` is ignored.

## Content versions

`readItem(..., { version: 'draft' })` reads a draft in collections with versioning. The reserved keys and the 403 on a missing version are in [content-versions.md](content-versions.md).
