# Keywords Data Tools

7 tools for search volume data, Google Trends, and DFS Trends analytics. All prefixed with `mcp__dataforseo__`.

## Tool Reference

### Google Ads Data

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `kw_data_google_ads_search_volume` | Get exact search volume from Google Ads | `keywords` (array), `location_name`, `language_code` |
| `kw_data_google_ads_locations` | Look up valid Google Ads location names | `country_iso_code` (required) |

### Google Trends

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `kw_data_google_trends_explore` | Explore Google Trends data for keywords | `keywords` (array, max 5), `location_name`, `time_range` |
| `kw_data_google_trends_categories` | List available Google Trends categories | (no required params) |

### DFS Trends (DataForSEO proprietary)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `kw_data_dfs_trends_explore` | Explore DFS trend data with more granularity | `keywords` (array, max 5), `location_name`, `time_range`, `type` (web/news/ecommerce), `date_from`, `date_to` |
| `kw_data_dfs_trends_demography` | Demographic breakdown of search interest | `keywords` (array), `location_name`, `time_range`, `type`, `date_from`, `date_to` |
| `kw_data_dfs_trends_subregion_interests` | Regional breakdown of search interest | `keywords` (array), `location_name`, `time_range`, `type`, `date_from`, `date_to` |

## Parameter Details

### Search Volume

- `keywords` -- array of keyword strings. Example: `["seo", "keyword research", "backlink checker"]`.
- `location_name` -- geographic location. Example: `"United States"`, `"United Kingdom"`.
- `language_code` -- ISO language code. Example: `"en"`, `"de"`, `"fr"`.

### Trends Parameters

- `time_range` -- predefined range: `"past_hour"`, `"past_4_hours"`, `"past_day"`, `"past_7_days"`, `"past_30_days"`, `"past_90_days"`, `"past_12_months"`, `"past_5_years"`.
- `type` -- search type for DFS Trends: `"web"` (default), `"news"`, `"ecommerce"`.
- `date_from`, `date_to` -- ISO date strings for custom date ranges. Example: `"2025-01-01"`.
- Google Trends allows max 5 keywords per call for comparison.

### Location Lookup

Call `kw_data_google_ads_locations` with a country ISO code to get the list of valid location names and their codes. This is essential when working with non-US markets.

## Usage Examples

### Get search volume for a keyword list

```
Tool: mcp__dataforseo__kw_data_google_ads_search_volume
Params:
  keywords: ["project management software", "task management app", "team collaboration tool"]
  location_name: "United States"
  language_code: "en"
```

Returns monthly search volume, CPC, competition level, and monthly trends.

### Compare keyword trends over time

```
Tool: mcp__dataforseo__kw_data_dfs_trends_explore
Params:
  keywords: ["chatgpt", "claude ai", "gemini ai"]
  location_name: "United States"
  type: "web"
  date_from: "2024-01-01"
  date_to: "2025-12-31"
```

Returns normalized interest scores over the specified period. Use for content timing and seasonal analysis.

## Tips

- Google Ads search volume gives the most accurate absolute numbers. DFS Trends gives relative interest over time.
- Use `kw_data_google_trends_categories` to get category IDs for filtering Trends results by topic.
- DFS Trends `type: "ecommerce"` is useful for product-focused keyword research.
- `dfs_trends_demography` reveals age/gender breakdowns -- valuable for audience targeting.
- `dfs_trends_subregion_interests` shows which regions have the most interest -- useful for local SEO planning.
- Always verify location names with the locations tool before running volume queries against non-US markets.
