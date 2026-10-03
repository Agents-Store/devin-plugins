# Perplexity MCP Tools (4 tools)

Perplexity provides **AI-synthesized answers** with citations (`@perplexity-ai/mcp-server` 1.x, backed by the Perplexity Agent API). Each tool maps to an Agent API preset.

**Argument shape matters:** `perplexity_ask`, `perplexity_reason` and `perplexity_research` take **`messages`** — an array of `{ "role", "content" }` objects — not `query`. Sending `query` fails validation ("'messages' must be an array"). Only `perplexity_search` takes `query`.

## perplexity_search
Direct web search — ranked results (title, URL, snippet, date), no AI synthesis. Best for finding pages, recent news, and verifying facts.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `max_results` | number | No | 1-20 (default 10) |
| `max_tokens_per_page` | number | No | Tokens extracted per page, 256-2048 (default 1024) |
| `country` | string | No | ISO 3166-1 alpha-2 code (`US`, `GB`) |
| `search_recency_filter` | string | No | `hour`, `day`, `week`, `month`, `year` |
| `search_domain_filter` | string[] | No | Restrict to domains; prefix `-` to exclude (`["-reddit.com"]`) |
| `search_type` | string | No | `web` (default) or `fast` — lower latency and cost, use for routine lookups inside agent loops |

```
Tool: perplexity_search
Input: { "query": "Next.js 15 release notes", "max_results": 5, "search_type": "fast" }
```

## perplexity_ask
Quick web-grounded answer with numbered citations (Agent API `fast` preset). Everyday questions and conversational queries.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `messages` | `{role, content}[]` | Yes | Conversation; `role` is `system`, `user` or `assistant` |
| `search_recency_filter` | string | No | `hour`, `day`, `week`, `month`, `year` |
| `search_domain_filter` | string[] | No | Restrict to domains; prefix `-` to exclude |
| `search_context_size` | string | No | `low` (fastest), `medium`, `high` (most comprehensive) |

```
Tool: perplexity_ask
Input: {
  "messages": [
    { "role": "user", "content": "How do I set up Tailwind CSS in a Next.js 15 project?" }
  ]
}
```

## perplexity_reason
Step-by-step reasoning with web grounding (Agent API `medium` preset). Math, logic, comparisons, debugging. Same parameters as `perplexity_ask`.

```
Tool: perplexity_reason
Input: {
  "messages": [
    { "role": "user", "content": "My Next.js app has a hydration mismatch when formatting dates: the server renders '3/29/2025' and the client renders '03/29/2025'. Why, and how do I fix it?" }
  ],
  "search_recency_filter": "year"
}
```

## perplexity_research
Deep multi-source research (Agent API `high` preset). **Slow (can take minutes) and the most expensive tool** — use it only when the question needs literature-review depth. Takes only `messages`; no filters.

```
Tool: perplexity_research
Input: {
  "messages": [
    { "role": "user", "content": "Compare tRPC, GraphQL and REST for Next.js applications: trade-offs, tooling and adoption." }
  ]
}
```

## When to Use Which Tool

| Need | Tool | Backing |
|------|------|---------|
| Find URLs, recent news, verify a fact | `perplexity_search` | Search API (`search_type: "fast"` for cheap lookups) |
| Simple questions | `perplexity_ask` | Agent API `fast` preset |
| Logic / debugging | `perplexity_reason` | Agent API `medium` preset |
| In-depth analysis | `perplexity_research` | Agent API `high` preset |

## API Key and Hosted MCP

The bundled stdio server reads `PERPLEXITY_API_KEY` (get one at https://console.perplexity.ai).

A hosted MCP is also available at `https://api.perplexity.ai/mcp` (Streamable HTTP) with the same tools. Since September 2026 it supports OAuth ("Sign in with Perplexity"); an API key stays available as the fallback.
