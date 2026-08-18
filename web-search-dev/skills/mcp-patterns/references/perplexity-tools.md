# Perplexity MCP Tools (4 tools)

Perplexity provides **AI-synthesized answers** with citations. Each tool is backed by a different API surface optimized for specific tasks.

## perplexity_search
Direct web search via the Perplexity Search API — returns ranked results (title/url/snippet), not an AI answer. Best for finding current information, news, facts, and specific web content.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |

```
Tool: perplexity_search
Input: { "query": "What are the latest Next.js 15 features?" }
```

Returns ranked search results with source URLs. Use this for factual lookups and finding pages.

## perplexity_ask
Quick questions backed by the Agent API `fast` preset. Best for everyday searches and conversational queries.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Question to ask |

```
Tool: perplexity_ask
Input: { "query": "How do I set up Tailwind CSS in a Next.js 15 project?" }
```

Good for straightforward questions that need an AI-synthesized answer.

## perplexity_research
Deep research backed by the Agent API `high` preset (can take minutes). Best for complex topics requiring comprehensive analysis.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Research topic |

```
Tool: perplexity_research
Input: { "query": "Compare tRPC vs GraphQL vs REST for Next.js applications in 2025" }
```

Takes longer but produces thorough, well-cited analysis. Use for complex comparisons, technical evaluations, and multi-aspect topics.

## perplexity_reason
Logical reasoning backed by the Agent API `medium` preset. Best for step-by-step analysis and complex problem solving.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Problem to reason about |

```
Tool: perplexity_reason
Input: { "query": "My Next.js app has a hydration mismatch error when using date formatting. The server renders '3/29/2025' but the client renders '03/29/2025'. Why does this happen and how to fix it?" }
```

Best for debugging, logic problems, and step-by-step explanations.

## When to Use Which Tool

| Need | Tool | Backing |
|------|------|---------|
| Quick facts, current info | `perplexity_search` | Search API |
| Simple questions | `perplexity_ask` | Agent API `fast` preset |
| In-depth analysis | `perplexity_research` | Agent API `high` preset |
| Logic / debugging | `perplexity_reason` | Agent API `medium` preset |

## API Key

All 4 tools require `PERPLEXITY_API_KEY`. Get one at https://console.perplexity.ai.

A hosted MCP is also available at `https://api.perplexity.ai/mcp` (Streamable HTTP) with identical tools.
