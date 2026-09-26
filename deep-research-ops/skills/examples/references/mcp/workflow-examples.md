# Workflow Examples

All workflows use `~~capability` with automatic fallback between providers (see CONNECTORS.md).

---

## 1. Quick Web Search with Fallback

```
Step 1: ~~search("best RAG frameworks 2026")
        → Tries: Exa → Perplexity → Jina → Firecrawl
        → First success returns results

Step 2: ~~scrape(best_result_url)
        → Tries: Jina → Firecrawl
        → Get full content from top result

Step 3: Summarize findings
```

---

## 2. Parallel Research Batch

```
Step 1: Expand query("AI code assistant market")
        → Related terms: "copilot", "code completion", "AI IDE"

Step 2: ~~batch_search([
          "AI code assistant market size 2026",
          "copilot vs cursor vs cody comparison",
          "AI developer tools funding investment",
          "code completion tools benchmark"
        ])

Step 3: Rank by relevance → top URLs

Step 4: ~~batch_scrape(top_5_ranked_urls)

Step 5: Deduplicate → clean, unique facts for report
```

---

## 3. Site Analysis

```
Step 1: ~~crawl("https://docs.example.com")
        → Firecrawl crawl → fallback: map + batch_scrape

Step 2: Select key URLs from results (docs, API, guides)

Step 3: ~~batch_scrape(key_page_urls)

Step 4: Synthesize into report
```

---

## 4. Academic Research

```
Step 1: ~~academic_search("retrieval augmented generation evaluation")
        → arXiv → SSRN → Perplexity

Step 2: Select top papers by relevance

Step 3: Extract PDF from top papers → figures/tables

Step 4: ~~batch_scrape(paper_landing_pages)

Step 5: ~~search("RAG evaluation current state 2026")
        → General context

Step 6: Synthesize into Deep Research Report
```

---

## 5. Named Entity Discovery (Exhaustive)

```
Step 1: Direct URL probing
  ~~scrape("https://openclaw.com")
  ~~scrape("https://openclaw.ai")
  ~~scrape("https://openclaw.dev")
  ~~scrape("https://openclaw.io")
  → Most will fail — that's expected. Any success = real homepage.

Step 2: Platform checks
  ~~scrape("https://github.com/openclaw")
  ~~scrape("https://www.npmjs.com/package/openclaw")
  ~~scrape("https://pypi.org/project/openclaw/")

Step 3: Search variations
  ~~search('"OpenClaw"')
  ~~search('"OpenClaw" AI tool')
  ~~search('"OpenClaw" site:github.com')

Step 4: Escalation
  ~~search("What is OpenClaw?") → Perplexity first
```
