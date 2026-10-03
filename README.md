# Agents Store — Devin Plugins

> Автогенерация из канонических плагинов Claude Code (`Agents-Store/claude-plugins`). Не редактируйте вручную — изменения перезатрутся.

## Install

Clone this repository, then copy a plugin's directory into your Devin plugin directory. Each `.devin-plugin/plugin.json` is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

```bash
git clone <this-repo>
cp -r agents-store-devin-plugins/<plugin-name> ~/.devin/plugins/<plugin-name>
```

## Плагины (42)

| Плагин | Описание | Skills | Agents | Commands | MCP |
|---|---|---|---|---|---|
| [atlassian-ops](./atlassian-ops) | Atlassian Jira + Confluence Cloud ops plugin. Drive the full Jira Cloud REST API v3 and Confluence Cloud REST API v2 by curl — Jira: issues (create/edit/transit | 6 | 1 | 0 | — |
| [chatwoot-dev](./chatwoot-dev) | Chatwoot dev plugin for Agents Store. Full REST API coverage (Application, Platform, and Public/Client APIs) with bundled OpenAPI specs, official chatwoot CLI r | 6 | 1 | 2 | — |
| [codemap-dev](./codemap-dev) | Code understanding plugin for developers. Helps onboard to unfamiliar projects through beginner-friendly code review, step-by-step explanations, visual diagrams | 5 | 4 | 7 | ✓ |
| [dataforseo-dev](./dataforseo-dev) | DataForSEO data for SEO work — keywords, SERP, backlinks, on-page, AI visibility — through the v3 MCP server. Not a general web-search tool. | 11 | 1 | 3 | ✓ |
| [deep-research-ops](./deep-research-ops) | Multi-step research workflow over any search MCP servers; installs web-search-dev for the tools. | 5 | 0 | 6 | — |
| [dify-ops](./dify-ops) | Dify self-hosted update operations plugin. Pre-flight the target release and the bundled Weaviate migration path, back up volumes with the stack down, merge a r | 4 | 1 | 2 | — |
| [directus-dev](./directus-dev) | Directus development plugin. Knowledge base for working with Directus MCP tools (12 tools), REST API, and @directus/sdk. Covers collections, items, fields, rela | 11 | 2 | 10 | — |
| [document-generator-ops](./document-generator-ops) | Professional document generator. Creates proposals, invoices, estimates/quotations, reports, presentations, contracts, NDAs, and certificates of completion in P | 7 | 1 | 10 | — |
| [dokploy-dev](./dokploy-dev) | Dokploy self-hosted PaaS development plugin (aligned with Dokploy v0.30.x). Deploy applications, provision 6 database types (Postgres, MySQL, MariaDB, MongoDB,  | 9 | 1 | 14 | ✓ |
| [flask-dev](./flask-dev) | Flask dev plugin for Agents Store. Project scaffold, application factory patterns, blueprint organization, Flask-Login authentication, CRUD views, Jinja2 templa | 8 | 1 | 0 | — |
| [google-workspace-dev](./google-workspace-dev) | Google Workspace plugin powered by the official googleworkspace/cli (gws) Agent Skills. ~95 skills for Gmail, Drive, Calendar, Sheets, Docs, Chat, Meet, Tasks,  | 97 | 0 | 0 | — |
| [grammy-dev](./grammy-dev) | grammY (Telegram bot framework) dev plugin for Agents Store. Covers bot core, filter queries, middleware, commands, keyboards, sessions, conversations, files, p | 16 | 1 | 0 | — |
| [infisical-dev](./infisical-dev) | Infisical CLI dev plugin for Agents Store. Complete command-line coverage for secrets management — install & auth, infisical run/secrets/export, dynamic secrets | 6 | 1 | 0 | — |
| [macstack-dev](./macstack-dev) | Turns what a client says into documents they can correct, a machine spec an agent can build from, and a work list somebody can pick up. Keeps the macstack/ fold | 18 | 1 | 8 | — |
| [mattermost-ops](./mattermost-ops) | Mattermost collaboration ops plugin. Drive the full Mattermost REST API v4 by curl — users, teams, channels (public/private/DM/group), posts & threads, reaction | 5 | 1 | 0 | — |
| [n8n-dev](./n8n-dev) | n8n workflow automation dev plugin for Agents Store. MCP tools guide (external + native), workflow patterns, expression syntax, validation, node configuration,  | 21 | 1 | 0 | — |
| [n8n-provision](./n8n-provision) | n8n instance provisioning plugin. Discover workflows from the official template library (12,900+ templates), GitHub repos, and community platforms, then analyze | 9 | 1 | 5 | — |
| [nextjs-dev](./nextjs-dev) | Next.js development plugin. Knowledge base for building modern Next.js 16 applications with App Router, Server/Client Components, data fetching, Cache Component | 18 | 1 | 0 | — |
| [nextjs-provision](./nextjs-provision) | Next.js provisioning plugin. Set up shadcn/ui and shadcn studio — component installation, theme configuration, MCP server setup, project scaffolding, and multi- | 8 | 1 | 3 | ✓ |
| [nocobase-dev](./nocobase-dev) | NocoBase v2 development plugin. Build, manage, and operate NocoBase through the `nb` CLI 2.2 (primary) or REST API (fallback). Bundles 20 official upstream skil | 25 | 0 | 0 | — |
| [nocodb-dev](./nocodb-dev) | NocoDB schema development plugin. Meta API v3 via curl and MCP (schema tools on Cloud/licensed through listTools/callTool) — tables, fields (35 types), views (9 | 12 | 1 | 6 | ✓ |
| [nocodb-ops](./nocodb-ops) | NocoDB ops plugin for Agents Store. Record management, filtering (structured filters, exactDate date filters), sorting, reports, search, webhooks (events, paylo | 10 | 1 | 6 | ✓ |
| [openclaw-ops](./openclaw-ops) | Operations plugin for a fleet of self-hosted OpenClaw gateway instances running as Docker Compose projects on one host. Discovers every instance from the live D | 23 | 2 | 11 | — |
| [outline-ops](./outline-ops) | Outline knowledge-base ops plugin. Drive the full Outline REST API by curl — documents (create, search, move, archive, trash, import/export, AI answers, members | 5 | 1 | 0 | — |
| [payloadcms-dev](./payloadcms-dev) | PayloadCMS dev plugin for Agents Store. Covers collections, fields, globals, hooks, access control, authentication, queries, data management (trash/query preset | 23 | 1 | 1 | — |
| [plane-ops](./plane-ops) | Plane Agile Ops knowledge plugin: sprint planning, task decomposition, estimation, backlog management, velocity tracking, retrospectives, standups, intake triag | 17 | 2 | 44 | — |
| [postgresql-external-dev](./postgresql-external-dev) | PostgreSQL knowledge for low-code stacks. Schema design for external database connections (compatible SQL patterns for NocoDB and NocoBase — table creation, col | 8 | 1 | 0 | — |
| [project-template-dev](./project-template-dev) | Manage project template hierarchy with unified improvement workflow. Route fixes to plugins or parent templates automatically, quick-capture ideas for later, an | 10 | 1 | 8 | — |
| [restic-dev](./restic-dev) | restic backup plugin for Agents Store. Set up encrypted daily backups on any Linux server to S3-compatible storage (Cloudflare R2): server recon + restic instal | 11 | 1 | 3 | — |
| [sendpulse-ops](./sendpulse-ops) | Sendpulse multi-channel marketing plugin. Manage chatbots (Telegram, WhatsApp, Instagram, Messenger, Viber, TikTok), CRM (contacts, deals, pipelines, boards, ta | 12 | 2 | 15 | ✓ |
| [seo-dev](./seo-dev) | SEO development plugin for Agents Store. Technical SEO, structured data (JSON-LD), metadata API, Core Web Vitals, sitemaps, and content optimization patterns fo | 10 | 1 | 1 | — |
| [sqlalchemy-dev](./sqlalchemy-dev) | SQLAlchemy dev plugin for Agents Store. Typed SQLAlchemy 2.0 style (Mapped, mapped_column, select) with a SQLAlchemy 2.1 section: model definition patterns, rel | 6 | 1 | 0 | — |
| [stack-composable-stack-v1](./stack-composable-stack-v1) | Composable Stack v1 architecture plugin. How PostgreSQL (direct MCP + PostgREST API), NocoDB, n8n, Trigger.dev, and NocoBase (prod + dev sandbox) fit together f | 7 | 1 | 0 | ✓ |
| [stack-directus-nextjs](./stack-directus-nextjs) | Directus + Next.js architecture plugin. How Directus (content, files, access) and a Next.js App Router frontend fit together: who holds the token, how the cache | 6 | 1 | 0 | ✓ |
| [stack-directus-nextjs-trigger](./stack-directus-nextjs-trigger) | Directus + Next.js + Trigger.dev architecture plugin. How Directus (content, files, access), a Next.js App Router frontend and self-hosted Trigger.dev (durable  | 8 | 1 | 0 | ✓ |
| [stack-flask-sqlalchemy](./stack-flask-sqlalchemy) | Flask + SQLAlchemy architecture plugin. How the application factory, the Flask-SQLAlchemy session, Alembic migrations and Jinja2 templates fit together: where d | 2 | 1 | 0 | — |
| [taiga-ops](./taiga-ops) | Taiga project-management ops plugin. Drive the full Taiga REST API by curl — projects, memberships, roles, milestones (sprints), epics, user stories, tasks, iss | 5 | 1 | 0 | — |
| [teams-dev](./teams-dev) | Microsoft Teams SDK dev plugin for Agents Store. TypeScript guidance for building Teams bots, message extensions, tabs, dialogs and AI agents on Teams SDK 2.1 a | 17 | 1 | 2 | — |
| [teleshop-ops](./teleshop-ops) | Teleshop store management plugin. Manage products, orders, categories, attributes, customers, webhooks, and addons for your Telegram store via 50 MCP tools. | 9 | 2 | 13 | ✓ |
| [trigger-dev](./trigger-dev) | Trigger.dev dev plugin for Agents Store. Comprehensive development knowledge for building background tasks, AI agent workflows, and durable execution on self-ho | 14 | 1 | 4 | — |
| [vercel-dev](./vercel-dev) | Vercel ecosystem plugin. Deployment, AI SDK, Edge Functions, storage, routing, performance optimization. Includes CLI deploy troubleshooting for non-Git project | 32 | 3 | 4 | ✓ |
| [web-search-dev](./web-search-dev) | Developer reference for web search, scraping and documentation lookup — Firecrawl, Exa, Jina, Perplexity, Context7 MCP tools and REST/SDK/CLI — plus Pexels and  | 10 | 1 | 0 | ✓ |
