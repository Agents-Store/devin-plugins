---
name: web-scraping
description: This skill should be used when the user asks to "scrape a website", "extract content from URL", "crawl a site for data", "parse website content", "build a scraper", "extract product data", "scrape for my app", or needs to extract web content for their application or data pipeline. Also use when researching external data sources, analyzing websites for data availability, or fetching page content during planning — any task that involves reading web page content should use MCP scraping tools (firecrawl, jina, exa) instead of basic WebFetch.
---

# Web Scraping for Development

Practical scraping patterns for building applications — extracting content, data pipelines, and content migration.

## Choose the Right Approach

| Need | Tool | When |
|------|------|------|
| Single page content | `read_url` (Jina) | Fast markdown extraction, no JS needed |
| Single page with JS | `firecrawl_scrape` | SPA, dynamic content, needs rendering |
| Multiple pages | `parallel_read_url` (Jina) | Batch reading known URLs |
| Entire site | `firecrawl_crawl` | Full site crawl with depth control |
| Site URL discovery | `firecrawl_map` | Find all URLs before selective scraping |
| Structured data | `firecrawl_extract` | Extract to JSON schema (LLM-powered) |
| Interactive pages | `firecrawl_interact` | Login, click, scroll before extraction |
| Screenshots | `capture_screenshot_url` (Jina) | Visual snapshots |

## Pattern 1: Scrape Single Page

### Simple Content Extraction

```
Tool: read_url
Input: { "url": "https://example.com/article" }
```

Fast, returns clean markdown. Use for blog posts, articles, documentation.

### JavaScript-Heavy Pages

```
Tool: firecrawl_scrape
Input: {
  "url": "https://example.com/spa-page",
  "formats": ["markdown"],
  "waitFor": 3000,
  "onlyMainContent": true
}
```

Use `waitFor` for SPAs and pages that load content dynamically.

## Pattern 2: Extract Structured Data

Turn unstructured web pages into structured JSON for your app:

```
Tool: firecrawl_extract
Input: {
  "urls": ["https://example.com/products/item-1"],
  "prompt": "Extract the product details",
  "schema": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "price": { "type": "number" },
      "description": { "type": "string" },
      "specs": { "type": "object" },
      "images": { "type": "array", "items": { "type": "string" } }
    }
  }
}
```

Use for: product catalogs, pricing pages, directory listings, event data.

## Pattern 3: Batch Scrape Multiple Pages

### Known URL List

```
Tool: parallel_read_url
Input: { "urls": [
  "https://docs.example.com/page-1",
  "https://docs.example.com/page-2",
  "https://docs.example.com/page-3"
]}
```

### Discover Then Scrape

```
Step 1 — Map the site:
Tool: firecrawl_map
Input: { "url": "https://example.com", "limit": 100 }

Step 2 — Scrape selected URLs:
Tool: parallel_read_url
Input: { "urls": [<selected URLs from step 1>] }
```

## Pattern 4: Full Site Crawl

Crawl an entire site for content migration or archival:

```
Tool: firecrawl_crawl
Input: {
  "url": "https://old-site.example.com",
  "limit": 200,
  "maxDiscoveryDepth": 4,
  "includePaths": ["/blog/*", "/docs/*"],
  "excludePaths": ["/admin/*", "/login/*"],
  "scrapeOptions": {
    "formats": ["markdown", "links"],
    "onlyMainContent": true
  }
}
```

Check progress with `firecrawl_check_crawl_status` using the returned job ID.

## Pattern 5: Interactive Scraping (Login Required)

For pages behind authentication, use `firecrawl_interact` — a single call drives a live browser session with a natural-language prompt (or code):

```
Step 1 — Interact:
Tool: firecrawl_interact
Input: {
  "url": "https://example.com/login",
  "prompt": "Log in with email user@example.com and password from my credentials, then navigate to the dashboard and return its content"
}

Step 2 — Clean up:
Tool: firecrawl_interact_stop
```

For lighter interactions (click, type, scroll before extraction), the `actions` array on `firecrawl_scrape` is a simpler alternative — no session to manage.

## Pattern 6: Content Pipeline Script

Generate a script that scrapes and imports content into your app:

1. **Identify source URLs** — use `firecrawl_map` or manual list
2. **Extract structured data** — use `firecrawl_extract` with app-specific schema
3. **Transform data** — map scraped fields to your app's data model
4. **Upload** — use your app's API/SDK to create records

Example workflow:
```
Map site → Filter URLs → Extract structured data → Transform → Upload to Directus/NocoDB/API
```

## Pattern 7: Generate Standalone Scraper Script

When the user needs a reusable script they can run independently (not just MCP tool calls):

### TypeScript (Node.js)

```typescript
import { Firecrawl } from 'firecrawl';

const firecrawl = new Firecrawl({ apiKey: process.env.FIRECRAWL_API_KEY });

async function scrapeProducts(baseUrl: string) {
  // 1. Discover URLs — map() returns { links: [{ url, title, description }] }
  const map = await firecrawl.map(baseUrl, { limit: 200 });
  const productUrls = map.links.map(l => l.url).filter(u => u.includes('/product'));

  // 2. Extract structured data
  const results = [];
  for (const batch of chunk(productUrls, 10)) {
    const extracted = await firecrawl.extract({
      urls: batch,
      schema: { type: 'object', properties: {
        name: { type: 'string' },
        price: { type: 'number' },
        description: { type: 'string' }
      }}
    });
    results.push(extracted);
    await sleep(1000); // Rate limit respect
  }
  return results;
}
```

### Python

```python
import requests, json, time

JINA_KEY = os.environ["JINA_API_KEY"]
headers = {"Authorization": f"Bearer {JINA_KEY}", "Accept": "application/json"}

def scrape_urls(urls: list[str]) -> list[str]:
    """Read multiple URLs via Jina Reader API."""
    results = []
    for url in urls:
        resp = requests.get(f"https://r.jina.ai/{url}", headers=headers)
        results.append(resp.text)
        time.sleep(0.5)
    return results
```

Use this pattern when the user says "build me a scraper," "create a script," or "I need something I can run on a schedule." For one-time extraction, MCP tool patterns (Patterns 1-6) are simpler.

## Best Practices

- Start with `read_url` (fastest), escalate to `firecrawl_scrape` only if needed
- Use `firecrawl_map` before crawling to estimate scope
- Set reasonable `limit` and `maxDiscoveryDepth` to avoid excessive crawling
- Use `includePaths`/`excludePaths` to focus on relevant content
- Always use `onlyMainContent: true` to skip navigation, footers, ads
- For large sites, process in batches of 10-25 URLs
- Respect rate limits — add delays between requests in scripts
- Handle errors gracefully — some pages will fail, continue with the rest
