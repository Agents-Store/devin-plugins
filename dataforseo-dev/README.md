# dataforseo-dev (Devin plugin)

DataForSEO data for SEO work — keywords, SERP, backlinks, on-page, AI visibility — through the v3 MCP server. Not a general web-search tool.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (11)

- `ai-optimization` — This skill should be used when the user asks about "AI optimization", "LLM mentions", "ChatGPT visibility", "AI search", "LLM ranking", "brand mentions in AI", "AI SEO", "GEO", "generative engine optimization", "AI Overview mentions", or needs to track and improve visibility in AI-powered search using DataForSEO.
- `api-reference` — This skill should be used when the user asks for "DataForSEO API endpoints", "DataForSEO REST API", "DataForSEO curl examples", "DataForSEO API documentation", "DataForSEO HTTP requests", or needs specific HTTP endpoint details for DataForSEO.
- `backlink-audit` — This skill should be used when the user asks about "backlink audit", "backlink analysis", "link profile", "toxic links", "referring domains", "link building", "backlink prospecting", "disavow list", "spam score", or needs to analyze backlink profiles using DataForSEO.
- `competitor-analysis` — This skill should be used when the user asks about "competitor analysis", "competitor research", "domain comparison", "who ranks for", "competitive landscape", "competitor keywords", "competitor traffic", or needs to analyze and compare domains using DataForSEO.
- `cost-awareness` — This skill should be used before any paid DataForSEO call, and when the user asks about "DataForSEO cost", "DataForSEO pricing", "how much will this cost", "DataForSEO budget", "credits", "billing", or wants to keep DataForSEO spending under control.
- `examples` — This skill should be used when the user asks for "DataForSEO examples", "DataForSEO workflows", "SEO analysis example", "show me how to use DataForSEO", or needs complete end-to-end scenario walkthroughs for SEO data analysis with DataForSEO.
- `keyword-research` — This skill should be used when the user asks about "keyword research", "find keywords", "keyword ideas", "search volume", "keyword difficulty", "long-tail keywords", "keyword gap analysis", "keyword strategy", or needs to discover and evaluate keywords using DataForSEO.
- `mcp-patterns` — This skill should be used when the user asks about "DataForSEO MCP tools", "api_request", "docs_search", "which DataForSEO endpoint", "how to call DataForSEO", "DataForSEO request body", "DataForSEO .ai mode", or needs to turn an SEO data task into the right DataForSEO API call through the MCP server.
- `setup` — This skill should be used when the user asks to "verify DataForSEO connection", "check DataForSEO MCP", "test DataForSEO setup", "is DataForSEO working", "set up DataForSEO credentials", or needs to confirm that the DataForSEO MCP integration is operational.
- `site-audit` — This skill should be used when the user asks about "site audit", "on-page audit", "lighthouse audit", "page speed", "technical SEO audit", "crawl site", "page analysis", "content analysis", "technology detection", or needs to analyze website pages and content using DataForSEO.
- `troubleshoot` — This skill should be used when the user encounters "DataForSEO errors", "DataForSEO not working", "DataForSEO connection issues", "debug DataForSEO", "DataForSEO MCP problems", "tool not found" for a DataForSEO tool, or needs to diagnose and fix common problems with the DataForSEO MCP server.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 3 command(s) — Devin plugins do not support commands
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/dataforseo-dev
