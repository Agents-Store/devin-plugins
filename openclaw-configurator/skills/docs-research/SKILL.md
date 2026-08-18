---
name: docs-research
description: How to fetch official OpenClaw documentation using whatever web-search/scrape tool is enabled, with a fallback ladder, plus the canonical OpenClaw doc URL map. Use whenever any openclaw-configurator skill or command needs to verify a feature, config field, auth method, or release note against official docs. Also use when the user asks to "check the latest docs", "is this still the recommended way", or before recommending any feature/auth change.
---

# Documentation Research

The single source of truth for **how** the openclaw-configurator plugin fetches official documentation and **where** OpenClaw's docs live. Every other skill, command, and agent in this plugin references this file instead of repeating the tool list or the URLs.

OpenClaw evolves quickly — auth methods, config fields, and recommended defaults change between releases. **Always verify against official docs before recommending a feature or auth change.** Never rely on memory for a current recommendation.

## Tool-Priority Ladder

Use the first tool that is actually available in the current session, then fall back down the list. Detect availability by whether the tool exists — do not assume.

1. **Firecrawl** — `firecrawl_search` (queries across the web), `firecrawl_scrape` (single page → markdown, or JSON with a schema for specific fields). Best for deep page scraping. Primary choice.
2. **Exa** — `web_search_exa` (semantic, code-aware search). Good for "find the page that explains X".
3. **Perplexity** — `perplexity_search` (ranked results + snippets), `perplexity_ask` (synthesized answer with citations). Good for "what's the current recommended way to …".
4. **Jina** — `read_url` (page → clean markdown), `search_web`. Reliable reader fallback.
5. **context7** — `resolve-library-id` then `query-docs`. Best for **library/CLI docs** (Infisical CLI, Claude API/SDK, Docker, etc.) rather than OpenClaw's own site.
6. **Built-in `WebFetch` / `WebSearch`** — always-available fallback when **no** MCP search/scrape tool is connected.

**Rule:** Prefer an enabled MCP search/scrape tool; if none are connected, use `WebFetch`/`WebSearch`. When a page is JavaScript-rendered and a tool returns empty, retry with a longer wait (`firecrawl_scrape` `waitFor`) or try the next tool down the ladder. Quote the source URL in findings so recommendations are auditable.

## OpenClaw Documentation Map

Canonical URLs — use these as entry points, then search within if a path 404s (docs paths can move):

| Topic | URL |
|-------|-----|
| Docs home / config reference | `https://docs.openclaw.ai/` (search "openclaw.json") |
| Gateway authentication (providers) | `https://docs.openclaw.ai/gateway/authentication` |
| OAuth concepts (auth-profiles, PKCE) | `https://docs.openclaw.ai/concepts/oauth` |
| Model providers (refs, runtimes) | `https://docs.openclaw.ai/concepts/model-providers` |
| Anthropic / Claude provider | `https://docs.openclaw.ai/providers/anthropic` |
| OpenAI / Codex provider | `https://docs.openclaw.ai/providers/openai` |
| CLI backends (claude-cli, codex) | `https://docs.openclaw.ai/gateway/cli-backends` |
| `openclaw models` CLI | `https://docs.openclaw.ai/cli/models` |
| Releases (changelog source) | `https://github.com/openclaw/openclaw/releases` + in-repo `CHANGELOG.md` |
| Skills examples | `https://github.com/openclaw/skills` |

**External CLIs referenced by this plugin** (use context7 or the ladder above):
- Infisical CLI — `https://infisical.com/docs/cli/overview`
- Anthropic Claude Code CLI / Codex CLI — provider docs for `claude auth login`, `codex auth login`.

## When to fetch vs. trust

- **Always fetch** before: recommending an auth method, enabling a "new" feature, flagging a setting as deprecated, or quoting a CLI flag.
- **Safe to trust** local state: the contents of the instance's own `openclaw.json`, `auth-profiles.json`, `.env`, and `git`/`docker` output.
