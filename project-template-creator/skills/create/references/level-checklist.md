# Level Checklist — Required Content Per Level

## Level 0 (Universal Base)

### Must Have
- [ ] `stack.json` with level=0, null stack/parent, empty layers/plugins
- [ ] Generic `CLAUDE.md` with placeholder sections
- [ ] `README.md` with comprehensive setup guide
- [ ] `.env.example` with all possible services commented out
- [ ] `.mcp.json.example` with placeholder structure
- [ ] `.gitignore` excluding .env, .mcp.json, node_modules, .next, etc.
- [ ] `.editorconfig`
- [ ] `scripts/sync-context.sh`

### Core Skills
- [ ] brainstorming — design thinking before implementation
- [ ] planning — break work into tasks
- [ ] tdd — test-driven development
- [ ] debugging — systematic debugging process
- [ ] verification — verify before declaring done
- [ ] project-config — resource IDs and MCP mappings (template)

### Core Commands
- [ ] init-stack — initialize stack.json and plugins
- [ ] commit — conventional commit
- [ ] pr — create pull request
- [ ] plan — implementation planning
- [ ] review — code review
- [ ] retro — sprint retrospective
- [ ] sync — CLAUDE.md → AGENTS.md mirroring
- [ ] fix-issue — fix a GitHub issue

### Core Agent
- [ ] code-reviewer — reviews code quality

### Core Rules
- [ ] safety — prevent destructive operations
- [ ] search-before-building — search before creating
- [ ] project-conventions — naming and organization rules

### Documentation
- [ ] docs/architecture.md — generic template
- [ ] docs/code-style.md — generic style guide
- [ ] docs/api-conventions.md — API response format template

---

## Level 1 (Stack Template) — Additions

### Must Customize
- [ ] `stack.json` — fill level, parent, stack, layers, plugins
- [ ] `CLAUDE.md` — fill Tech Stack, Installed Plugins, add Gotchas
- [ ] `.env.example` — uncomment relevant vars, add stack-specific vars
- [ ] `.mcp.json.example` — add stack-specific MCP server templates
- [ ] `docs/architecture.md` — describe stack layers and data flow
- [ ] `docs/code-style.md` — add stack-specific style rules

### Stack-Specific Skills (add at least one)

Suggested per technology:

**Next.js stacks:**
- `new-page` — scaffold a page with data fetching
- `new-component` — scaffold a UI component
- `new-api-route` — scaffold an API route

**Directus stacks:**
- `new-collection` — scaffold a Directus collection with fields
- `new-flow` — scaffold a Directus Flow/automation

**NocoDB stacks:**
- `new-table` — scaffold a NocoDB table with fields
- `new-view` — scaffold a NocoDB view

**n8n stacks:**
- `new-workflow` — scaffold an n8n workflow

**General (any stack with Docker):**
- `deploy` — deployment workflow

### Stack-Specific Config Files
- [ ] `package.json` (Node.js stacks)
- [ ] `next.config.ts` / `nuxt.config.ts` (framework config)
- [ ] `tsconfig.json` (TypeScript projects)
- [ ] `Dockerfile` + `Dockerfile.dev` (Docker stacks)
- [ ] `docker-compose.yml` (multi-service stacks)
- [ ] `eslint.config.mjs` (JS/TS stacks)

---

## Level 1.5 (Demo) — Additions

### Must Have
- [ ] Working application source code (`src/` or equivalent)
- [ ] Sample data or seed scripts
- [ ] At least 2-3 working pages/views
- [ ] Configured UI components (theme, layouts)
- [ ] Docker Compose for full local environment
- [ ] Updated `stack.json` with level=1.5

### Must NOT Have
- [ ] Client-specific resource IDs
- [ ] Production credentials
- [ ] Custom business logic (keep generic/showcase)

---

## Level 2 (Client Project) — Additions

### Must Customize
- [ ] `project-config/SKILL.md` — real resource IDs, service URLs
- [ ] `.env.local` / `.env` — real credentials (gitignored)
- [ ] `.mcp.json` — real MCP connections (gitignored)
- [ ] `CLAUDE.md` — client project name, client-specific commands
- [ ] `docs/architecture.md` — client-specific architecture decisions

### Optional Additions
- [ ] Domain-specific skills (business logic workflows)
- [ ] Custom agents (data analyst, report generator, etc.)
- [ ] Custom rules (client-specific conventions)
