# Scenario: Scrape Product Data for an App

You're building an e-commerce app and need to import product data from a competitor's website.

## Step 1: Discover Product URLs

```
Tool: firecrawl_map
Input: {
  "url": "https://store.example.com",
  "limit": 200,
  "search": "product"
}
```

Result: List of product page URLs.

## Step 2: Filter Relevant URLs

From the mapped URLs, select only product pages (e.g., those matching `/products/` or `/shop/`).

## Step 3: Extract Structured Product Data

`firecrawl_scrape` has no `json` format, so let the research agent extract to your schema. Pass the selected product URLs in `urls` and keep it on them with `strictConstrainToURLs`:

```
Tool: firecrawl_agent
Input: {
  "prompt": "For each URL extract product details including name, price, description, category, and image URLs",
  "urls": ["https://store.example.com/products/item-1", "https://store.example.com/products/item-2"],
  "strictConstrainToURLs": true,
  "schema": {
    "type": "object",
    "properties": {
      "products": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "price": { "type": "number" },
            "currency": { "type": "string" },
            "description": { "type": "string" },
            "category": { "type": "string" },
            "images": { "type": "array", "items": { "type": "string" } },
            "specs": { "type": "object" }
          }
        }
      }
    }
  },
  "maxCredits": 200
}

Tool: firecrawl_agent_status
Input: { "id": "<job id from the previous call>" }   # repeat every 15-30 s until completed
```

Send the URLs in batches of 10-20 per job. If the product URLs are not known up front, leave out `urls` and `strictConstrainToURLs` and let the agent find them.

## Step 4: Transform and Import

Use the extracted JSON to create records in your database:

```typescript
// Example: Import to your API
for (const product of extractedProducts) {
  await fetch('/api/products', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: product.name,
      price: product.price,
      body_html: product.description,
      images: product.images.map(url => ({ src: url })),
    }),
  });
}
```

## Alternative: Read + Manual Extraction

If the agent result doesn't capture the data cleanly, or the cost is not worth it for a few fields:

```
Tool: read_url
Input: { "url": ["<up to 5 product URLs>"] }
```

Then parse the markdown output to extract product data using code.

## Tips

- Process in batches of 10-20 products to stay within rate limits
- Save raw scraped data before transforming — useful for debugging
- Add delays between batch requests (1-2 seconds)
- Verify extracted data quality on first few items before bulk import
