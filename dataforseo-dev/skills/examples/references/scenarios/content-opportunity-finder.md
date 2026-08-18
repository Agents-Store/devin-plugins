# Scenario: Content Opportunity Finder

Discover content topics with high traffic potential and low competition using DataForSEO's content analysis and keyword tools.

## Step 1: Analyze Content Landscape

Find how a topic is covered across the web:

```
Tool: mcp__dataforseo__content_analysis_summary
Input: {
  "keyword": "ai project management",
  "page_type": ["blogs", "news"]
}
```

Review: total citations, sentiment distribution, top categories. High citation count with positive sentiment = hot topic.

## Step 2: Track Topic Trends

```
Tool: mcp__dataforseo__content_analysis_phrase_trends
Input: {
  "keyword": "ai project management",
  "date_from": "2024-01-01",
  "date_to": "2024-12-31",
  "date_group": "month"
}
```

Look for upward trends — growing topics mean increasing search demand.

## Step 3: Find Related Keywords

```
Tool: mcp__dataforseo__dataforseo_labs_google_keyword_ideas
Input: {
  "keywords": ["ai project management"],
  "location_name": "United States",
  "language_code": "en",
  "limit": 50,
  "filters": [["keyword_info.search_volume", ">", 50]],
  "order_by": ["keyword_info.search_volume,desc"]
}
```

Build a topic cluster from returned keywords.

## Step 4: Evaluate Keyword Difficulty

```
Tool: mcp__dataforseo__dataforseo_labs_google_keyword_overview
Input: {
  "keywords": ["ai project management tools", "ai task automation", "ai for teams", "smart project planning"],
  "location_name": "United States",
  "language_code": "en"
}
```

Focus on keywords with: search_volume > 100, keyword_difficulty < 40, positive trend.

## Step 5: Check SERP Competitiveness

For the top 3 content opportunities, analyze the actual SERP:

```
Tool: mcp__dataforseo__serp_organic_live_advanced
Input: {
  "keyword": "ai project management tools",
  "location_name": "United States",
  "language_code": "en",
  "depth": 20
}
```

Look for:
- Are the top results from high-authority domains only? (Hard to compete)
- Are there thin or outdated articles in the top 10? (Opportunity)
- What content format dominates? (Listicles, reviews, guides)

## Step 6: Validate with Google Trends

```
Tool: mcp__dataforseo__kw_data_google_trends_explore
Input: {
  "keywords": ["ai project management", "ai task management"],
  "location_name": "United States",
  "time_range": "past_12_months"
}
```

Confirm the topic has sustained or growing interest.

## Step 7: Check AI Visibility Potential

```
Tool: mcp__dataforseo__ai_opt_llm_ment_search
Input: {
  "target": [{"keyword": "ai project management tools", "match_type": "word_match"}],
  "platform": "chat_gpt",
  "location_name": "United States",
  "language_code": "en",
  "limit": 20
}
```

If LLMs already cite sources for this topic, creating authoritative content increases chances of being cited in AI responses.

## Expected Output

A content opportunity report containing:
- 10-20 content topic ideas ranked by potential
- Search volume and difficulty for each topic
- Trend direction (growing, stable, declining)
- Recommended content format per topic
- SERP competitiveness assessment
- AI visibility opportunity notes
