---
name: setup
description: This skill should be used when the user asks to "verify web search setup", "check search services", "test firecrawl connection", "test exa connection", "is jina working", "check perplexity MCP", or needs to confirm which web search and scraping services are operational.
---

# Web Search Services Setup Verification

Verify which search and scraping services are connected and operational.

## Service Availability Check

Run one lightweight call per service to confirm connectivity. Not all services need to be active — the plugin works with any subset.

### 1. Firecrawl

```
Tool: firecrawl_search
Input: { "query": "test", "limit": 1, "sources": ["web"] }
```

**Expected:** Returns search results. If error, check `FIRECRAWL_API_TOKEN` — the env var this plugin's `.mcp.json` maps to the server's `FIRECRAWL_API_KEY`. Without a key only `firecrawl_scrape`, `firecrawl_search` and `firecrawl_parse` work (rate-limited). Optional: `firecrawl_credit_usage` confirms the key and shows the balance. The server needs Node.js 22+.

### 2. Exa

```
Tool: web_search_exa
Input: { "query": "test", "numResults": 1 }
```

**Expected:** Returns results with URLs. If error, check `EXA_API_KEY`. `agent_run` and `web_search_advanced_exa` are opt-in on the bundled server (`ENABLED_TOOLS` environment variable) — their absence is not an error.

### 3. Perplexity

```
Tool: perplexity_search
Input: { "query": "test", "max_results": 1, "search_type": "fast" }
```

**Expected:** Returns a ranked result (title, URL, snippet). If error, check `PERPLEXITY_API_KEY`. The answer tools take `messages`, not `query`:

```
Tool: perplexity_ask
Input: { "messages": [{ "role": "user", "content": "What is 2+2?" }] }
```

### 4. Jina

```
Tool: read_url
Input: { "url": "https://example.com", "question": "What is this page about?" }
```

**Expected:** Returns the passage(s) answering the question (omit `question` for the full page). `read_url` works without an API key (rate-limited); search tools need a key. The server exposes 12 tools.

### 5. Context7

```
Tool: resolve-library-id
Input: { "query": "hooks", "libraryName": "React" }
```

**Expected:** Returns library ID like `/facebook/react`. Both `query` and `libraryName` are required. API key optional — keyless works with low rate limits; a key (context7.com/dashboard) grants higher limits and private repos.

### 6. Media Services (Pexels / Unsplash — REST)

These are plain REST APIs, not MCP servers. Check the keys with one request each (the output shows only status codes, never the keys):

```bash
curl -s -o /dev/null -w "pexels %{http_code}\n" -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/search?query=nature&per_page=1"
curl -s -o /dev/null -w "unsplash %{http_code}\n" -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}" \
  "https://api.unsplash.com/search/photos?query=nature&per_page=1"
```

**Expected:** `200` for each configured service; `401` means a missing or wrong key. Both keys are optional (`PEXELS_API_KEY`, `UNSPLASH_ACCESS_KEY` — set them in the environment that launches Claude Code).

## Service Status Summary

After running checks, report which services are available:

| Service | Status | Capabilities |
|---------|--------|-------------|
| Firecrawl | Connected / Not available | scrape (incl. JSON format), crawl, search, parse, agent, interact, monitors, research/developer search, Alexandria |
| Exa | Connected / Not available | semantic search, page fetch (+ advanced search, `agent_run` when enabled) |
| Perplexity | Connected / Not available | search, AI answers, research, reasoning |
| Jina | Connected / Not available | read pages (batch + question mode), search, images, rerank, deduplicate |
| Context7 | Connected / Not available | framework documentation search |
| Pexels (REST) | Key valid / No key | stock photos and videos |
| Unsplash (REST) | Key valid / No key | stock photos |

## Working with Partial Availability

Not all services need to be active — the plugin works with any subset. Here's what you can do with common combinations:

| Available Services | You Can Do |
|-------------------|------------|
| Firecrawl only | Scrape, crawl, search, structured JSON extraction, agent research, live-page interaction, parse files, monitor changes |
| Jina only | Read pages (batch + question mode), search web/papers/images, rerank, deduplicate |
| Exa only | Semantic search, page fetch, domain-scoped search |
| Perplexity only | AI Q&A, research, reasoning with citations |
| Context7 only | Framework/library documentation search |
| Firecrawl + Jina | Full scraping pipeline with fallbacks |
| Any service + Context7 | Dev workflow with doc search |

If a recommended tool is unavailable, the mcp-patterns skill routing table shows fallback alternatives for every task.

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `npx` command not found | Node.js not installed | Install Node.js 22+ (required by `firecrawl-mcp`; the other servers need 20+) |
| 401 Unauthorized | Invalid API key | Check key in plugin settings or regenerate |
| Connection timeout | Network or firewall | Check internet connectivity |
| MCP server not starting | npm package issue | Run `npx -y firecrawl-mcp` manually to see errors |
| Tool not found | MCP server not configured | Check `.mcp.json` or Claude Code MCP settings |

## What This Skill Does NOT Cover

- Creating API accounts — visit each service's website to sign up
- Configuring MCP servers from scratch — the plugin's `.mcp.json` handles this automatically
