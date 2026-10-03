---
name: ai-optimization
description: This skill should be used when the user asks about "AI optimization", "LLM mentions", "ChatGPT visibility", "AI search", "LLM ranking", "brand mentions in AI", "AI SEO", "GEO", "generative engine optimization", "AI Overview mentions", or needs to track and improve visibility in AI-powered search using DataForSEO.
---

# AI Optimization

Track and improve brand visibility in AI-powered search: ChatGPT and Google's AI Overviews through LLM Mentions, plus the live answers of ChatGPT and Gemini. This is Generative Engine Optimization (GEO): making your brand appear when LLMs answer user questions.

All calls go through `api_request` (see the `mcp-patterns` skill); paths and minimal bodies for every endpoint below are in `../mcp-patterns/references/endpoint-paths.md`. Read each endpoint's page with `docs_search` before the first call and agree a budget first (`cost-awareness` skill).

## What DataForSEO offers here

| Family | Paths under `/v3/ai_optimization/` | Answers |
|---|---|---|
| LLM Mentions | `llm_mentions/search_mentions/live`, `target_metrics/live`, `multi_target_metrics/live`, `top_mentioned_domains/live`, `top_mentioned_pages/live`, `top_mentioned_brands/live`, `top_mentioned_brand_categories/live`, `historical/live`, `timeseries_delta/live`, `timeseries_new_lost/live`, plus `_lite` variants | Which questions and answers mention a domain or keyword, how often, next to whom, and how that changes |
| LLM Scraper | `chat_gpt/llm_scraper/live/advanced`, `gemini/llm_scraper/live/advanced` | What ChatGPT or Gemini actually shows for one query: text, sources, brands, products |
| LLM Responses | `chat_gpt/llm_responses/live`, `claude/llm_responses/live`, `gemini/llm_responses/live`, `perplexity/llm_responses/live` | A raw model answer to a prompt you write, optionally with web search |
| AI Keyword Data | `ai_keyword_data/keywords_search_volume/live` | How often keywords are searched inside AI assistants |

LLM Mentions has two platforms: `chat_gpt` (United States and English only) and `google` (Google AI Overview, other markets available). Leave `platform` out to get both.

## Target entities

`target` is an array of up to 10 entities. Each is one domain or one keyword.

| Entity | Example | Notes |
|---|---|---|
| Domain | `{"domain": "example.com", "search_scope": ["sources"]}` | No `https://` or `www.`; `search_scope` values `any`, `sources`, `search_results` (`search_results` is ChatGPT only); `include_subdomains: true` widens it |
| Keyword | `{"keyword": "acme", "search_scope": ["answer"], "match_type": "word_match"}` | `search_scope` values `any`, `question`, `answer`, `brand_entities`, `fan_out_queries`; `match_type` `word_match` or `partial_match` |

Either kind accepts `"search_filter": "exclude"`. A request needs at least one entity left on `include`.

## Workflow 1: brand visibility baseline

Find out where the brand is mentioned and how visible it is overall.

```
api_request({
  method: "POST",
  path: "/v3/ai_optimization/llm_mentions/search_mentions/live",
  data: [{
    "target": [{"domain": "yourdomain.com", "search_scope": ["sources"]}],
    "platform": "chat_gpt", "location_code": 2840, "language_code": "en", "limit": 50
  }]
})
```

Each item is a mention: the `question`, the `answer` in markdown, the `sources` the model cited, `ai_search_volume` for the query, and the model name. For the totals:

```
api_request({
  method: "POST",
  path: "/v3/ai_optimization/llm_mentions/target_metrics/live",
  data: [{
    "target": [{"domain": "yourdomain.com"}],
    "platform": "chat_gpt", "location_code": 2840, "language_code": "en"
  }]
})
```

`aggregated_metrics` splits the mentions by platform, location, language and cited source domain. This is the GEO baseline; run it again every month.

## Workflow 2: you against competitors

```
api_request({
  method: "POST",
  path: "/v3/ai_optimization/llm_mentions/multi_target_metrics/live",
  data: [{
    "targets": [
      {"key": "us", "target": [{"domain": "yourdomain.com"}]},
      {"key": "rival1", "target": [{"domain": "competitor1.com"}]},
      {"key": "rival2", "target": [{"domain": "competitor2.com"}]}
    ],
    "platform": "chat_gpt", "location_code": 2840, "language_code": "en"
  }]
})
```

Two to ten keyed targets, one comparable result per key. To see who owns a topic rather than a named rival, ask for the leaders:

```
api_request({
  method: "POST",
  path: "/v3/ai_optimization/llm_mentions/top_mentioned_domains/live",
  data: [{
    "target": [{"keyword": "best project management tool"}],
    "platform": "chat_gpt", "location_code": 2840, "language_code": "en", "limit": 20
  }]
})
```

`top_mentioned_pages`, `top_mentioned_brands` and `top_mentioned_brand_categories` take the same body and answer which pages, which brands and which brand categories the models cite for that topic.

## Workflow 3: what an assistant says for one query

```
api_request({
  method: "POST",
  path: "/v3/ai_optimization/chat_gpt/llm_scraper/live/advanced",
  data: [{"keyword": "best crm for startups", "location_code": 2840, "language_code": "en"}]
})
```

The result carries the answer as typed items (text, tables, navigation lists, images, local businesses, products, ads), the `sources`, the `brand_entities` and the `search_results` the model looked at. Read it for: which brands are recommended and in what order, which sites are cited, and which content shapes (lists, comparisons, reviews) get cited. The Gemini scraper has the same body at `/v3/ai_optimization/gemini/llm_scraper/live/advanced`. Execution takes up to 120 seconds.

To put your own prompt to a model, use LLM Responses. `model_name` must come from the models endpoint of that vendor:

```
api_request({method: "GET", path: "/v3/ai_optimization/chat_gpt/llm_responses/models"})

api_request({
  method: "POST",
  path: "/v3/ai_optimization/chat_gpt/llm_responses/live",
  data: [{"user_prompt": "Compare monday.com and asana for a 20-person agency", "model_name": "<id from the models list>", "web_search": true}]
})
```

The same body works at `/v3/ai_optimization/claude/llm_responses/live`, `/v3/ai_optimization/gemini/llm_responses/live` and `/v3/ai_optimization/perplexity/llm_responses/live`. The answer is a model's output for one prompt, not a measurement of how many users see it; use it to test phrasing, use LLM Mentions to measure.

## Workflow 4: AI keyword research

Find the queries people put to AI assistants.

```
api_request({
  method: "POST",
  path: "/v3/ai_optimization/ai_keyword_data/keywords_search_volume/live",
  data: [{"keywords": ["best crm for startups", "crm comparison", "affordable crm tools"], "location_code": 2840, "language_code": "en"}]
})
```

Up to 1000 keywords per call. Rank the list by AI search volume, then check the top queries with Workflow 3.

## Trends over time

| Question | Path |
|---|---|
| Mentions month by month | `/v3/ai_optimization/llm_mentions/historical/live` |
| Change between two periods | `/v3/ai_optimization/llm_mentions/timeseries_delta/live` (`date_from`, `date_to`, `group_range` required) |
| Mentions gained and lost | `/v3/ai_optimization/llm_mentions/timeseries_new_lost/live` |

## Practical GEO strategy

1. **Baseline**: Workflow 1, monthly.
2. **Competitive landscape**: Workflow 2 and the top-domains call.
3. **Content audit**: Workflow 3 on your ten most valuable queries.
4. **Keyword targets**: Workflow 4, then fill the gaps Workflow 3 shows.
5. **Optimize**: write content the models cite: clear definitions, comparisons, data-backed claims, FAQ structure.
6. **Measure**: Workflow 1 again next month; compare with the historical and delta endpoints.

<example>
User: "How visible is acme.io in AI search? Compare us with competitor1.com and competitor2.com."

1. docs_search for llm_mentions/multi_target_metrics/live and llm_mentions/target_metrics/live; read the Pricing links.
2. Show the plan: one target_metrics call, one multi_target_metrics call, one top_mentioned_domains call; ask the user for a ceiling.
3. After approval, call api_request on `/v3/ai_optimization/llm_mentions/target_metrics/live` for acme.io, then on `/v3/ai_optimization/llm_mentions/multi_target_metrics/live` with the three keyed targets.
4. Compare the keyed results: mention counts, cited source domains, platform split.
5. Report where competitors are mentioned and acme.io is not, and which queries to cover with new content.
</example>

<example>
User: "What does ChatGPT say when someone asks for the best project management tool for remote teams?"

1. docs_search for ai_optimization/chat_gpt/llm_scraper/live/advanced; read the Pricing link and note the 120-second execution time.
2. Get the user's go-ahead for one scraper call.
3. Call api_request on `/v3/ai_optimization/chat_gpt/llm_scraper/live/advanced` with keyword "best project management tool for remote teams", location_code 2840, language_code "en".
4. List the recommended tools in order, the cited URLs and the comparison criteria the answer uses.
5. If the user's product is missing, recommend content in the format of the cited pages.
</example>
