# firecrawl (Devin plugin)

DEPRECATED — superseded by web-search-dev, which covers the current Firecrawl MCP tools and REST API v2 alongside Exa, Perplexity, Jina and Context7; this plugin teaches tool names the official Firecrawl MCP server does not expose. Firecrawl web scraping and search plugin. Scrape URLs, crawl sites, search the web, map site structures, extract structured data, batch scraping, autonomous research agents, and cloud browser sessions via MCP tools.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (7)

- `agent-research` — Autonomous research agent — start complex web research tasks, get structured results. This skill should be used when the user asks for multi-site exploration, open-ended web research, or deep-dive analysis across multiple sources.
- `batch-operations` — Batch scraping — scrape multiple URLs in a single request with rate limiting and progress tracking. This skill should be used when the user asks to scrape multiple pages at once, process a list of URLs, or bulk extract content.
- `browser-sessions` — Cloud browser sessions — create sessions, execute code, interact with dynamic pages. This skill should be used when the user needs to interact with SPAs, handle authentication flows, or execute browser automation on JavaScript-heavy sites.
- `crawling` — Multi-page crawling and site mapping. This skill should be used when the user asks to crawl an entire website, map all URLs on a site, discover site structure, or scrape multiple pages from a domain.
- `examples` — Tool call patterns, end-to-end workflow examples, and scenario references. This skill should be used when the user needs reference implementations, complete examples, or tool call patterns.
- `scraping` — Single URL scraping — formats, selectors, wait strategies, headers. This skill should be used when the user asks to scrape a web page, get content from a URL, convert a page to markdown, or extract text from a site.
- `search-extract` — Web search and structured data extraction. This skill should be used when the user asks to search the web, extract structured data from pages into JSON, research a topic using online sources, or perform competitive analysis.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 7 command(s) — Devin plugins do not support commands
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/firecrawl
