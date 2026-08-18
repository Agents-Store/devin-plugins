# seo-dev (Devin plugin)

SEO development plugin for Agents Store. Technical SEO, structured data (JSON-LD), metadata API, Core Web Vitals, sitemaps, and content optimization patterns for Next.js App Router.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (10)

- `audit` — SEO audit checklist and automated testing for Next.js sites. This skill should be used when the user asks to "audit SEO", "check SEO", "SEO checklist", "Lighthouse SEO", "SEO test", "automated SEO testing", "SEO report", or wants to systematically evaluate their site's SEO health and identify issues.
- `content-seo` — Content optimization for SEO — headings, images, internal linking, and URL structure. This skill should be used when the user asks about "content SEO", "heading structure", "h1 tag", "alt text", "image SEO", "internal linking", "URL slugs", "content optimization", "heading hierarchy", "image optimization for SEO", or needs guidance on structuring page content for search engines.
- `examples` — Complete SEO recipes and implementation examples for Next.js App Router. This skill should be used when the user asks for "SEO example", "blog SEO setup", "e-commerce SEO", "landing page SEO", "SaaS SEO", "full SEO implementation", "SEO recipe", "SEO template", or needs a complete, copy-paste ready SEO implementation for a specific page type.
- `meta-tags` — Meta tags, Open Graph, Twitter Cards, and Next.js Metadata API patterns. This skill should be used when the user asks about "meta tags", "Open Graph", "og:image", "Twitter Card", "social sharing preview", "generateMetadata", "metadata API", "canonical URL", "OG image generation", "opengraph-image.tsx", or needs to configure page-level metadata for SEO and social sharing.
- `performance` — Core Web Vitals optimization and page speed for Next.js. This skill should be used when the user asks about "Core Web Vitals", "page speed", "PageSpeed", "LCP", "INP", "CLS", "Lighthouse score", "performance optimization", "next/image optimization", "next/font", "lazy loading", "code splitting", "bundle size", or needs to improve their site's loading speed and interaction responsiveness.
- `setup` — SEO setup and initial audit for Next.js projects. This skill should be used when the user asks to "set up SEO", "add SEO to my project", "audit SEO", "check SEO setup", "initialize SEO", "configure metadata", or wants to verify their Next.js project has proper SEO foundations in place.
- `sitemap-robots` — Sitemap and robots.txt configuration for Next.js App Router. This skill should be used when the user asks about "sitemap", "sitemap.xml", "robots.txt", "robots.ts", "next-sitemap", "XML sitemap", "sitemap generation", "block crawlers", "crawl budget", or needs to configure how search engines discover and crawl their pages.
- `structured-data` — Schema.org structured data and JSON-LD implementation for Next.js. This skill should be used when the user asks about "structured data", "JSON-LD", "Schema.org", "rich snippets", "rich results", "schema markup", "Organization schema", "Article schema", "Product schema", "BreadcrumbList", "FAQ schema", or needs to add structured data to improve search appearance.
- `technical-seo` — Technical SEO for Next.js — crawlability, indexability, redirects, hreflang, and security. This skill should be used when the user asks about "technical SEO", "crawlability", "indexability", "noindex", "nofollow", "canonical tags", "redirects", "301 redirect", "hreflang", "internationalization SEO", "mobile-first indexing", "security headers", "URL structure", or needs to solve crawling and indexing issues.
- `troubleshoot` — SEO problem diagnosis and solutions for Next.js. This skill should be used when the user reports "page not indexed", "no rich snippets", "low PageSpeed score", "duplicate content", "OG image not showing", "search console errors", "SEO not working", "Google not finding my page", or needs to debug any SEO-related issue.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 1 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/seo-dev
