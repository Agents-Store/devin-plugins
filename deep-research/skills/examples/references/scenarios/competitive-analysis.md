# Scenario: Competitive Analysis

**Query:** "Сравни Notion vs Linear vs Asana для управления проектами"
**Type:** Competitive Analysis
**Depth:** standard
**Template:** Comparison Table

## Step-by-Step Execution

### Step 1: CLASSIFY
```
Signals: "сравни", "vs" → Competitive Analysis
Depth: standard (3 products to compare)
```

### Step 2: PLAN
```
expand_query({ query: "project management tools comparison" })

Queries:
1. "Notion project management features pricing 2026"
2. "Linear project management features pricing 2026"
3. "Asana project management features pricing 2026"
4. "Notion vs Linear vs Asana comparison review"
5. "best project management tool for teams 2026"
```

### Step 3: SEARCH
```
~~batch_search([
  "Notion project management pricing features",
  "Linear project management pricing features",
  "Asana project management pricing features"
])

~~search("Notion vs Linear vs Asana comparison 2026")

~~search("best project management tool comparison 2026")
```

### Step 4: READ
```
Rank by relevance("project management comparison", all_urls)

~~batch_scrape([
  "https://notion.so/pricing",
  "https://linear.app/pricing",
  "https://asana.com/pricing",
  top_comparison_article_url,
  top_review_url
])
```

### Step 5: EXTRACT
```
~~extract(
  urls: ["https://notion.so/pricing", "https://linear.app/pricing", "https://asana.com/pricing"],
  prompt: "Extract plan names, monthly prices, key features, and user limits",
  schema: { plans: [{ name, price_monthly, features[], user_limit }] }
)
```

### Step 6: SYNTHESIZE
```
deduplicate_strings(all_facts)
Cross-check pricing across official sites and review articles
Note discrepancies in feature comparisons
```

### Step 7: REPORT
Output: Comparison Table template with:
- Feature comparison table (pricing, features, integrations, UX)
- Detailed analysis per product (Strengths, Weaknesses, Best for)
- Verdict by use case
- Sources (5+ URLs)
- Methodology section

### Expected Capabilities Used
`~~batch_search`, `~~search`, `~~batch_scrape`, `~~extract`, relevance ranking, deduplication
