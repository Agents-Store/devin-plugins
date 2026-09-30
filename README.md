# Agents Store — Devin Plugins

> Автогенерация из канонических плагинов Claude Code (`Agents-Store/claude-plugins`). Не редактируйте вручную — изменения перезатрутся.

## Install

Clone this repository, then copy a plugin's directory into your Devin plugin directory. Each `.devin-plugin/plugin.json` is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

```bash
git clone <this-repo>
cp -r agents-store-devin-plugins/<plugin-name> ~/.devin/plugins/<plugin-name>
```

## Плагины (49)

| Плагин | Описание | Skills | Agents | Commands | MCP |
|---|---|---|---|---|---|
| [atlassian-ops](./atlassian-ops) | Atlassian Jira + Confluence Cloud ops plugin. Drive the full Jira Cloud REST API v3 and Confluence Cloud REST API v2 by curl — Jira: issues (create/edit/transit | 6 | 1 | 0 | — |
| [chatwoot-dev](./chatwoot-dev) | Chatwoot dev plugin for Agents Store. Full REST API coverage (Application, Platform, and Public/Client APIs) with bundled OpenAPI specs, official chatwoot CLI r | 6 | 1 | 2 | — |
| [codemap-dev](./codemap-dev) | Code understanding plugin for developers. Helps onboard to unfamiliar projects through beginner-friendly code review, step-by-step explanations, visual diagrams | 5 | 4 | 7 | ✓ |
| [dataforseo-dev](./dataforseo-dev) | DataForSEO data analysis plugin. Keyword research, competitor analysis, backlink auditing, SERP monitoring, on-page audits, content analysis, and AI optimizatio | 10 | 1 | 3 | ✓ |
| [deep-research-ops](./deep-research-ops) | Deep Research plugin. Comprehensive web research using 4 providers (Exa, Firecrawl, Jina, Perplexity) with capability-based CONNECTORS pattern and automatic FAL | 5 | 0 | 6 | — |
| [dify-ops](./dify-ops) | Dify self-hosted update operations plugin. Pull upstream changes, merge into local dev branch, sync .env variables, detect Docker project names, and rebuild con | 4 | 1 | 2 | — |
| [directus-dev](./directus-dev) | Directus development plugin. Knowledge base for working with Directus MCP tools (12 tools), REST API, and @directus/sdk. Covers collections, items, fields, rela | 10 | 2 | 10 | — |
| [document-generator-ops](./document-generator-ops) | Professional document generator. Creates proposals, invoices, estimates/quotations, reports, presentations, contracts, NDAs, and certificates of completion in P | 6 | 1 | 10 | — |
| [dokploy-dev](./dokploy-dev) | Dokploy self-hosted PaaS development plugin (aligned with Dokploy v0.29.14). Deploy applications, provision 6 database types (Postgres, MySQL, MariaDB, MongoDB, | 9 | 1 | 14 | ✓ |
| [firecrawl](./firecrawl) | DEPRECATED — superseded by web-search-dev, which covers the current Firecrawl MCP tools and REST API v2 alongside Exa, Perplexity, Jina and Context7; this plugi | 7 | 1 | 7 | ✓ |
| [flask-dev](./flask-dev) | Flask dev plugin for Agents Store. Application factory patterns, blueprint organization, Jinja2 templates, Flask CLI recipes, and troubleshooting for developers | 6 | 1 | 0 | — |
| [google-workspace-dev](./google-workspace-dev) | Google Workspace plugin powered by the official googleworkspace/cli (gws) Agent Skills. ~95 skills for Gmail, Drive, Calendar, Sheets, Docs, Chat, Meet, Tasks,  | 97 | 0 | 0 | — |
| [grammy-dev](./grammy-dev) | grammY (Telegram bot framework) dev plugin for Agents Store. Covers bot core, filter queries, middleware, commands, keyboards, sessions, conversations, files, p | 16 | 1 | 0 | — |
| [image-search-dev](./image-search-dev) | Stock image and video search developer toolkit. MCP tool patterns for Pexels (9 tools) and Unsplash (4 tools) from mcpware-dev-tools. Photo search, video search | 4 | 1 | 0 | — |
| [infisical-dev](./infisical-dev) | Infisical CLI dev plugin for Agents Store. Complete command-line coverage for secrets management — install & auth, infisical run/secrets/export, dynamic secrets | 6 | 1 | 0 | — |
| [macstack-dev](./macstack-dev) | Turns what a client says into documents they can correct, a machine spec an agent can build from, and a work list somebody can pick up. Keeps the macstack/ fold | 18 | 1 | 8 | — |
| [mattermost-ops](./mattermost-ops) | Mattermost collaboration ops plugin. Drive the full Mattermost REST API v4 by curl — users, teams, channels (public/private/DM/group), posts & threads, reaction | 5 | 1 | 0 | — |
| [media-hosting-ops](./media-hosting-ops) | Media hosting operations plugin. Upload images by public URL to MinIO-based media hosting via the uploadImageToMinio MCP tool. | 2 | 1 | 0 | — |
| [n8n](./n8n) | DEPRECATED — superseded by n8n-dev (building, validating and debugging workflows against both current n8n MCP servers) and n8n-provision (template discovery and | 8 | 2 | 9 | ✓ |
| [n8n-dev](./n8n-dev) | n8n workflow automation dev plugin for Agents Store. MCP tools guide (external + native), workflow patterns, expression syntax, validation, node configuration,  | 13 | 1 | 0 | — |
| [n8n-provision](./n8n-provision) | n8n instance provisioning plugin. Discover workflows from the official template library (9,166+ templates), GitHub repos, and community platforms, then analyze, | 9 | 1 | 5 | — |
| [nextjs-dev](./nextjs-dev) | Next.js development plugin. Knowledge base for building modern Next.js 16 applications with App Router, Server/Client Components, data fetching, Cache Component | 18 | 1 | 0 | — |
| [nextjs-provision](./nextjs-provision) | Next.js provisioning plugin. Set up shadcn/ui and shadcn studio — component installation, theme configuration, MCP server setup, project scaffolding, and multi- | 8 | 1 | 3 | ✓ |
| [nocobase](./nocobase) | DEPRECATED — superseded by nocobase-dev, which bundles the official nocobase/skills library and works through the nb CLI and REST API. Its MCP server package (@ | 7 | 2 | 8 | — |
| [nocobase-dev](./nocobase-dev) | NocoBase v2 development plugin. Build, manage, and operate NocoBase through the `nb` CLI (primary) or REST API (fallback). Bundles 11 official upstream skills f | 17 | 0 | 0 | — |
| [nocodb](./nocodb) | DEPRECATED — superseded by nocodb-dev (schema, fields, views, Meta API) and nocodb-ops (records, search, views, reports), which teach the current NocoDB MCP too | 8 | 2 | 10 | ✓ |
| [nocodb-dev](./nocodb-dev) | NocoDB schema development plugin. Full Meta API v3 coverage — tables, fields (30+ types), views, filters, sorts, hooks (HookV3), comments, scripts, dashboards & | 12 | 1 | 6 | ✓ |
| [nocodb-ops](./nocodb-ops) | NocoDB ops plugin for Agents Store. Record management, views, reports, filtering, search, and data import/export for business users via MCP tools and CLI. | 9 | 1 | 6 | ✓ |
| [openclaw-configurator](./openclaw-configurator) | DEPRECATED — superseded by openclaw-ops, which operates instances from live Docker state instead of hard-coded paths. Kept for its workspace-authoring skills (A | 19 | 2 | 7 | — |
| [openclaw-ops](./openclaw-ops) | Operations plugin for a fleet of self-hosted OpenClaw gateway instances running as Docker Compose projects on one host. Discovers every instance from the live D | 12 | 2 | 11 | — |
| [outline-ops](./outline-ops) | Outline knowledge-base ops plugin. Drive the full Outline REST API by curl — documents (create, search, move, archive, trash, import/export, AI answers, members | 5 | 1 | 0 | — |
| [payloadcms-dev](./payloadcms-dev) | PayloadCMS dev plugin for Agents Store. Covers collections, fields, globals, hooks, access control, authentication, queries, data management (trash/query preset | 23 | 1 | 1 | — |
| [plane-ops](./plane-ops) | Plane Agile Ops knowledge plugin. Full coverage of the Plane MCP surface: sprint planning, task decomposition, estimation, backlog management, velocity tracking | 17 | 2 | 44 | — |
| [postgresql-external-dev](./postgresql-external-dev) | PostgreSQL schema design for external database connections. Compatible SQL patterns for NocoDB and NocoBase — table creation, column types, relations, indexes,  | 6 | 1 | 0 | — |
| [project-template-dev](./project-template-dev) | Manage project template hierarchy with unified improvement workflow. Route fixes to plugins or parent templates automatically, quick-capture ideas for later, an | 10 | 1 | 8 | — |
| [restic-dev](./restic-dev) | restic backup plugin for Agents Store. Set up encrypted daily backups on any Linux server to S3-compatible storage (Cloudflare R2): server recon + restic instal | 11 | 1 | 3 | — |
| [sendpulse-ops](./sendpulse-ops) | Sendpulse multi-channel marketing plugin. Manage chatbots (Telegram, WhatsApp, Instagram, Messenger, Viber), CRM (contacts, deals, pipelines, boards, tasks), em | 11 | 2 | 15 | ✓ |
| [seo-dev](./seo-dev) | SEO development plugin for Agents Store. Technical SEO, structured data (JSON-LD), metadata API, Core Web Vitals, sitemaps, and content optimization patterns fo | 10 | 1 | 1 | — |
| [sqlalchemy-dev](./sqlalchemy-dev) | SQLAlchemy dev plugin for Agents Store. Model definition patterns, relationship mapping, query optimization, Alembic migrations, and troubleshooting for develop | 6 | 1 | 0 | — |
| [stack-composable-stack-v1](./stack-composable-stack-v1) | Composable Stack v1 dev plugin. Integrates PostgreSQL (direct MCP + PostgREST API), NocoDB, n8n, Trigger.dev, and NocoBase (prod + dev sandbox via nc-mcp) for b | 7 | 1 | 0 | ✓ |
| [stack-directus-nextjs-dev](./stack-directus-nextjs-dev) | Directus + Next.js stack dev plugin. Integrates Directus headless CMS with Next.js App Router for content-driven applications. | 6 | 1 | 0 | ✓ |
| [stack-directus-nextjs-trigger-dev](./stack-directus-nextjs-trigger-dev) | Directus + Next.js + Trigger.dev stack dev plugin. Adds self-hosted Trigger.dev as a workflow engine for AI agents, durable async logic, and scheduled jobs on t | 9 | 1 | 0 | ✓ |
| [stack-flask-sqlalchemy-dev](./stack-flask-sqlalchemy-dev) | Flask + SQLAlchemy stack dev plugin for Agents Store. Integration patterns for app factory wiring, blueprint-model coordination, Flask-Login + SQLAlchemy auth,  | 4 | 1 | 0 | — |
| [taiga-ops](./taiga-ops) | Taiga project-management ops plugin. Drive the full Taiga REST API by curl — projects, memberships, roles, milestones (sprints), epics, user stories, tasks, iss | 5 | 1 | 0 | — |
| [teams-dev](./teams-dev) | Microsoft Teams SDK dev plugin for Agents Store. TypeScript-first guidance for building Teams bots, message extensions, tabs, dialogs, and AI agents using @micr | 18 | 1 | 2 | — |
| [teleshop-ops](./teleshop-ops) | Teleshop store management plugin. Manage products, orders, categories, attributes, customers, webhooks, and addons for your Telegram store via 50 MCP tools. | 9 | 2 | 13 | ✓ |
| [trigger-dev](./trigger-dev) | Trigger.dev dev plugin for Agents Store. Comprehensive development knowledge for building background tasks, AI agent workflows, and durable execution on self-ho | 12 | 1 | 4 | — |
| [vercel-dev](./vercel-dev) | Vercel ecosystem plugin. Deployment, AI SDK, Edge Functions, storage, routing, performance optimization. Includes CLI deploy troubleshooting for non-Git project | 25 | 3 | 6 | ✓ |
| [web-search-dev](./web-search-dev) | Web search and scraping developer toolkit. MCP tool patterns, REST API reference (Firecrawl v2), SDK/CLI usage for Firecrawl, Exa, Perplexity, Jina, Pexels, Uns | 10 | 1 | 0 | ✓ |
