# Pages Backed by a Headless CMS or External API

Patterns for a Next.js app whose content lives in another system (Directus, Contentful, Strapi, your own API) and is fetched on the server. Checked with `tsc --strict` against `next@16.3.8`. Directus is the worked example in the comments; nothing here depends on it. The two caching models (`cacheComponents` off or on) are explained in [cache-components.md](cache-components.md).

## Wrap every CMS read in one module

One function per query, wrapped in React `cache()` so `generateMetadata` and the page share a single request:

```typescript
// lib/content.ts
import 'server-only';
import { cache } from 'react';
import { getPostBySlug, listPostSlugs } from '@/lib/cms'; // your CMS client calls, tagged for the cache

export const getPost = cache(async (slug: string) => getPostBySlug(slug));
export const getPostSlugs = cache(async () => listPostSlugs());
```

How the tag gets onto the request is the part that depends on the model:

- **Previous model** (default, `cacheComponents` off): `fetch` is not cached unless you ask. Pass `cache: 'force-cache'` and `next: { tags: ['posts'], revalidate: 3600 }` to the fetch your client makes (an SDK that forwards `fetch` options can do it per request).
- **Cache Components** (`cacheComponents: true`): `fetch` options and the `revalidate` export no longer apply. Put `'use cache'`, `cacheTag('posts')` and `cacheLife('hours')` inside the function that reads the CMS, instead.

Either way, keep one tag per CMS collection (`posts`, `authors`). It is the unit a CMS webhook can name. And never cache a read that runs with the signed-in user's credentials: a cache entry is shared by every visitor who produces the same key.

## Static pages from CMS slugs

```tsx
// app/blog/[slug]/page.tsx
import { notFound } from 'next/navigation';
import { getPost, getPostSlugs } from '@/lib/content';

export async function generateStaticParams() {
  const slugs = await getPostSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPost(slug);
  return { title: post?.title, description: post?.excerpt };
}

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPost(slug);
  if (!post) notFound();
  return <article><h1>{post.title}</h1></article>;
}
```

With `cacheComponents: true` `generateStaticParams` must return at least one entry, and a page that awaits `params` for unlisted slugs needs a `<Suspense>` boundary. See `cache-components.md`.

## On-demand revalidation from a CMS webhook

The CMS calls a Route Handler when content changes, and the handler expires the tag. The secret travels in a header, never in the URL (URLs are logged by every proxy on the way), and only tags you list can be expired:

```typescript
// app/api/revalidate/route.ts
import { revalidateTag } from 'next/cache';
import { timingSafeEqual } from 'node:crypto';

const COLLECTION_TAGS = new Set(['posts', 'authors', 'categories']);

function secretMatches(received: string | null): boolean {
  const expected = process.env.REVALIDATION_SECRET;
  if (!expected || !received) return false;
  const a = Buffer.from(received);
  const b = Buffer.from(expected);
  return a.length === b.length && timingSafeEqual(a, b);
}

export async function POST(request: Request) {
  if (!secretMatches(request.headers.get('x-revalidate-secret'))) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }
  const body = (await request.json().catch(() => null)) as { collection?: unknown } | null;
  const collection = typeof body?.collection === 'string' ? body.collection : '';
  if (!COLLECTION_TAGS.has(collection)) {
    return Response.json({ error: 'Unknown collection' }, { status: 400 });
  }
  revalidateTag(collection, { expire: 0 });
  return Response.json({ revalidated: true, collection });
}
```

- `{ expire: 0 }` expires the entry immediately: the next visitor waits for fresh data. It is what the Next.js docs suggest for webhooks. `'max'` is the lazier variant: the next visitor still gets the stale page while the new one is built.
- A missed webhook leaves the site stale until something else invalidates it. Keep a `revalidate` lifetime (previous model) or a `cacheLife` (Cache Components) as a safety net.
- The route is public. The secret check and the tag allow-list are the whole defence.

## Mutations

A Server Action is a public POST endpoint, and anyone can call it with an id of their choosing. Authenticating the caller is not enough: with a server credential and only a "signed in" check, any signed-in user can change any item. Authenticate **and** authorize, then expire the tag:

```typescript
// app/posts/actions.ts
'use server';
import { updateTag } from 'next/cache';
import { requireUser } from '@/lib/session'; // your session library; redirects when nobody is signed in
import { updatePostInCms } from '@/lib/cms';

export async function updatePost(id: string, formData: FormData) {
  const session = await requireUser(); // authenticate
  // Authorize: act with the user's own credential, so the CMS applies that user's permissions
  await updatePostInCms(session.accessToken, id, { title: String(formData.get('title') ?? '') });
  updateTag('posts');
}
```

There are two ways to authorize, and one of them is always required:

- **The CMS enforces it.** Send the signed-in user's own token to the CMS (as above). The CMS answers `403` for what that user may not change. This needs a session library that holds a CMS token for the user.
- **Your code enforces it.** When the CMS only ever sees a server credential (a login library with its own user table), check role or ownership before the write (`if (post.authorId !== session.user.id) throw new Error('Forbidden')`) and never skip it for "internal" actions.

Validate `formData` (Zod, see `form-handling`) before it reaches the CMS.

## Images that live in the CMS

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const cms = new URL(process.env.NEXT_PUBLIC_CMS_URL!); // the CMS address; name the variable as your project does

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: cms.protocol === 'https:' ? 'https' : 'http',
        hostname: cms.hostname,
        port: cms.port,
        pathname: '/assets/**', // where the CMS serves files; Directus uses /assets/<id>
      },
    ],
    // Next 16 refuses to optimize images from localhost and private IPs (SSRF protection):
    // allow it while developing against a local CMS, never in production
    dangerouslyAllowLocalIP: process.env.NODE_ENV !== 'production',
  },
};

export default nextConfig;
```

- Pin `pathname` and `port`: a pattern with only a hostname lets `/_next/image` fetch anything on that host.
- **Never put a token or API key into an image URL.** `next/image` writes the whole source URL into the page (`/_next/image?url=...`), so every visitor receives the credential, and it lands in access logs. Make the files public in the CMS, or serve them from a Route Handler of your own that adds the credential on the server.
- A source on your own domain with a query string (a proxy route such as `/api/assets/<id>?width=800`) needs `images.localPatterns` (`[{ pathname: '/api/assets/**' }]`). Without it Next 16 answers `400`.
