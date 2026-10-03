---
name: api-reference
description: This skill should be used when the user asks for "Firecrawl API endpoints", "Exa REST API", "Perplexity API reference", "Jina API curl examples", "web search API documentation", or needs specific HTTP endpoint details for any of the web search and scraping services.
disable-model-invocation: true
---

# Web Search Services API Reference

Curated REST API endpoints for the 4 core services plus the Pexels and Unsplash media APIs. For full documentation, visit each service's official docs.

## Authentication Summary

| Service | Auth Header | Key Format | Docs |
|---------|------------|------------|------|
| Firecrawl | `Authorization: Bearer KEY` | `fc-xxx` | https://docs.firecrawl.dev |
| Exa | `x-api-key: KEY` (also accepts `Authorization: Bearer KEY`) | UUID string | https://exa.ai/docs |
| Perplexity | `Authorization: Bearer KEY` | String | https://docs.perplexity.ai |
| Jina | `Authorization: Bearer KEY` | `jina_xxx` | https://jina.ai/reader |
| Pexels | `Authorization: KEY` (no `Bearer`) | String | https://www.pexels.com/api/documentation/ |
| Unsplash | `Authorization: Client-ID ACCESS_KEY` | Access key | https://unsplash.com/documentation |

## Service Endpoints

### Firecrawl — `https://api.firecrawl.dev`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v2/scrape` | Scrape single URL |
| POST | `/v2/search` | Web search with content |
| POST | `/v2/crawl` | Start site crawl |
| GET | `/v2/crawl/{id}` | Check crawl status |
| POST | `/v2/crawl/params-preview` | Preview crawler options from a natural-language prompt |
| POST | `/v2/map` | Map site URLs |
| POST | `/v2/extract` | Legacy LLM structured extraction (maintenance mode — prefer `/v2/scrape` with a `json` format, or `/v2/agent`) |
| POST | `/v2/batch/scrape` | Batch scrape multiple URLs |
| POST | `/v2/agent` | Autonomous research agent (default model `spark-2`; `GET /v2/agent/{jobId}` for status) |
| POST | `/v2/scrape/{jobId}/interact` | Run a prompt or code in the live browser session of a scrape (`DELETE` the same path to stop) |
| POST | `/v2/interact` | Create a standalone interact session (`/v2/interact/{sessionId}/execute` to run code, `DELETE /v2/interact/{sessionId}` to stop) |
| POST | `/v2/parse` | Parse files (PDF, DOCX, …) into LLM-ready output |
| POST / GET | `/v2/monitor` | Create / list page-change monitors (CRUD + run + checks) |
| GET / POST | `/v2/search/developer` | Search the developer index (GitHub issues, PRs, READMEs, docs) |
| GET | `/v2/search/research/papers` | Search academic papers (`/{id}` for one paper, `/{id}/similar` for related) |
| GET | `/v2/team/credit-usage` | Remaining credits (`/v2/team/credit-usage/historical` for history) |

See `references/firecrawl-api.md` for curl examples.

### Exa — `https://api.exa.ai`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/search` | Semantic web search (single powerful endpoint) |
| POST | `/contents` | Get text/highlights/summary for URLs or result ids |
| POST | `/answer` | Direct answer with citations |
| POST | `/agent/runs` | Start an Exa Agent run (multi-step research) |
| GET | `/agent/runs/{id}` | Poll an agent run |
| POST | `/monitors` | Create a monitor (`GET /monitors`, `/monitors/{id}`, `/monitors/{id}/trigger`, `/monitors/{id}/runs`) |
| POST | `/batches` | Batch API for bulk requests (`GET /batches/{id}`) |

Exa also offers a Websets API — see https://exa.ai/docs for details. The URL-similarity endpoint is deprecated; describe the source page in a normal `/search` query instead.

See `references/exa-api.md` for curl examples.

### Perplexity — `https://api.perplexity.ai`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/agent` | Agent API (presets or models + web search) — the primary path |
| POST | `/search` | Web search (no `/v1` prefix) |
| POST | `/v1/sonar` | Legacy Sonar chat completion (support ended 2026-09-27; requests are being rerouted to the Agent API — migrate) |
| POST | `/v1/embeddings` | Text embeddings (`pplx-embed-v1-0.6b`/`4b`; contextualized variants via the contextualized embeddings endpoint) |
| POST | `/router/v1/chat/completions` | Gateway API (OpenAI-compatible) |

See `references/perplexity-api.md` for curl examples.

### Jina — Multiple base URLs

| Method | URL Pattern | Description |
|--------|------------|-------------|
| GET | `https://r.jina.ai/{URL}` | Read any URL as markdown |
| GET | `https://s.jina.ai/?q={QUERY}` | Web search |
| POST | `https://api.jina.ai/v1/embeddings` | Text embeddings |
| POST | `https://api.jina.ai/v1/rerank` | Rerank documents |
| POST | `https://api.jina.ai/v1/classify` | Text classification |

See `references/jina-api.md` for curl examples.

### Pexels and Unsplash — media search

| Method | URL | Description |
|--------|-----|-------------|
| GET | `https://api.pexels.com/v1/search` | Search photos (`query`, `orientation`, `size`, `color`, `locale`, `per_page`) |
| GET | `https://api.pexels.com/v1/videos/search` | Search videos (videos live under `/v1/videos/`) |
| GET | `https://api.pexels.com/v1/videos/popular` | Popular videos (`min_width`, `min_height`, `min_duration`, `max_duration`) |
| GET | `https://api.unsplash.com/search/photos` | Search photos |
| GET | `<photo.links.download_location>` | Unsplash download event — required when a photo is used |

Rate limits: Pexels 200 req/hour and 20,000 req/month; Unsplash 50 req/hour (demo) or 1,000 req/hour (production). Unsplash API rules (hotlink `photo.urls.*`, download event, attribution) are in `mcp-patterns/references/media-tools.md`.
