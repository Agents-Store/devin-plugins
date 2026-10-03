# File Inventory — Per Template Level

Complete list of files in each template level, with descriptions.

## Level 0: `project-template`

### Root Files

| File | Description |
|------|-------------|
| `stack.json` | Template metadata: level, parent, layers, plugins (empty at L0) |
| `AGENTS.md` | Shared rules for every coding tool (Cursor, Gemini, Codex, Claude) — the single source, not generated |
| `CLAUDE.md` | Claude Code project memory — starts with `@AGENTS.md`, then Claude-specific lines; generic with placeholders |
| `README.md` | Comprehensive setup guide |
| `.env.example` | All possible env vars commented out — uncomment per stack |
| `.mcp.json` | MCP connections, committed — `${VAR}` references only (empty `mcpServers` at L0); values live in `.env` / `.claude/settings.local.json` |
| `.editorconfig` | Editor formatting rules |
| `.gitignore` | Excludes `.env`, `.env.local`, `.claude/settings.local.json`, node_modules, etc. (not `.mcp.json`) |

### `.claude/` Directory

| File | Type | Description |
|------|------|-------------|
| `settings.json` | Config | Committed project settings: `enabledPlugins` and `extraKnownMarketplaces` (L0: marketplace registered, `enabledPlugins` empty; L1+: `enabledPlugins` filled from `stack.json` `plugins`) — see `conventions.md` |
| `settings.local.json.example` | Config | Template for Claude Code local settings (the `env` block `${VAR}` expands from) |
| `settings.local.json` | Config | Actual local settings (gitignored) |

### `.claude/skills/`

| Skill | Description |
|-------|-------------|
| `brainstorming/SKILL.md` | Structured design thinking before implementation |
| `planning/SKILL.md` | Break work into small executable tasks |
| `tdd/SKILL.md` | Test-Driven Development (RED-GREEN-REFACTOR) |
| `debugging/SKILL.md` | Systematic 4-phase debugging process |
| `verification/SKILL.md` | Verify changes before declaring done |
| `project-config/SKILL.md` | Project-specific resource IDs and MCP mappings (template) |
| `project-config/references/_template.md` | Reference template for project config |

### `.claude/skills/` — workflow skills

Base workflows are skills (`.claude/skills/<name>/SKILL.md`), invoked as `/<name>`. The older `.claude/commands/<name>.md` form still works and a skill wins over a command of the same name, so existing templates migrate by moving the file.

| Skill | Description |
|-------|-------------|
| `init-stack/SKILL.md` | Initialize stack.json with technologies and plugins |
| `commit/SKILL.md` | Create a conventional commit |
| `pr/SKILL.md` | Create a pull request |
| `plan-feature/SKILL.md` | Create structured implementation plan (not `plan`: collides with the built-in `/plan`) |
| `code-review-project/SKILL.md` | Comprehensive code review (not `review`: the built-in `/review` alias of `/code-review` shadows it) |
| `retro/SKILL.md` | Sprint retrospective |
| `sync/SKILL.md` | Mirror the shared rules into `.cursor/` (runs `scripts/sync-context.sh`) |
| `fix-issue/SKILL.md` | Fix a GitHub issue |

### `.claude/agents/`

| Agent | Description |
|-------|-------------|
| `code-reviewer.md` | Reviews code for bugs, style, security |

### `.claude/rules/`

| Rule | Description |
|------|-------------|
| `safety.md` | Prevent destructive operations |
| `search-before-building.md` | Always search for existing code first |
| `project-conventions.md` | Naming conventions, file organization |

### `docs/`

| File | Description |
|------|-------------|
| `architecture.md` | Architecture overview (template with placeholders) |
| `code-style.md` | Code style guide |
| `api-conventions.md` | API response format, status codes, auth |

### `scripts/`

| File | Description |
|------|-------------|
| `sync-context.sh` | Mirrors the shared rules (`AGENTS.md`) into `.cursor/` — `AGENTS.md` itself is the source and is never generated |

---

## Level 1: `project-{stack}` — Additions

Everything from Level 0 plus:

### Modified Files

| File | What Changes |
|------|-------------|
| `stack.json` | level=1, parent="project-template", layers and plugins filled |
| `CLAUDE.md` | Tech stack filled, installed plugins listed, stack-specific gotchas |
| `.mcp.json` | Stack-specific MCP servers added, `${VAR}` references only |
| `.claude/settings.json` | `enabledPlugins` lists every plugin from `stack.json`; `extraKnownMarketplaces` registers the marketplace |
| `.env.example` | Only relevant variables uncommented (e.g., DIRECTUS_URL, NEXTAUTH_SECRET) |
| `docs/architecture.md` | Stack-specific architecture description |
| `docs/code-style.md` | Stack-specific style rules |

### New Files (stack-specific)

Varies by stack. Example for `project-directus-nextjs`:

| File | Description |
|------|-------------|
| `package.json` | Node.js dependencies |
| `pnpm-lock.yaml` | Lock file |
| `next.config.ts` | Next.js configuration |
| `tsconfig.json` | TypeScript configuration |
| `eslint.config.mjs` | ESLint configuration |
| `postcss.config.mjs` | PostCSS configuration |
| `components.json` | shadcn/ui configuration |
| `Dockerfile` | Production Docker image |
| `Dockerfile.dev` | Development Docker image |
| `docker-compose.yml` | Docker Compose for local dev |
| `deploy.sh` | Deployment script |
| `.dockerignore` | Docker build exclusions |
| `src/` | Application source code |
| `public/` | Static assets |

### New Skills

| Skill | Description |
|-------|-------------|
| `new-page/SKILL.md` | Scaffold a new page with data fetching (Next.js + Directus) |
| (other stack-specific skills) | Varies by stack |

### New Rules

| Rule | Description |
|------|-------------|
| `.claude/rules/<name>.md` with `paths:` frontmatter | Stack-specific rules that load only when Claude reads a matching file (e.g. `paths: ["src/app/**"]`), keeping CLAUDE.md short |

---

## Level 1.5: `demo-{stack}` — Additions

Everything from Level 1 plus:

| Content | Description |
|---------|-------------|
| Sample collections/tables | Seed data for demo |
| Working pages | Real pages consuming data |
| Configured components | Theme, layouts, shadcn/ui components |
| Seed scripts | Scripts to populate demo data |
| Docker Compose (extended) | Full local dev environment with all services |

---

## Level 2: `{client}-{project}` — Additions

Everything from Level 1 (or forked from Level 1.5) plus:

| Content | Description |
|---------|-------------|
| `.env.local` / `.env` | Real credentials and the values behind the `${VAR}` references in `.mcp.json` (never committed) |
| `.claude/settings.local.json` | `env` block holding the same values for Claude Code (never committed) |
| `project-config/SKILL.md` | Filled with actual resource IDs |
| Domain-specific skills | Business logic skills |
| Custom agents | Client-specific agents |
| Custom pages/components | Client-specific UI |
