---
name: api-reference
description: This skill should be used when the user asks for "Firecrawl API endpoints", "Exa REST API", "Perplexity API reference", "Jina API curl examples", "web search API documentation", or needs specific HTTP endpoint details for any of the web search and scraping services.
disable-model-invocation: true
---

# Web Search Services API Reference

Curated REST API endpoints for all 4 core services. For full documentation, visit each service's official docs.

## Authentication Summary

| Service | Auth Header | Key Format | Docs |
|---------|------------|------------|------|
| Firecrawl | `Authorization: Bearer KEY` | `fc-xxx` | https://docs.firecrawl.dev |
| Exa | `x-api-key: KEY` (also accepts `Authorization: Bearer KEY`) | UUID string | https://exa.ai/docs |
| Perplexity | `Authorization: Bearer KEY` | String | https://docs.perplexity.ai |
| Jina | `Authorization: Bearer KEY` | `jina_xxx` | https://jina.ai/reader |

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
| POST | `/v2/extract` | LLM structured extraction |
| POST | `/v2/batch/scrape` | Batch scrape multiple URLs |
| POST | `/v2/agent` | Autonomous research agent |
| POST | `/v2/browser` | Create browser session |
| POST | `/v2/parse` | Parse files (PDF, DOCX, …) into LLM-ready output |
| POST / GET | `/v2/monitor` | Create / list page-change monitors (CRUD + run + checks) |
| GET | `/v2/developer/search` | Search the developer index (GitHub issues, PRs, READMEs, docs) |
| POST | `/v2/research/papers/search` | Search academic papers |

See `references/firecrawl-api.md` for curl examples.

### Exa — `https://api.exa.ai`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/search` | Semantic web search (single powerful endpoint) |
| POST | `/contents` | Get text/highlights/summary for URLs or result ids |
| POST | `/findSimilar` | Find pages similar to a URL |
| POST | `/answer` | Direct answer with citations |
| POST | `/agent/runs` | Start an Exa Agent run (multi-step research) |
| GET | `/agent/runs/{id}` | Poll an agent run |

Exa also offers Websets and Monitors APIs — see https://exa.ai/docs for details.

See `references/exa-api.md` for curl examples.

### Perplexity — `https://api.perplexity.ai`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/agent` | Agent API (third-party models + web search) |
| POST | `/search` | Web search (no `/v1` prefix) |
| POST | `/v1/sonar` | Chat completion with web grounding |
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
