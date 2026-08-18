---
name: batch-operations
description: Batch scraping — scrape multiple URLs in a single request with rate limiting and progress tracking. This skill should be used when the user asks to scrape multiple pages at once, process a list of URLs, or bulk extract content.
---

# Batch Operations

This skill covers batch scraping of multiple URLs — scraping many pages efficiently in a single request with progress monitoring.

## Available Tools

| Tool | Description |
|------|-------------|
| `batch_scrape` | Scrape multiple URLs in one request with rate limiting |
| `check_batch_status` | Check batch scrape progress and get results |

## Batch Scrape

### Basic Batch Scrape
```
Tool: batch_scrape
Input: {
  "urls": [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
  ]
}

Returns: { "batch_id": "batch_xxx", "status": "processing" }
```

### Batch Scrape with Options
```
Tool: batch_scrape
Input: {
  "urls": [
    "https://example.com/product/1",
    "https://example.com/product/2",
    "https://example.com/product/3"
  ],
  "options": {
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `urls` | string[] | Array of URLs to scrape (required) |
| `options.formats` | string[] | Output formats: markdown, html, rawHtml, screenshot, links |
| `options.onlyMainContent` | boolean | Strip boilerplate (default: true) |

## Check Batch Status

```
Tool: check_batch_status
Input: { "id": "batch_xxx" }

Returns: {
  "status": "completed" | "processing" | "failed",
  "completed": 15,
  "total": 20,
  "data": [
    {
      "url": "https://example.com/page1",
      "content": "# Page Title\n\n...",
      "metadata": { "title": "...", "statusCode": 200 }
    }
  ]
}
```

## Workflows

### Batch Scrape Product Pages
```
1. map_site(url) → Discover all product URLs
2. Filter URLs matching /products/* pattern
3. batch_scrape(product_urls, options={formats: ["markdown"]}) → Start batch
4. check_batch_status(batch_id) → Poll until complete
5. Process all product content
```

### Batch Scrape with Extraction
```
1. Prepare URL list from search results or map_site
2. batch_scrape(urls) → Scrape all pages
3. check_batch_status(batch_id) → Get results
4. For each result: extract_data(url, schema) → Get structured data
```

### Monitor Large Batches
```
1. batch_scrape(100_urls) → Start large batch
2. check_batch_status(batch_id) → { completed: 25, total: 100 }
3. Wait and re-check periodically
4. check_batch_status(batch_id) → { status: "completed", data: [...] }
```

## When to Use Batch vs Crawl

| Use Case | Tool | Why |
|----------|------|-----|
| Known list of URLs | `batch_scrape` | Direct, no crawling overhead |
| Discover + scrape site | `crawl_site` | Handles URL discovery |
| Multiple unrelated pages | `batch_scrape` | Pages don't need to be from same site |
| Entire site section | `crawl_site` | Automatic URL pattern filtering |

## Best Practices

1. **Use batch for known URLs** — more efficient than individual scrape_url calls
2. **Monitor progress** — poll check_batch_status for large batches
3. **Combine with map_site** — discover URLs first, then batch scrape
4. **Set onlyMainContent** — reduces noise in results
5. **Handle partial failures** — some URLs may fail while others succeed
