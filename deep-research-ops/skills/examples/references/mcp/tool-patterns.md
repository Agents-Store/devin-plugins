# Tool Call Patterns

Patterns organized by `~~capability`. The agent resolves these to actual tools from available MCP servers with automatic fallback (see CONNECTORS.md).

---

## ~~search — Web Search

```
~~search("best alternatives to Notion")
→ Tries: Exa → Perplexity → Jina → Firecrawl
→ First success returns results with URLs

~~answer("What is the current market size for AI code assistants?")
→ Tries: perplexity_ask → perplexity_reason → search results + your own cited synthesis
→ Short AI answer with numbered citations (~~search returns links only)

~~search("AI code assistant market size report")
→ Exa for semantic search results, Perplexity search for dated links
```

---

## ~~scrape — Read Single Page

```
~~scrape("https://example.com/article")
→ Tries: Jina read_url → Firecrawl scrape → Exa fetch (maxCharacters: 20000; default 3000)
→ Returns clean markdown content

Cheap mode — only the passages that answer a question:
~~scrape("https://example.com/docs/limits", question: "What are the default rate limits?", topk: 3)
→ Jina read_url with question/topk; fallback Firecrawl scrape in "query" format

For JS-heavy pages:
→ Firecrawl provider supports waitFor for JS rendering
```

---

## ~~batch_search — Parallel Search

```
~~batch_search([
  "RAG frameworks comparison",
  "vector database benchmarks 2026",
  "embedding models performance"
])
→ Tries: Jina search with a query array (≤5) → one Exa search per query → one Perplexity search per query
→ Returns batch results from all queries
```

---

## ~~batch_scrape — Read Multiple Pages

```
~~batch_scrape([
  "https://example.com/page1",
  "https://example.com/page2",
  "https://example.com/page3"
])
→ Tries: Jina read_url with a URL array (≤5) → Exa fetch with several URLs (maxCharacters: 20000; default 3000) → one Firecrawl scrape per URL
→ Returns content from all URLs
→ Add question/topk to get only the relevant passages from each page (Jina only; the fallbacks return full pages)
```

---

## ~~crawl — Crawl Site

```
~~crawl("https://docs.example.com", limit: 20, depth: 3)
→ Firecrawl crawl — waits for completion and returns the pages
→ Fallback: Firecrawl map → get URLs → ~~batch_scrape
```

---

## ~~extract — Structured Data

```
~~extract(
  url: "https://example.com/pricing",
  prompt: "Extract all pricing plans",
  schema: { plans: [{ name, price, features[] }] }
)
→ Firecrawl scrape in JSON format with prompt + schema — one URL per call
→ Unknown URLs / several sites: Firecrawl agent (poll its job until completed)
→ Last resort: ~~scrape, then extract the fields yourself
```

---

## ~~academic_search — Papers

```
~~academic_search("retrieval augmented generation transformer")
→ Tries: Firecrawl paper search → Jina arXiv → Jina SSRN → Perplexity search restricted to paper domains
→ Returns papers with titles, abstracts, URLs

Full text of one paper (paper-index step):
→ Firecrawl read-paper with paperId "arxiv:<id>" and a question → the passages that answer it

Citation graph:
→ Firecrawl related-papers with seed_ids and mode similar | citers | references

Batch variant:
~~academic_search(["RAG transformer", "dense passage retrieval"])
→ Jina arXiv/SSRN search with a query array (≤5)
```

---

## ~~code_search — Code

```
~~code_search("React server components implementation pattern")
→ Tries: Firecrawl developer search → Exa advanced search with includeDomains github.com (opt-in) → ~~search + "github code example"
→ Returns repositories, issues, PRs and docs with the matched passages
→ Firecrawl developer search with skills "only" searches agent-skill files
```

---

## ~~deep_agent — Heavy Tier (depth deep)

```
~~deep_agent("List 10 headless CMS vendors with pricing model and licence, with sources")
→ Tries: Exa agent_run (API key or OAuth) → Firecrawl agent → Perplexity research
→ Slow (minutes) and billed by usage: use once, at depth deep, as an extra pass
→ Firecrawl agent returns a job id — poll its status every 15-30 seconds; set a credit limit
→ Exa agent_run reports status "running" — call again with its runId, never start a duplicate
→ Perplexity research takes messages: [{ role: "user", content: "..." }]
```

---

## Utility Tools (unique, no fallback)

Query expansion and text classification have no tools: you plan the queries and categorize content yourself.

### Relevance ranking
```
sort_by_relevance(query: "machine learning", documents: ["text1", "text2"])
→ Documents ranked by relevance
```

### Deduplication
```
deduplicate_strings(["fact A", "fact A rephrased", "fact B"])
→ Unique facts only
```

### PDF extraction
```
extract_pdf(id: "1706.03762")
→ Figures, tables, equations from arXiv paper
```

### Screenshots
```
capture_screenshot_url("https://example.com", return_url: true)
→ URL of the page image (without return_url the tool returns base64 JPEG and fills the context)
```

### Date detection
```
guess_datetime_url("https://blog.example.com/post")
→ Publication/update timestamp
```

### Browser automation (Firecrawl)
```
Open a page with an instruction → scrapeId → follow-up instructions on the same scrapeId → stop the session
```
