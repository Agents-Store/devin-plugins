---
name: structured-data
description: Schema.org structured data and JSON-LD implementation for Next.js. This skill should be used when the user asks about "structured data", "JSON-LD", "Schema.org", "rich snippets", "rich results", "schema markup", "Organization schema", "Article schema", "Product schema", "BreadcrumbList", or needs to add structured data to improve search appearance.
---

# Structured Data (Schema.org / JSON-LD)

Structured data tells search engines what your content means, not just what it says. Google uses it to generate rich results (product prices and ratings, breadcrumb trails, event listings, article and video appearances) and to pick a site name. Use JSON-LD format — Google's recommended approach.

Not every type still produces a visible result. Google retires features over time — the FAQ rich result stopped appearing on 2026-05-07, the HowTo rich result was removed from desktop and mobile (fully gone since September 2023), and the search box under brand results was removed on 2024-11-21. Markup for a retired feature is harmless (Google says unsupported structured data causes no problems in Search or errors in Search Console), but it earns no SERP appearance. Before recommending a type for its search appearance, check the current [Search Gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery).

## Setup

Install TypeScript types for Schema.org (zero bundle impact — types only):

```bash
pnpm add -D schema-dts
```

## Reusable JSON-LD Component

Create a type-safe component for rendering structured data:

```tsx
// components/json-ld.tsx
import type { Thing, WithContext } from 'schema-dts'

export function JsonLd<T extends Thing>({ data }: { data: WithContext<T> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data).replace(/</g, '\\u003c'),
      }}
    />
  )
}
```

The `.replace(/</g, '\\u003c')` sanitizes the output to prevent XSS via `</script>` injection.

## Schema Factory Functions

Create reusable factory functions in a utility file:

```tsx
// lib/schema.ts
import type {
  Article,
  BreadcrumbList,
  Organization,
  Product,
  WebSite,
  WithContext,
} from 'schema-dts'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'

export function createOrganization(org: {
  name: string
  logo: string
  url: string
  description?: string
  sameAs?: string[]
}): WithContext<Organization> {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': `${org.url}/#organization`,
    name: org.name,
    url: org.url,
    logo: { '@type': 'ImageObject', url: org.logo },
    description: org.description,
    sameAs: org.sameAs,
  }
}

export function createWebSite(
  url: string,
  name: string,
  alternateName?: string[]
): WithContext<WebSite> {
  // Google reads WebSite name / alternateName / url as the site name shown in
  // results. It only uses this markup on the home page. Do not add a
  // SearchAction here: Google removed the search-box feature it powered, and
  // the markup no longer does anything in Google Search.
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    url,
    name,
    alternateName,
  }
}

export function createBreadcrumbList(
  items: Array<{ name: string; url: string }>
): WithContext<BreadcrumbList> {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  }
}

export function createArticle(article: {
  headline: string
  description: string
  image: string
  datePublished: string
  dateModified?: string
  author: { name: string; url?: string }
  url: string
}): WithContext<Article> {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.headline,
    description: article.description,
    image: article.image,
    datePublished: article.datePublished,
    dateModified: article.dateModified || article.datePublished,
    author: { '@type': 'Person', name: article.author.name, url: article.author.url },
    mainEntityOfPage: { '@type': 'WebPage', '@id': article.url },
  }
}

export function createProduct(product: {
  name: string
  description: string
  image: string
  price: string
  currency: string
  availability: 'InStock' | 'OutOfStock' | 'PreOrder'
  sku?: string
  brand?: string
  ratingValue?: string
  reviewCount?: number
  url: string
}): WithContext<Product> {
  return {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    image: product.image,
    sku: product.sku,
    brand: product.brand ? { '@type': 'Brand', name: product.brand } : undefined,
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: product.currency,
      availability: `https://schema.org/${product.availability}`,
      url: product.url,
    },
    // schema-dts expects ratingCount/reviewCount as number, not string
    aggregateRating: product.ratingValue
      ? {
          '@type': 'AggregateRating' as const,
          ratingValue: product.ratingValue,
          reviewCount: product.reviewCount,
        }
      : undefined,
  }
}
```

## Usage in Pages

### Sitewide Schema (Root Layout)

Place Organization schema in the root layout — it applies to every page. `WebSite` (site name) is read by Google from the home page only, so render it in `app/page.tsx` instead (see below):

```tsx
// app/layout.tsx
import { JsonLd } from '@/components/json-ld'
import { createOrganization } from '@/lib/schema'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <JsonLd
          data={createOrganization({
            name: 'Your Company',
            logo: 'https://yourdomain.com/logo.png',
            url: 'https://yourdomain.com',
            sameAs: [
              'https://twitter.com/yourcompany',
              'https://linkedin.com/company/yourcompany',
            ],
          })}
        />
        {children}
      </body>
    </html>
  )
}
```

### Home Page (Site Name)

```tsx
// app/page.tsx
import { JsonLd } from '@/components/json-ld'
import { createWebSite } from '@/lib/schema'

export default function HomePage() {
  return (
    <>
      <JsonLd data={createWebSite('https://yourdomain.com', 'Your Company', ['YC'])} />
      {/* page content */}
    </>
  )
}
```

### Article Page

```tsx
// app/blog/[slug]/page.tsx
import { JsonLd } from '@/components/json-ld'
import { createArticle, createBreadcrumbList } from '@/lib/schema'

export default async function BlogPost({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPost(slug)

  return (
    <>
      <JsonLd
        data={createArticle({
          headline: post.title,
          description: post.excerpt,
          image: post.image,
          datePublished: post.publishedAt,
          dateModified: post.updatedAt,
          author: { name: post.author.name, url: `/authors/${post.author.slug}` },
          url: `https://yourdomain.com/blog/${slug}`,
        })}
      />
      <JsonLd
        data={createBreadcrumbList([
          { name: 'Home', url: 'https://yourdomain.com' },
          { name: 'Blog', url: 'https://yourdomain.com/blog' },
          { name: post.title, url: `https://yourdomain.com/blog/${slug}` },
        ])}
      />
      <article>{/* page content */}</article>
    </>
  )
}
```

## @graph Pattern for Multiple Schemas

Combine multiple schemas in a single `<script>` tag:

```tsx
const schemas = {
  '@context': 'https://schema.org',
  '@graph': [
    createOrganization({ name: 'Acme', logo: '/logo.png', url: 'https://acme.com' }),
    createWebSite('https://acme.com', 'Acme'), // home page only
  ],
}

<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(schemas).replace(/</g, '\\u003c') }}
/>
```

## What Google Still Renders (2026)

Types Google lists in its [Search Gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery) (last updated 2026-06-15): Article, Breadcrumb, Carousel, Course list, Dataset, Discussion forum, Education Q&A, Employer aggregate rating, Event, Image metadata, Job posting, Local business, Math solver, Movie, Organization, Product, Profile page, Q&A, Recipe, Review snippet, Software app, Speakable, Subscription and paywalled content, Vacation rental, Video. Eligibility and the exact appearance differ per type — read the type's own documentation.

| Schema Type | What it feeds | Use On |
|-------------|---------------|--------|
| Organization | Organization details, logo, knowledge panel signals | Root layout |
| WebSite (`name`, `alternateName`) | Site name in results | Home page only |
| BreadcrumbList | Breadcrumb trail in the result | Inner pages |
| Article | Article appearance (headline, image, dates, author) | Blog / news posts |
| Product + Offer | Product snippets and merchant listings (price, availability, ratings) | Product pages |
| Event | Event experiences | Event pages |
| SoftwareApplication | Software app appearance | App pages |

**No longer produce a Google SERP feature** — do not implement these to win a result:

| Type | Status |
|------|--------|
| FAQPage | The FAQ rich result stopped appearing for all sites on 2026-05-07; Google removed its documentation and Rich Results Test support |
| HowTo | The HowTo rich result is removed on both desktop and mobile (fully gone since September 2023); its documentation was removed |
| WebSite + SearchAction (search box under brand results) | Feature removed on 2024-11-21 |

Existing valid markup of these types is harmless and does not need to be deleted — other consumers may still read it. Just do not spend effort adding it for Google, and write useful visible content (an FAQ section, numbered steps) for readers instead. Do not quote click-through-rate lifts for any type: Google publishes none.

## Validation

Always validate structured data before deploying:

1. **Google Rich Results Test**: https://search.google.com/test/rich-results — test by URL or paste code (only for types Google still renders; it no longer evaluates FAQ markup)
2. **Schema.org Validator**: https://validator.schema.org/ — syntax validation, works for any type
3. **Google Search Console** → Enhancements — monitor after deployment (2-4 weeks for results)

For complete JSON-LD examples covering all schema types, see `references/schema-examples.md`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Adding `FAQPage` or `HowTo` markup to win a rich result | Both features are removed from Google Search (FAQ since 2026-05-07, HowTo since 2023). Markup is harmless, but build a good visible FAQ or step list and skip the effort |
| Adding `WebSite` + `SearchAction` for a search box in results | That feature was removed in 2024. Keep `WebSite` with `name` / `alternateName` for the site name |
| Missing `@context` field | Always include `'@context': 'https://schema.org'` |
| Two identical schema types on same page | Combine into one or use `@graph` |
| Hardcoded dates | Use dynamic dates from CMS/database |
| Missing sanitization | Always use `.replace(/</g, '\\u003c')` |
| Schema doesn't match visible content | Google penalizes mismatched schema and page content |
