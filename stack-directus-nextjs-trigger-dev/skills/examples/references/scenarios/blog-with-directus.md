# Scenario: Blog with Directus + Next.js

Build a content blog with posts, authors, categories, featured images, and SEO metadata.

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

### `posts_categories` (junction)

| Field | Type |
|-------|------|
| `posts_id` | M2O → posts |
| `categories_id` | M2O → categories |

## TypeScript Types

```typescript
// types/directus.ts

export interface Author {
  id: string;
  name: string;
  bio: string;
  avatar: string | null;
  slug: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
}

export interface Post {
  id: string;
  status: 'draft' | 'published' | 'archived';
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  featured_image: string | null;
  author: string | Author;
  categories: { categories_id: string | Category }[];
  date_published: string;
  date_created: string;
}

export interface Schema {
  posts: Post[];
  authors: Author[];
  categories: Category[];
}
```

## Blog Listing Page

```typescript
// app/blog/page.tsx
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';
import Image from 'next/image';
import Link from 'next/link';
import { directusAsset } from '@/lib/directus-asset';

export const revalidate = 60;

export const metadata = {
  title: 'Blog',
  description: 'Latest articles and updates',
};

export default async function BlogPage() {
  const posts = await directus.request(
    readItems('posts', {
      filter: { status: { _eq: 'published' } },
      sort: ['-date_published'],
      fields: [
        'id', 'title', 'slug', 'excerpt', 'featured_image',
        'date_published', 'author.name', 'author.slug',
      ],
      limit: 20,
    })
  );

  return (
    <main>
      <h1>Blog</h1>
      <div>
        {posts.map((post) => (
          <article key={post.id}>
            {post.featured_image && (
              <Image
                src={directusAsset(post.featured_image, { width: 600, height: 340, fit: 'cover' })!}
                alt={post.title}
                width={600}
                height={340}
              />
            )}
            <h2>
              <Link href={`/blog/${post.slug}`}>{post.title}</Link>
            </h2>
            <p>{post.excerpt}</p>
            <span>
              By {typeof post.author === 'object' ? post.author.name : 'Unknown'} &middot;{' '}
              {new Date(post.date_published).toLocaleDateString()}
            </span>
          </article>
        ))}
      </div>
    </main>
  );
}
```

## Blog Detail Page

```typescript
// app/blog/[slug]/page.tsx
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { directusAsset } from '@/lib/directus-asset';

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
    readItems('posts', {
      filter: { slug: { _eq: slug }, status: { _eq: 'published' } },
      fields: ['title', 'excerpt', 'featured_image'],
      limit: 1,
    })
  );
  if (!post) return {};
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: post.featured_image
        ? [directusAsset(post.featured_image, { width: 1200, height: 630, fit: 'cover' })!]
        : [],
    },
  };
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [post] = await directus.request(
    readItems('posts', {
      filter: { slug: { _eq: slug }, status: { _eq: 'published' } },
      fields: ['*', 'author.*', 'categories.categories_id.*'],
      limit: 1,
    })
  );

  if (!post) notFound();

  const author = typeof post.author === 'object' ? post.author : null;

  return (
    <article>
      {post.featured_image && (
        <Image
          src={directusAsset(post.featured_image, { width: 1200, height: 600, fit: 'cover' })!}
          alt={post.title}
          width={1200}
          height={600}
          priority
        />
      )}
      <h1>{post.title}</h1>
      {author && <p>By {author.name}</p>}
      <time>{new Date(post.date_published).toLocaleDateString()}</time>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
    </article>
  );
}
```

## RSS Feed

```typescript
// app/feed.xml/route.ts
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';

export async function GET() {
  const posts = await directus.request(
    readItems('posts', {
      filter: { status: { _eq: 'published' } },
      sort: ['-date_published'],
      fields: ['title', 'slug', 'excerpt', 'date_published'],
      limit: 50,
    })
  );

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com';
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Blog</title>
    <link>${siteUrl}/blog</link>
    ${posts
      .map(
        (post) => `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${siteUrl}/blog/${post.slug}</link>
      <description><![CDATA[${post.excerpt}]]></description>
      <pubDate>${new Date(post.date_published).toUTCString()}</pubDate>
    </item>`
      )
      .join('')}
  </channel>
</rss>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml' },
  });
}
```

## Revalidation Strategy

- Listing page: `revalidate = 60` (ISR every 60 seconds)
- Detail pages: Static at build time via `generateStaticParams`, revalidated on-demand via Directus Automate webhook
- RSS feed: Dynamic (no caching)
