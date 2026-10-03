---
name: directus-to-nextjs
description: This skill should be used when the user wants to "fetch Directus data in Next.js", "display Directus content in Next.js pages", "render Directus images in Next.js", "use Directus SDK with Server Components", "create Next.js pages from Directus collections", "add TypeScript types for Directus", "cache Directus data in Next.js", "revalidate after Directus content changes", "fix 403 on Directus images", or needs the rules where Directus data meets Next.js rendering: who holds the token, what is cached, how files are served, and how types follow the schema.
---

# Directus to Next.js: The Boundary

Four rules decide whether the two systems work together: who holds the token, what is cached and who expires it, how files reach the page, and how types follow the schema. SDK calls (`readItems`, relations, filters) are taught by `directus-dev` → `sdk-patterns` (`references/content-queries.md`); pages, `generateStaticParams` and Server Actions by `nextjs-dev` → `data-fetching` (`references/headless-cms.md`). This skill links them.

## Token

| Who | Holds | Where |
|-----|-------|-------|
| Next.js server | Static token of a **dedicated Directus user** with a narrow policy (`DIRECTUS_ADMIN_TOKEN`) | `lib/directus.ts` behind `import 'server-only'` |
| Signed-in end user | Their own access token, only if the session path forwards it (see `authentication`) | The session cookie |
| Browser | Nothing of Directus. Public reads only, through whatever the Public policy allows | — |

- Never `NEXT_PUBLIC_` on a token. The prefix ships the value to every visitor.
- A token of an administrator turns every bug of the app into full access. Use one only locally.
- A Server Action and a Route Handler are public endpoints that take any id. **Authenticate and authorize** (`requireUser()` from `authentication`) before they use the server token: write with the signed-in user's own token (`withToken(session.accessToken, ...)`) so Directus applies that user's policies, or check role or ownership in code. A "signed in" check followed by a write with the server token lets any user change any item.

## Cache

Passing `cache` to `rest()` does not compile (TS2353): `RestConfig` has no `cache`. A blanket `no-store` is not the right rule anyway. Since Next.js 15 `fetch` is not cached by default, but every route that reads no request data is prerendered at build time, so Directus content is frozen at the build until something expires it. Decide the cache on purpose:

1. **Tag every read with the collections it reads**, including the ones it expands (a post query that expands `author` is tagged `posts` and `authors`). The tag is the unit a Directus Flow can name.
2. **One module holds the reads** (`lib/content.ts`), so tags live next to the queries and pages stay free of cache details.
3. **A Flow expires the tag** when an editor changes content (`deployment`).

Previous caching model (default, `cacheComponents` off): the SDK forwards `fetch` options per request. `requestTagged` is in `directus-dev` → `sdk-patterns` → `references/ssr-client.md`:

```typescript
// lib/content.ts
import 'server-only';
import { cache } from 'react';
import { readItems } from '@directus/sdk';
import { requestTagged } from '@/lib/directus-tagged';

const ONE_HOUR = 3600; // safety net: a missed webhook heals itself within the hour
const LIST_TAGS = ['posts', 'authors'];
const DETAIL_TAGS = ['posts', 'authors', 'categories']; // the detail read expands all three

export const getPublishedPosts = cache(async () =>
  requestTagged(
    readItems('posts', {
      filter: { status: { _eq: 'published' } },
      sort: ['-date_published'],
      fields: ['id', 'title', 'slug', 'excerpt', 'featured_image', 'date_published', { author: ['name', 'slug'] }],
      limit: 20,
    }),
    LIST_TAGS,
    ONE_HOUR,
  ),
);

export const getPostSlugs = cache(async () => {
  const posts = await requestTagged(
    readItems('posts', { filter: { status: { _eq: 'published' } }, fields: ['slug'], limit: -1 }),
    ['posts'],
    ONE_HOUR,
  );
  return posts.map((post) => post.slug);
});

export const getPostBySlug = cache(async (slug: string) => {
  const [post] = await requestTagged(
    readItems('posts', {
      filter: { slug: { _eq: slug }, status: { _eq: 'published' } },
      fields: ['*', { author: ['name', 'bio', 'avatar'] }, { categories: [{ categories_id: ['name', 'slug'] }] }],
      limit: 1,
    }),
    DETAIL_TAGS,
    ONE_HOUR,
  );
  return post ?? null;
});
```

With `cacheComponents: true` the `fetch` options and the `revalidate` export no longer apply. The same read moves into a cached function:

```typescript
// lib/content-cache-components.ts
import 'server-only';
import { cacheLife, cacheTag } from 'next/cache';
import { readItems } from '@directus/sdk';
import directus from '@/lib/directus';

export async function getPublishedPosts() {
  'use cache';
  cacheTag('posts', 'authors');
  cacheLife('hours');
  return directus.request(
    readItems('posts', {
      filter: { status: { _eq: 'published' } },
      sort: ['-date_published'],
      fields: ['id', 'title', 'slug', 'excerpt', { author: ['name', 'slug'] }],
      limit: 20,
    }),
  );
}
```

**Never cache a read made with a user's token** (`withToken(session.accessToken, ...)`). A cache entry is served to every visitor with the same key, so a user's private rows would reach strangers. Cached reads use the server token and public content only.

## Assets

`/assets/<id>` answers `403` to anonymous requests until a policy allows it. The tempting fix, a token in the URL's query string, **leaks the token**: `next/image` writes the whole source URL into the HTML (`/_next/image?url=...`), so every visitor receives it, and it lands in access logs. Pick one of two modes:

| Mode | When | What it costs |
|------|------|---------------|
| **A. Public files** | Every uploaded file may be public | Grant the Public policy read on `directus_files`. Without a license this must be an unrestricted rule (a folder filter is a custom permission rule and answered `403 RESOURCE_RESTRICTED` on Directus 12.4.1), so **every** file becomes downloadable and listable through `GET /files` by anyone |
| **B. Proxy route** | Some files are private, or the library is mixed | A Route Handler adds the token on the server and serves only one folder. One extra request per image on a cold cache |

Mode A:

```typescript
// lib/directus-asset.ts
export type AssetParams = {
  width?: number;
  height?: number;
  fit?: 'cover' | 'contain' | 'inside' | 'outside';
  quality?: number;
};

/** Address of a Directus file for next/image. It carries no token. */
export function directusAsset(fileId: string | null, params: AssetParams = {}): string | null {
  if (!fileId) return null;
  const url = new URL(`/assets/${fileId}`, process.env.NEXT_PUBLIC_DIRECTUS_URL);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) url.searchParams.set(key, String(value));
  }
  return url.toString();
}
```

Add the Directus host to `images.remotePatterns` (`nextjs-dev` → `data-fetching` → `references/headless-cms.md`).

Mode B: keep the helper's name and signature, return the local route instead (`/api/assets/<id>?width=800`), and allow it with `images.localPatterns: [{ pathname: '/api/assets/**' }]`:

```typescript
// lib/directus-asset.proxy.ts: the body of directusAsset() in mode B
import type { AssetParams } from '@/lib/directus-asset';

export function directusAssetViaProxy(fileId: string | null, params: AssetParams = {}): string | null {
  if (!fileId) return null;
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) query.set(key, String(value));
  }
  const search = query.toString();
  return `/api/assets/${fileId}${search ? `?${search}` : ''}`;
}
```

```typescript
// app/api/assets/[id]/route.ts
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const TRANSFORMS = ['width', 'height', 'fit', 'quality', 'format'] as const;
const RASTER = /^image\/(png|jpe?g|webp|avif|gif)$/; // an exact list: no SVG, no HTML, no parameters
const NOSNIFF = { 'X-Content-Type-Options': 'nosniff' };

const notFound = () => new Response('Not found', { status: 404, headers: NOSNIFF });

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!UUID.test(id)) return notFound();

  const base = process.env.NEXT_PUBLIC_DIRECTUS_URL!;
  const headers = { Authorization: `Bearer ${process.env.DIRECTUS_ADMIN_TOKEN}` };

  // Serve one folder only. Without this the route is a public mirror of every file the token can read.
  const meta = await fetch(`${base}/files/${id}?fields=folder`, { headers });
  const folder = meta.ok ? ((await meta.json()) as { data: { folder: string | null } }).data.folder : null;
  if (!folder || folder !== process.env.PUBLIC_ASSET_FOLDER_ID) return notFound();

  const upstreamUrl = new URL(`/assets/${id}`, base);
  const requested = new URL(request.url).searchParams;
  for (const key of TRANSFORMS) {
    const value = requested.get(key);
    if (value) upstreamUrl.searchParams.set(key, value);
  }

  const upstream = await fetch(upstreamUrl, { headers });
  if (!upstream.ok || !upstream.body) return notFound();

  // Raster images only: an HTML or SVG file from the library would run script on your own origin
  const type = (upstream.headers.get('Content-Type') ?? '').trim().toLowerCase();
  if (!RASTER.test(type)) return notFound();

  return new Response(upstream.body, {
    headers: {
      ...NOSNIFF,
      'Content-Type': type,
      'Cache-Control': 'public, max-age=3600, stale-while-revalidate=86400',
    },
  });
}
```

Both modes use `next/image` as usual (`<Image src={directusAsset(post.featured_image, { width: 800 })!} ... />`). If Directus already resized the file (`width` set), pass `unoptimized` to avoid processing it twice.

## Types

`types/directus.ts` mirrors the Directus schema, in this order of work: change the schema (Studio or the Directus MCP `collections` and `fields` tools), then the interface, then the pages that use it.

- Read the schema with the MCP `schema` tool before writing an interface. Do not guess field names.
- Relations are unions (`author: string | Author`), and a many-to-many junction collection is part of `Schema`. The patterns are in `directus-dev` → `sdk-patterns` → `references/content-queries.md`.
- A singleton (site settings) is an object in `Schema` and is read with `readSingleton`.
- A `decimal` field (a price) arrives as a string, `"19.99"`. Type it `string` and convert with `Number()` when you format it.
- Directus 12 gives a new collection a boolean `archived` instead of a string `status`. Existing `status` fields keep working. Types, filters and form fields must follow what the collection really has.
- `tsc` is the drift check: run `npx tsc --noEmit` after every schema change, in CI too. A renamed or removed field in a query fails the build instead of rendering `undefined`.

## Mutations

Mutations go through Server Actions that authenticate the caller, **authorize** the write (the user's own token with `withToken`, or a role or ownership check in code), and then expire the tag. The full pattern is in `nextjs-dev` → `data-fetching` → `references/headless-cms.md`; the stack version with Directus is in `full-feature/template.md`.

## Where the Rest Lives

| Topic | Skill |
|-------|-------|
| Client module, fetch options, system collections, per-request token, login REST contract | `directus-dev` → `sdk-patterns` → `references/ssr-client.md` |
| `readItems`, relations, singletons, typed filters | `directus-dev` → `sdk-patterns` → `references/content-queries.md` |
| `generateStaticParams`, webhook route, Server Actions, `next/image` config | `nextjs-dev` → `data-fetching` → `references/headless-cms.md` |
| Flow that calls the revalidation route | `directus-dev` → `flow-automation` → `references/notify-external-app.md` |
| Local Directus | `directus-dev` → `docker-local-dev` |
