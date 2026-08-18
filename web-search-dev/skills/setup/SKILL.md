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
Input: { "query": "test", "limit": 1 }
```

**Expected:** Returns search results. If error, check `FIRECRAWL_API_TOKEN` — the env var this plugin's `.mcp.json` maps to the server's `FIRECRAWL_API_KEY`.

### 2. Exa

```
Tool: web_search_exa
Input: { "query": "test", "numResults": 1 }
```

**Expected:** Returns results with URLs. If error, check Exa API key.

### 3. Perplexity

```
Tool: perplexity_search
Input: { "query": "test" }
```

**Expected:** Returns AI-synthesized answer. If error, check `PERPLEXITY_API_KEY`.

### 4. Jina

```
Tool: read_url
Input: { "url": "https://example.com" }
```

**Expected:** Returns markdown content. Works without API key (rate-limited), with key for full access.

### 5. Context7

```
Tool: resolve-library-id
Input: { "libraryName": "react" }
```

**Expected:** Returns library ID like `/facebook/react`. API key optional — keyless works with low rate limits; a key (context7.com/dashboard) grants higher limits and private repos.

### 6. Media Services (Pexels / Unsplash)

Check if media search tools are available in your session:

```
Tool: searchPhotos (Pexels)
Input: { "query": "nature", "per_page": 1 }
```

```
Tool: get_search_photos (Unsplash)
Input: { "query": "nature", "per_page": 1 }
```

Media services require separate MCP configuration — they are not bundled with this plugin.

## Service Status Summary

After running checks, report which services are available:

| Service | Status | Capabilities |
|---------|--------|-------------|
| Firecrawl | Connected / Not available | scrape, crawl, search, extract, parse, agent, interact, monitors, research/developer search |
| Exa | Connected / Not available | semantic search, page fetch |
| Perplexity | Connected / Not available | AI search, research, reasoning |
| Jina | Connected / Not available | read pages, search, images, classify, deduplicate |
| Context7 | Connected / Not available | framework documentation search |
| Pexels | Connected / Not available | stock photos and videos |
| Unsplash | Connected / Not available | stock photos |

## Working with Partial Availability

Not all services need to be active — the plugin works with any subset. Here's what you can do with common combinations:

| Available Services | You Can Do |
|-------------------|------------|
| Firecrawl only | Scrape, crawl, search, extract structured data, live-page interaction, parse files, monitor changes |
| Jina only | Read pages, search web, image search, classify, deduplicate, batch ops |
| Exa only | Semantic search, page fetch, domain-scoped search |
| Perplexity only | AI Q&A, research, reasoning with citations |
| Context7 only | Framework/library documentation search |
| Firecrawl + Jina | Full scraping pipeline with fallbacks |
| Any service + Context7 | Dev workflow with doc search |

If a recommended tool is unavailable, the mcp-patterns skill routing table shows fallback alternatives for every task.

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `npx` command not found | Node.js not installed | Install Node.js 18+ |
| 401 Unauthorized | Invalid API key | Check key in plugin settings or regenerate |
| Connection timeout | Network or firewall | Check internet connectivity |
| MCP server not starting | npm package issue | Run `npx -y firecrawl-mcp` manually to see errors |
| Tool not found | MCP server not configured | Check `.mcp.json` or Claude Code MCP settings |

## What This Skill Does NOT Cover

- Creating API accounts — visit each service's website to sign up
- Configuring MCP servers from scratch — the plugin's `.mcp.json` handles this automatically
