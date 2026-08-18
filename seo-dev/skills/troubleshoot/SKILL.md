---
name: troubleshoot
description: SEO problem diagnosis and solutions for Next.js. This skill should be used when the user reports "page not indexed", "no rich snippets", "low PageSpeed score", "duplicate content", "OG image not showing", "search console errors", "SEO not working", "Google not finding my page", or needs to debug any SEO-related issue.
---

# SEO Troubleshooting

Diagnostic trees for common SEO problems. Start from the symptom, follow the tree to the fix.

## "Page Not Indexed by Google"

```
Page not appearing in Google?
├─ Is the page in your sitemap?
│  └─ No → Add it to sitemap.ts, resubmit in GSC
├─ Does robots.txt block it?
│  └─ Check /robots.txt — is the path in Disallow?
├─ Does the page have noindex?
│  └─ Check metadata: robots.index should be true (or absent)
├─ Is there a canonical pointing elsewhere?
│  └─ Check alternates.canonical — must point to self
├─ Is the staging env blocking crawlers?
│  └─ Check robots.ts — VERCEL_ENV or NODE_ENV check
├─ Is the page behind JavaScript only?
│  └─ Use Server Components — content must be in initial HTML
├─ Is the page returning non-200 status?
│  └─ Google excludes non-200 pages from rendering queue (Dec 2025)
├─ Is the page new?
│  └─ Wait 2-4 weeks. Use GSC URL Inspection to request indexing
└─ Is the page thin or duplicate?
   └─ Add unique, valuable content. Check for duplicate URLs
```

**Quick fix**: In Google Search Console → URL Inspection → paste the URL → "Request Indexing". This does not guarantee indexing but puts the URL in the crawl queue.

## "No Rich Snippets / Rich Results"

```
Structured data not showing rich results?
├─ Is the JSON-LD valid?
│  └─ Test at https://search.google.com/test/rich-results
│     ├─ Errors found → Fix the JSON-LD (missing fields, wrong types)
│     └─ Valid but "not eligible" → Schema type restrictions apply
├─ Is the schema type still supported?
│  ├─ FAQPage → Restricted to gov/health sites since 2023
│  ├─ HowTo → Desktop removed in 2023, mobile/voice only
│  └─ Other types → Check Google's supported types list
├─ Does the schema match page content?
│  └─ Google verifies schema against visible content — mismatches are penalized
├─ Is the site new or low-authority?
│  └─ Rich results require page authority. New sites may wait 1-3 months
├─ Is there competing structured data?
│  └─ Don't use two identical @types on the same page
└─ Has it been enough time?
   └─ Rich results take 2-4 weeks to appear after successful crawl
```

**Common fix**: Most rich result failures come from missing required fields. Run the Rich Results Test and fix every error and warning.

## "Low PageSpeed / Lighthouse Score"

```
PageSpeed Insights score < 90?
├─ LCP > 2.5s?
│  ├─ Is the LCP element an image?
│  │  ├─ Missing priority prop → Add priority to hero/banner Image
│  │  ├─ Missing sizes prop → Add responsive sizes attribute
│  │  └─ Image too large → Use AVIF/WebP, configure formats in next.config
│  ├─ Is the LCP element text?
│  │  ├─ Font blocking render → Use next/font with display: swap
│  │  └─ Server response slow → Check API/database latency, use ISR
│  └─ Server-side rendering delay?
│     └─ Use Suspense with streaming, add loading.tsx skeletons
├─ INP > 200ms? (or high TBT in lab)
│  ├─ Long JavaScript tasks?
│  │  ├─ Heavy components → Use dynamic() imports with ssr: false
│  │  ├─ Large event handlers → Use startTransition, useDeferredValue
│  │  └─ Third-party scripts → Defer with next/script strategy="lazyOnload"
│  ├─ Large DOM?
│  │  └─ Target < 1500 nodes. Use virtual scrolling for long lists
│  └─ Large bundle?
│     └─ Run NEXT_BUNDLE_ANALYZE=true next build. Remove unused deps
├─ CLS > 0.1?
│  ├─ Images without dimensions → Add width/height to all Image components
│  ├─ Font flash (FOUT) → Use next/font (self-hosted, no FOUT)
│  ├─ Dynamic content injection → Reserve space with min-height or Suspense
│  └─ Ads or embeds loading late → Set explicit dimensions, use placeholder
└─ General slow?
   ├─ Not using ISR → Add revalidate to static pages
   ├─ No CDN → Deploy to Vercel or edge-enabled host
   └─ Too many third-party scripts → Audit and remove unused scripts
```

## "Duplicate Content"

```
Google reporting duplicate content?
├─ Same content, different URLs?
│  ├─ www vs non-www → 301 redirect to one version
│  ├─ HTTP vs HTTPS → 301 redirect HTTP → HTTPS
│  ├─ Trailing slash inconsistency → Set trailingSlash in next.config.ts
│  └─ Query parameters → Canonical to base URL (without params)
├─ Same content across pages?
│  ├─ Category/tag pages with overlap → Canonical to primary page
│  ├─ Pagination → Canonical to page 1 (or self-referencing)
│  └─ Translated content without hreflang → Add hreflang alternates
├─ Syndicated or republished content?
│  └─ Add canonical pointing to the original source
└─ Near-duplicate pages?
   └─ Consolidate thin pages or add unique content to each
```

## "OG Image Not Showing on Social Media"

```
Social media preview missing image?
├─ Is the image URL absolute?
│  └─ Must be full URL (https://...), not relative (/og.png)
│     Fix: Set metadataBase in root layout
├─ Is the image accessible?
│  └─ Try opening the URL directly in a browser
│     ├─ 404 → Image path is wrong or file missing
│     ├─ 403 → Server blocking social media crawlers
│     └─ Loads fine → Continue debugging
├─ Is the image the right size?
│  └─ Minimum 600x315, recommended 1200x630
├─ Is there a cache issue?
│  ├─ Facebook → Use Sharing Debugger to clear cache
│  ├─ Twitter/X → Use Card Validator to refresh
│  ├─ LinkedIn → Use Post Inspector to recrawl
│  └─ Slack → Append ?v=2 to URL to bust cache
├─ Is the og:image tag in the HTML?
│  └─ View page source, search for og:image
│     ├─ Missing → Check metadata export has openGraph.images
│     └─ Present but wrong URL → Check metadataBase configuration
└─ Using opengraph-image.tsx?
   └─ Test by visiting /opengraph-image directly in browser
      └─ Error → Check ImageResponse code for bugs
```

## "Google Search Console Errors"

### "Crawled - currently not indexed"

Google found the page but chose not to index it. Common reasons:
- Content is thin or duplicates another page
- Page has low quality signals
- Site has too many low-quality pages diluting crawl budget

**Fix**: Improve content quality, add unique value, ensure page has inbound internal links.

### "Discovered - currently not indexed"

Google knows the URL exists but hasn't crawled it yet. This is normal for new pages.

**Fix**: Wait. Ensure the page is in the sitemap. Use URL Inspection to request crawling.

### "Excluded by noindex tag"

Page has `robots: { index: false }` in metadata. If intentional, ignore. If not, remove the noindex.

### "Page with redirect"

Page returns a 301/302 redirect. Google follows the redirect and indexes the destination instead.

**Fix**: If the redirect is correct, no action needed. If not, fix the redirect in `next.config.ts`.

### "Server error (5xx)"

Page returned a 500 error when Googlebot crawled it.

**Fix**: Check server logs, fix the error. Common causes: missing env vars in production, database timeouts, unhandled exceptions in Server Components.

### "Blocked by robots.txt"

The URL is disallowed in `robots.txt`.

**Fix**: Review `robots.ts` rules. Remove the page from Disallow if it should be indexed.

## Diagnostic Tools

| Tool | URL | Use For |
|------|-----|---------|
| Google Search Console | search.google.com/search-console | Index status, crawl errors, performance |
| Google Rich Results Test | search.google.com/test/rich-results | Structured data validation |
| PageSpeed Insights | pagespeed.web.dev | Core Web Vitals, performance |
| Facebook Sharing Debugger | developers.facebook.com/tools/debug/ | OG tag preview |
| Twitter Card Validator | cards-dev.twitter.com/validator | Twitter Card preview |
| Schema.org Validator | validator.schema.org | JSON-LD syntax validation |
| Lighthouse (DevTools) | Chrome DevTools → Lighthouse tab | Full audit |
