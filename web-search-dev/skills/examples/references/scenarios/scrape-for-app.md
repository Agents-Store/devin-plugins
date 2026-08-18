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

```
Tool: firecrawl_extract
Input: {
  "urls": [
    "https://store.example.com/products/item-1",
    "https://store.example.com/products/item-2",
    "https://store.example.com/products/item-3"
  ],
  "prompt": "Extract product details including name, price, description, category, and image URLs",
  "schema": {
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
```

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

If `firecrawl_extract` doesn't capture the data cleanly:

```
Tool: parallel_read_url
Input: { "urls": ["<product_urls>"] }
```

Then parse the markdown output to extract product data using code.

## Tips

- Process in batches of 10-20 products to stay within rate limits
- Save raw scraped data before transforming — useful for debugging
- Add delays between batch requests (1-2 seconds)
- Verify extracted data quality on first few items before bulk import
