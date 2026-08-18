# Content Analysis Tools

3 tools for analyzing web content at scale -- search, summarize, and track phrase trends. All prefixed with `mcp__dataforseo__`.

## Tool Reference

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `content_analysis_search` | Search for web content mentioning a keyword | `keyword` (required), `limit`, `offset`, `filters`, `order_by`, `page_type`, `search_mode`, `keyword_fields` |
| `content_analysis_summary` | Get aggregated content metrics for a keyword | `keyword` (required), `page_type`, `keyword_fields`, `initial_dataset_filters`, `positive_connotation_threshold` |
| `content_analysis_phrase_trends` | Track how a phrase appears over time | `keyword` (required), `date_from` (required), `date_to`, `date_group`, `page_type`, `keyword_fields` |

## Parameter Details

### Common Parameters

- `keyword` -- the phrase or topic to analyze. Example: `"artificial intelligence in healthcare"`.
- `page_type` -- filter by content type: `"ecommerce"`, `"news"`, `"blogs"`, `"message-boards"`, `"organization"`.
- `keyword_fields` -- where to look for the keyword: `"title"`, `"main_title"`, `"previous_title"`, `"snippet"`. Pass as a comma-separated string.

### content_analysis_search

- `search_mode` -- `"as_is"` (exact match) or `"relevance"` (semantic). Default `"as_is"`.
- `filters` -- array syntax: `[["content_info.sentiment_connotations.anger", ">", 0.5]]`.
- `order_by` -- array: `["content_info.rating,desc"]`.
- `limit` -- max results. Default 10, max 1000.
- `offset` -- pagination offset.

### content_analysis_summary

- `initial_dataset_filters` -- pre-filter the dataset before aggregation. Same filter syntax as search.
- `positive_connotation_threshold` -- float (0-1). Threshold for classifying content as positive sentiment.

### content_analysis_phrase_trends

- `date_from` -- required. ISO date string. Example: `"2025-01-01"`.
- `date_to` -- optional end date. Defaults to current date.
- `date_group` -- grouping period: `"day"`, `"week"`, `"month"`. Default `"month"`.

## Usage Examples

### Analyze content landscape for a topic

```
Step 1 -- Tool: mcp__dataforseo__content_analysis_summary
Params:
  keyword: "remote work productivity"
  page_type: "blogs"
  keyword_fields: "title,snippet"

Step 2 -- Tool: mcp__dataforseo__content_analysis_search
Params:
  keyword: "remote work productivity"
  page_type: "blogs"
  limit: 30
  order_by: ["content_info.rating,desc"]
```

Summary gives you aggregate stats (total mentions, sentiment distribution, top domains). Search gives individual content pieces for deeper analysis.

### Track brand mentions over time

```
Tool: mcp__dataforseo__content_analysis_phrase_trends
Params:
  keyword: "your-brand-name"
  date_from: "2025-01-01"
  date_to: "2026-01-01"
  date_group: "week"
  page_type: "news"
```

Returns weekly counts of content mentioning the keyword in news articles.

## Tips

- `content_analysis_summary` is the cheapest entry point. Use it to check if there is enough content before running search.
- Combine `page_type` and `keyword_fields` to narrow results precisely. Searching only in titles yields higher-relevance matches.
- `search_mode: "relevance"` is useful for broad topic research; `"as_is"` for exact brand or phrase monitoring.
- Sentiment data (anger, joy, sadness, surprise) in results is useful for brand reputation analysis.
- `phrase_trends` with `date_group: "week"` catches spikes from news events or campaigns.
