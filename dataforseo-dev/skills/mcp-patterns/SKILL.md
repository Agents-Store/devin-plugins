---
name: mcp-patterns
description: This skill should be used when the user asks about "DataForSEO MCP tools", "which DataForSEO tools are available", "how to use DataForSEO MCP", "DataForSEO tool parameters", "dataforseo tool list", or needs to know which MCP operations are available for DataForSEO and how to use them correctly.
---

# DataForSEO MCP Tools Reference

All tools use the `mcp__dataforseo__` prefix. 76 tools across 8 API modules.

## Task Routing Table

Use this to pick the right tool for a given task.

| Task | Best Tools | Category |
|------|-----------|----------|
| Research keywords for a topic | `mcp__dataforseo__dataforseo_labs_google_keyword_ideas`, `mcp__dataforseo__dataforseo_labs_google_keyword_suggestions` | Labs |
| Check keyword difficulty + volume | `mcp__dataforseo__dataforseo_labs_google_keyword_overview`, `mcp__dataforseo__dataforseo_labs_bulk_keyword_difficulty` | Labs |
| Find keywords a competitor ranks for | `mcp__dataforseo__dataforseo_labs_google_keywords_for_site`, `mcp__dataforseo__dataforseo_labs_google_ranked_keywords` | Labs |
| Compare domains side-by-side | `mcp__dataforseo__dataforseo_labs_google_competitors_domain`, `mcp__dataforseo__dataforseo_labs_google_domain_intersection` | Labs |
| Analyze SERP for a keyword | `mcp__dataforseo__serp_organic_live_advanced` | SERP |
| Get backlink profile | `mcp__dataforseo__backlinks_summary`, `mcp__dataforseo__backlinks_backlinks`, `mcp__dataforseo__backlinks_referring_domains` | Backlinks |
| Find competitor backlinks | `mcp__dataforseo__backlinks_competitors`, `mcp__dataforseo__backlinks_domain_intersection` | Backlinks |
| Check for spam/toxic links | `mcp__dataforseo__backlinks_bulk_spam_score`, `mcp__dataforseo__backlinks_anchors` | Backlinks |
| Run on-page audit | `mcp__dataforseo__on_page_lighthouse`, `mcp__dataforseo__on_page_instant_pages`, `mcp__dataforseo__on_page_content_parsing` | OnPage |
| Analyze content landscape | `mcp__dataforseo__content_analysis_search`, `mcp__dataforseo__content_analysis_summary`, `mcp__dataforseo__content_analysis_phrase_trends` | Content |
| Track Google Trends | `mcp__dataforseo__kw_data_google_trends_explore`, `mcp__dataforseo__kw_data_dfs_trends_explore` | Keywords Data |
| Check domain tech stack | `mcp__dataforseo__domain_analytics_technologies_domain_technologies` | Domain Analytics |
| WHOIS lookup | `mcp__dataforseo__domain_analytics_whois_overview` | Domain Analytics |
| Check LLM mentions of brand | `mcp__dataforseo__ai_opt_llm_ment_search`, `mcp__dataforseo__ai_opt_llm_ment_agg_metrics` | AI Optimization |
| Understand search intent | `mcp__dataforseo__dataforseo_labs_search_intent` | Labs |
| Get historical rankings | `mcp__dataforseo__dataforseo_labs_google_historical_rank_overview`, `mcp__dataforseo__dataforseo_labs_google_historical_serp` | Labs |
| Estimate traffic for keywords | `mcp__dataforseo__dataforseo_labs_bulk_traffic_estimation` | Labs |
| Get search volume from Google Ads | `mcp__dataforseo__kw_data_google_ads_search_volume` | Keywords Data |

## Category Overview

| Module | Tools | Description |
|--------|-------|-------------|
| SERP | 7 | Live Google/YouTube SERP scraping and location lookup |
| DataForSEO Labs | 20 | Keyword research, domain analysis, competitor intelligence, search intent |
| Backlinks | 19 | Link profiles, anchor text, bulk analysis, spam scores, timeseries |
| Keywords Data | 7 | Google Ads search volume, Google Trends, DFS Trends with demographics |
| OnPage | 3 | Lighthouse audits, instant page analysis, content parsing |
| Content Analysis | 3 | Content search, summaries, and phrase trend tracking |
| Domain Analytics | 4 | Technology detection and WHOIS data |
| AI Optimization | 13 | LLM mention tracking, ChatGPT scraping, AI keyword data |

## Location and Language Codes

Most tools require `location_name` (e.g., `"United States"`) and `language_code` (e.g., `"en"`).

- Use `mcp__dataforseo__serp_locations` to look up valid SERP location names by country ISO code.
- Use `mcp__dataforseo__kw_data_google_ads_locations` to look up valid Google Ads location names.
- If omitted, many tools default to United States / English, but always specify explicitly for accuracy.

## Common Parameters

These parameters appear across most tools:

| Parameter | Description | Default | Max |
|-----------|-------------|---------|-----|
| `limit` | Number of results to return | 10 | 1000 |
| `offset` | Skip N results for pagination | 0 | -- |
| `filters` | Array of filter conditions: `["metric", "operator", "value"]` | -- | -- |
| `order_by` | Array of sort directives: `["metric,asc"]` or `["metric,desc"]` | -- | -- |

Filter operators: `=`, `<>`, `>`, `<`, `>=`, `<=`, `contains`, `not_contains`, `in`, `not_in`, `like`, `not_like`.

Combine filters with `"and"` or `"or"` between filter arrays.

## Cost Awareness

DataForSEO charges per API call. Keep costs down:

1. **Use bulk tools** -- `bulk_keyword_difficulty`, `bulk_backlinks`, `bulk_ranks` process many targets in one call.
2. **Set reasonable limits** -- do not request 1000 results when 50 will do.
3. **Avoid redundant calls** -- check if a broader tool already returns what you need before calling a narrower one.
4. **Cache results mentally** -- if you already fetched keyword data, do not re-fetch it.

## Reference Files

Detailed per-category documentation with full parameter lists and usage examples:

- [SERP Tools](references/serp-tools.md) -- 7 tools for Google/YouTube SERP analysis
- [Labs Tools](references/labs-tools.md) -- 20 tools for keyword research and domain intelligence
- [Backlinks Tools](references/backlinks-tools.md) -- 19 tools for link analysis
- [Keywords Data Tools](references/keywords-data-tools.md) -- 7 tools for search volume and trends
- [OnPage Tools](references/onpage-tools.md) -- 3 tools for page audits
- [Content Analysis Tools](references/content-analysis-tools.md) -- 3 tools for content research
- [Domain Analytics Tools](references/domain-analytics-tools.md) -- 4 tools for tech stack and WHOIS
- [AI Optimization Tools](references/ai-optimization-tools.md) -- 13 tools for LLM monitoring
