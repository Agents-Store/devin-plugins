---
name: sdk-patterns
description: This skill should be used when the user asks about "Firecrawl SDK", "Exa SDK", "exa-js", "exa-py", "Perplexity SDK", "Jina SDK", "web search client library", "search npm package", "search Python package", or needs code patterns for integrating web search services into a project.
---

# Web Search Services SDK Patterns

Code patterns for integrating Firecrawl, Exa, Perplexity, and Jina into application code.

## Firecrawl

### Installation

```bash
npm install firecrawl     # Node.js (v4.x — package also published as @mendable/firecrawl-js)
pip install firecrawl-py  # Python (v4.x)
```

### TypeScript

```typescript
import { Firecrawl } from 'firecrawl';

const firecrawl = new Firecrawl({ apiKey: process.env.FIRECRAWL_API_KEY });

// Scrape a page
const result = await firecrawl.scrape('https://example.com', {
  formats: ['markdown', 'links'],
});
console.log(result.markdown);

// Search the web
const searchResults = await firecrawl.search('Next.js tutorials', { limit: 10 });

// Crawl a site (waiter — blocks until done)
const crawl = await firecrawl.crawl('https://docs.example.com', { limit: 50 });

// Or async: start + poll
const job = await firecrawl.startCrawl('https://docs.example.com', { limit: 50 });
const status = await firecrawl.getCrawlStatus(job.id);

// Map site URLs
const map = await firecrawl.map('https://example.com');

// Batch scrape
const batch = await firecrawl.batchScrape(['https://example.com/a', 'https://example.com/b'], {
  options: { formats: ['markdown'] },
});

// Extract structured data
const extracted = await firecrawl.extract({
  urls: ['https://example.com/pricing'],
  prompt: 'Extract pricing plans',
  schema: { type: 'array', items: { type: 'object', properties: { plan: { type: 'string' }, price: { type: 'string' } } } },
});
```

v4 also adds `interact()` / `stopInteraction()` for live browser-session page manipulation.

### Python

```python
from firecrawl import Firecrawl

firecrawl = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])

# Scrape (kwargs — no params dict in v4)
doc = firecrawl.scrape("https://example.com", formats=["markdown"])
print(doc.markdown)

# Search
results = firecrawl.search("Next.js tutorials", limit=10)

# Crawl
crawl = firecrawl.crawl("https://docs.example.com", limit=50)
```

---

## Exa

### Installation

```bash
npm install exa-js        # Node.js
pip install exa-py        # Python
```

### TypeScript

```typescript
import Exa from 'exa-js';

const exa = new Exa(process.env.EXA_API_KEY);

// Basic search
const results = await exa.search('React hooks best practices', {
  numResults: 10,
  type: 'auto',
});

// Search with content
const withContent = await exa.search('Prisma ORM examples', {
  numResults: 5,
  contents: {
    text: { maxCharacters: 5000 },
    highlights: { maxCharacters: 200 },
  },
});

// Domain-scoped search
const githubResults = await exa.search('authentication middleware', {
  numResults: 10,
  includeDomains: ['github.com'],
});

// Find similar pages
const similar = await exa.findSimilar('https://example.com/article', {
  numResults: 10,
});

// Direct answer with citations
const { answer } = await exa.answer('What changed in React 19 server components?');
// Streaming variants: exa.streamAnswer(...), exa.streamSearch(...)

// Agent API — multi-step research
const run = await exa.agent.runs.create({
  query: 'Compare the top 3 vector databases for a Next.js RAG app',
  effort: 'auto',
});
const finished = await exa.agent.runs.pollUntilFinished(run.id);
```

### Python

```python
from exa_py import Exa

exa = Exa(api_key=os.environ["EXA_API_KEY"])

# Search (Python uses snake_case for all params)
results = exa.search(
    "React hooks patterns",
    num_results=10,
    type="auto"
)

# Search with content
with_content = exa.search(
    "Prisma examples",
    num_results=5,
    contents={"text": {"max_characters": 5000}}
)
```

---

## Perplexity

### Installation

```bash
npm install @perplexity-ai/perplexity_ai  # Node.js
pip install perplexityai                    # Python
```

### TypeScript

```typescript
import { Perplexity } from '@perplexity-ai/perplexity_ai';

const client = new Perplexity({ apiKey: process.env.PERPLEXITY_API_KEY });

// Agent API (recommended) — client.responses namespace
const response = await client.responses.create({
  preset: 'low',
  input: 'Compare tRPC vs GraphQL for Next.js',
});

// Sonar API — OpenAI-style chat completions
const sonarResponse = await client.chat.completions.create({
  model: 'sonar-pro',
  messages: [
    { role: 'user', content: 'What are the latest React 19 features?' },
  ],
});

// Search API — ranked results, no AI answer
const searchResults = await client.search.create({
  query: 'React 19 new features',
  max_results: 5,
});
```

### Python

```python
from perplexity import Perplexity

client = Perplexity()  # auto-reads PERPLEXITY_API_KEY env var

# Agent API
response = client.responses.create(
    preset="low",
    input="Compare tRPC vs GraphQL for Next.js"
)

# Sonar API
sonar_response = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "React 19 features"}]
)

# Search API
search_results = client.search.create(query="React 19 new features", max_results=5)
```

---

## Jina

Jina's API is HTTP-based — no dedicated SDK package needed. Use `fetch` or `requests` directly.

### TypeScript

```typescript
// Read a URL
const response = await fetch('https://r.jina.ai/https://nextjs.org/docs', {
  headers: { 'Authorization': `Bearer ${process.env.JINA_API_KEY}` },
});
const markdown = await response.text();

// Search
const searchResponse = await fetch('https://s.jina.ai/?q=React+hooks', {
  headers: {
    'Authorization': `Bearer ${process.env.JINA_API_KEY}`,
    'Accept': 'application/json',
  },
});
const results = await searchResponse.json();

// Embeddings
const embedResponse = await fetch('https://api.jina.ai/v1/embeddings', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.JINA_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'jina-embeddings-v5-text-small',
    input: ['text to embed'],
  }),
});
```

### Python

```python
import requests

headers = {"Authorization": f"Bearer {os.environ['JINA_API_KEY']}"}

# Read a URL
response = requests.get("https://r.jina.ai/https://example.com", headers=headers)
markdown = response.text

# Search
search = requests.get(
    "https://s.jina.ai/",
    params={"q": "React hooks"},
    headers={**headers, "Accept": "application/json"}
)
results = search.json()

# Rerank
rerank = requests.post(
    "https://api.jina.ai/v1/rerank",
    headers={**headers, "Content-Type": "application/json"},
    json={
        "model": "jina-reranker-v3.5",
        "query": "best database for real-time",
        "documents": ["PostgreSQL", "Redis", "MongoDB"]
    }
)
```

---

## Best Practices

- Store API keys in environment variables, never in code
- Handle rate limits with exponential backoff
- Use the appropriate service for each task (see mcp-patterns routing table)
- Prefer SDK methods over raw HTTP when SDK is available
- Use TypeScript types for type safety when integrating search results
