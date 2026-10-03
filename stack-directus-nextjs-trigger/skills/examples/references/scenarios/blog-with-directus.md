# Scenario: Blog with Directus + Next.js

Build a content blog with posts, authors, categories, featured images and SEO metadata. Uses the boundary rules of `directus-to-nextjs` (tagged reads in `lib/content.ts`, asset URLs without a token) and the revalidation pipeline of `deployment`.

## Directus Collections

### `authors`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `name` | String | Display name |
| `bio` | Text | Author biography |
| `avatar` | File (M2O → directus_files) | Profile image |
| `slug` | String (unique) | URL identifier |

### `categories`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `name` | String | Category name |
| `slug` | String (unique) | URL identifier |

### `posts`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `status` | String | draft / published / archived |
| `title` | String | Post title |
| `slug` | String (unique) | URL identifier |
| `excerpt` | Text | Short summary for listings and SEO |
| `content` | WYSIWYG | Post body (HTML) |
| `featured_image` | File (M2O → directus_files) | Hero image |
| `author` | M2O → authors | Post author |
| `date_published` | Datetime | Publish date |
| `date_created` | Timestamp (auto) | System field |

A new collection in Directus 12 gets a boolean `archived` field instead of a `status` dropdown. This scenario models `status`; with `archived`, filter on `{ archived: { _eq: false } }` and change the type to match.

### `posts_categories` (junction)

| Field | Type |
|-------|------|
| `posts_id` | M2O → posts |
| `categories_id` | M2O → categories |

## TypeScript Types

The schema above maps to the blog interfaces in `directus-dev` → `sdk-patterns` → `references/content-queries.md` (`Post`, `Author`, `Category`, the `PostCategory` junction and `Schema`). Copy them into `types/directus.ts`. The junction must be in `Schema` for the nested `categories` query to type-check.

## Reads

`lib/content.ts` from `directus-to-nextjs` has everything this scenario reads: `getPublishedPosts()`, `getPostSlugs()` and `getPostBySlug()`, each tagged with the collections it reads (`posts`, `authors`). The pages below call it and know nothing about caching.

## Blog Listing Page

```typescript
// app/blog/page.tsx
import Image from 'next/image';
import Link from 'next/link';
import { directusAsset } from '@/lib/directus-asset';
import { getPublishedPosts } from '@/lib/content';

export const metadata = {
  title: 'Blog',
  description: 'Latest articles and updates',
};

export default async function BlogPage() {
  const posts = await getPublishedPosts();

  return (
    <main>
      <h1>Blog</h1>
      <div>
        {posts.map((post) => {
          const cover = directusAsset(post.featured_image, { width: 600, height: 340, fit: 'cover' });
          return (
            <article key={post.id}>
              {cover && <Image src={cover} alt={post.title} width={600} height={340} />}
              <h2>
                <Link href={`/blog/${post.slug}`}>{post.title}</Link>
              </h2>
              <p>{post.excerpt}</p>
              <span>
                By {typeof post.author === 'object' ? post.author.name : 'Unknown'} &middot;{' '}
                {new Date(post.date_published).toLocaleDateString()}
              </span>
            </article>
          );
        })}
      </div>
    </main>
  );
}
```

## Blog Detail Page

```typescript
// app/blog/[slug]/page.tsx
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { directusAsset } from '@/lib/directus-asset';
import { getPostBySlug, getPostSlugs } from '@/lib/content';

export async function generateStaticParams() {
  const slugs = await getPostSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPostBySlug(slug);
  if (!post) return {};
  // openGraph needs an absolute URL: that holds in asset mode A. In proxy mode B resolve it against the site URL
  const cover = directusAsset(post.featured_image, { width: 1200, height: 630, fit: 'cover' });
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: { title: post.title, description: post.excerpt, images: cover ? [cover] : [] },
  };
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPostBySlug(slug);
  if (!post) notFound();

  const author = typeof post.author === 'object' ? post.author : null;
  const cover = directusAsset(post.featured_image, { width: 1200, height: 600, fit: 'cover' });

  return (
    <article>
      {cover && <Image src={cover} alt={post.title} width={1200} height={600} priority />}
      <h1>{post.title}</h1>
      {author && <p>By {author.name}</p>}
      <time>{new Date(post.date_published).toLocaleDateString()}</time>
      {/* The body is HTML written by Directus editors. Sanitize it first if anyone less trusted can write it */}
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
    </article>
  );
}
```

## RSS Feed

```typescript
// app/feed.xml/route.ts
import { getPublishedPosts } from '@/lib/content';

export async function GET() {
  const posts = await getPublishedPosts();
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com';

  const items = posts
    .map(
      (post) => `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${siteUrl}/blog/${post.slug}</link>
      <description><![CDATA[${post.excerpt}]]></description>
      <pubDate>${new Date(post.date_published).toUTCString()}</pubDate>
    </item>`,
    )
    .join('');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Blog</title>
    <link>${siteUrl}/blog</link>${items}
  </channel>
</rss>`;

  return new Response(xml, { headers: { 'Content-Type': 'application/xml' } });
}
```

## Revalidation Strategy

- Every read carries a tag for each collection it reads, expanded relations included: the listing reads `posts` and `authors`, the detail page also `categories`, the slug list only `posts`. The pages carry no `revalidate` export.
- The Directus Flow of `deployment` lists `posts`, `authors` and `categories`; so does `COLLECTION_TAGS` in `/api/revalidate`. An edit to an author or a category then refreshes every page that shows it.
- Detail pages are generated at build time from `generateStaticParams`; a post published later is rendered on its first request.
- The one-hour lifetime in `lib/content.ts` is only a safety net for a missed webhook.
- The RSS route is dynamic (a `GET` Route Handler is not cached by default) and cheap, because its Directus read comes from the tagged cache.
