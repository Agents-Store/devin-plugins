---
name: search-extract
description: Web search and structured data extraction. This skill should be used when the user asks to search the web, extract structured data from pages into JSON, research a topic using online sources, or perform competitive analysis.
---

# Search & Data Extraction

This skill covers web search and structured data extraction with Firecrawl — searching with content, extracting data with JSON schemas, and LLM-powered extraction.

## Available Tools

| Tool | Description |
|------|-------------|
| `search` | Search the web and get results with content |
| `extract_data` | Extract structured data from URLs |

## Web Search

### Basic Search
```
Tool: search
Input: {
  "query": "best REST API design patterns 2024",
  "limit": 5
}

Returns: Array of results with URL, title, description, and full page content.
```

### Search with Geographic and Language Filters
```
Tool: search
Input: {
  "query": "best CRM software",
  "limit": 10,
  "lang": "en",
  "country": "us",
  "location": "San Francisco, CA"
}
```

### Search with Time Filter
```
Tool: search
Input: {
  "query": "AI automation tools",
  "limit": 5,
  "tbs": "qdr:m"
}
```

Time filter values (`tbs`): `qdr:h` (past hour), `qdr:d` (past day), `qdr:w` (past week), `qdr:m` (past month), `qdr:y` (past year).

### Search with Source Filtering
```
Tool: search
Input: {
  "query": "workflow automation comparison",
  "limit": 5,
  "sources": ["techcrunch.com", "producthunt.com"]
}
```

### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query (required) |
| `limit` | number | Max results (default: 5) |
| `lang` | string | Language code (e.g., "en", "de", "fr") |
| `country` | string | Country code (e.g., "us", "uk", "de") |
| `location` | string | Specific location (e.g., "New York") |
| `tbs` | string | Time-based filter (qdr:h, qdr:d, qdr:w, qdr:m, qdr:y) |
| `filter` | string | Additional search filter |
| `sources` | string[] | Limit to specific domains |
| `scrapeOptions` | object | Options for scraping results (formats, etc.) |

Each result includes the full scraped content of the page, not just a snippet.

## Structured Data Extraction

### Extract Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `urls` | string[] | URLs to extract from (array) |
| `prompt` | string | What to extract (required) |
| `systemPrompt` | string | System-level extraction instructions |
| `schema` | object | JSON schema for structured output |
| `allowExternalLinks` | boolean | Follow external links during extraction |
| `enableWebSearch` | boolean | Augment extraction with web search |
| `includeSubdomains` | boolean | Include subdomain pages |

### Extract with JSON Schema
```
Tool: extract_data
Input: {
  "urls": ["https://store.example.com/product/123"],
  "prompt": "Extract product details",
  "schema": {
    "type": "object",
    "properties": {
      "name": { "type": "string", "description": "Product name" },
      "price": { "type": "number", "description": "Price in USD" },
      "description": { "type": "string", "description": "Product description" },
      "rating": { "type": "number", "description": "Average rating out of 5" },
      "in_stock": { "type": "boolean", "description": "Whether product is in stock" }
    },
    "required": ["name", "price"]
  }
}

Returns: { "name": "Widget Pro", "price": 29.99, "description": "...", "rating": 4.5, "in_stock": true }
```

### Extract from Multiple URLs
```
Tool: extract_data
Input: {
  "urls": [
    "https://store.example.com/product/123",
    "https://store.example.com/product/456"
  ],
  "prompt": "Extract product name and price",
  "schema": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "price": { "type": "number" }
    }
  }
}
```

### Extract with Web Search Augmentation
```
Tool: extract_data
Input: {
  "urls": ["https://example.com/company"],
  "prompt": "Extract company revenue and employee count",
  "enableWebSearch": true,
  "systemPrompt": "If data is not on the page, use web search to find it"
}
```

### Extract List Data
```
Tool: extract_data
Input: {
  "urls": ["https://example.com/team"],
  "schema": {
    "type": "object",
    "properties": {
      "team_members": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "role": { "type": "string" },
            "bio": { "type": "string" }
          }
        }
      }
    }
  }
}
```

### Extract with Prompt
```
Tool: extract_data
Input: {
  "urls": ["https://example.com/pricing"],
  "prompt": "Extract all pricing plans with their names, prices, and included features"
}
```

## Common Workflows

### Research a Topic
```
1. search(query, limit=10) -> Find relevant sources
2. Review results — identify most relevant URLs
3. scrape_url(best_url) -> Get full content for deep analysis
```

### Extract Data from Multiple Pages
```
1. map_site(url) -> Discover product/listing pages
2. Filter URLs matching pattern (e.g., /products/*)
3. For each URL: extract_data(url, schema) -> Get structured data
4. Compile results
```

### Competitive Analysis
```
1. search("competitor product features", limit=5) -> Find competitor pages
2. For each competitor: extract_data(url, features_schema) -> Get structured feature data
3. Compare features across competitors
```

### Content Research
```
1. search(topic, limit=10) -> Get source pages
2. For top results: scrape_url(url) -> Get full content
3. Synthesize information from multiple sources
```

## Schema Design Tips

1. **Use descriptive field names** — helps LLM extraction accuracy
2. **Add descriptions to properties** — guides the extraction model
3. **Use required fields** — ensure critical data is extracted
4. **Keep schemas focused** — extract one type of data per call
5. **Use arrays for lists** — team members, pricing plans, features
6. **Test with one URL first** — verify schema works before batch extraction

## Best Practices

1. **Search before scraping** — search is faster for finding specific information
2. **Use schemas for consistency** — structured extraction is more reliable than free-form
3. **Provide descriptions in schemas** — helps the extraction model understand context
4. **Start with simple schemas** — add complexity gradually
5. **Combine search + extract** — search to find, extract to structure
6. **Limit search results** — 5-10 results is usually sufficient
