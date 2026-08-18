---
name: structured-data
description: Schema.org structured data and JSON-LD implementation for Next.js. This skill should be used when the user asks about "structured data", "JSON-LD", "Schema.org", "rich snippets", "rich results", "schema markup", "Organization schema", "Article schema", "Product schema", "BreadcrumbList", "FAQ schema", or needs to add structured data to improve search appearance.
---

# Structured Data (Schema.org / JSON-LD)

Structured data tells search engines what your content means, not just what it says. Google uses it to generate rich results (star ratings, product prices, breadcrumb trails, FAQ dropdowns). Use JSON-LD format — Google's recommended approach.

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

export function createWebSite(url: string, name: string): WithContext<WebSite> {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    url,
    name,
    // SearchAction with query-input requires a type assertion because schema-dts
    // does not include the 'query-input' property in its SearchAction type.
    // The JSON-LD output is valid — Google requires this exact format.
    potentialAction: {
      '@type': 'SearchAction',
      target: `${url}/search?q={search_term_string}`,
    } as WithContext<WebSite>['potentialAction'],
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

Place Organization and WebSite schema in the root layout — they apply to every page:

```tsx
// app/layout.tsx
import { JsonLd } from '@/components/json-ld'
import { createOrganization, createWebSite } from '@/lib/schema'

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
        <JsonLd data={createWebSite('https://yourdomain.com', 'Your Company')} />
        {children}
      </body>
    </html>
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
    createWebSite('https://acme.com', 'Acme'),
  ],
}

<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(schemas).replace(/</g, '\\u003c') }}
/>
```

## Rich Results Impact (2026)

| Schema Type | Rich Result | CTR Lift | Use On |
|-------------|-------------|----------|--------|
| Organization | Knowledge panel | Brand queries | Root layout |
| WebSite + SearchAction | Sitelinks searchbox | Brand queries | Root layout |
| BreadcrumbList | Breadcrumb trail in SERP | +5-10% | All pages |
| Article | Article snippets | High | Blog/news posts |
| Product + Offer | Price, stock, ratings | +30-35% | Product pages |
| HowTo | Step display (mobile only) | +15-25% | Tutorial pages |
| Event | Event listing | +20-25% | Event pages |

**FAQPage is restricted** to government and health websites since 2023. Do not implement it for regular websites — the rich result will not appear.

## Validation

Always validate structured data before deploying:

1. **Google Rich Results Test**: https://search.google.com/test/rich-results — test by URL or paste code
2. **Schema.org Validator**: https://validator.schema.org/ — syntax validation
3. **Google Search Console** → Enhancements — monitor after deployment (2-4 weeks for results)

For complete JSON-LD examples covering all schema types, see `references/schema-examples.md`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `FAQPage` on a regular website | Restricted to gov/health since 2023 — remove it |
| Missing `@context` field | Always include `'@context': 'https://schema.org'` |
| Two identical schema types on same page | Combine into one or use `@graph` |
| Hardcoded dates | Use dynamic dates from CMS/database |
| Missing sanitization | Always use `.replace(/</g, '\\u003c')` |
| Schema doesn't match visible content | Google penalizes mismatched schema and page content |
