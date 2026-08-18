# AI Optimization Tools

13 tools for tracking LLM mentions, ChatGPT scraping, and AI-related keyword data. All prefixed with `mcp__dataforseo__`.

## Tool Reference

### LLM Mentions

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ai_opt_llm_ment_search` | Search for brand/keyword mentions in LLM responses | `target` (array of {domain} or {keyword} objects), `platform` (chat_gpt/google), `location_name`, `language_code`, `limit`, `filters` |
| `ai_opt_llm_ment_agg_metrics` | Get aggregated mention metrics | `target` (array), `platform`, `location_name`, `language_code`, `filters` |
| `ai_opt_llm_ment_cross_agg_metrics` | Cross-aggregate mentions across targets | `targets` (array with aggregation_key), `platform`, `location_name`, `language_code`, `filters` |
| `ai_opt_llm_ment_loc_and_lang` | List supported locations and languages for LLM mentions | (no params) |
| `ai_opt_llm_ment_top_domains` | Get top domains mentioned by LLMs for a target | `target`, `platform`, `location_name`, `language_code` |
| `ai_opt_llm_ment_top_pages` | Get top pages mentioned by LLMs for a target | `target`, `platform`, `location_name`, `language_code` |

### ChatGPT Scraper

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ai_optimization_chat_gpt_scraper` | Get ChatGPT response for a query | `keyword`, `location`, `language` |
| `ai_optimization_chat_gpt_scraper_locations` | List available ChatGPT scraper locations | (no params) |

### AI Keyword Data

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ai_optimization_keyword_data_search_volume` | Get search volume for AI-related keywords | `keywords`, `location_name`, `language_code` |
| `ai_opt_kw_data_loc_and_lang` | List supported locations and languages for AI keyword data | (no params) |

### LLM Reference

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ai_optimization_llm_mentions_filters` | List available filters for LLM mention queries | (no params) |
| `ai_optimization_llm_models` | List supported LLM models | (no params) |
| `ai_optimization_llm_response` | Get a raw LLM response for a query | `keyword`, `model`, `location_name`, `language_code` |

## Parameter Details

### Target Format for LLM Mentions

The `target` parameter accepts an array of objects. Each object specifies either a domain or a keyword:

```json
[
  {"domain": "example.com"},
  {"keyword": "project management tools"}
]
```

You can mix domain and keyword targets in the same call.

### Platform

- `"chat_gpt"` -- track mentions in ChatGPT responses.
- `"google"` -- track mentions in Google AI Overviews.

### Cross-Aggregation

`ai_opt_llm_ment_cross_agg_metrics` uses `targets` with an `aggregation_key` to group results:

```json
{
  "targets": [
    {"domain": "site1.com", "aggregation_key": "group_a"},
    {"domain": "site2.com", "aggregation_key": "group_b"}
  ]
}
```

### LLM Response

- `model` -- which LLM to query. Call `ai_optimization_llm_models` to see available models.
- Returns the full LLM response text, which you can analyze for brand mentions, sentiment, or factual accuracy.

## Usage Examples

### Check if LLMs mention your brand

```
Tool: mcp__dataforseo__ai_opt_llm_ment_search
Params:
  target: [{"domain": "mysite.com"}, {"keyword": "my brand name"}]
  platform: "chat_gpt"
  location_name: "United States"
  language_code: "en"
  limit: 50
```

Returns prompts where ChatGPT mentions the target domain or keyword, with context and sentiment data.

### Compare brand visibility across LLMs

```
Step 1 -- Tool: mcp__dataforseo__ai_opt_llm_ment_agg_metrics
Params:
  target: [{"domain": "mysite.com"}]
  platform: "chat_gpt"
  location_name: "United States"
  language_code: "en"

Step 2 -- Tool: mcp__dataforseo__ai_opt_llm_ment_agg_metrics
Params:
  target: [{"domain": "mysite.com"}]
  platform: "google"
  location_name: "United States"
  language_code: "en"
```

Compare aggregate mention rates between ChatGPT and Google AI Overviews.

## Tips

- Call `ai_opt_llm_ment_loc_and_lang` first to verify supported locations before running mention queries.
- LLM mentions data is relatively new. Coverage varies by market and language.
- `ai_optimization_chat_gpt_scraper` gets a real-time ChatGPT response, which is expensive. Use it sparingly.
- Use `ai_opt_llm_ment_top_domains` to discover which competitors LLMs recommend alongside your brand.
- `ai_optimization_llm_response` with different models helps compare how different LLMs present your brand.
- AI Optimization is the fastest-evolving module. Check `llm_models` periodically for newly supported models.
