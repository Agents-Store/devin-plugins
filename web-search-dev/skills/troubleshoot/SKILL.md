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
| Firecrawl crawl | Site crawl | Firecrawl `map` + Jina `read_url` (up to 5 URLs per call) |
| Exa search | Web search | Perplexity `perplexity_search` → Jina `search_web` |
| Jina read | Read page | Firecrawl `scrape` |
| Jina search | Web search | Exa `web_search_exa` |
| Perplexity | AI Q&A | Exa search + Jina read (manual synthesis) |
| Context7 | Framework docs | Exa `web_search_advanced_exa` with `includeDomains` for official docs site |
| Exa code search (removed) | Code examples | Firecrawl `firecrawl_developer_search` |
| Pexels/Unsplash REST | Stock photos | Jina `search_images` with `return_url: true` (web-wide), or the other stock service |

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
| `DEPRECATED_TOOL` | Called a tool that no longer exists (the old extract and GitHub-search tools) | Use `firecrawl_scrape` with `formats: ["json"]` + `jsonOptions`, `firecrawl_agent`, or `firecrawl_developer_search` |
| Free-tier rate-limit message | Keyless hosted MCP exhausted | Set `FIRECRAWL_API_TOKEN` (API key) |
| `Alexandria requires an API key on a team with Alexandria access` | Keyless session or team without Alexandria | Use an authenticated key; otherwise fall back to `firecrawl_agent` / web search |
| `THIRD_PARTY_DATA_TERMS_REQUIRED` | Alexandria provider terms not accepted | A human reviews the terms (`terms/show`) and explicitly accepts them — never accept on the user's behalf |
| Crawl response huge | `firecrawl_crawl` returns all pages in one response | Lower `limit`, add `includePaths`, set `scrapeOptions.formats` to `["markdown"]` |

### Exa

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Invalid API key | Wrong `EXA_API_KEY` | Regenerate at https://dashboard.exa.ai/api-keys |
| 400 Bad Request | Invalid params | Check: `category: "company"` disables date/text filters |
| 422 Validation Error | Wrong param format | Check param names (camelCase for API, snake_case for Python SDK) |
| 429 Rate Limited | Exceeded rate limit | Add API key for higher limits or wait |
| Empty results | Query too specific | Broaden query, remove filters, try `type: "deep"` |
| `agent_run` missing from the tool list | Opt-in on the bundled npx server; needs a key | Set `ENABLED_TOOLS=web_search_exa,web_fetch_exa,web_search_advanced_exa,agent_run` and `EXA_API_KEY`, restart Claude Code |

### Perplexity

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid `PERPLEXITY_API_KEY` | Regenerate at https://console.perplexity.ai |
| `'messages' must be an array` | Called `perplexity_ask` / `perplexity_reason` / `perplexity_research` with `query` | Send `messages: [{ "role": "user", "content": "..." }]` (`perplexity_search` still takes `query`) |
| Model not available | Invalid or retired model ID (some `openai/gpt-5.x` IDs are retired on 2026-10-24) | Use `provider/model` format with a current ID (e.g., `anthropic/claude-sonnet-5-5`, `openai/gpt-6-sol`) |
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
| `[jina-mcp] ...` truncation note | `read_url` output exceeded the client's 25k-token limit | Pass `question` to get only relevant passages, or add `?max_tokens=50000` to the endpoint URL |
| Context fills with base64 data | `search_images` / `capture_screenshot_url` default to base64 | Pass `"return_url": true` |
| `tool not found` for a Jina tool from an older guide (batch `parallel` variants, classification, query expansion, image de-duplication, BibTeX, key display) | Jina cut its MCP surface from 21 to 12 tools on 2026-09-18 | Use array inputs on `read_url` / `search_*`; the model classifies, expands queries and reads citations itself |
| PDF extraction fails | Invalid PDF URL | Verify PDF is publicly accessible |

### Context7

| Error | Cause | Fix |
|-------|-------|-----|
| `query` required error on `resolve-library-id` | Sent only `libraryName` | Always send both `query` and `libraryName` |
| Library not found | Unknown library name | Use the official name with its punctuation (`Next.js`, `Three.js`), or try variations |
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

### Pexels / Unsplash (REST)

There is no MCP server for these services — they are called with `curl` using `PEXELS_API_KEY` and `UNSPLASH_ACCESS_KEY` (see `media-search`).

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized (Pexels) | Missing or invalid `PEXELS_API_KEY` | The header is `Authorization: <key>` with no `Bearer` prefix; regenerate at https://www.pexels.com/api/ |
| 401 Unauthorized (Unsplash) | Missing or invalid Access Key | Header must be `Authorization: Client-ID <access key>`; the same applies to the `download_location` call |
| 403 Forbidden (Unsplash) | Rate limit reached or key lacks permission | Wait for the hourly window; apply for production access on the developer dashboard |
| 429 Rate Limited | Too many requests | Pexels: 200 req/hour and 20,000 req/month; Unsplash: 50 req/hour demo, 1,000 req/hour production. Cache results; watch `X-Ratelimit-Remaining` |
| Video request 404 | Old `/videos/` path | Use `https://api.pexels.com/v1/videos/...` |
| Empty `$PEXELS_API_KEY` in curl | Variable not exported in the shell that launched Claude Code | Export the variable (or set it in the local settings `env` block) and restart |
| Unsplash photo shows no credit / usage warning | Missing attribution or download event | Add the attribution with `utm_source` / `utm_medium=referral` and call `photo.links.download_location` |

## Common Cross-Service Issues

### MCP Server Won't Start

```bash
# Check Node.js version (firecrawl-mcp needs 22+; context7-mcp 20.18.1+; exa-mcp-server 20+)
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
| Pexels | 200 req/hr, 20,000 req/month | Same (higher limits on request) |
| Unsplash | 50 req/hr (demo) | 1,000 req/hr (production) |

When hitting rate limits:
1. Switch to an alternative service (see mcp-patterns routing table)
2. Add delays between requests (1-2 seconds)
3. Batch operations where possible (Jina `read_url` / `search_*` array inputs, Firecrawl batch scrape)
4. Cache results to avoid duplicate requests

### API Key Not Working After Plugin Setup

Sensitive `userConfig` values (API keys) are stored in the system keychain and only available in MCP configs and hooks — not in skill/agent content. If a direct API call from a skill needs the key:
1. Use the MCP tool instead (it has the key via .mcp.json)
2. Or reference `process.env.CLAUDE_PLUGIN_OPTION_FIRECRAWL_API_KEY` in scripts

## When to Escalate

- Consistent 500 errors from a service → service is down, wait or use alternative
- API key works in curl but not in MCP → MCP server config issue, check .mcp.json
- Data corruption or garbled output → try different output format (markdown → html → text)
