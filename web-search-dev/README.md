# web-search-dev (Devin plugin)

Developer reference for web search, scraping and documentation lookup — Firecrawl, Exa, Jina, Perplexity, Context7 MCP tools and REST/SDK/CLI — plus Pexels and Unsplash REST media search.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (10)

- `api-reference` — This skill should be used when the user asks for "Firecrawl API endpoints", "Exa REST API", "Perplexity API reference", "Jina API curl examples", "web search API documentation", or needs specific HTTP endpoint details for any of the web search and scraping services.
- `cli-recipes` — This skill should be used when the user asks about "firecrawl CLI", "jina CLI", "firecrawl command line", "jina command line", "scrape from terminal", "search from shell", or needs ready-to-use CLI commands for web scraping and search.
- `doc-search` — This skill should be used when the user asks to "find docs", "search documentation", "look up API reference", "find framework docs", "check Next.js docs", "search React docs", "find current docs for a library", or needs to find up-to-date documentation for a framework, library, or service while developing.
- `examples` — This skill should be used when the user asks for "web search examples", "scraping examples", "show me how to use search tools", "search workflow examples", or needs end-to-end scenario walkthroughs for web search and scraping development tasks.
- `mcp-patterns` — This skill should be used when the user asks about "web search MCP tools", "which search tools are available", "firecrawl tools", "exa tools", "jina tools", "perplexity tools", "how to use search MCP", "scraping MCP tools", "media search tools", or needs to know which MCP operations are available across web search and scraping services. Also triggers when doing any web research, URL fetching, or page content extraction — including during planning, exploration, or data source analysis.
- `media-search` — This skill should be used when the user asks to "find images", "search photos", "find stock photos", "search videos", "find media for app", "get stock images", "find pictures for website", "Pexels API", "Unsplash API", or needs to find images, videos, or other media content for their application or website.
- `sdk-patterns` — This skill should be used when the user asks about "Firecrawl SDK", "Exa SDK", "exa-js", "exa-py", "Perplexity SDK", "Jina SDK", "web search client library", "search npm package", "search Python package", or needs code patterns for integrating web search services into a project.
- `setup` — This skill should be used when the user asks to "verify web search setup", "check search services", "test firecrawl connection", "test exa connection", "is jina working", "check perplexity MCP", or needs to confirm which web search and scraping services are operational.
- `troubleshoot` — This skill should be used when the user encounters "search not working", "scrape failing", "firecrawl error", "exa error", "jina error", "perplexity error", "rate limit", "401 unauthorized", "MCP connection failed", or needs to diagnose and fix problems with any web search or scraping service.
- `web-scraping` — This skill should be used when the user asks to "scrape a website", "extract content from URL", "crawl a site for data", "parse website content", "build a scraper", "extract product data", "scrape for my app", or needs to extract web content for their application or data pipeline. Also use when researching external data sources, analyzing websites for data availability, or fetching page content during planning — any task that involves reading web page content should use MCP scraping tools (firecrawl, jina, exa) instead of basic WebFetch.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/web-search-dev
