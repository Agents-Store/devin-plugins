---
name: sitemap-robots
description: Sitemap and robots.txt configuration for Next.js App Router. This skill should be used when the user asks about "sitemap", "sitemap.xml", "robots.txt", "robots.ts", "next-sitemap", "XML sitemap", "sitemap generation", "block crawlers", "crawl budget", or needs to configure how search engines discover and crawl their pages.
---

# Sitemap & Robots.txt

Next.js App Router has built-in support for `sitemap.ts` and `robots.ts` — file conventions that generate `sitemap.xml` and `robots.txt` at build/request time.

## sitemap.ts — Basic

Create `app/sitemap.ts` to generate `/sitemap.xml`:

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    { url: `${BASE_URL}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${BASE_URL}/blog`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${BASE_URL}/contact`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.5 },
  ]
}
```

## sitemap.ts — Dynamic (CMS/Database)

Fetch pages from your CMS or database:

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Fetch dynamic pages from CMS
  const posts = await getAllPosts()
  const products = await getAllProducts()

  const postEntries: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${BASE_URL}/blog/${post.slug}`,
    lastModified: new Date(post.updatedAt),
    changeFrequency: 'weekly',
    priority: 0.7,
  }))

  const productEntries: MetadataRoute.Sitemap = products.map((product) => ({
    url: `${BASE_URL}/products/${product.slug}`,
    lastModified: new Date(product.updatedAt),
    changeFrequency: 'daily',
    priority: 0.8,
  }))

  return [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    ...postEntries,
    ...productEntries,
  ]
}
```

## Multiple Sitemaps (Large Sites)

For sites with more than 50,000 URLs, use `generateSitemaps` to split into multiple sitemap files:

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next'

const URLS_PER_SITEMAP = 50000

export async function generateSitemaps() {
  const totalProducts = await getProductCount()
  const sitemapCount = Math.ceil(totalProducts / URLS_PER_SITEMAP)

  return Array.from({ length: sitemapCount }, (_, i) => ({ id: i }))
}

export default async function sitemap(
  props: { id: Promise<string> }
): Promise<MetadataRoute.Sitemap> {
  const id = Number(await props.id)
  const start = id * URLS_PER_SITEMAP
  const products = await getProducts({ offset: start, limit: URLS_PER_SITEMAP })

  return products.map((product) => ({
    url: `https://yourdomain.com/products/${product.slug}`,
    lastModified: new Date(product.updatedAt),
  }))
}
```

This generates `/sitemap/0.xml`, `/sitemap/1.xml`, etc., with an automatic sitemap index.

## Nested Sitemaps

Place `sitemap.ts` in route segments for section-specific sitemaps:

```
app/
  sitemap.ts              → /sitemap.xml (main pages)
  blog/sitemap.ts         → /blog/sitemap.xml (blog posts)
  products/sitemap.ts     → /products/sitemap.xml (products)
```

## robots.ts — Basic

```tsx
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/', disallow: ['/api/', '/admin/'] },
    sitemap: `${process.env.NEXT_PUBLIC_SITE_URL}/sitemap.xml`,
  }
}
```

## robots.ts — Production vs Staging

Block indexing on non-production environments:

```tsx
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'
  const isProduction = process.env.VERCEL_ENV === 'production'

  if (!isProduction) {
    return { rules: { userAgent: '*', disallow: ['/'] } }
  }

  return {
    rules: [
      { userAgent: '*', allow: '/', disallow: ['/api/', '/admin/', '/_next/'] },
      { userAgent: 'GPTBot', disallow: ['/'] },
      { userAgent: 'CCBot', disallow: ['/'] },
      { userAgent: 'Google-Extended', disallow: ['/'] },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  }
}
```

## AI Crawler Management (2025-2026)

New crawler types to manage in `robots.txt`:

| Crawler | Purpose | Recommendation |
|---------|---------|----------------|
| `Googlebot` | Google Search indexing | Allow |
| `Bingbot` | Bing Search indexing | Allow |
| `GPTBot` | OpenAI training data | Block (unless opted in) |
| `CCBot` | Common Crawl / AI training | Block (unless opted in) |
| `Google-Extended` | Google AI training (not Search) | Block (unless opted in) |
| `OAI-SearchBot` | OpenAI Search (ChatGPT search) | Allow (beneficial for traffic) |
| `Applebot-Extended` | Apple AI training | Block (unless opted in) |

Differentiate beneficial crawlers (drive traffic) from training scrapers (use your content without attribution).

## Multilingual Sitemap (Hreflang)

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'
const LOCALES = ['en', 'de', 'fr']
const ROUTES = ['', '/about', '/blog']

export default function sitemap(): MetadataRoute.Sitemap {
  const entries: MetadataRoute.Sitemap = []

  for (const locale of LOCALES) {
    for (const route of ROUTES) {
      entries.push({
        url: `${BASE_URL}/${locale}${route}`,
        lastModified: new Date(),
        alternates: {
          languages: Object.fromEntries([
            ...LOCALES.map((l) => [l, `${BASE_URL}/${l}${route}`]),
            ['x-default', `${BASE_URL}/en${route}`],
          ]),
        },
      })
    }
  }

  return entries
}
```

## When to Use next-sitemap

The built-in `sitemap.ts` covers most use cases. Consider `next-sitemap` only for:

- Complex `transform` functions that modify URLs based on external data
- Server-side sitemap generation (App Router `sitemap.ts` is already server-rendered)
- Legacy Pages Router projects

For new App Router projects, prefer the built-in approach.

## Priority & changeFrequency Guide

| Page Type | Priority | changeFrequency |
|-----------|----------|-----------------|
| Homepage | 1.0 | daily |
| Category pages | 0.8-0.9 | weekly |
| Blog posts | 0.6-0.7 | weekly |
| Product pages | 0.7-0.8 | daily |
| Static pages (about, contact) | 0.5-0.6 | monthly |
| Legal pages (terms, privacy) | 0.3 | yearly |

Note: Google has stated that `priority` and `changeFrequency` are largely ignored. `lastModified` with an accurate date is the most useful signal. Include priority for other search engines that may still use it.

## Verification

After setting up sitemap and robots:

1. Visit `/sitemap.xml` — valid XML with all pages
2. Visit `/robots.txt` — correct rules
3. Submit sitemap URL in Google Search Console → Sitemaps
4. Check Google Search Console → Settings → Crawl stats for crawl activity
