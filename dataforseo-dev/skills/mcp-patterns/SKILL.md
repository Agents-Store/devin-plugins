---
name: mcp-patterns
description: This skill should be used when the user asks about "DataForSEO MCP tools", "api_request", "docs_search", "which DataForSEO endpoint", "how to call DataForSEO", "DataForSEO request body", "DataForSEO .ai mode", or needs to turn an SEO data task into the right DataForSEO API call through the MCP server.
---

# DataForSEO through the v3 MCP server

The plugin runs `dataforseo-mcp-server@3`. It exposes **four tools**, not one tool per endpoint. Every DataForSEO endpoint is reached through a single request tool, and the documentation is searchable from the same server.

| Tool | What it does | Cost |
|---|---|---|
| `docs_list_sections` | Lists the 13 documentation sections: SERP, AI Optimization, Keywords Data, Domain Analytics, Labs, OnPage, Backlinks, Content Analysis, Merchant, App Data, Business Data, Databases, Appendix | free |
| `docs_index` | Lists the endpoints of one section (`{section: "SERP API"}`) or of all | free |
| `docs_search` | Returns the documentation page of one endpoint: fields, limits, Pricing link, example (`needCodeExample: true` adds PHP, Node.js, Python, C#) | free, cached 24 hours |
| `api_request` | Sends an authenticated request to the DataForSEO API | **paid** |

Claude Code names each tool with the plugin server prefix, for example `mcp__plugin_dataforseo-dev_dataforseo__api_request`; the rest of this plugin uses the short names `api_request`, `docs_search`, `docs_index` and `docs_list_sections`. The old per-endpoint tools of the v2 server (`dataforseo_labs_google_keyword_ideas`, `backlinks_summary` and the rest) no longer exist; a call to one of them fails with "tool not found".

## The docs-first cycle

Follow it for every endpoint the first time it is used in a session.

1. **Find the endpoint.** Look in [references/endpoint-paths.md](references/endpoint-paths.md) first. If the task is not there, `docs_list_sections()` then `docs_index({section: "<name>"})`.
2. **Read its page.** `docs_search({url: "dataforseo_labs/google/keyword_ideas/live"})`. Add `needCodeExample: true` only when the body shape is unclear. Note the required fields, the limits and the Pricing link. Free.
3. **Agree the budget.** State the calls you plan, with their `limit` and `depth`, and get the user's go-ahead. See the `cost-awareness` skill. No `api_request` before this.
4. **Send the request.** One call, then read `status_code` and `items` before planning the next call.

```
docs_search({url: "serp/google/organic/live/advanced"})

api_request({
  method: "POST",
  path: "/v3/serp/google/organic/live/advanced",
  data: [{"keyword": "best crm software", "location_code": 2840, "language_code": "en", "depth": 10}]
})
```

## Shape of an `api_request`

| Field | Meaning |
|---|---|
| `method` | `POST` for every Live endpoint; `GET` for location, language, model and account lookups |
| `path` | The REST path, starting `/v3/`, without a host and without `.ai` |
| `data` | The body. For a Live endpoint an array with exactly one task object |
| `noAiMode` | `true` returns the full response instead of the trimmed one; default `false` |
| `url` | A full URL instead of `path`; leave it alone unless the user asks |

A Live endpoint takes **one task per request**. To cover many keywords or targets, use the endpoint's own array field (`keywords`, `targets`), not several tasks.

## `.ai` mode and `noAiMode`

By default the server appends `.ai` to the path. DataForSEO then returns a cropped response: the envelope shrinks to `id`, `status_code` and `status_message`; empty, `null` and `false` fields are dropped; floats are rounded to three places; `position` and `xpath` are removed; `monthly_searches` becomes `{"2025-03": 201000, ...}`; and `limit` and `depth` **default to 10** where the endpoint accepts them. It costs the same as the full response.

- Set `limit` or `depth` explicitly whenever you want more than 10 rows.
- The cropped form is documented for Live and Task GET endpoints. If a lookup or an Appendix path is rejected, retry it once with `noAiMode: true`.
- The `cost` field is not in the cropped envelope. To see what a call cost, read the balance before and after (`GET /v3/appendix/user_data` with `noAiMode: true`, free) or send that one call with `noAiMode: true`.
- Use `noAiMode: true` only when a field you need is missing from the cropped answer. It can multiply the context size.
- The server can also trim responses per endpoint through a field-config file (`--configuration`, or the `FIELD_CONFIG_PATH` or `FIELD_CONFIG_JSON` environment variable), keyed by endpoint path such as `/v3/backlinks/summary/live`. It is off in this plugin, except for a built-in trim of the Lighthouse payload.

## Pick the endpoint

The full table with a minimal body per row is [references/endpoint-paths.md](references/endpoint-paths.md). The short version:

| Task | Endpoint family |
|---|---|
| Keyword ideas, volume, difficulty, intent | Labs `keyword_ideas`, `keyword_overview`, `bulk_keyword_difficulty`, `search_intent` |
| What a competitor ranks for, who competes | Labs `ranked_keywords`, `competitors_domain`, `domain_intersection` |
| The live SERP for a keyword | SERP `google/organic/live/advanced` |
| Backlink profile, spam, link gaps | Backlinks `summary`, `referring_domains`, `bulk_spam_score`, `domain_intersection` |
| Page audit, tech stack | OnPage `lighthouse`, `instant_pages`; Domain Analytics `domain_technologies` |
| Web mentions and sentiment | Content Analysis `search`, `summary`, `phrase_trends` |
| Brand visibility in ChatGPT and Google AI | AI Optimization `llm_mentions/*`, `chat_gpt/llm_scraper` (the `ai-optimization` skill) |
| Amazon, app stores, local businesses | Merchant, App Data, Business Data |

## Parameters that appear everywhere

| Parameter | Description |
|---|---|
| `location_code` or `location_name` | One of the two. `2840` is United States. Look codes up with the GET location endpoints |
| `language_code` or `language_name` | `"en"` for English. ChatGPT data in AI Optimization is United States and English only |
| `limit`, `offset` | Rows to return and rows to skip; `limit` is 10 in `.ai` mode unless set, 1000 at most |
| `filters` | `[["field", "operator", value], "and", ["field2", "operator", value2]]` |
| `order_by` | `["field,desc"]`; at most three rules |
| `tag` | Your own label, echoed back in the response `data` |

Filter operators: `=`, `<>`, `>`, `<`, `>=`, `<=`, `like`, `not_like`, `in`, `not_in`, and on some endpoints `regex`, `ilike`, `match`. Field names differ per API; `docs_search({url: "dataforseo_labs/filters"})` and its siblings list them.

## Reading the answer

- `status_code: 20000` is success. `40000` and up is a client error, `50000` and up a server error; `docs_search({url: "appendix/errors"})` has the list.
- The data is in `tasks[].result[]`, usually in an `items` array. In `.ai` mode the envelope is flattened to `id`, `status_code`, `status_message` and `items`.
- An empty `items` array is an answer, not an error: DataForSEO has no data for that query.
- Targets are domains **without** `https://` and `www.`; pages are absolute URLs.

## Cost

Every `api_request` is billed, and the plugin never sends one without an agreed budget. The rules and the free balance check are in the `cost-awareness` skill.
