# Scenario: Product Data Extraction

Extract product data from an e-commerce site for analysis.

## Goal

Extract structured product data (name, price, description, ratings) from multiple product pages on an e-commerce site.

## Steps

### 1. Map the Site
```
map_site({ url: "https://store.example.com" })
→ 500 URLs found
→ 120 match /products/* pattern
```

### 2. Scrape a Sample Page
```
scrape_url({
  url: "https://store.example.com/products/widget-pro",
  formats: ["markdown"]
})
→ Review page structure:
  - Product name in h1
  - Price in .price-tag
  - Description in .product-description
  - Rating in .star-rating
  - Features listed in .feature-list
```

### 3. Design Extraction Schema
```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string", "description": "Product name from the page title" },
    "price": { "type": "number", "description": "Current price in USD" },
    "original_price": { "type": "number", "description": "Original price before discount" },
    "description": { "type": "string", "description": "Product description" },
    "rating": { "type": "number", "description": "Average star rating (1-5)" },
    "review_count": { "type": "integer", "description": "Number of reviews" },
    "features": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of product features"
    },
    "in_stock": { "type": "boolean", "description": "Whether the product is available" },
    "category": { "type": "string", "description": "Product category" }
  },
  "required": ["name", "price"]
}
```

### 4. Test Schema on Sample
```
extract_data({
  urls: ["https://store.example.com/products/widget-pro"],
  schema: <above schema>
})
→ Verify: all fields extracted correctly
```

### 5. Extract from Multiple Products
```
For each product URL (/products/*):
  extract_data(url, schema)
→ Compile all results into dataset
```

## Result

Structured dataset of all products with consistent schema for analysis, comparison, or import into another system.
