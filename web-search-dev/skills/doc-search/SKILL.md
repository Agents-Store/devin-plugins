---
name: doc-search
description: This skill should be used when the user asks to "find docs", "search documentation", "look up API reference", "find framework docs", "check Next.js docs", "search React docs", "find current docs for a library", or needs to find up-to-date documentation for a framework, library, or service while developing.
---

# Documentation Search for Development

Find current, accurate documentation for any framework, library, or service.

## Mandatory First Step: Context7

For ANY question about a known framework or library (React, Next.js, Prisma, Tailwind, Vue, etc.), ALWAYS start with Context7. It returns indexed, up-to-date documentation — faster and more accurate than general web search. Skip Context7 only if the tool/library is unknown or Context7 doesn't resolve it.

```
Step 1 — Resolve library:
Tool: resolve-library-id
Input: { "libraryName": "nextjs" }
→ Returns: "/vercel/next.js"

Step 2 — Query docs:
Tool: query-docs
Input: {
  "libraryId": "/vercel/next.js",
  "query": "useSearchParams suspense boundary error"
}
→ Returns: current documentation sections with code examples
```

If Context7 resolves the library, use its results as the primary source. Supplement with other services only if you need additional context (community examples, debugging explanations, multiple pages).

## Strategy: Choose by Need

| Need | Best Approach | Tool |
|------|--------------|------|
| Official docs for a known library | **Context7 first (mandatory)** | `resolve-library-id` → `query-docs` |
| Find docs for unfamiliar tool | Exa semantic search | `web_search_exa` (or `web_search_advanced_exa` for domain scoping) |
| Quick answer to "how do I..." | Context7 first, then Perplexity | `query-docs` → `perplexity_ask` |
| Read a specific docs page | Jina reader | `read_url` |
| Debug error with framework | Context7 first, then Perplexity | `query-docs` → `perplexity_reason` |
| Find code examples | Firecrawl developer index | `firecrawl_developer_search` (fallback: `web_search_advanced_exa` with `includeDomains: ["github.com"]`) |

## Pattern 1: Context7 — Primary for All Known Libraries

ALWAYS use Context7 first when the library name is known. This is the fastest path to accurate, current documentation.

```
Step 1 — Resolve library:
Tool: resolve-library-id
Input: { "libraryName": "nextjs" }
→ Returns: "/vercel/next.js"

Step 2 — Query docs:
Tool: query-docs
Input: {
  "libraryId": "/vercel/next.js",
  "query": "How to implement middleware for authentication"
}
```

Context7 returns documentation sections with code examples from the **current version**. Ideal for:
- API signatures that change between versions
- Migration guides
- Best practices from official docs

## Pattern 2: Exa Semantic Search — Best for Discovery

Use when exploring documentation across multiple sources.

```
Tool: web_search_exa
Input: {
  "query": "Prisma ORM connection pooling configuration",
  "numResults": 10
}
```

Note: `web_search_exa` accepts only `query` and `numResults`. Domain filters require `web_search_advanced_exa`, an opt-in tool enabled via the remote MCP URL's `tools` parameter (see `mcp-patterns/references/exa-tools.md`).

### Domain-Scoped Doc Search

```
Tool: web_search_advanced_exa
Input: {
  "query": "server actions form validation",
  "numResults": 10,
  "includeDomains": ["nextjs.org", "react.dev"]
}
```

### Find Code Examples

```
Tool: firecrawl_developer_search
Input: {
  "query": "TypeScript Prisma middleware logging example"
}
```

Searches the developer index (GitHub issues, merged PRs, READMEs, docs). Fallback:

```
Tool: web_search_advanced_exa
Input: {
  "query": "TypeScript Prisma middleware logging example",
  "includeDomains": ["github.com"],
  "numResults": 5
}
```

## Pattern 3: Perplexity — Best for Quick Answers

Use for "how do I" questions and debugging.

### Quick How-To

```
Tool: perplexity_ask
Input: { "query": "How to set up Tailwind CSS v4 in Next.js 15" }
```

### Debug a Framework Error

```
Tool: perplexity_reason
Input: { "query": "Next.js error: 'useSearchParams() should be wrapped in a suspense boundary'. What causes this and how to fix it?" }
```

### Compare Approaches

```
Tool: perplexity_search
Input: { "query": "Server Components vs Client Components data fetching patterns Next.js 15" }
```

## Pattern 4: Read Specific Docs Page

When you have a URL and need its content:

```
Tool: read_url
Input: { "url": "https://nextjs.org/docs/app/api-reference/functions/use-router" }
```

### Read Multiple Doc Pages

```
Tool: parallel_read_url
Input: { "urls": [
  "https://react.dev/reference/react/use",
  "https://react.dev/reference/react/useActionState",
  "https://react.dev/reference/react/useOptimistic"
]}
```

## Pattern 5: Combined Workflow — Deep Doc Research

For complex questions that need multiple sources:

```
Step 1 — Get official docs:
Tool: resolve-library-id + query-docs

Step 2 — Search for community patterns:
Tool: web_search_advanced_exa (with GitHub/StackOverflow domains)

Step 3 — Get AI summary:
Tool: perplexity_search

Step 4 — Read the most relevant pages:
Tool: parallel_read_url (with top URLs from steps 1-3)
```

## Common Documentation Domains

For domain-scoped search with Exa (`web_search_advanced_exa`):

| Framework | Domains |
|-----------|---------|
| React | `react.dev` |
| Next.js | `nextjs.org` |
| Vue | `vuejs.org` |
| Svelte | `svelte.dev` |
| Prisma | `prisma.io` |
| Tailwind | `tailwindcss.com` |
| TypeScript | `typescriptlang.org` |
| Node.js | `nodejs.org` |
| Python | `docs.python.org` |
| Django | `docs.djangoproject.com` |

## Best Practices

- **Context7 first, always** — for any known library, resolve + query Context7 before trying other services. It returns current, indexed docs faster than web search.
- Fall back to Exa when searching across multiple doc sites or for unfamiliar tools
- Use Perplexity to supplement Context7 with AI explanations, especially for debugging
- Always verify AI-generated answers against official docs (Context7 or direct page reads)
- For version-specific questions, include the version in your query
- Combine multiple sources for complex topics — Context7 for facts, Perplexity for explanations, Exa for community patterns
