# image-search-dev (Devin plugin)

Stock image and video search developer toolkit. MCP tool patterns for Pexels (9 tools) and Unsplash (4 tools) from mcpware-dev-tools. Photo search, video search, collections, curated content, and MinIO upload integration.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (4)

- `examples` — This skill should be used when the user asks for "image search examples", "stock photo workflow", "show me how to find images", "media search walkthrough", "pexels usage example", "unsplash usage example", or wants to see end-to-end scenarios for finding and using stock images and videos.
- `mcp-patterns` — This skill should be used when the user asks about "image search MCP tools", "pexels tools", "unsplash tools", "which image search tools are available", "how to find stock photos", "search photos MCP", "stock image tools", "pexels parameters", "unsplash parameters", or needs to know which MCP operations are available for searching stock images and videos.
- `setup` — This skill should be used when the user asks to "verify image search setup", "check pexels connection", "check unsplash MCP", "test image search tools", "is pexels working", "is unsplash working", or needs to confirm that the Pexels and Unsplash MCP tools are operational.
- `troubleshoot` — This skill should be used when the user encounters "pexels error", "unsplash error", "image search not working", "rate limit on stock photos", "stock photo tool not found", "image search rate limited", or needs to diagnose and fix problems with Pexels, Unsplash, or MinIO upload tools.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/image-search-dev
