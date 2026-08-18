# File Inventory — Per Template Level

Complete list of files in each template level, with descriptions.

## Level 0: `project-template`

### Root Files

| File | Description |
|------|-------------|
| `stack.json` | Template metadata: level, parent, layers, plugins (empty at L0) |
| `CLAUDE.md` | Claude Code project memory — generic with placeholders |
| `AGENTS.md` | Auto-generated from CLAUDE.md via sync script (for Cursor/Gemini) |
| `README.md` | Comprehensive setup guide |
| `.env.example` | All possible env vars commented out — uncomment per stack |
| `.mcp.json.example` | MCP connection template with placeholder URLs |
| `.mcp.json` | Real MCP connections (gitignored) |
| `.editorconfig` | Editor formatting rules |
| `.gitignore` | Excludes .env, .mcp.json, node_modules, etc. |

### `.claude/` Directory

| File | Type | Description |
|------|------|-------------|
| `settings.local.json.example` | Config | Template for Claude Code local settings |
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

### `.claude/commands/`

| Command | Description |
|---------|-------------|
| `init-stack.md` | Initialize stack.json with technologies and plugins |
| `commit.md` | Create a conventional commit |
| `pr.md` | Create a pull request |
| `plan.md` | Create structured implementation plan |
| `review.md` | Comprehensive code review |
| `retro.md` | Sprint retrospective |
| `sync.md` | Sync CLAUDE.md → AGENTS.md and .cursor/ |
| `fix-issue.md` | Fix a GitHub issue |

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
| `sync-context.sh` | Syncs CLAUDE.md → AGENTS.md, .cursor/ |

---

## Level 1: `project-{stack}` — Additions

Everything from Level 0 plus:

### Modified Files

| File | What Changes |
|------|-------------|
| `stack.json` | level=1, parent="project-template", layers and plugins filled |
| `CLAUDE.md` | Tech stack filled, installed plugins listed, stack-specific gotchas |
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
| `.env.local` / `.env` | Real credentials (never committed) |
| `.mcp.json` | Real MCP connections (never committed) |
| `project-config/SKILL.md` | Filled with actual resource IDs |
| Domain-specific skills | Business logic skills |
| Custom agents | Client-specific agents |
| Custom pages/components | Client-specific UI |
