# deep-research-ops (Devin plugin)

Multi-step research workflow over any search MCP servers; installs web-search-dev for the tools.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (5)

- `content-extraction` — Content reading and extraction guidelines — reading URLs, scraping pages, crawling sites, extracting PDFs, and taking screenshots. Use when reading web content, extracting structured data from pages, or processing documents.
- `deep-research` — Main research automation skill. 7-step algorithm for comprehensive research with 6 research types, query planning, parallel search, extraction, synthesis, and structured reporting. Use when conducting any multi-step research task.
- `examples` — Tool call patterns, end-to-end research workflow examples, and scenario references for all 6 research types. Use when you need reference implementations or complete research examples.
- `report-generation` — Report templates and generation guidelines — Executive Summary, Deep Research Report, and Comparison Table formats with methodology and citation rules. Use when formatting research results into structured reports.
- `search-strategies` — Search strategy guidelines — tool selection, fallback chains, query optimization, and parallel search orchestration. Use when choosing which search tools to use, handling tool failures, or optimizing search queries.

## Not carried over

- 6 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/deep-research-ops
