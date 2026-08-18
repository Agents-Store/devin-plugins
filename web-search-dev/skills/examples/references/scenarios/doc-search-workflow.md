# Scenario: Find Framework Docs While Coding

You're building a Next.js app and encounter a hydration error. You need to find the current documentation to understand and fix it.

## Step 1: Search Context7 for Official Docs

```
Tool: resolve-library-id
Input: { "libraryName": "nextjs" }
→ Returns: "/vercel/next.js"

Tool: query-docs
Input: {
  "libraryId": "/vercel/next.js",
  "query": "hydration mismatch error causes and solutions"
}
```

Context7 returns relevant documentation sections with code examples from the current Next.js version.

## Step 2: Get AI-Powered Explanation

If Context7 docs don't fully explain the issue:

```
Tool: perplexity_reason
Input: {
  "query": "Next.js hydration mismatch error: server renders 'March 29' but client renders '03/29/2025'. Why does this happen with date formatting and how to fix it?"
}
```

Perplexity Reasoning provides step-by-step analysis with citations.

## Step 3: Search the Developer Index

Search GitHub issues, PRs, READMEs, and docs for how others solved similar issues:

```
Tool: firecrawl_developer_search
Input: {
  "query": "Next.js hydration mismatch date formatting fix"
}
```

## Step 4: Read the Most Helpful Result

```
Tool: read_url
Input: { "url": "<best_result_url_from_step_3>" }
```

## Result

Combining these sources, you find that:
1. The error occurs because `toLocaleDateString()` produces different output on server (Node) vs client (browser)
2. Fix: use a consistent date formatting library or suppress hydration with `suppressHydrationWarning`
3. Better fix: format dates in a `useEffect` or use `Intl.DateTimeFormat` with explicit locale

## When to Use Each Service

| Situation | Best Service |
|-----------|-------------|
| Known library, need current docs | Context7 |
| Need to understand an error | Perplexity (reason) |
| Find code examples and patterns | Firecrawl (developer_search) or Exa (domain-scoped web_search_advanced_exa) |
| Read a specific docs page | Jina (read_url) |
| Quick "how do I" question | Perplexity (ask) |
