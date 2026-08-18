# DataForSEO Labs Tools

20 tools for keyword research, domain analysis, and competitive intelligence. All prefixed with `mcp__dataforseo__dataforseo_labs_`.

## Tool Reference

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `google_keyword_overview` | Get volume, CPC, difficulty for keywords | `keywords` (array, max 700), `location_name`, `language_code` |
| `google_keyword_ideas` | Generate keyword ideas from seed keywords | `keywords` (array), `location_name`, `language_code`, `limit`, `offset`, `filters`, `order_by` |
| `google_keyword_suggestions` | Get autocomplete-style suggestions | `keyword` (single string), `location_name`, `language_code`, `limit`, `offset`, `filters`, `order_by` |
| `google_keywords_for_site` | Find keywords a domain ranks for | `target` (domain), `location_name`, `language_code`, `limit`, `include_subdomains` |
| `google_ranked_keywords` | Get all ranked keywords for a domain/URL | `target` (domain/URL), `location_name`, `language_code`, `limit`, `item_types`, `filters`, `include_subdomains` |
| `google_competitors_domain` | Find competing domains | `target` (domain), `location_name`, `language_code`, `limit`, `exclude_top_domains`, `item_types` |
| `google_domain_intersection` | Find shared keywords between domains | `targets` (object with domains), `location_name`, `language_code`, `limit` |
| `google_domain_rank_overview` | Get domain authority metrics | `target` (domain), `location_name`, `language_code` |
| `google_historical_keyword_data` | Historical monthly volume for keywords | `keywords` (array), `location_name`, `language_code` |
| `google_historical_rank_overview` | Historical domain rank metrics | `target` (domain), `location_name`, `language_code` |
| `google_historical_serp` | Historical SERP snapshots for a keyword | `keyword` (string), `location_name`, `language_code` |
| `google_related_keywords` | Find semantically related keywords | `keyword` (string), `location_name`, `language_code`, `limit` |
| `google_relevant_pages` | Find most relevant pages for a domain | `target` (domain), `location_name`, `language_code`, `limit` |
| `google_serp_competitors` | Find domains competing for given keywords | `keywords` (array), `location_name`, `language_code`, `limit` |
| `google_subdomains` | List subdomains with ranking data | `target` (domain), `location_name`, `language_code`, `limit` |
| `google_top_searches` | Get trending searches | `location_name`, `language_code`, `limit` |
| `google_page_intersection` | Find shared keywords between pages | `pages` (object), `location_name`, `language_code` |
| `search_intent` | Classify search intent for keywords | `keywords` (array), `language_code` |
| `bulk_keyword_difficulty` | Get difficulty scores in bulk | `keywords` (array), `location_name`, `language_code` |
| `bulk_traffic_estimation` | Estimate traffic for domains | `targets` (array of domains), `location_name`, `language_code` |

## Parameter Details

### Keyword Parameters

- `keywords` -- array of keyword strings. Most tools accept up to 700. Example: `["seo tools", "keyword research"]`.
- `keyword` -- single keyword string (used by `keyword_suggestions`, `historical_serp`, `related_keywords`).
- `target` -- a domain (e.g., `"example.com"`) or full URL. Do not include `https://`.
- `targets` -- for intersection/bulk tools, either an object `{"1": "domain1.com", "2": "domain2.com"}` or an array `["domain1.com", "domain2.com"]`.
- `pages` -- object mapping page URLs: `{"1": "example.com/page1", "2": "competitor.com/page2"}`.

### Filtering and Sorting

- `filters` -- array syntax: `[["keyword_data.keyword_info.search_volume", ">", 1000]]`. Combine with `"and"` / `"or"`.
- `order_by` -- array: `["keyword_data.keyword_info.search_volume,desc"]`.
- `item_types` -- filter result types: `["organic"]`, `["paid"]`, `["featured_snippet"]`.
- `include_subdomains` -- boolean. Default `true`. Set `false` to restrict to exact domain.

## Usage Examples

### Research keywords for a topic

```
Tool: mcp__dataforseo__dataforseo_labs_google_keyword_ideas
Params:
  keywords: ["project management", "task tracking"]
  location_name: "United States"
  language_code: "en"
  limit: 50
  filters: [["keyword_data.keyword_info.search_volume", ">", 500]]
  order_by: ["keyword_data.keyword_info.search_volume,desc"]
```

### Compare two domains

```
Tool: mcp__dataforseo__dataforseo_labs_google_domain_intersection
Params:
  targets: {"1": "ahrefs.com", "2": "semrush.com"}
  location_name: "United States"
  language_code: "en"
  limit: 100
```

Returns keywords where both domains rank, with position data for each.

## Tips

- `keyword_overview` is the cheapest way to check volume and difficulty -- use it before deeper research.
- `search_intent` classifies keywords as informational, navigational, commercial, or transactional. Useful for content planning.
- `bulk_keyword_difficulty` and `bulk_traffic_estimation` are cost-effective for large keyword/domain lists.
- Always specify `location_name` and `language_code` -- results differ significantly by market.
