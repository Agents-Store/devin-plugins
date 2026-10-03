---
name: cli-recipes
description: This skill should be used when the user asks about "firecrawl CLI", "jina CLI", "firecrawl command line", "jina command line", "scrape from terminal", "search from shell", or needs ready-to-use CLI commands for web scraping and search.
---

# Web Search CLI Recipes

CLI commands for Firecrawl and Jina — the two services with official CLIs.

## Firecrawl CLI

### Installation

```bash
npm install -g firecrawl-cli
# or run without install:
npx -y firecrawl-cli@latest
```

### Authentication

```bash
firecrawl login                        # Interactive (browser by default)
firecrawl login --method browser       # Browser-based login
firecrawl login --api-key fc-YOUR_KEY  # Direct key
export FIRECRAWL_API_KEY=fc-YOUR_KEY   # Or via environment variable
firecrawl view-config        # Show current auth/config
firecrawl logout             # Sign out
```

### Scrape a Page

```bash
firecrawl https://example.com/page
firecrawl scrape https://example.com/page --format markdown,links
firecrawl scrape https://example.com/spa --wait-for 3000  # JS rendering
firecrawl scrape https://example.com --screenshot  # Capture screenshot
firecrawl scrape https://example.com -o output.md  # Save to file
firecrawl scrape https://example.com --json --pretty  # JSON output
# Structured data from one page (JSON format + schema)
firecrawl scrape https://example.com/pricing --format json --schema-file schema.json -o pricing.json --pretty
```

### Search the Web

```bash
firecrawl search "Next.js server components tutorial"
firecrawl search "React hooks" --limit 20
firecrawl search "TypeScript patterns" --scrape  # Search + scrape results
firecrawl search "AI news" --tbs qdr:d  # Last 24 hours
firecrawl search "tech startups" --location "San Francisco"
firecrawl search "axum middleware ordering" --categories developer  # Developer index next to web results
```

### Crawl a Site

```bash
firecrawl crawl https://docs.example.com --wait --progress
firecrawl crawl https://docs.example.com --limit 50 --max-depth 3
firecrawl crawl https://docs.example.com --include-paths "/docs/*"
firecrawl crawl https://docs.example.com --exclude-paths "/blog/*"
firecrawl crawl JOB_ID  # Check existing crawl status
```

### Map Site URLs

```bash
firecrawl map https://example.com
firecrawl map https://example.com --limit 200
firecrawl map https://example.com --include-subdomains   # (--allow-subdomains belongs to `crawl`)
```

### Autonomous Agent

```bash
firecrawl agent "Find top 5 headless CMS and compare pricing"
firecrawl agent "Research React state management libraries" --wait
firecrawl agent "Find API rate limits" --urls https://docs.example.com --schema-file schema.json --wait
firecrawl agent "Compare pricing of the top 3 CMS" --effort medium --max-credits 200 --wait   # cap the spend
firecrawl agent JOB_ID --wait   # Check or wait for an existing job
```

Agent tasks take minutes and spend credits — set `--max-credits`.

### Interact (live browser)

Drive dynamic pages with natural language or code. `interact` works on the **last scrape** (or a scrape id with `-s`), so scrape first:

```bash
firecrawl scrape https://example.com/login          # 1. scrape the page
firecrawl interact "log in and open the dashboard"  # 2. act on it (prompt)
firecrawl interact -c "await page.title()"          # code (Node/Playwright by default; --python, --bash)
firecrawl interact -s SCRAPE_ID "extract the table" # target a specific scrape
firecrawl interact stop                             # 3. close the session
```

Persist logins between scrapes with `--profile <name>` on `firecrawl scrape`.

### Monitor Changes

Recurring scrapes with change detection:

```bash
firecrawl monitor create --name "Pricing" \
  --goal "Notify me when plans or prices change" \
  --schedule "every 30 minutes" \
  --page https://example.com/pricing
firecrawl monitor list
firecrawl monitor run MONITOR_ID
firecrawl monitor checks MONITOR_ID
firecrawl monitor update MONITOR_ID --state paused
```

Advanced targets (JSON-mode change tracking) go in a JSON file: `firecrawl monitor create monitor.json`. Monitors schedule future network calls — confirm before creating one.

### Developer Index Search

Search GitHub issues, PRs, READMEs, and docs:

```bash
firecrawl developer "nextjs hydration mismatch"
firecrawl developer "tokio select cancellation safety" --limit 10 --json
```

Research papers and credits:

```bash
firecrawl research search-papers "large language models" --json
firecrawl credit-usage
firecrawl --status    # version, auth, concurrency, credits
```

### Useful Flags

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON |
| `--pretty` | Pretty-print JSON |
| `-o FILE` | Save output to file |
| `--timing` | Show request timing |
| `--only-main-content` | Strip boilerplate |
| `--api-key KEY` | Override API key |

---

## Jina CLI

### Installation

```bash
pip install jina-cli
# or
uv pip install jina-cli
```

### Authentication

```bash
export JINA_API_KEY=jina_xxx
```

### Read a Page

```bash
jina read https://example.com/page
jina read https://example.com --json  # Structured output
```

### Search the Web

```bash
jina search "React hooks best practices"
jina search "React hooks" -n 10  # Number of results
jina search "AI news" --time d   # Past day (d/w/m)
jina search "tech" --gl us --hl en  # Geo/language targeting
```

### Specialized Search

```bash
jina search "transformer models" --arxiv   # Search arXiv
jina search "financial analysis" --ssrn    # Search SSRN
jina search "UI components" --images       # Image search
jina search "Jina releases" --blog         # Jina blog
```

### Text Processing

```bash
jina embed "text to embed"
jina rerank "query" < documents.txt
jina classify "product review text" --labels positive,negative,neutral
jina dedup < urls.txt  # Deduplicate
```

### Utilities

```bash
jina screenshot https://example.com -o screenshot.png
jina screenshot https://example.com --full-page
jina bibtex "attention is all you need"
jina expand "machine learning optimization"
jina pdf https://arxiv.org/pdf/2301.00001 --type figure,table
jina datetime https://example.com/article  # Guess publish date
```

### Pipe Composability

Jina CLI follows Unix philosophy — pipe commands together:

```bash
# Search and rerank
jina search "transformer models" | jina rerank "efficient inference"

# Read multiple URLs
cat urls.txt | jina read

# Search and deduplicate
jina search "attention mechanism" | jina dedup

# Search, read, and save
jina search "React patterns" -n 5 | jina read > research.md
```

### Local Mode (Apple Silicon)

Run embed, rerank, classify, and dedup locally without API key:

```bash
pip install jina-grep
jina grep serve start  # Start local embedding server
jina embed --local "hello world"
jina classify --local "text" --labels positive,negative
```

**Caveat:** `jina-grep` is not currently published on PyPI, so `pip install jina-grep` fails as of 2026-08 (upstream `jina-cli` docs give this same instruction; an npm package named `jina-grep` exists but is an empty placeholder). Check https://github.com/jina-ai/jina-grep-cli for the actual install method before relying on local mode.

### Useful Flags

| Flag | Description |
|------|-------------|
| `--json` | Structured JSON output |
| `-n NUM` | Number of results |
| `--time d/w/m` | Time filter (day/week/month) |
| `--gl CODE` | Geographic location |
| `--local` | Run locally (Apple Silicon) |

---

## Cross-CLI Workflow Examples

### Scrape and process content pipeline

```bash
# Use Firecrawl to find URLs, Jina to process
firecrawl map https://docs.example.com --json | \
  jq -r '.urls[]' | \
  head -10 | \
  while read url; do jina read "$url"; done > all_docs.md
```

### Search with both engines and compare

```bash
firecrawl search "React server components" --json > firecrawl_results.json
jina search "React server components" --json > jina_results.json
```
