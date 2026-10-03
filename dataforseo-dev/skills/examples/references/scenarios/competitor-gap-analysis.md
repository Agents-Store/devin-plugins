# Scenario: Competitor Gap Analysis

Analyze the competitive landscape for a B2B SaaS domain and find keyword and backlink gaps. Each step is one `api_request` call with the method, path and `data` shown. Read each path's page with `docs_search` and agree a budget first.

## Step 1: Identify Competitors

```
POST /v3/dataforseo_labs/google/competitors_domain/live
data: [{"target": "example.com", "location_code": 2840, "language_code": "en",
        "exclude_top_domains": true, "limit": 15}]
```

Review the returned domains. Pick the 3 to 5 most relevant competitors and ignore generic sites such as Wikipedia and Reddit.

## Step 2: Compare Domain Metrics

```
POST /v3/dataforseo_labs/google/domain_rank_overview/live
data: [{"target": "example.com", "location_code": 2840, "language_code": "en"}]
```

Repeat for each competitor. Compare:
- `organic.count`: total ranking keywords
- `organic.etv`: estimated traffic value
- `organic.pos_1` through `organic.pos_4_10`: the position distribution

## Step 3: Find Keyword Gaps

`target1` is the competitor and `target2` is you; `intersections: false` returns the keywords the competitor ranks for and you do not.

```
POST /v3/dataforseo_labs/google/domain_intersection/live
data: [{"target1": "competitor1.com", "target2": "example.com", "intersections": false,
        "location_code": 2840, "language_code": "en", "limit": 100,
        "filters": [["keyword_data.keyword_info.search_volume", ">", 100]],
        "order_by": ["keyword_data.keyword_info.search_volume,desc"]}]
```

## Step 4: Analyze the SERP for the Top Opportunities

Pick the top 5 gap keywords and check how hard the SERP is:

```
POST /v3/serp/google/organic/live/advanced
data: [{"keyword": "best project management tool for agencies", "location_code": 2840,
        "language_code": "en", "depth": 20}]
```

Assess: are the top results dominated by high-authority sites? Is there room for a new entrant?

## Step 5: Backlink Gap Analysis

```
POST /v3/backlinks/competitors/live
data: [{"target": "example.com", "limit": 20}]
```

Then compare authority:

```
POST /v3/backlinks/bulk_ranks/live
data: [{"targets": ["example.com", "competitor1.com", "competitor2.com", "competitor3.com"]}]
```

## Step 6: Content Gap

```
POST /v3/dataforseo_labs/google/relevant_pages/live
data: [{"target": "competitor1.com", "location_code": 2840, "language_code": "en", "limit": 20}]
```

Find the competitor's top pages by traffic. Identify the content types you are missing (guides, comparisons, tools).

## Expected Output

A competitive analysis report containing:
- Competitor domain metrics comparison table
- 20-50 keyword gap opportunities with volume and difficulty
- Backlink gap: domains linking to competitors but not you
- Content gap: page types and topics competitors cover that you do not
- Priority recommendations: quick win keywords, link building targets, content to create
