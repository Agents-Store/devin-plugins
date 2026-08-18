# Scenario: Topic Deep Dive

**Query:** "Как работает vector search — подробное объяснение"
**Type:** Topic Deep Dive
**Depth:** deep
**Template:** Deep Research Report

## Step-by-Step Execution

### Step 1: CLASSIFY
```
Signals: "как работает", "подробное объяснение" → Topic Deep Dive
Depth: deep
```

### Step 2: PLAN
```
expand_query({ query: "vector search how it works" })

Queries:
1. "vector search explained how it works"
2. "vector embeddings similarity search fundamentals"
3. "vector database architecture HNSW IVF"
4. "ANN approximate nearest neighbor algorithms comparison"
5. "vector search vs keyword search comparison"
6. "vector search production use cases applications"
7. "vector search performance optimization scaling"
```

### Step 3: SEARCH
```
~~batch_search([
  "vector search how it works explained",
  "vector embeddings similarity algorithms",
  "HNSW IVF vector index comparison",
  "vector database architecture production"
])

~~academic_search("approximate nearest neighbor search vector")

~~code_search("vector search implementation example")

~~search("how does vector search work comprehensive explanation")
```

### Step 4: READ
```
Rank by relevance("vector search explanation", all_urls)
~~batch_scrape(top_8_urls)
Extract PDF from best arXiv paper
```

### Step 5: EXTRACT
```
From each source:
- Core concepts (embeddings, similarity metrics, indexing)
- Algorithm comparisons (brute force, HNSW, IVF, PQ)
- Performance characteristics (speed, accuracy, memory)
- Real-world use cases
- Code examples
- Visual explanations / diagrams descriptions
```

### Step 6: SYNTHESIZE
```
deduplicate_strings(concepts)
Build logical flow: concepts → algorithms → implementations → use cases
Cross-reference algorithm benchmarks
Identify knowledge progression (beginner → advanced)
```

### Step 7: REPORT
Output: Deep Research Report with:
- Executive Summary
- Background (why vector search matters)
- Findings:
  - Core concepts (embeddings, distance metrics)
  - Indexing algorithms (HNSW, IVF, PQ)
  - Vector databases comparison
  - Production considerations
- Data & Metrics (performance benchmarks)
- Code examples
- Use cases
- Gaps & Limitations
- Methodology

### Expected Capabilities Used
`~~batch_search`, `~~academic_search`, `~~code_search`, `~~search`, `~~batch_scrape`, query expansion, PDF extraction, relevance ranking, deduplication
