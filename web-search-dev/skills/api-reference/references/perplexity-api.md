# Perplexity REST API

Base URL: `https://api.perplexity.ai`

## Agent API (Recommended)

The Agent API is the primary Perplexity path: one `input`, an effort level (or an explicit model) and built-in tools such as web search, URL fetching, sandboxes and MCP. The **simplest way** to use it is the `effort` parameter — one value sets the research depth. (`effort` replaced `preset` in October 2026; `preset` is still accepted as a deprecated alias, and `effort` wins when both are sent.)

### Quick Start with Effort Levels

```bash
# Fast factual lookup (cheapest, fastest)
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": "What are the latest Next.js 15 features?", "effort": "fast"}' | jq .

# Everyday research with light multi-step lookups
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": "Compare tRPC vs GraphQL for Next.js apps", "effort": "low"}' | jq .

# Expert-level, exhaustive coverage (slowest of the three)
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": "State of WebAssembly adoption", "effort": "high"}' | jq .
```

| Effort | Good at | Use when |
|--------|---------|----------|
| `fast` | Single-fact lookups, definitions, quick summaries | One fact or short summary; latency matters most |
| `low` | Everyday research with light multi-step lookups | Current information with light tool use |
| `medium` | Multi-hop browsing and wide aggregation across many sources | Evidence must be chained across many sources |
| `high` | Expert-level reasoning, exhaustive source coverage | Completeness matters more than latency |
| `xhigh` | Open-ended agentic work: sandboxed code, long tool loops | The task is a build-up of steps, not a single question |
| `ultra` | The deepest configuration; long runs | Maximum depth matters more than time or cost — call it by name, consider background mode |

An effort level by name is **dynamic**: Perplexity updates the underlying model and tools over time. To keep one released configuration, pin a version (`"effort": "fast@<version>"`, versions listed on https://docs.perplexity.ai/docs/agent-api/effort); to freeze the public fields, copy the current values into your request and omit `effort` (`ultra` has no frozen form). Any field you pass next to `effort` (for example `model`, `max_steps`) overrides its default. `effort` is not `reasoning.effort`, which tunes the selected model's reasoning.

### With Specific Model

```bash
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Compare React Server Components vs Client Components performance",
    "model": "anthropic/claude-sonnet-5-5",
    "effort": "low"
  }' | jq .
```

Model IDs use `provider/model`. The list of supported IDs is the Agent API Models reference (https://docs.perplexity.ai/docs/agent-api/models); several older `openai/gpt-5.x` IDs were retired on 2026-10-24, so check it before pinning a model.

### Model Fallback Chain

```bash
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Explain React 19 new hooks",
    "models": ["anthropic/claude-sonnet-5-5", "openai/gpt-6-sol", "xai/grok-4.7"],
    "effort": "low"
  }' | jq .
```

### With Streaming

```bash
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "How to implement OAuth 2.0 in Next.js",
    "effort": "fast",
    "stream": true
  }'
```

## Sonar API (legacy)

Sonar Chat Completions support ended on **2026-09-27**. Synchronous and streaming requests keep working only because they are being reformulated into Agent API requests, gradually and model by model; asynchronous Sonar requests are no longer supported (use the Agent API background mode). Do not build new code on Sonar — migrate:

| Sonar model | Agent API effort |
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

Params: `query` (string or array of strings for multi-query), `max_results`, `max_tokens_per_page`, `country`, `search_domain_filter`, `search_recency_filter`. Fast Search is available through the Agent API `fast` effort level and the MCP tool's `search_type: "fast"`.

## Orchestrator API

Model routing behind OpenAI- and Anthropic-compatible endpoints (formerly the Gateway API at `/router/v1/...`, no longer documented): `POST https://api.perplexity.ai/orchestrator/v1/chat/completions`, `POST https://api.perplexity.ai/orchestrator/v1/responses` (OpenAI formats, base URL `https://api.perplexity.ai/orchestrator/v1`) and `POST https://api.perplexity.ai/orchestrator/v1/messages` (Anthropic Messages, base URL `https://api.perplexity.ai/orchestrator`). Quickstart: https://docs.perplexity.ai/docs/orchestrator/quickstart

## Response Format (Agent API)

```json
{
  "id": "resp_xxx",
  "model": "openai/gpt-6-luna",
  "status": "completed",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        { "type": "output_text", "text": "AI-generated response..." }
      ]
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
    "total_tokens": 650,
    "cost": { "currency": "USD", "input_cost": 0.003, "output_cost": 0.012, "total_cost": 0.015 }
  }
}
```

The answer text is in the `message` item's `content` array (`type: "output_text"`); the SDKs also expose it as `response.output_text`. Cost is under `usage.cost.total_cost`.
