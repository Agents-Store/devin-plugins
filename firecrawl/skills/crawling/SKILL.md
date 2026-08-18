---
name: crawling
description: Multi-page crawling and site mapping. This skill should be used when the user asks to crawl an entire website, map all URLs on a site, discover site structure, or scrape multiple pages from a domain.
---

# Site Crawling

This skill covers crawling entire websites and mapping site structures — async crawling, URL patterns, depth control, and progress monitoring.

## Available Tools

| Tool | Description |
|------|-------------|
| `crawl_site` | Start an async crawl of a website |
| `get_crawl_status` | Check crawl progress and get results |
| `map_site` | Discover all URLs on a site |

## Map Site (URL Discovery)

Quickly discover all URLs on a site without downloading content.

```
Tool: map_site
Input: {
  "url": "https://example.com"
}

Returns: Array of all discovered URLs on the site.
```

Use this BEFORE crawling to understand site structure and set appropriate include/exclude patterns.

## Start a Crawl

```
Tool: crawl_site
Input: {
  "url": "https://example.com",
  "max_pages": 50,
  "include_patterns": ["/blog/*", "/docs/*"],
  "exclude_patterns": ["/admin/*", "/api/*"],
  "formats": ["markdown"]
}

Returns: { "crawl_id": "crawl_xxx", "status": "crawling" }
```

### Configuration Options

| Parameter | Type | Description |
|-----------|------|-------------|
| url | string | Starting URL |
| max_pages | number | Maximum pages to crawl (default: 50) |
| max_depth | number | Maximum link depth from start URL |
| include_patterns | string[] | URL patterns to include (glob) |
| exclude_patterns | string[] | URL patterns to exclude (glob) |
| formats | string[] | Output formats per page |

## Check Crawl Status

Crawls are async — poll for progress.

```
Tool: get_crawl_status
Input: {
  "crawl_id": "crawl_xxx"
}

Returns: {
  "status": "crawling" | "completed" | "failed",
  "pages_crawled": 35,
  "total_pages": 50,
  "data": [...] // page content when completed
}
```

## Common Workflows

### Crawl Blog Section
```
1. map_site(url) -> Discover all URLs
2. Identify blog URL pattern (e.g., /blog/*)
3. crawl_site(url, include_patterns=["/blog/*"], max_pages=100)
4. get_crawl_status(crawl_id) -> Poll until complete
5. Process all blog post content
```

### Full Site Crawl with Monitoring
```
1. map_site(url) -> Estimate site size
2. crawl_site(url, max_pages=200) -> Start crawl
3. get_crawl_status(crawl_id) -> Check progress periodically
4. When complete: process results
```

### Selective Documentation Crawl
```
1. map_site(url) -> See URL structure
2. crawl_site(url, include_patterns=["/docs/*"], exclude_patterns=["/docs/api/*"])
3. get_crawl_status(crawl_id) -> Wait for completion
4. Extract and organize documentation content
```

## URL Pattern Syntax

Patterns use glob-style matching:
- `*` matches any characters within a path segment
- `**` matches any characters across path segments
- `/blog/*` matches `/blog/post-1`, `/blog/post-2`
- `/docs/**` matches `/docs/guide/intro`, `/docs/api/v2/ref`

## Additional crawl_site Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | number | Alias for max_pages |
| `maxDepth` | number | Maximum crawl depth |
| `maxDiscoveryDepth` | number | Maximum depth for URL discovery |
| `allowExternalLinks` | boolean | Follow links to other domains |
| `deduplicateSimilarURLs` | boolean | Skip pages with similar content |

## Error Handling and Recovery

### Handle Failed Crawls
```
1. crawl_site(url, max_pages=100) → Start crawl
2. get_crawl_status(crawl_id) → Check status
3. If status == "failed":
   - Verify URL is accessible: scrape_url(url) first
   - Reduce max_pages and retry
   - Try with more specific include_patterns
```

### Large Site Strategy
```
For sites with 1000+ pages:
1. map_site(url) → Get full URL list (fast, no content)
2. Identify sections: /blog/*, /docs/*, /products/*
3. Crawl each section separately:
   crawl_site(url, include_patterns=["/blog/*"], max_pages=200)
   crawl_site(url, include_patterns=["/docs/*"], max_pages=200)
4. Process results per section
```

### Incremental Crawling
```
For monitoring site changes over time:
1. crawl_site(url, max_pages=50) → Initial crawl
2. Store results with URLs and timestamps
3. Later: crawl_site(url, max_pages=50) → New crawl
4. Compare results to identify new/changed pages
```

## Best Practices

1. **Map before crawl** — use `map_site` to understand structure first
2. **Set max_pages** — always limit crawls to avoid scraping too much
3. **Use include patterns** — focus on relevant sections
4. **Exclude admin/API paths** — avoid non-content URLs
5. **Monitor progress** — poll `get_crawl_status` periodically
6. **Start small** — test with max_pages=10, then increase
7. **Use markdown format** — most efficient for content processing
8. **Split large sites** — crawl by section rather than all at once
9. **Handle failures** — check status and retry with adjusted parameters
10. **Deduplicate** — use `deduplicateSimilarURLs` to skip similar pages
