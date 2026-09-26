# Tool Call Patterns

Patterns organized by `~~capability`. The agent resolves these to actual tools from available MCP servers with automatic fallback (see CONNECTORS.md).

---

## ~~search — Web Search

```
~~search("best alternatives to Notion")
→ Tries: Exa → Perplexity → Jina → Firecrawl
→ First success returns results with URLs

~~search("What is the current market size for AI code assistants?")
→ Perplexity first gives AI answer with citations
→ Exa for semantic search results
```

---

## ~~scrape — Read Single Page

```
~~scrape("https://example.com/article")
→ Tries: Jina → Firecrawl
→ Returns clean markdown content

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
→ Tries: Jina parallel → sequential Exa → sequential Perplexity
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
→ Tries: Jina parallel → sequential Firecrawl
→ Returns content from all URLs
```

---

## ~~crawl — Crawl Site

```
~~crawl("https://docs.example.com", limit: 20, depth: 3)
→ Firecrawl crawl → poll status until completed
→ Fallback: Firecrawl map → get URLs → ~~batch_scrape
```

---

## ~~extract — Structured Data

```
~~extract(
  urls: ["https://example.com/pricing"],
  prompt: "Extract all pricing plans",
  schema: { plans: [{ name, price, features[] }] }
)
→ Firecrawl extract with LLM
→ Fallback: Firecrawl scrape with JSON options
```

---

## ~~academic_search — Papers

```
~~academic_search("retrieval augmented generation transformer")
→ Tries: Jina arXiv → Jina SSRN → Perplexity + "research paper"
→ Returns papers with titles, abstracts, URLs

Parallel variant:
~~academic_search(["RAG transformer", "dense passage retrieval"])
→ Jina parallel arXiv/SSRN search
```

---

## ~~code_search — Code

```
~~code_search("React server components implementation pattern")
→ Tries: Exa code search → ~~search + "github code example"
→ Returns code snippets with context
```

---

## Utility Tools (unique, no fallback)

### Query expansion
```
expand_query("AI code assistant")
→ Related terms for broader search
```

### Text classification
```
classify_text(texts: ["article..."], labels: ["tech", "science", "business"])
→ Category for each text
```

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
capture_screenshot_url("https://example.com")
→ JPEG image of the page
```

### Date detection
```
guess_datetime_url("https://blog.example.com/post")
→ Publication/update timestamp
```

### Autonomous agent (Firecrawl)
```
Start agent with prompt → agent_id
Poll agent status until "completed" (1-5 min)
```

### Browser automation (Firecrawl)
```
Create session → execute actions → delete session
```
