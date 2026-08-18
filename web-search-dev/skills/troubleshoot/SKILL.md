---
name: troubleshoot
description: This skill should be used when the user encounters "search not working", "scrape failing", "firecrawl error", "exa error", "jina error", "perplexity error", "rate limit", "401 unauthorized", "MCP connection failed", or needs to diagnose and fix problems with any web search or scraping service.
---

# Web Search Services Troubleshooting

Diagnostic steps and fixes for common problems across all services.

## Quick Fallback Matrix

When a service fails, switch to an alternative immediately:

| Failing Service | Task | Switch To |
|----------------|------|-----------|
| Firecrawl scrape | Read page | Jina `read_url` |
| Firecrawl search | Web search | Exa `web_search_exa` → Jina `search_web` |
| Firecrawl crawl | Site crawl | Firecrawl `map` + Jina `parallel_read_url` |
| Exa search | Web search | Perplexity `perplexity_search` → Jina `search_web` |
| Jina read | Read page | Firecrawl `scrape` |
| Jina search | Web search | Exa `web_search_exa` |
| Perplexity | AI Q&A | Exa search + Jina read (manual synthesis) |
| Context7 | Framework docs | Exa `web_search_advanced_exa` with `includeDomains` for official docs site |
| Exa code search (removed) | Code examples | Firecrawl `firecrawl_developer_search` |
| Pexels/Unsplash | Stock photos | Jina `search_images` (web-wide) |

## Quick Diagnostics

Run these checks in order:

1. **MCP connection** — try a simple tool call (see setup skill)
2. **API key validity** — check for 401/403 errors
3. **Rate limits** — check for 429 errors
4. **Service status** — check if the service is up
5. **Network** — check internet connectivity

## Per-Service Error Reference

### Firecrawl

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid `FIRECRAWL_API_KEY` | Regenerate at https://firecrawl.dev/app/api-keys |
| 402 Payment Required | Insufficient credits | Top up credits or check billing |
| 429 Rate Limited | Too many requests | Wait and retry with backoff |
| `SCRAPE_ALL_ENGINES_FAILED` | Page unscrapable | Try with `waitFor`, try Jina `read_url` instead |
| `SCRAPE_SSL_ERROR` | SSL certificate issue | Try with different URL scheme |
| `SCRAPE_DNS_RESOLUTION_ERROR` | Invalid domain | Verify URL is correct |
| Timeout | Page too large or slow | Increase `waitFor`, try `onlyMainContent: true` |

### Exa

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Invalid API key | Wrong `EXA_API_KEY` | Regenerate at https://dashboard.exa.ai/api-keys |
| 400 Bad Request | Invalid params | Check: `category: "company"` disables date/text filters |
| 422 Validation Error | Wrong param format | Check param names (camelCase for API, snake_case for Python SDK) |
| 429 Rate Limited | Exceeded rate limit | Add API key for higher limits or wait |
| Empty results | Query too specific | Broaden query, remove filters, try `type: "deep"` |

### Perplexity

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid `PERPLEXITY_API_KEY` | Regenerate at https://console.perplexity.ai |
| Model not available | Invalid model ID | Use `provider/model` format (e.g., `openai/gpt-5.5`) |
| Preset not found | Old preset name (`fast-search`/`pro-search`/`deep-research`) | Use `fast` / `low` / `medium` / `high` / `xhigh` |
| Empty response | Query too vague | Be more specific, try different preset |
| MCP server not starting | `npx` or Node issue | Run `npx -y @perplexity-ai/mcp-server` manually |

### Jina

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid `JINA_API_KEY` | Get new key at https://jina.ai/?sui=apikey |
| 429 Rate Limited | Exceeded RPM | Use API key — reader: 20 RPM without, 500 with key; search requires a key (100 RPM) |
| Empty markdown | Page uses heavy JS | Try Firecrawl `scrape` with `waitFor` instead |
| Timeout | Large page or slow server | Try with `X-Target-Selector` to extract specific section |
| PDF extraction fails | Invalid PDF URL | Verify PDF is publicly accessible |

### Context7

| Error | Cause | Fix |
|-------|-------|-----|
| Library not found | Unknown library name | Try different name variations (e.g., "nextjs" vs "next.js") |
| No results | Library not indexed | Fall back to Exa search with official docs domain |
| MCP server not starting | npm issue | Run `npx -y @upstash/context7-mcp` manually |
| `ERR_MODULE_NOT_FOUND` for `@modelcontextprotocol/sdk/dist/esm/server/mcp.js` | Corrupted npx cache | Clear the stale cache — see fix below |

#### Context7 `ERR_MODULE_NOT_FOUND` Fix

This happens when the npx cache has a broken installation where `@modelcontextprotocol/sdk` is missing JS runtime files (only `.d.ts` present). Caused by version conflicts between context7-mcp and the MCP SDK.

**Automatic fix** — run this to clear and re-download:

```bash
# Remove corrupted context7 npx cache
find ~/.npm/_npx -path "*/@upstash/context7-mcp" -print -quit 2>/dev/null | while read p; do
  cache_dir=$(echo "$p" | sed 's|/node_modules/.*||')
  echo "Removing corrupted cache: $cache_dir"
  rm -rf "$cache_dir"
done

# Verify fresh install works
npx -y @upstash/context7-mcp --help
```

After clearing, restart Claude Code or run `/mcp` to reconnect.

### Pexels / Unsplash

| Error | Cause | Fix |
|-------|-------|-----|
| Tool not found | MCP not configured | These services need separate MCP config |
| 401 Unauthorized | Invalid API key | Check Pexels/Unsplash API key |
| 429 Rate Limited | Too many requests | Pexels: 200 req/hr; Unsplash: 50 req/hr demo, 1,000 req/hr production |

## Common Cross-Service Issues

### MCP Server Won't Start

```bash
# Check Node.js version (need 18+)
node --version

# Test MCP server manually
npx -y firecrawl-mcp
npx -y @perplexity-ai/mcp-server
npx -y @upstash/context7-mcp

# If you see ERR_MODULE_NOT_FOUND, clear the corrupted npx cache
# This removes ALL npx caches (they re-download on next use):
rm -rf ~/.npm/_npx/

# Or clean just npm cache
npm cache clean --force
```

### All Services Return Empty Results

1. Check internet connectivity
2. Verify the query is specific enough
3. Try a known-good query like "React tutorial"
4. Check if you're behind a VPN/proxy that blocks requests

### Rate Limiting Across Services

| Service | Free Tier Limit | With API Key |
|---------|----------------|--------------|
| Firecrawl | — | Based on plan |
| Exa | Rate limited | Higher limits |
| Perplexity | — | Based on plan |
| Jina | Reader 20 RPM (search requires key) | Reader 500 RPM, search 100 RPM |
| Pexels | 200 req/hr | Same |
| Unsplash | 50 req/hr (demo) | 1,000 req/hr (production) |

When hitting rate limits:
1. Switch to an alternative service (see mcp-patterns routing table)
2. Add delays between requests (1-2 seconds)
3. Batch operations where possible (Jina parallel tools, Firecrawl batch scrape)
4. Cache results to avoid duplicate requests

### API Key Not Working After Plugin Setup

Sensitive `userConfig` values (API keys) are stored in the system keychain and only available in MCP configs and hooks — not in skill/agent content. If a direct API call from a skill needs the key:
1. Use the MCP tool instead (it has the key via .mcp.json)
2. Or reference `process.env.CLAUDE_PLUGIN_OPTION_FIRECRAWL_API_KEY` in scripts

## When to Escalate

- Consistent 500 errors from a service → service is down, wait or use alternative
- API key works in curl but not in MCP → MCP server config issue, check .mcp.json
- Data corruption or garbled output → try different output format (markdown → html → text)
