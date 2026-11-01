# dataforseo-dev (Devin plugin)

DataForSEO data for SEO work — keywords, SERP, backlinks, on-page, AI visibility — through the v3 MCP server. Not a general web-search tool.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (11)

- `ai-optimization` — This skill should be used when the user asks about "AI optimization", "LLM mentions", "ChatGPT visibility", "AI search", "LLM ranking", "brand mentions in AI", "AI SEO", "GEO", "generative engine optimization", "AI Overview mentions", or needs to track and improve visibility in AI-powered search using DataForSEO.
- `api-reference` — This skill should be used when the user asks for "DataForSEO API endpoints", "DataForSEO REST API", "DataForSEO curl examples", "DataForSEO API documentation", "DataForSEO HTTP requests", or needs specific HTTP endpoint details for DataForSEO.
- `backlink-audit` — This skill should be used when the user asks about "backlink audit", "backlink analysis", "link profile", "toxic links", "referring domains", "link building", "backlink prospecting", "disavow list", "spam score", or needs to analyze backlink profiles using DataForSEO.
- `competitor-analysis` — Use for competitor SEO research with DataForSEO Labs data - who competes for the same organic keywords, who ranks in the top 10 for a query, how domains compare on organic traffic, keywords and trend, a competitor's top pages, and keyword or domain gaps. Not for keyword ideation (keyword-research), backlink audits (backlink-audit) or page audits (site-audit).
- `cost-awareness` — Use as the budget gate before the first paid DataForSEO api_request of a task, after the task skill has chosen its endpoints, and for any question about DataForSEO pricing - what a call costs, which calls are free, how to estimate or cap spend, how to check the account balance, and how to keep a bill small with bulk endpoints and explicit limit or depth.
- `examples` — This skill should be used when the user asks for "DataForSEO examples", "DataForSEO workflows", "SEO analysis example", "show me how to use DataForSEO", or needs complete end-to-end scenario walkthroughs for SEO data analysis with DataForSEO.
- `keyword-research` — This skill should be used when the user asks about "keyword research", "find keywords", "keyword ideas", "search volume", "keyword difficulty", "long-tail keywords", "keyword gap analysis", "keyword strategy", or needs to discover and evaluate keywords using DataForSEO.
- `mcp-patterns` — Use for how to call the DataForSEO MCP server - its tools (api_request, docs_search, docs_index, docs_list_sections), the docs-first cycle, request bodies and the .ai response mode - and to build the right call for an endpoint family without a task skill, such as SERP, Merchant, App Data or Business Data. Not for site audits, content analysis, page parsing, technologies or WHOIS (site-audit).
- `setup` — This skill should be used when the user asks to "verify DataForSEO connection", "check DataForSEO MCP", "test DataForSEO setup", "is DataForSEO working", "set up DataForSEO credentials", or needs to confirm that the DataForSEO MCP integration is operational.
- `site-audit` — Use for page and site inspection with DataForSEO OnPage, Content Analysis and Domain Analytics - Lighthouse and page speed, on-page SEO checks (title, meta, headings, alt text), site crawls, parsing a page's content, content and sentiment analysis for a keyword, the technologies a domain runs, and WHOIS data. Not for backlinks (backlink-audit), competitor comparison (competitor-analysis) or keyword research.
- `troubleshoot` — This skill should be used when the user encounters "DataForSEO errors", "DataForSEO not working", "DataForSEO connection issues", "debug DataForSEO", "DataForSEO MCP problems", "tool not found" for a DataForSEO tool, or needs to diagnose and fix common problems with the DataForSEO MCP server.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 3 command(s) — Devin plugins do not support commands
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/dataforseo-dev
