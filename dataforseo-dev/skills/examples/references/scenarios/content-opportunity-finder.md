# Scenario: Content Opportunity Finder

Discover content topics with high traffic potential and low competition using DataForSEO's content analysis and keyword endpoints. Each step is one `api_request` call with the method, path and `data` shown. Read each path's page with `docs_search` and agree a budget first.

## Step 1: Analyze the Content Landscape

Find how a topic is covered across the web:

```
POST /v3/content_analysis/summary/live
data: [{"keyword": "ai project management", "page_type": ["blogs", "news"]}]
```

Review total citations, sentiment distribution and top categories. A high citation count with positive sentiment means a hot topic.

## Step 2: Track Topic Trends

```
POST /v3/content_analysis/phrase_trends/live
data: [{"keyword": "ai project management", "date_from": "2025-01-01", "date_group": "month"}]
```

Look for upward trends; growing topics mean growing search demand.

## Step 3: Find Related Keywords

```
POST /v3/dataforseo_labs/google/keyword_ideas/live
data: [{"keywords": ["ai project management"], "location_code": 2840, "language_code": "en",
        "limit": 50, "filters": [["keyword_info.search_volume", ">", 50]],
        "order_by": ["keyword_info.search_volume,desc"]}]
```

Build a topic cluster from the returned keywords.

## Step 4: Evaluate Keyword Difficulty

```
POST /v3/dataforseo_labs/google/keyword_overview/live
data: [{"keywords": ["ai project management tools", "ai task automation", "ai for teams", "smart project planning"],
        "location_code": 2840, "language_code": "en"}]
```

Focus on keywords with search volume above 100, difficulty below 40 and a positive trend.

## Step 5: Check SERP Competitiveness

For the top 3 content opportunities, read the actual SERP:

```
POST /v3/serp/google/organic/live/advanced
data: [{"keyword": "ai project management tools", "location_code": 2840, "language_code": "en", "depth": 20}]
```

Look for:
- Are the top results all from high-authority domains? (hard to compete)
- Are there thin or outdated articles in the top 10? (opportunity)
- What content format dominates? (listicles, reviews, guides)

## Step 6: Validate with Google Trends

```
POST /v3/keywords_data/google_trends/explore/live
data: [{"keywords": ["ai project management", "ai task management"], "location_code": 2840,
        "time_range": "past_12_months"}]
```

Confirm the topic has sustained or growing interest.

## Step 7: Check AI Visibility Potential

```
POST /v3/ai_optimization/llm_mentions/search_mentions/live
data: [{"target": [{"keyword": "ai project management tools", "match_type": "word_match"}],
        "platform": "chat_gpt", "location_code": 2840, "language_code": "en", "limit": 20}]
```

If LLMs already cite sources for this topic, authoritative content raises your chance of being cited in AI answers.

## Expected Output

A content opportunity report containing:
- 10-20 content topic ideas ranked by potential
- Search volume and difficulty for each topic
- Trend direction (growing, stable, declining)
- Recommended content format per topic
- SERP competitiveness assessment
- AI visibility opportunity notes
