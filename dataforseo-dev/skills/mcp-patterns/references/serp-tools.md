# SERP Tools

7 tools for live search engine results and location lookups. All prefixed with `mcp__dataforseo__`.

## Tool Reference

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `serp_organic_live_advanced` | Get live Google organic SERP for a keyword | `keyword` (required), `language_code` (required), `location_name` (default "United States"), `depth` (10-700), `device` (desktop/mobile), `search_engine` (google/yahoo/bing), `max_crawl_pages` (1-7) |
| `serp_youtube_organic_live_advanced` | Get live YouTube search results | `keyword` (required), `location_name` (required), `language_code` (required), `block_depth`, `device`, `os` |
| `serp_youtube_video_info_live_advanced` | Get metadata for a specific YouTube video | `video_id` (required), `location_name` (required), `language_code` (required) |
| `serp_youtube_video_comments_live_advanced` | Get comments on a YouTube video | `video_id` (required), `location_name` (required), `language_code` (required), `depth` |
| `serp_youtube_video_subtitles_live_advanced` | Get subtitles/captions for a YouTube video | `video_id` (required), `location_name` (required), `language_code` (required) |
| `serp_locations` | Look up valid SERP location names | `country_iso_code` (required), `location_name`, `location_type`, `search_engine` |
| `serp_youtube_locations` | Look up valid YouTube location names | `country_iso_code` (required), `location_name`, `location_type` |

## Parameter Details

### serp_organic_live_advanced

- `keyword` -- the search query string.
- `depth` -- number of results to retrieve. Multiples of 10. Default 10, max 700.
- `device` -- `"desktop"` or `"mobile"`. Affects the SERP layout returned.
- `search_engine` -- `"google"` (default), `"yahoo"`, or `"bing"`.
- `max_crawl_pages` -- how many SERP pages to crawl (1-7). Higher = more results but higher cost.

### YouTube Tools

- `video_id` -- the YouTube video identifier (the part after `v=` in the URL).
- `block_depth` -- number of result blocks to return for YouTube search.
- `os` -- operating system filter: `"windows"`, `"macos"`, `"android"`, `"ios"`.

### Location Lookup

Call `serp_locations` or `serp_youtube_locations` first if you are unsure about the exact location name string. Pass the `country_iso_code` (e.g., `"US"`, `"GB"`, `"DE"`) to get all available locations for that country.

## Usage Examples

### Analyze Google SERP for a keyword

```
Tool: mcp__dataforseo__serp_organic_live_advanced
Params:
  keyword: "best project management tools"
  language_code: "en"
  location_name: "United States"
  depth: 30
  device: "desktop"
```

Returns organic results with URLs, titles, descriptions, positions, and SERP features (featured snippets, people also ask, etc.).

### Get YouTube video metadata and comments

```
Step 1 -- Tool: mcp__dataforseo__serp_youtube_video_info_live_advanced
Params:
  video_id: "dQw4w9WgXcQ"
  location_name: "United States"
  language_code: "en"

Step 2 -- Tool: mcp__dataforseo__serp_youtube_video_comments_live_advanced
Params:
  video_id: "dQw4w9WgXcQ"
  location_name: "United States"
  language_code: "en"
  depth: 50
```

## Tips

- Google SERP calls are relatively expensive. Set `depth` to only what you need.
- Use `device: "mobile"` to check mobile-specific rankings and SERP features.
- YouTube location/language values differ from Google SERP values. Always verify with `serp_youtube_locations` first.
- The `max_crawl_pages` parameter multiplies cost -- use 1 unless you need deep results.
