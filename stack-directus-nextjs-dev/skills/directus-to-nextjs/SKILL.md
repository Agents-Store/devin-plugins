---
name: directus-to-nextjs
description: This skill should be used when the user wants to "fetch Directus data in Next.js", "display Directus content in Next.js pages", "render Directus images in Next.js", "use Directus SDK with Server Components", "create Next.js pages from Directus collections", "add TypeScript types for Directus", or needs integration patterns between Directus data and Next.js rendering.
---

# Directus to Next.js Integration

Patterns for fetching Directus data in Next.js Server Components, handling images, typing schemas, and managing cache revalidation.

## SDK Client Setup

The Directus client lives in `lib/directus.ts` as a singleton. Two client variants:

**Server-side (admin operations):**

```typescript
import 'server-only';
import { createDirectus, rest, staticToken } from '@directus/sdk';
import type { Schema } from '@/types/directus';

const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
  .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
  .with(rest({ cache: 'no-store' }));

export default directus;
```

**Client-side (public reads only):**

```typescript
import { createDirectus, rest } from '@directus/sdk';
import type { Schema } from '@/types/directus';

const publicDirectus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
  .with(rest({ cache: 'no-store' }));

export default publicDirectus;
```

Always use `cache: 'no-store'` — Next.js force-caches fetch by default, which returns stale Directus data.

## Data Fetching in Server Components

**Read multiple items with filtering and sorting:**

```typescript
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';

export default async function PostsPage() {
  const posts = await directus.request(
    readItems('posts', {
      filter: { status: { _eq: 'published' } },
      sort: ['-date_created'],
      fields: ['id', 'title', 'slug', 'excerpt', 'featured_image', 'date_created'],
      limit: 20,
    })
  );

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

**Read a single item by ID or slug:**

```typescript
import { readItem, readItems } from '@directus/sdk';

// By primary key
const post = await directus.request(readItem('posts', id));

// By slug (filter to single result)
const [post] = await directus.request(
  readItems('posts', {
    filter: { slug: { _eq: slug } },
    fields: ['*', 'author.name', 'author.avatar'],
    limit: 1,
  })
);
```

**Fetch relational data (nested fields):**

```typescript
const post = await directus.request(
  readItems('posts', {
    fields: ['*', 'author.name', 'author.bio', 'categories.categories_id.name'],
  })
);
```

Use dot notation for M2O relations (`author.name`) and double dot for M2M junction tables (`categories.categories_id.name`).

**Parallel fetching:**

```typescript
const [posts, categories, settings] = await Promise.all([
  directus.request(readItems('posts', { limit: 10 })),
  directus.request(readItems('categories')),
  directus.request(readItems('global')),
]);
```

## TypeScript Schema

Define interfaces matching Directus collections in `types/directus.ts`:

```typescript
export interface Post {
  id: string;
  title: string;
  slug: string;
  content: string;
  status: 'draft' | 'published' | 'archived';
  featured_image: string | null;
  author: string | Author;
  date_created: string;
}

export interface Author {
  id: string;
  name: string;
  bio: string;
  avatar: string | null;
}

export interface Schema {
  posts: Post[];
  authors: Author[];
}
```

Relational fields use union types: `author: string | Author` — it's a UUID string when not expanded, or the full object when fetched with `fields: ['author.*']`.

## Image Handling

Directus serves file assets at `{DIRECTUS_URL}/assets/{file_id}`. Create a helper that includes authentication — Directus assets return **403 Forbidden** unless the public role has read access to `directus_files` or the URL includes an `access_token`:

```typescript
export function directusAsset(
  fileId: string | null,
  params?: { width?: number; height?: number; fit?: 'cover' | 'contain' | 'inside'; quality?: number }
): string | null {
  if (!fileId) return null;
  const url = new URL(`/assets/${fileId}`, process.env.NEXT_PUBLIC_DIRECTUS_URL);
  if (params?.width) url.searchParams.set('width', String(params.width));
  if (params?.height) url.searchParams.set('height', String(params.height));
  if (params?.fit) url.searchParams.set('fit', params.fit);
  if (params?.quality) url.searchParams.set('quality', String(params.quality));
  // Include access_token — without it, assets return 403 unless the public role has file read access
  const token = process.env.DIRECTUS_ADMIN_TOKEN;
  if (token) url.searchParams.set('access_token', token);
  return url.toString();
}
```

**Asset authentication options (pick one):**

| Approach | When to use |
|----------|------------|
| `access_token` in URL (above) | Quick setup — token is in the URL but proxied through `next/image` so not directly exposed to end users |
| Public role with file read access | Production best practice — configure in Directus: Settings > Roles > Public > `directus_files` read permission |
| API route proxy | Maximum security — create `/api/assets/[id]` route that fetches with the token server-side |

Use with `next/image`:

```tsx
import Image from 'next/image';

<Image
  src={directusAsset(post.featured_image, { width: 800, height: 400, fit: 'cover' })!}
  alt={post.title}
  width={800}
  height={400}
/>
```

Ensure `next.config.ts` includes the Directus domain in `images.remotePatterns`.

## Dynamic Routes with generateStaticParams

Generate static pages from Directus content at build time:

```typescript
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await directus.request(
    readItems('posts', {
      filter: { status: { _eq: 'published' } },
      fields: ['slug'],
    })
  );
  return posts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [post] = await directus.request(
    readItems('posts', { filter: { slug: { _eq: slug } }, fields: ['title', 'excerpt'], limit: 1 })
  );
  return { title: post?.title, description: post?.excerpt };
}
```

## Revalidation Patterns

**Time-based ISR:**

```typescript
// At the top of a page file
export const revalidate = 60; // Revalidate every 60 seconds
```

**On-demand revalidation via Server Action:**

```typescript
'use server';
import { revalidateTag } from 'next/cache';

export async function publishPost(formData: FormData) {
  // ... create/update item in Directus
  revalidateTag('posts');
}
```

**Webhook-triggered revalidation (Directus Automate → Next.js API):**

```typescript
// app/api/revalidate/route.ts
import { revalidateTag } from 'next/cache';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get('secret');
  if (secret !== process.env.REVALIDATION_SECRET) {
    return Response.json({ error: 'Invalid secret' }, { status: 401 });
  }
  const { collection } = await request.json();
  revalidateTag(collection);
  return Response.json({ revalidated: true });
}
```

## Server Actions for Mutations

```typescript
// app/posts/actions.ts
'use server';
import directus from '@/lib/directus';
import { createItem, updateItem } from '@directus/sdk';
import { revalidatePath } from 'next/cache';

export async function createPost(formData: FormData) {
  await directus.request(
    createItem('posts', {
      title: formData.get('title') as string,
      content: formData.get('content') as string,
      status: 'draft',
    })
  );
  revalidatePath('/posts');
}
```

## Common Patterns Reference

| Pattern | Approach |
|---------|----------|
| Collection listing | Server Component + `readItems` with filter/sort |
| Detail page | Dynamic route `[slug]` + `readItem` or filtered `readItems` |
| Static generation | `generateStaticParams` + `readItems` for slugs |
| Search | `searchParams` → `readItems` with `search` param |
| Filtered list | `searchParams` → Directus `filter` object |
| Image gallery | `readItems` on files collection + `next/image` with asset URL helper |
| Form submission | Server Action → `createItem`/`updateItem` → `revalidatePath` |
| Global settings | Singleton collection + `readItems('global')` in layout |
| SEO metadata | `generateMetadata` + `readItems` by slug |
