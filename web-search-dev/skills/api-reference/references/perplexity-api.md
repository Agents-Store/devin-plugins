# Perplexity REST API

Base URL: `https://api.perplexity.ai`

## Agent API (Recommended)

The Agent API is the primary Perplexity path: one `input`, a preset (or an explicit model) and built-in tools such as web search, URL fetching, sandboxes and MCP. The **simplest way** to use it is a preset — one parameter sets the research depth:

### Quick Start with Presets

```bash
# Fast factual lookup (cheapest, fastest)
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": "What are the latest Next.js 15 features?", "preset": "fast"}' | jq .

# Everyday research with light multi-step lookups
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": "Compare tRPC vs GraphQL for Next.js apps", "preset": "low"}' | jq .

# Expert-level, exhaustive coverage (slowest of the three)
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": "State of WebAssembly adoption", "preset": "high"}' | jq .
```

| Preset | Good at | Use when |
|--------|---------|----------|
| `fast` | Single-fact lookups, definitions, quick summaries | One fact or short summary; latency matters most |
| `low` | Everyday research with light multi-step lookups | Current information with light tool use |
| `medium` | Multi-hop browsing and wide aggregation across many sources | Evidence must be chained across many sources |
| `high` | Expert-level reasoning, exhaustive source coverage | Completeness matters more than latency |
| `xhigh` | Open-ended agentic work: sandboxed code, long tool loops | The task is a build-up of steps, not a single question |

A preset by name is a **dynamic preset**: Perplexity updates the underlying model and tools over time. To pin the exact configuration, copy the current values from https://docs.perplexity.ai/docs/agent-api/presets into your request and omit `preset`. Any field you pass next to `preset` (for example `model`, `max_steps`) overrides the preset default.

### With Specific Model

```bash
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Compare React Server Components vs Client Components performance",
    "model": "anthropic/claude-sonnet-5-5",
    "preset": "low"
  }' | jq .
```

Model IDs use `provider/model`. The list of supported IDs is the Agent API Models reference (https://docs.perplexity.ai/docs/agent-api/models); on 2026-10-24 the Agent and Router APIs retire several older `openai/gpt-5.x` IDs, so check it before pinning a model.

### Model Fallback Chain

```bash
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Explain React 19 new hooks",
    "models": ["anthropic/claude-sonnet-5-5", "openai/gpt-6-sol", "xai/grok-4.7"],
    "preset": "low"
  }' | jq .
```

### With Streaming

```bash
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "How to implement OAuth 2.0 in Next.js",
    "preset": "fast",
    "stream": true
  }'
```

## Sonar API (legacy)

Sonar Chat Completions support ended on **2026-09-27**. Synchronous and streaming requests keep working only because they are being reformulated into Agent API requests, gradually and model by model; asynchronous Sonar requests are no longer supported (use the Agent API background mode). Do not build new code on Sonar — migrate:

| Sonar model | Agent API preset |
|-------------|------------------|
| `sonar`, `sonar-pro` | `fast` |
| `sonar-reasoning-pro` | `low` |
| `sonar-deep-research` | `high` (use `xhigh` for the highest quality) |

Request shape: Sonar takes a `messages` array and returns `choices`; the Agent API takes `input` and returns a typed `output` array (a `message` item with the answer and a `search_results` item with the sources). Migration guide: https://docs.perplexity.ai/docs/agent-api/migrate-from-sonar/overview

```bash
# legacy shape, shown for recognition only
curl -s -X POST https://api.perplexity.ai/v1/sonar \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{ "model": "sonar-pro", "messages": [{ "role": "user", "content": "..." }] }'
```

## Search API

Endpoint is `POST https://api.perplexity.ai/search` — no `/v1` prefix.

```bash
curl -s -X POST https://api.perplexity.ai/search \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "React 19 new features",
    "max_results": 5
  }' | jq .
```

Params: `query` (string or array of strings for multi-query), `max_results`, `max_tokens_per_page`, `country`, `search_domain_filter`, `search_recency_filter`. Fast Search is available through the Agent API `fast` preset and the MCP tool's `search_type: "fast"`.

## Gateway API

OpenAI-compatible chat completions proxy: `POST https://api.perplexity.ai/router/v1/chat/completions`.

## Response Format (Agent API)

```json
{
  "id": "resp_xxx",
  "model": "openai/gpt-6-luna",
  "status": "completed",
  "output": [
    {
      "type": "message",
      "content": "AI-generated response..."
    },
    {
      "type": "search_results",
      "results": [
        { "title": "...", "url": "..." }
      ]
    }
  ],
  "usage": {
    "input_tokens": 150,
    "output_tokens": 500,
    "total_cost": 0.015
  }
}
```
