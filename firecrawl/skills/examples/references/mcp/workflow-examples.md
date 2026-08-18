# Firecrawl Workflow Examples

Multi-step workflows combining multiple Firecrawl tools.

## Example 1: Documentation Crawl

Crawl a documentation site and organize content.

```
Step 1: Map the site
Tool: map_site
Input: { "url": "https://docs.example.com" }
→ Result: 150 URLs found

Step 2: Identify documentation pages
→ Filter: URLs matching /docs/* pattern → 85 pages

Step 3: Crawl documentation section
Tool: crawl_site
Input: {
  "url": "https://docs.example.com",
  "max_pages": 100,
  "include_patterns": ["/docs/*"],
  "exclude_patterns": ["/docs/changelog/*"],
  "formats": ["markdown"]
}
→ Result: { "crawl_id": "crawl_abc" }

Step 4: Monitor progress
Tool: get_crawl_status
Input: { "crawl_id": "crawl_abc" }
→ Result: { "status": "crawling", "pages_crawled": 42, "total_pages": 85 }

Step 5: Get final results (when complete)
Tool: get_crawl_status
Input: { "crawl_id": "crawl_abc" }
→ Result: { "status": "completed", "pages_crawled": 85, "data": [...] }
```

## Example 2: Product Data Extraction

Extract product information from an e-commerce site.

```
Step 1: Scrape a sample product page
Tool: scrape_url
Input: { "url": "https://store.example.com/products/widget-pro", "formats": ["markdown"] }
→ Review page structure to design extraction schema

Step 2: Extract structured data
Tool: extract_data
Input: {
  "urls": ["https://store.example.com/products/widget-pro"],
  "schema": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "price": { "type": "number" },
      "description": { "type": "string" },
      "specs": { "type": "array", "items": { "type": "string" } },
      "rating": { "type": "number" },
      "reviews_count": { "type": "integer" }
    }
  }
}
→ Result: structured product data

Step 3: Extract from multiple products
→ Repeat extract_data for each product URL
→ Compile into comparison table
```

## Example 3: Research and Summarize

Research a topic using search and scraping.

```
Step 1: Search for topic
Tool: search
Input: { "query": "NocoDB vs Airtable features comparison 2024", "limit": 5 }
→ Result: 5 relevant articles with content

Step 2: Deep-dive on best article
Tool: scrape_url
Input: {
  "url": "https://bestresult.com/comparison",
  "formats": ["markdown"],
  "includeTags": ["article"]
}
→ Result: Full article content

Step 3: Extract structured comparison
Tool: extract_data
Input: {
  "urls": ["https://bestresult.com/comparison"],
  "prompt": "Extract feature comparison table between NocoDB and Airtable"
}
→ Result: structured feature comparison
```
