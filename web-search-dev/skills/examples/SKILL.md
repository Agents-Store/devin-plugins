---
name: examples
description: This skill should be used when the user asks for "web search examples", "scraping examples", "show me how to use search tools", "search workflow examples", or needs end-to-end scenario walkthroughs for web search and scraping development tasks.
---

# Web Search & Scraping Examples

End-to-end scenario walkthroughs for common development tasks. Each scenario shows the complete workflow from start to finish.

## Scenario Index

| Scenario | Use Case | Services Used |
|----------|----------|---------------|
| [Scrape for App](references/scenarios/scrape-for-app.md) | Extract product data and import into your application | Firecrawl (map, extract), Jina (read) |
| [Doc Search Workflow](references/scenarios/doc-search-workflow.md) | Find framework docs while coding to fix a bug | Context7, Perplexity, Firecrawl, Jina |
| [Media for Content](references/scenarios/media-for-content.md) | Find stock photos/videos for a blog or app | Pexels, Unsplash, Jina (images) |
| [Content Pipeline](references/scenarios/content-pipeline.md) | Multi-service data pipeline: discover, extract, transform, load | Firecrawl, Jina, Exa |

## Quick Reference: Common Workflows

### Search → Read → Use

```
1. Search: web_search_exa({ query: "topic", numResults: 5 })
2. Read best result: read_url({ url: "<top_url>" })
3. Use the content in your app
```

### Discover → Extract → Import

```
1. Map site: firecrawl_map({ url: "https://example.com" })
2. Extract data: firecrawl_extract({ urls: [...], schema: {...} })
3. Import: write to your database/API
```

### Question → Answer → Verify

```
1. Ask: perplexity_ask({ query: "How to implement X?" })
2. Find docs: query-docs({ libraryId: "...", query: "X" })
3. Verify answer against official docs
```

### Find Media → Select → Download

```
1. Search: searchPhotos({ query: "topic", per_page: 20 })
2. Select best matches from results
3. Use image URLs in your app (src.medium for web)
```
