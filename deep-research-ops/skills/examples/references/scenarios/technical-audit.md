# Scenario: Technical Audit

**Query:** "Архитектура RAG pipeline — best practices и сравнение подходов"
**Type:** Technical Audit
**Depth:** deep
**Template:** Deep Research Report

## Step-by-Step Execution

### Step 1: CLASSIFY
```
Signals: "архитектура", "best practices", "сравнение подходов" → Technical Audit
Depth: deep (architecture analysis)
```

### Step 2: PLAN
```
IF topic is a specific named tool/framework/product:
  → Run Exhaustive Discovery Protocol FIRST
  → Probe: {name}.com, {name}.ai, {name}.dev, {name}.io, github.com/{name}/{name},
    npmjs.com/package/{name}, pypi.org/project/{name}, docs.{name}.ai
  → Use discovered URLs as primary sources

expand_query({ query: "RAG pipeline architecture" })

Queries:
1. "RAG pipeline architecture components design"
2. "retrieval augmented generation best practices 2026"
3. "RAG vs fine-tuning comparison"
4. "RAG chunking strategies embedding models"
5. "RAG performance benchmarks evaluation"
6. "production RAG system architecture patterns"
7. "advanced RAG techniques agentic RAG"
```

### Step 3: SEARCH
```
~~code_search("RAG pipeline implementation architecture")
→ Code examples and technical context

~~academic_search("retrieval augmented generation architecture evaluation")
→ Academic papers

~~batch_search([
  "RAG best practices production 2026",
  "RAG chunking strategies comparison",
  "RAG evaluation metrics benchmarks"
])

~~search("current state of RAG architecture best practices 2026")
```

### Step 4: READ
```
Rank by relevance("RAG architecture best practices", all_urls)
~~batch_scrape(top_8_urls)

Extract PDF from arxiv paper → full paper text for key papers
```

### Step 5: EXTRACT
```
From each source:
- Architecture patterns (naive RAG, advanced RAG, modular RAG)
- Component comparisons (chunkers, embeddings, retrievers, rerankers)
- Performance metrics
- Code patterns and examples
- Failure modes and solutions
```

### Step 6: SYNTHESIZE
```
deduplicate_strings(facts)
Compare architecture approaches across sources
Map consensus vs emerging patterns
Identify implementation trade-offs
```

### Step 7: REPORT
Output: Deep Research Report with:
- Architecture overview (diagram description)
- Component comparison tables
- Best practices per component
- Performance benchmarks
- Code examples
- Common pitfalls
- Recommendations by use case
- Academic references
- Methodology

### Expected Capabilities Used
`~~code_search`, `~~academic_search`, `~~batch_search`, `~~search`, `~~batch_scrape`, PDF extraction, relevance ranking, deduplication
