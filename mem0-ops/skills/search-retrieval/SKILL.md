---
name: search-retrieval
description: Search and retrieval — semantic search, listing, filtering, and relevance tuning. This skill should be used when the user asks to find memories, search knowledge, list stored information, or tune search results.
---

# Search & Retrieval

Semantic search and memory retrieval patterns — finding, filtering, and tuning results.

## Available Tools

| Tool | Purpose | Required Params |
|------|---------|----------------|
| search_memories | Semantic search by query | query |
| get_all_memories | List all memories | — |
| get_memory | Get single memory by ID | memory_id |

## Semantic Search

Tool: `search_memories`

```
search_memories({
  query: "database migration strategy",
  user_id: "project-alpha",
  threshold: 0.7,
  top_k: 10,
  filters: {"category": "infrastructure"}
})
```

### Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | Yes | Natural language search query |
| user_id | string | No | Scope to user |
| agent_id | string | No | Scope to agent |
| app_id | string | No | Scope to app |
| run_id | string | No | Scope to run |
| filters | object | No | Metadata filter criteria |
| threshold | float | No | Min relevance score (0.0-1.0) |
| top_k | int | No | Max results to return |

### Threshold Guide

| Threshold | Use Case |
|-----------|----------|
| 0.0 - 0.3 | Very broad — returns loosely related results |
| 0.4 - 0.6 | Balanced — good default for exploration |
| 0.7 - 0.9 | Precise — only highly relevant results |
| 0.9 - 1.0 | Exact — near-exact matches only |

## Listing All Memories

Tool: `get_all_memories`

```
get_all_memories({
  user_id: "project-alpha",
  page: 1,
  page_size: 50
})
```

### Paginating Through All Memories
```
Step 1: get_all_memories(user_id, page=1, page_size=50) -> first 50
Step 2: get_all_memories(user_id, page=2, page_size=50) -> next 50
Step 3: Continue until empty results
```

## Search Strategies

### Broad Discovery
Find anything related to a topic:
```
search_memories({
  query: "authentication",
  top_k: 20,
  threshold: 0.3
})
```

### Precise Lookup
Find specific information:
```
search_memories({
  query: "PostgreSQL connection string for production",
  top_k: 3,
  threshold: 0.8
})
```

### Scoped Search
Search within a specific context:
```
search_memories({
  query: "API endpoints",
  user_id: "project-alpha",
  filters: {"category": "api"}
})
```

### Multi-Query Search
When one query isn't enough, try multiple angles:
```
1. search_memories(query="auth middleware") -> results A
2. search_memories(query="JWT token validation") -> results B
3. search_memories(query="session management") -> results C
4. Combine and deduplicate results
```

## Common Workflows

### Find Relevant Context
```
1. search_memories(query) -> get matching memories
2. Review results and relevance scores
3. get_memory(best_match_id) -> get full details if needed
```

### Comprehensive Audit
```
1. get_all_memories(user_id, page=1) -> start paginating
2. Continue through all pages
3. Categorize and report on memory contents
```

### Duplicate Detection
```
1. search_memories(query, top_k=10, threshold=0.9)
2. Compare results for near-duplicates
3. Flag for cleanup via batch_delete_memories
```

### Knowledge Gap Analysis
```
1. Define expected topics list
2. search_memories(topic) for each topic
3. Report which topics have coverage vs gaps
```

## Tuning Tips

1. **Start broad, narrow down** — begin with low threshold and high top_k
2. **Rephrase queries** — try different wording for better semantic matching
3. **Use scoping** — user_id/agent_id reduces noise in multi-tenant setups
4. **Combine search + list** — search for specific topics, list for full audits
5. **Use filters** — metadata filters complement semantic search
6. **Check scores** — low relevance scores suggest poor query match, try rephrasing

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Empty results | Wrong scope or too high threshold | Lower threshold, check user_id |
| Irrelevant results | Query too broad | Be more specific, raise threshold |
| Too many results | No top_k limit | Set top_k to limit volume |
| Missing memories | Wrong user_id/agent_id scope | Verify correct scope identifier |
