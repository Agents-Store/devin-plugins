# Firecrawl MCP Tool Patterns

Exact parameter formats for all Firecrawl MCP tools.

## scrape_url
```json
Input: {
  "url": "https://example.com/page",
  "formats": ["markdown"],
  "onlyMainContent": true,
  "mobile": false,
  "prompt": "Extract key information",
  "schema": { "type": "object", "properties": { "title": { "type": "string" } } },
  "includeTags": ["article", "main"],
  "excludeTags": ["nav", "footer"],
  "headers": { "Authorization": "Bearer token" },
  "waitFor": ".content-loaded",
  "timeout": 30000,
  "skipTlsVerification": false
}
Output: {
  "content": "# Page Title\n\nPage content...",
  "metadata": {
    "title": "Page Title",
    "description": "Page description",
    "statusCode": 200,
    "url": "https://example.com/page"
  },
  "links": ["https://example.com/link1", "https://example.com/link2"]
}
```

## crawl_site
```json
Input: {
  "url": "https://example.com",
  "max_pages": 50,
  "max_depth": 3,
  "include_patterns": ["/blog/*", "/docs/*"],
  "exclude_patterns": ["/admin/*"],
  "formats": ["markdown"]
}
Output: {
  "crawl_id": "crawl_xxx",
  "status": "crawling"
}
```

## get_crawl_status
```json
Input: { "crawl_id": "crawl_xxx" }
Output: {
  "status": "completed",
  "pages_crawled": 47,
  "total_pages": 50,
  "data": [
    {
      "url": "https://example.com/blog/post-1",
      "content": "# Post Title\n\n...",
      "metadata": { "title": "...", "statusCode": 200 }
    }
  ]
}
```

## map_site
```json
Input: { "url": "https://example.com" }
Output: {
  "urls": [
    "https://example.com/",
    "https://example.com/about",
    "https://example.com/blog",
    "https://example.com/blog/post-1",
    "https://example.com/docs/intro"
  ]
}
```

## search
```json
Input: {
  "query": "best workflow automation tools 2024",
  "limit": 5,
  "lang": "en",
  "country": "us",
  "location": "San Francisco, CA",
  "tbs": "qdr:m",
  "sources": ["techcrunch.com"],
  "scrapeOptions": { "formats": ["markdown"] }
}
Output: {
  "results": [
    {
      "url": "https://example.com/article",
      "title": "Top Workflow Tools",
      "description": "A comprehensive comparison...",
      "content": "# Top Workflow Tools\n\n..."
    }
  ]
}
```

## extract_data
```json
// With JSON schema
Input: {
  "urls": ["https://store.example.com/product/123"],
  "prompt": "Extract product details",
  "systemPrompt": "Extract accurate product information",
  "schema": {
    "type": "object",
    "properties": {
      "name": { "type": "string", "description": "Product name" },
      "price": { "type": "number", "description": "Price in USD" },
      "features": {
        "type": "array",
        "items": { "type": "string" },
        "description": "List of product features"
      }
    },
    "required": ["name", "price"]
  }
}
Output: {
  "name": "Widget Pro",
  "price": 29.99,
  "features": ["Feature A", "Feature B", "Feature C"]
}

// With prompt
Input: {
  "urls": ["https://example.com/pricing"],
  "prompt": "Extract all pricing tiers with name, monthly price, and features",
  "allowExternalLinks": false,
  "enableWebSearch": false
}
Output: {
  "tiers": [
    { "name": "Free", "price": 0, "features": ["Basic", "1 user"] },
    { "name": "Pro", "price": 29, "features": ["Advanced", "10 users"] }
  ]
}
```

## batch_scrape
```json
Input: {
  "urls": [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
  ],
  "options": {
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
Output: {
  "batch_id": "batch_xxx",
  "status": "processing"
}
```

## check_batch_status
```json
Input: { "id": "batch_xxx" }
Output: {
  "status": "completed",
  "completed": 3,
  "total": 3,
  "data": [
    {
      "url": "https://example.com/page1",
      "content": "# Page 1\n\n...",
      "metadata": { "title": "Page 1", "statusCode": 200 }
    }
  ]
}
```

## agent
```json
Input: {
  "prompt": "Find and compare pricing for the top 5 CRM tools",
  "urls": ["https://salesforce.com/pricing", "https://hubspot.com/pricing"],
  "schema": {
    "type": "object",
    "properties": {
      "tools": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "pricing": { "type": "string" },
            "features": { "type": "array", "items": { "type": "string" } }
          }
        }
      }
    }
  }
}
Output: {
  "agent_id": "agent_xxx",
  "status": "running"
}
```

## agent_status
```json
Input: { "id": "agent_xxx" }
Output: {
  "status": "completed",
  "result": {
    "tools": [
      { "name": "Salesforce", "pricing": "$25/user/mo", "features": ["CRM", "Analytics"] }
    ]
  }
}
```

## browser_create
```json
Input: {
  "ttl": 300,
  "activityTtl": 60,
  "streamWebView": false,
  "profile": { "name": "my-profile", "saveChanges": true }
}
Output: {
  "sessionId": "session_xxx",
  "wsUrl": "wss://browser.firecrawl.dev/session_xxx"
}
```

## browser_execute
```json
Input: {
  "sessionId": "session_xxx",
  "code": "await page.goto('https://example.com'); return await page.title();",
  "language": "javascript"
}
Output: {
  "result": "Example Domain"
}
```

## browser_list
```json
Input: { "status": "active" }
Output: [
  { "sessionId": "session_xxx", "status": "active", "createdAt": "2024-01-01T00:00:00Z" }
]
```

## browser_delete
```json
Input: { "sessionId": "session_xxx" }
Output: { "success": true }
```
