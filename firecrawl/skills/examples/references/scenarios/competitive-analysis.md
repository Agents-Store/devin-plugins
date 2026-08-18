# Scenario: Competitive Analysis

Research competitors by scraping their pages and extracting key information.

## Goal

Analyze competitor products, pricing, and features by searching, scraping, and extracting structured data.

## Steps

### 1. Search for Competitors
```
search({
  query: "project management software pricing 2024",
  limit: 10
})
→ Results: 10 URLs with content snippets
→ Identify top 5 competitor pricing pages
```

### 2. Extract Pricing Data
For each competitor pricing page:
```
extract_data({
  urls: ["https://competitor1.com/pricing"],
  schema: {
    "type": "object",
    "properties": {
      "company": { "type": "string", "description": "Company name" },
      "plans": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": { "type": "string", "description": "Plan name" },
            "monthly_price": { "type": "number", "description": "Monthly price in USD" },
            "annual_price": { "type": "number", "description": "Annual price per month" },
            "features": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Included features"
            },
            "user_limit": { "type": "string", "description": "User limit description" }
          }
        }
      }
    }
  }
})
```

### 3. Extract Feature Details
For each competitor:
```
scrape_url({
  url: "https://competitor1.com/features",
  formats: ["markdown"],
  includeTags: ["main"]
})
→ Get full feature descriptions

extract_data({
  urls: ["https://competitor1.com/features"],
  prompt: "List all product features with their category and description"
})
→ Structured feature list
```

### 4. Compile Analysis
- Create pricing comparison table
- Create feature matrix (which competitors have which features)
- Identify pricing gaps and feature differentiators

## Result

A comprehensive competitive analysis with:
- Pricing comparison across all plans
- Feature matrix showing coverage
- Market positioning insights
