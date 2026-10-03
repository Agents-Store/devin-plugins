---
name: search-strategies
description: Search strategy guidelines — tool selection, fallback chains, query optimization, and parallel search orchestration. Use when choosing which search tools to use, handling tool failures, or optimizing search queries.
---

# Search Strategies

Search strategies, provider selection, and query optimization. All calls use `~~capability` — on error, automatically try the next provider (see CONNECTORS.md for fallback chains).

## When to Use Each Provider

### Exa
- Semantic meaning-based search (not keyword matching)
- Find similar content
- Company and people lookup (`category:company`, `category:people` inside the query)
- Date and domain filters through the opt-in advanced search tool
- Heavy research runs (`~~deep_agent`) when an API key or OAuth is set up

### Perplexity
- Factual questions (market size, dates, definitions)
- AI-synthesized answer with citations — `~~answer` (Agent API presets: `fast`, `medium`, `high`)
- Search with recency and domain filters (`perplexity_search`)
- Quick fact-checking

### Jina
- Multiple queries at once (~~batch_search — an array of up to 5 queries)
- Reading URLs (~~scrape — primary), several at once, or only the passages that answer a question
- Scientific preprints (arXiv, SSRN)
- Deduplication and relevance ranking

### Firecrawl
- JS-heavy pages (with waitFor)
- Crawling entire sites (~~crawl)
- Structured data extraction (~~extract with JSON schema)
- Code, GitHub issues and docs (~~code_search); scientific papers (~~academic_search)
- Autonomous agent for unknown URLs (~~deep_agent); browser sessions; screenshots

## Exhaustive Discovery Protocol

**CRITICAL**: When searching for a specific product, project, brand, or tool by name — ALWAYS run this protocol BEFORE concluding "not found".

### Step 1: Direct URL Probing

Try reading the project's likely homepage across ALL common domain zones:

```
For query "{Name}":
1. ~~scrape("https://{name}.com")
2. ~~scrape("https://{name}.ai")       ← CRITICAL for AI projects
3. ~~scrape("https://{name}.dev")
4. ~~scrape("https://{name}.io")
5. ~~scrape("https://{name}.app")
6. ~~scrape("https://{name}.org")
7. ~~scrape("https://{name}.co")
8. ~~scrape("https://{name}.sh")       ← for CLI tools

Run ALL. Most will fail — that's expected.
Even ONE success gives you the real homepage.
```

### Step 2: Platform-Specific Checks

```
GitHub:
- ~~scrape("https://github.com/{name}")
- ~~scrape("https://github.com/{name}/{name}")
- ~~search("{name} site:github.com")

Package registries:
- ~~scrape("https://www.npmjs.com/package/{name}")
- ~~scrape("https://pypi.org/project/{name}/")

Documentation:
- ~~scrape("https://docs.{name}.ai")
- ~~scrape("https://docs.{name}.dev")
```

### Step 3: Search Variations

```
1. Exact match:     "{Name}" (in quotes)
2. With context:    "{Name}" + domain keywords
3. Hyphenated:      "{name-name}" or "{name_name}"
4. GitHub search:   "{name}" site:github.com
5. Discussions:     "{name}" site:reddit.com OR site:news.ycombinator.com
```

### Step 4: Escalation

If Steps 1-3 all return empty:
```
1. ~~answer("What is {Name}? {context}") — Perplexity first
2. ~~search("{Name}") — try other providers
3. ~~search("{Name} twitter OR linkedin OR discord")
```

**NEVER conclude "not found" until ALL 4 steps are exhausted.**

### Minimum Discovery Attempts

| Query Type | Minimum Probes Before "Not Found" |
|-----------|----------------------------------|
| Product/Project name | 8 domain probes + 3 GitHub + 2 registry + 5 search = 18 |
| Company name | 5 domain probes + 3 search + Perplexity + Crunchbase = 10 |
| Person name | 3 search queries + Perplexity + LinkedIn search = 5 |
| Generic topic | 3 search queries across providers = 3 |

## Query Optimization

### Expanding queries
```
1. Think of related terms, synonyms and the field's own vocabulary — you do this yourself
2. Form 3-7 queries from different angles:
   - Direct: "RAG frameworks comparison"
   - Synonym: "retrieval augmented generation tools"
   - Comparison: "RAG vs fine-tuning"
   - Expert: "best RAG framework expert review"
   - Data: "RAG benchmark results 2026"
```

### Parallel Search Strategy
```
1. Think of related terms and synonyms
2. Form 3-5 queries from different angles (a batch holds at most 5)
3. ~~batch_search(queries) → batch results
4. Rank by relevance → top results
5. Deduplicate → remove duplicates
```

## Domain-Specific Search

Target specific domains based on research type:

| Research Type | Domain Strategy |
|--------------|----------------|
| Technical / Code | ~~search + `site:github.com` OR `site:stackoverflow.com` OR `site:dev.to` |
| Business / Market | ~~search + `site:crunchbase.com` OR `site:linkedin.com` OR `site:bloomberg.com` |
| Academic / Papers | ~~academic_search (arXiv, SSRN) |
| News / Trends | ~~search + date filter (last 3-6 months) + `site:techcrunch.com` OR `site:reuters.com` |
| Product / Company | Exhaustive Discovery Protocol (domain probes + GitHub + registries) |

Combine domain filtering with general search for broader coverage. Never rely on domain filtering alone.

## Exa Semantic Search

Exa provides meaning-based search (not keyword matching). The default search tool accepts only a query and a result count; a category goes inline in the query string, and only two inline categories exist:

| Inline category | What it finds | When to use |
|-----------------|--------------|-------------|
| `category:company` | Company profiles, about pages, team info | Person/Company Lookup |
| `category:people` | Professional profiles | Person/Company Lookup |
| (none) | Everything — semantic matching by meaning | Topic Deep Dive, general search |

Describe the ideal page, not keywords: "blog post comparing RAG frameworks", not "RAG frameworks".

**Filters live elsewhere.** Domain scoping, date windows and the other categories (`news`, `publication`, `pdf`, `github`, ...) need the opt-in advanced search tool (`category`, `includeDomains`, `startPublishedDate`, `type`: `auto`/`fast`/`instant`). If it is not enabled, use another provider for the same need:

| Need | Without the advanced Exa tool |
|------|-------------------------------|
| Recent news / date window | Perplexity search with a recency filter; Jina search with the age limit (`tbs`) |
| Only some domains | Perplexity search with a domain filter; Firecrawl search with `includeDomains` |
| Academic papers | `~~academic_search` |
| Code and GitHub | `~~code_search` |

**When Exa shines:**
- Finding conceptually similar content (not just keyword matches)
- Discovering competitors and alternatives
- Finding company/product information with structured context

## Error Handling

| Error | Action |
|-------|--------|
| Provider error | Try next provider in fallback chain |
| Empty results | Broaden query, try different provider |
| Rate limited | Try alternative provider immediately |
| Timeout | Try lighter alternative (map instead of crawl) |
| Invalid URL | Check URL, try ~~scrape with next provider |
| Content blocked | Try provider with proxy/stealth support |
