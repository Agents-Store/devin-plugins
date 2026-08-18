---
name: content-seo
description: Content optimization for SEO — headings, images, internal linking, and URL structure. This skill should be used when the user asks about "content SEO", "heading structure", "h1 tag", "alt text", "image SEO", "internal linking", "URL slugs", "content optimization", "heading hierarchy", "image optimization for SEO", or needs guidance on structuring page content for search engines.
---

# Content SEO

Content SEO covers how to structure page content so search engines understand it and rank it appropriately.

## Heading Hierarchy

### Rules

1. **One H1 per page** — the primary topic of the page
2. **Logical nesting** — H2 under H1, H3 under H2 (never skip levels)
3. **Descriptive text** — headings should describe the section content
4. **Include keywords naturally** — no keyword stuffing

```tsx
// Good hierarchy
<h1>Next.js SEO Complete Guide</h1>          // Page topic
  <h2>Metadata Configuration</h2>             // Major section
    <h3>Static Metadata</h3>                   // Subsection
    <h3>Dynamic Metadata</h3>                  // Subsection
  <h2>Structured Data</h2>                     // Major section
    <h3>JSON-LD Setup</h3>                     // Subsection
    <h3>Schema Types</h3>                      // Subsection

// Bad — skipped levels, multiple H1s
<h1>Guide</h1>
<h1>Another Title</h1>         // Two H1s
<h3>Section</h3>               // Skipped H2
```

### Next.js Pattern

In App Router, the H1 typically comes from the page component, not the layout:

```tsx
// app/layout.tsx — NO H1 here (layout wraps all pages)
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header><nav>{/* navigation */}</nav></header>
        <main>{children}</main>
      </body>
    </html>
  )
}

// app/blog/[slug]/page.tsx — H1 here
export default async function BlogPost({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPost(slug)

  return (
    <article>
      <h1>{post.title}</h1>
      {/* content */}
    </article>
  )
}
```

## Image SEO

### Alt Text Rules

| Rule | Example |
|------|---------|
| Be descriptive and specific | `alt="Red Nike running shoes on forest trail"` |
| Under 125 characters | Concise but meaningful |
| Include keywords naturally | Don't force irrelevant keywords |
| No "image of" or "picture of" | Screen readers already announce "image" |
| Empty for decorative images | `alt=""` for dividers, backgrounds |
| Describe function for interactive images | `alt="Search"` for a search icon button |

```tsx
// Good alt text
<Image
  src="/products/red-running-shoes.webp"
  alt="Red Nike Air Max running shoes on white background"
  width={800}
  height={600}
/>

// Decorative image — empty alt
<Image src="/decorative-line.svg" alt="" width={100} height={2} />
```

### File Naming

Search engines read file names. Use descriptive, hyphenated names:

```
Good: red-nike-running-shoes.webp
Bad:  IMG_4827.jpg
Bad:  shoe_photo_final_v2.png
```

### Image Format Priority (2026)

1. **AVIF** — best compression (50% smaller than JPEG), 93%+ browser support
2. **WebP** — 30% smaller than JPEG, universal support
3. **JPEG/PNG** — fallback only

`next/image` handles format negotiation automatically when configured:
```ts
images: { formats: ['image/avif', 'image/webp'] }
```

### Responsive Images

Always provide `sizes` attribute so browsers download the correct size:

```tsx
<Image
  src="/hero.jpg"
  alt="Hero image showing team collaboration"
  width={1920}
  height={1080}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  priority  // Only for above-the-fold LCP image
/>
```

### Lazy Loading

`next/image` lazy-loads by default. Only disable for above-the-fold images using `priority`:

```tsx
// Above the fold — preload immediately
<Image src="/hero.jpg" alt="Hero" width={1200} height={630} priority />

// Below the fold — lazy loads automatically
<Image src="/feature.jpg" alt="Feature" width={600} height={400} />
```

## Internal Linking

### Strategy

Internal links distribute page authority and help crawlers discover content.

1. **Link contextually** — from within body content, not just navigation
2. **Use descriptive anchor text** — not "click here" or "read more"
3. **Link to important pages frequently** — high-priority pages get more internal links
4. **Link deep** — connect related content, not just top-level pages
5. **Fix broken links** — 404s waste crawl budget and authority

```tsx
// Good — descriptive anchor text
<p>
  Learn how to implement
  <Link href="/blog/structured-data-guide">Schema.org structured data</Link>
  for better search results.
</p>

// Bad — generic anchor text
<p>
  For structured data, <Link href="/blog/structured-data-guide">click here</Link>.
</p>
```

### Breadcrumbs

Breadcrumbs provide both navigation and SEO value:

```tsx
// components/breadcrumbs.tsx
import Link from 'next/link'
import { JsonLd } from '@/components/json-ld'
import { createBreadcrumbList } from '@/lib/schema'

interface BreadcrumbItem {
  name: string
  href: string
}

export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  return (
    <>
      <JsonLd
        data={createBreadcrumbList(
          items.map((item) => ({ name: item.name, url: `https://yourdomain.com${item.href}` }))
        )}
      />
      <nav aria-label="Breadcrumb">
        <ol className="flex gap-2 text-sm text-muted-foreground">
          {items.map((item, i) => (
            <li key={item.href} className="flex items-center gap-2">
              {i > 0 && <span>/</span>}
              {i === items.length - 1 ? (
                <span aria-current="page">{item.name}</span>
              ) : (
                <Link href={item.href}>{item.name}</Link>
              )}
            </li>
          ))}
        </ol>
      </nav>
    </>
  )
}
```

## URL Slug Best Practices

| Rule | Good | Bad |
|------|------|-----|
| Lowercase | `/blog/seo-guide` | `/Blog/SEO-Guide` |
| Hyphens between words | `/seo-best-practices` | `/seo_best_practices` |
| Include keywords | `/products/running-shoes` | `/products/item-42` |
| Short and descriptive | `/blog/nextjs-seo` | `/blog/complete-guide-to-seo-in-nextjs-2026` |
| No stop words | `/blog/seo-guide` | `/blog/a-guide-to-the-seo` |
| No dates (usually) | `/blog/seo-guide` | `/blog/2026/03/seo-guide` |

### Generating Slugs

```tsx
function generateSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')    // Remove special chars
    .replace(/\s+/g, '-')             // Spaces to hyphens
    .replace(/-+/g, '-')              // Collapse multiple hyphens
    .replace(/^-|-$/g, '')            // Trim leading/trailing hyphens
}

generateSlug('Next.js SEO: A Complete Guide!')  // → 'nextjs-seo-a-complete-guide'
```

## Content Formatting for AI Overviews

Google's AI Overviews cite content formatted with BLUF (Bottom Line Up Front):

1. **Lead with the answer** — first 2-3 sentences should directly answer the query
2. **Use clear headers** — structured sections that match search intent
3. **Include specific facts** — numbers, dates, steps (not vague generalizations)
4. **Use lists and tables** — easy to parse and cite

```tsx
// Good — BLUF pattern
<h2>How to Add Structured Data to Next.js</h2>
<p>
  Install the schema-dts package and create a JsonLd component that renders
  a <code>&lt;script type="application/ld+json"&gt;</code> tag in your
  Server Component. Use factory functions for type-safe schema creation.
</p>

// Bad — buries the answer
<h2>How to Add Structured Data to Next.js</h2>
<p>
  Structured data has been an important part of SEO for many years.
  In this section, we'll explore the various approaches...
</p>
```

## E-E-A-T Signals (2026)

Google's quality evaluation emphasizes Experience, Expertise, Authoritativeness, Trustworthiness:

| Signal | Implementation |
|--------|----------------|
| **Author bios** | Show author name, credentials, photo on articles |
| **Publish dates** | Display `datePublished` and `dateModified` visibly |
| **Author schema** | Add `Person` schema with author URL |
| **About page** | Company info, team, mission |
| **Contact page** | Real contact methods (not just a form) |
| **External references** | Cite sources, link to authoritative references |
