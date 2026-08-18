---
name: ai-optimization
description: This skill should be used when the user asks about "AI optimization", "LLM mentions", "ChatGPT visibility", "AI search", "LLM ranking", "brand mentions in AI", "AI SEO", "GEO", "generative engine optimization", or needs to track and improve visibility in AI-powered search using DataForSEO.
---

# AI Optimization

Track and improve brand visibility in AI-powered search — ChatGPT, Google AI Overviews, Perplexity, and other LLMs. This is Generative Engine Optimization (GEO): the discipline of making your brand appear when LLMs answer user questions.

## Why AI Optimization Matters

Traditional SEO optimizes for Google's 10 blue links. But users increasingly get answers directly from LLMs — ChatGPT, Google AI Overviews, Perplexity, Gemini. These models cite sources, recommend products, and shape purchasing decisions. If your brand is not mentioned in LLM responses, you are invisible to a growing segment of searchers.

DataForSEO provides the only programmatic way to track LLM mentions at scale: which queries mention your domain, how often, across which models, and how you compare to competitors. This data is the foundation of any GEO strategy.

## Available Tools

| Tool | Description |
|------|-------------|
| `ai_opt_llm_ment_search` | Search for LLM mentions of your domain/keyword |
| `ai_opt_llm_ment_agg_metrics` | Get aggregated mention visibility metrics |
| `ai_opt_llm_ment_cross_agg_metrics` | Cross-model comparison of mentions |
| `ai_opt_llm_ment_top_domains` | Top domains mentioned for a keyword area |
| `ai_opt_llm_ment_top_pages` | Top pages cited by LLMs |
| `ai_optimization_chat_gpt_scraper` | Scrape ChatGPT responses for specific queries |
| `ai_optimization_keyword_data_search_volume` | AI keyword search volume data |
| `ai_optimization_llm_models` | List supported LLM models |
| `ai_optimization_llm_response` | Get actual LLM responses for queries |
| `ai_optimization_llm_mentions_filters` | Available filters for mention searches |
| `ai_opt_llm_ment_loc_and_lang` | Supported locations/languages for LLM mentions |
| `ai_opt_kw_data_loc_and_lang` | Supported locations/languages for AI keyword data |
| `ai_optimization_chat_gpt_scraper_locations` | Supported locations for ChatGPT scraper |

## Workflow 1: Brand Visibility Check

Discover which LLM queries mention your domain and get an overall visibility score.

### Step 1 — Search for Mentions
```
Tool: ai_opt_llm_ment_search
Input: {
  "targets": [{"domain": "yourdomain.com"}],
  "location_name": "United States",
  "language_name": "English",
  "limit": 100
}
```

Returns a list of queries where LLMs mention your domain, with context: the query text, which model cited you, position in the response, and whether you appeared in the answer text, citations, or both. Each result includes `mention_type` (recommendation, citation, comparison) and `sentiment`.

### Step 2 — Aggregated Metrics
```
Tool: ai_opt_llm_ment_agg_metrics
Input: {
  "targets": [{"domain": "yourdomain.com"}],
  "location_name": "United States",
  "language_name": "English"
}
```

Returns your overall LLM visibility score: total mention count, mention share (your mentions vs. total for those queries), average position in responses, and distribution across mention types. This is your GEO baseline metric.

## Workflow 2: Cross-Model Analysis

Compare how different AI models cite your brand versus competitors.

```
Tool: ai_opt_llm_ment_cross_agg_metrics
Input: {
  "targets": [
    {"domain": "yourdomain.com"},
    {"domain": "competitor1.com"},
    {"domain": "competitor2.com"}
  ],
  "aggregation_keys": ["llm_model", "target"],
  "location_name": "United States",
  "language_name": "English"
}
```

Returns a matrix: each target domain x each LLM model, with mention counts and visibility scores. Use this to discover:
- Which model favors your brand (optimize content for models where you are weak)
- Which competitors dominate which models
- Whether your visibility is concentrated in one model or distributed

Combine with `ai_opt_llm_ment_top_domains` to see who dominates your keyword space:
```
Tool: ai_opt_llm_ment_top_domains
Input: {
  "keyword": "best project management tool",
  "location_name": "United States",
  "language_name": "English"
}
```

## Workflow 3: ChatGPT SERP Scraping

See exactly how ChatGPT answers a specific query — the full response, citations, and recommendations.

```
Tool: ai_optimization_chat_gpt_scraper
Input: {
  "keyword": "best CRM for startups",
  "location_code": 2840,
  "language_code": "en"
}
```

Use `ai_optimization_chat_gpt_scraper_locations` to find valid location codes. The scraper returns the complete ChatGPT response as structured data: text segments, cited URLs, product recommendations, and comparison tables when present. Analyze this to understand:
- What ChatGPT recommends for queries in your space
- How your competitors are positioned in ChatGPT responses
- What content patterns trigger citations (lists, comparisons, reviews)

## Workflow 4: AI Keyword Research

Find queries where LLMs actively cite sources — these are the high-value targets for GEO.

```
Tool: ai_optimization_keyword_data_search_volume
Input: {
  "keywords": ["best CRM for startups", "CRM comparison 2026", "affordable CRM tools"],
  "location_name": "United States",
  "language_name": "English"
}
```

Returns AI-specific search volume: how many times each query triggers LLM responses that cite external sources. High citation volume = high GEO opportunity. Prioritize keywords where LLMs actively link to sources over keywords where they give generic answers.

Check available regions first:
```
Tool: ai_opt_kw_data_loc_and_lang
Input: {}
```

## Target Object Format

The `targets` parameter accepts an array of objects. Each target can be:

| Format | Example | Use Case |
|--------|---------|----------|
| Domain | `{"domain": "example.com"}` | Track all mentions of your site |
| Keyword | `{"keyword": "your brand name"}` | Track brand name mentions |

Additional target options:
- `search_scope` — `"any"` (default), `"question"`, or `"answer"` — filter where the mention appears
- `match_type` — `"word_match"` (exact word boundary) or `"partial_match"` (substring) — control matching strictness

Example with all options:
```json
{
  "domain": "yourdomain.com",
  "search_scope": "answer",
  "match_type": "word_match"
}
```

## Platform Selection

| Platform Value | What It Tracks |
|---------------|----------------|
| `"chat_gpt"` | ChatGPT responses and citations |
| `"google"` | Google AI Overviews (formerly SGE) |

Specify with the `platform` parameter in mention search tools. Track both to get full AI visibility coverage.

## Discovering Available Models

```
Tool: ai_optimization_llm_models
Input: {}
```

Returns all supported LLM models with their identifiers. Use these model IDs in cross-aggregation queries to compare specific model versions.

To get an actual LLM response for a query:
```
Tool: ai_optimization_llm_response
Input: {
  "keyword": "best headless CMS",
  "model": "chat_gpt_4o"
}
```

## Practical GEO Strategy

1. **Baseline** — Run Workflow 1 to measure current LLM mention count and share
2. **Competitive landscape** — Run Workflow 2 to see who dominates your space in AI
3. **Content audit** — Run Workflow 3 to see what ChatGPT currently recommends
4. **Keyword targets** — Run Workflow 4 to find high-citation queries to optimize for
5. **Optimize content** — Create authoritative, well-structured content that LLMs prefer to cite: clear definitions, comparisons, data-backed claims, and FAQ structures
6. **Measure progress** — Re-run Workflow 1 monthly to track mention growth

<example>
User: "How visible is our brand acme.io in AI search? Compare us to competitor1.com and competitor2.com."

1. Call ai_opt_llm_ment_search with targets=[{"domain": "acme.io"}], location_name="United States", language_name="English", limit=100
2. Call ai_opt_llm_ment_agg_metrics with targets=[{"domain": "acme.io"}] for baseline score
3. Call ai_opt_llm_ment_cross_agg_metrics with all three domains and aggregation_keys=["llm_model", "target"]
4. Call ai_opt_llm_ment_top_domains for the primary keyword in acme.io's space
5. Report: "acme.io is mentioned in 23 queries by ChatGPT and 8 by Google AI. Competitor1 leads with 67 mentions. Your strongest model is ChatGPT where you rank 3rd; you are absent from Google AI Overviews for 80% of tracked queries."
6. Recommend specific queries where competitors are cited but acme.io is not — these are content gaps to fill
</example>

<example>
User: "What does ChatGPT say when someone asks 'best project management tool for remote teams'?"

1. Call ai_optimization_chat_gpt_scraper with keyword="best project management tool for remote teams", location_code=2840, language_code="en"
2. Call ai_opt_llm_ment_top_pages with keyword="best project management tool for remote teams"
3. Parse the ChatGPT response: list recommended tools, cited URLs, comparison criteria used
4. Report: "ChatGPT recommends 5 tools in this order: [Tool A], [Tool B], [Tool C], [Tool D], [Tool E]. It cites 3 review articles from [Site1], [Site2], [Site3]. Key selection criteria mentioned: async communication features, time zone management, pricing."
5. Identify optimization opportunity: if the user's product is not listed, recommend creating content that matches the cited article format (comparison + data + user testimonials)
</example>
