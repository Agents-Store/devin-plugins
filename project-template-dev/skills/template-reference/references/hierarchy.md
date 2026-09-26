# Template Hierarchy — Detailed Reference

## Level 0: `project-template`

The universal base template. Created once by the core team. All other templates inherit from it.

**Repository:** `git@github.com:stackmakers-ai/project-template.git`

**What it contains:**
- Empty `stack.json` (level 0, no stack, no parent)
- Generic `CLAUDE.md` with placeholder sections
- Generic `README.md` with comprehensive setup guide
- `.env.example` with all possible services commented out
- `.mcp.json.example` with placeholder structure
- Process skills: brainstorming, planning, tdd, debugging, verification
- Project-config skill (template with empty tables)
- Core commands: init-stack, commit, pr, plan, review, retro, sync, fix-issue
- Core agent: code-reviewer
- Core rules: safety, search-before-building, project-conventions
- Docs templates: architecture.md, code-style.md, api-conventions.md
- Sync script for CLAUDE.md → AGENTS.md mirroring

**When to modify Level 0:**
- Adding a new process skill that all stacks benefit from
- Updating a core command (commit, pr, plan, etc.)
- Adding a universal safety rule
- Improving documentation templates
- Updating the sync script
- Adding new fields to stack.json schema

---

## Level 1: `project-{stack}`

Stack-specific template. Created per technology combination. Reused for multiple demos and clients.

**Example:** `project-directus-nextjs` → `git@github.com:stackmakers-ai/project-directus-nextjs.git`

**What it adds over Level 0:**
- Filled `stack.json` (level 1, parent = project-template, layers and plugins populated)
- Stack-specific `CLAUDE.md` with technology details, gotchas, installed plugins
- Stack-specific `.env.example` with only relevant variables uncommented
- Stack-specific skills (e.g., `new-page` for Next.js projects)
- Stack-specific documentation in `docs/`
- Technology-specific config files (next.config.ts, tsconfig.json, docker-compose.yml, etc.)
- Package management files (package.json, pnpm-lock.yaml, etc.)

**Naming:** `project-{data}-{interface}` or `project-{primary-technology}`

Examples: `project-directus-nextjs`, `project-nocodb-saas`, `project-nocobase-crm`, `project-supabase-nuxt`

**When to modify Level 1:**
- Adding a stack-specific skill (e.g., `new-api-route` for Next.js)
- Updating stack-specific gotchas in CLAUDE.md
- Adding/removing env variables for the stack
- Updating Docker or deployment configuration
- Adding stack-specific dependencies

---

## Level 1.5: `demo-{stack}`

A working application built on a Level 1 template. Serves as showcase, reference implementation, and starting point.

**Example:** `demo-directus-nextjs`

**What it adds over Level 1:**
- Sample Directus collections with seed data
- Working Next.js pages consuming that data
- Configured components (shadcn/ui, layouts, theme)
- Example Server Actions, API routes
- Docker Compose for local development
- Seed scripts for reproducible demo data

**What it does NOT contain:**
- Client-specific resource IDs or credentials
- Production .env values
- Custom business logic

**Naming:** `demo-{stack}` (same stack identifier as the Level 1 parent)

---

## Level 2: `{client}-{project}`

Final client project with real credentials and resource IDs.

**Example:** `acme-website`, `globex-portal`

**What it adds over Level 1 (or 1.5 if forked from demo):**
- Filled `project-config` skill with real resource IDs (table IDs, workflow IDs, webhook URLs)
- Real `.env` / `.env.local` with actual credentials (never committed)
- Real `.mcp.json` with actual service URLs and tokens (never committed)
- Client-specific skills (domain logic, business workflows)
- Client-specific agents (data analyst, report generator, etc.)
- Custom business logic, pages, components

**Naming:** `{client}-{project}` — no `project-` prefix to distinguish from reusable templates

---

## Hierarchy Diagram

```
Level 0: project-template                        ← universal base
  │
  ├── Level 1: project-directus-nextjs           ← stack template
  │     │
  │     ├── Level 1.5: demo-directus-nextjs      ← demo project
  │     │
  │     ├── Level 2: acme-website                ← client project
  │     │
  │     └── Level 2: globex-portal               ← another client
  │
  ├── Level 1: project-nocodb-saas
  │
  └── Level 1: project-nocobase-crm
```

## Creating Templates

```bash
# Level 1 from Level 0
git clone project-template project-directus-nextjs
cd project-directus-nextjs && claude   # then: /init-stack

# Level 1.5 from Level 1
git clone project-directus-nextjs demo-directus-nextjs
cd demo-directus-nextjs   # build sample app, add seed data

# Level 2 from Level 1
git clone project-directus-nextjs acme-website
cd acme-website   # fill credentials, build features
```
