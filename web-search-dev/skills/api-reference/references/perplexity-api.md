# Perplexity REST API

Base URL: `https://api.perplexity.ai`

## Agent API (Recommended)

The Agent API supports third-party models with web search tools, presets, and model fallback chains. The **simplest way** to use it is with presets — one parameter controls the depth of research:

### Quick Start with Presets

```bash
# Fast factual lookup (cheapest, fastest)
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": "What are the latest Next.js 15 features?", "preset": "fast"}' | jq .

# Detailed analysis with web search
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": "Compare tRPC vs GraphQL for Next.js apps", "preset": "low"}' | jq .

# Comprehensive multi-step research (most thorough, slowest)
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"input": "State of WebAssembly adoption in 2025", "preset": "medium"}' | jq .
```

| Preset | Speed | Depth | Best For |
|--------|-------|-------|----------|
| `fast` | Fast | Light | Quick facts, current info (was `fast-search`) |
| `low` | Medium | Detailed | Comparisons, technical analysis (was `pro-search`) |
| `medium` | Slow | Comprehensive | In-depth reports, multi-aspect topics (was `deep-research`) |
| `high` | Slower | Expert | Expert multi-hop research |
| `xhigh` | Slowest | Agentic | Agentic research with sandbox |
| `wide-research` | Slow | Broad | Large evidence-backed collections |

### With Specific Model

```bash
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Compare React Server Components vs Client Components performance",
    "model": "openai/gpt-5.5",
    "preset": "low"
  }' | jq .
```

### Presets

| Preset | Best For |
|--------|----------|
| `fast` | Quick factual lookups |
| `low` | Detailed analysis with web search |
| `medium` | Comprehensive multi-step research |
| `high` | Expert multi-hop research |
| `xhigh` | Agentic research with sandbox |
| `wide-research` | Large evidence-backed collections |

### Model Fallback Chain

```bash
curl -s -X POST https://api.perplexity.ai/v1/agent \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Explain React 19 new hooks",
    "models": ["anthropic/claude-sonnet-4-6", "openai/gpt-5.5", "xai/grok-4.5"],
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

## Sonar API (Perplexity Models)

Direct access to Perplexity's own models with web-grounded responses.

```bash
curl -s -X POST https://api.perplexity.ai/v1/sonar \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-pro",
    "messages": [
      { "role": "user", "content": "What is the current state of WebAssembly support in browsers?" }
    ]
  }' | jq .
```

### Sonar Models

| Model | Best For |
|-------|----------|
| `sonar` | Quick answers |
| `sonar-pro` | Detailed answers with citations |
| `sonar-reasoning-pro` | Step-by-step reasoning |
| `sonar-deep-research` | Comprehensive research |

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

Params: `query` (string or array of strings for multi-query), `max_results`, `search_domain_filter`, `search_recency_filter`.

## Gateway API

OpenAI-compatible chat completions proxy: `POST https://api.perplexity.ai/router/v1/chat/completions`.

## Response Format (Agent API)

```json
{
  "id": "resp_xxx",
  "model": "openai/gpt-5.5",
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
