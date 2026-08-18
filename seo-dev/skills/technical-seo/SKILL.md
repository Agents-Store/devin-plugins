---
name: technical-seo
description: Technical SEO for Next.js — crawlability, indexability, redirects, hreflang, and security. This skill should be used when the user asks about "technical SEO", "crawlability", "indexability", "noindex", "nofollow", "canonical tags", "redirects", "301 redirect", "hreflang", "internationalization SEO", "mobile-first indexing", "security headers", "URL structure", or needs to solve crawling and indexing issues.
---

# Technical SEO

Technical SEO ensures search engines can discover, crawl, render, and index your pages correctly.

## Crawlability

### URL Structure

Good URLs are short, descriptive, and keyword-inclusive:

```
Good: /blog/nextjs-seo-guide
Bad:  /blog/post?id=12345
Bad:  /blog/2026/03/15/my-first-blog-post-about-seo-optimization-techniques
```

Rules:
- Lowercase only — `/About` and `/about` are different URLs to crawlers
- Hyphens between words (not underscores)
- No trailing slashes (or always trailing — be consistent)
- No dates in URLs unless content is time-sensitive (news)
- No query parameters for indexable pages

Configure trailing slash behavior in `next.config.ts`:
```ts
const nextConfig = {
  trailingSlash: false,  // Pick one and be consistent
}
```

### Internal Linking

Every page must be reachable from at least one other page. Orphan pages (no inbound links) are rarely crawled.

```tsx
// Good: contextual internal links
<p>
  Read our <Link href="/blog/nextjs-seo-guide">complete SEO guide</Link> for details.
</p>

// Good: navigation and breadcrumbs provide crawl paths
<nav>
  <Link href="/blog">Blog</Link>
  <Link href="/products">Products</Link>
</nav>
```

### Pagination

For paginated content (blog listing, product catalog):

```tsx
// app/blog/page.tsx
export async function generateMetadata({ searchParams }: {
  searchParams: Promise<{ page?: string }>
}): Promise<Metadata> {
  const { page } = await searchParams
  const pageNum = Number(page) || 1

  return {
    title: pageNum > 1 ? `Blog - Page ${pageNum}` : 'Blog',
    alternates: {
      canonical: '/blog',  // All pages canonicalize to the first page
    },
  }
}
```

Google ignores `rel="prev"` and `rel="next"` since 2019. Use canonical to the first page, or let Google discover pagination naturally.

## Indexability

### Canonical Tags

Every page needs a canonical URL. Set in `alternates.canonical`:

```tsx
export const metadata: Metadata = {
  alternates: {
    canonical: '/products/blue-shoes',  // Resolves against metadataBase
  },
}
```

Canonical tells Google which URL is the "master" when multiple URLs show the same content (e.g., with/without query params, with/without trailing slash).

### noindex / nofollow

Block specific pages from indexing:

```tsx
// app/admin/page.tsx
export const metadata: Metadata = {
  robots: {
    index: false,
    follow: false,  // Also don't follow links on this page
  },
}

// Or for specific pages that should be crawled but not indexed:
export const metadata: Metadata = {
  robots: {
    index: false,
    follow: true,   // Follow links, but don't index this page
  },
}
```

Use `noindex` for: admin pages, thank-you pages, search results, user dashboards, duplicate content.

### Duplicate Content

Common causes and solutions:

| Cause | Solution |
|-------|----------|
| www vs non-www | 301 redirect to one version |
| HTTP vs HTTPS | 301 redirect HTTP → HTTPS |
| Trailing slash inconsistency | Pick one, redirect the other |
| URL parameters (`?sort=price`) | Canonical to base URL |
| Pagination (`?page=2`) | Canonical to page 1 or self-referencing |
| Same content, different paths | Canonical to primary URL |

## Redirects

### next.config.ts Redirects

```ts
// next.config.ts
const nextConfig = {
  async redirects() {
    return [
      {
        source: '/old-blog/:slug',
        destination: '/blog/:slug',
        permanent: true,       // 301 — use for permanent URL changes
      },
      {
        source: '/temp-promo',
        destination: '/products',
        permanent: false,      // 302 — use for temporary redirects
      },
    ]
  },
}
```

### Rewrites (URL Masking)

Rewrites change the backend URL without changing the browser URL:

```ts
async rewrites() {
  return [
    {
      source: '/blog/:slug',
      destination: '/posts/:slug',  // Internal path — user sees /blog/:slug
    },
  ]
}
```

### Redirect Rules
- **301 (permanent)**: URL permanently moved. Link equity transfers. Use for domain changes, slug changes, removed pages.
- **302 (temporary)**: URL temporarily moved. No link equity transfer. Use for A/B tests, maintenance, seasonal content.
- Avoid redirect chains (A → B → C). Maximum 2 hops.
- Never redirect to a page that itself redirects.

## International SEO (Hreflang)

### Next.js Metadata API

```tsx
// app/[locale]/about/page.tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>
}): Promise<Metadata> {
  const { locale } = await params

  return {
    alternates: {
      canonical: `/${locale}/about`,
      languages: {
        'en': '/en/about',
        'de': '/de/about',
        'fr': '/fr/about',
        'x-default': '/en/about',  // Fallback for unspecified languages
      },
    },
  }
}
```

This generates `<link rel="alternate" hreflang="en" href="https://yourdomain.com/en/about" />` tags.

### Hreflang Rules

1. **Always include `x-default`** — points to the default language version
2. **Self-reference required** — each page must include itself in the hreflang set
3. **Reciprocal linking** — every page must link to all its language variants
4. **Use RFC 5646 codes** — `en-US`, `de-DE`, not `en_US` or `english`
5. **Include in sitemap** — add `alternates.languages` to sitemap entries

### Subdirectory vs Subdomain

| Approach | Example | Best For |
|----------|---------|----------|
| **Subdirectory** | `/en/`, `/de/` | Most apps — consolidates domain authority |
| **Subdomain** | `en.example.com` | Region-specific content, separate teams |
| **ccTLD** | `example.de` | Maximum geo-targeting, highest effort |

Prefer subdirectories for most Next.js apps.

## Mobile-First Indexing

Google uses the mobile version of your site for indexing. Requirements:

- **Viewport meta tag**: Next.js sets this automatically via `metadata.viewport` or the default
- **Responsive design**: All content accessible on mobile
- **Touch targets**: Minimum 48x48px for interactive elements
- **No horizontal scroll**: Content fits viewport width
- **Same content on mobile and desktop**: Google indexes the mobile version

```tsx
// Explicit viewport (Next.js sets sensible defaults)
export const metadata: Metadata = {
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
  },
}
```

## Security Headers

Security headers improve trust and can indirectly help SEO:

```ts
// next.config.ts
const nextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
        ],
      },
    ]
  },
}
```

HTTPS is mandatory for SEO — Google confirmed it as a ranking signal.

## Technical SEO Checklist

| Category | Item | Priority |
|----------|------|----------|
| **Crawl** | robots.txt allows important pages | Critical |
| **Crawl** | XML sitemap submitted to GSC | Critical |
| **Crawl** | No orphan pages | High |
| **Crawl** | Clean URL structure | High |
| **Index** | Canonical tags on all pages | Critical |
| **Index** | noindex on non-public pages | High |
| **Index** | No duplicate content | High |
| **Redirect** | 301 for permanent moves | High |
| **Redirect** | No redirect chains | Medium |
| **i18n** | Hreflang with x-default | High (if multilingual) |
| **Mobile** | Responsive on all viewports | Critical |
| **Mobile** | Touch targets >= 48px | High |
| **Security** | HTTPS everywhere | Critical |
| **Security** | Security headers configured | Medium |
