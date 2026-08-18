---
name: audit-stack
description: >
  Use when the user asks to "audit project stack", "analyze technologies",
  "scan dependencies", "generate stack.json", "what template level is this project",
  "map project to layers", or wants to discover all technologies in a codebase
  and get template and stack.json recommendations.
disable-model-invocation: true
---

# Audit Project Stack

Scan a project's source code, classify technologies into Logic/Interface/Data layers, research each technology online, recommend architecture improvements, and generate template and stack.json recommendations.

Read reference files before starting:
- `@references/technology-signatures.md` — detection signatures for 80+ technologies
- `@references/layer-classification.md` — canonical tech-to-layer mapping

<!-- SYNC NOTE: Phases 1-4 are identical to plugin-creator/skills/audit-stack/SKILL.md — keep in sync -->

---

## Phase 1: Source Code Scan

Scan the target project directory. Do NOT modify any files — this is read-only.

### Step 1.1 — Package Manifests

Read all package manifests found in the project root (and monorepo packages if applicable):

- `package.json` (Node.js) — extract `dependencies` and `devDependencies`
- `requirements.txt` / `pyproject.toml` / `Pipfile` (Python)
- `go.mod` (Go)
- `Cargo.toml` (Rust)
- `Gemfile` (Ruby)
- `composer.json` (PHP)
- `pom.xml` / `build.gradle` (Java/Kotlin)

For each dependency found, match against the package manifest tables in `@references/technology-signatures.md`.

### Step 1.2 — Configuration Files

Use Glob to detect configuration files. Check for:

```
**/next.config.* , **/nuxt.config.* , **/svelte.config.* , **/angular.json ,
**/tailwind.config.* , **/vite.config.* , **/webpack.config.* ,
**/tsconfig.json , **/prisma/schema.prisma , **/drizzle.config.* ,
**/trigger.config.* , **/docker-compose.yml , **/docker-compose.yaml ,
**/Dockerfile* , **/.github/workflows/*.yml , **/vercel.json ,
**/terraform/*.tf , **/k8s/** , **/.storybook/** ,
**/jest.config.* , **/vitest.config.* , **/playwright.config.* ,
**/sentry.*.config.*
```

Match each against the configuration file table in `@references/technology-signatures.md`.

### Step 1.3 — Docker Compose Services

If `docker-compose.yml` or `docker-compose.yaml` exists, read it and extract all `image:` values. Match against the Docker Compose service table in `@references/technology-signatures.md`.

### Step 1.4 — Import Pattern Scanning

Use Grep to search source files for distinctive import patterns. Focus on `src/` and root-level source files:

```
Glob: src/**/*.{ts,tsx,js,jsx,py,go,rs}
```

Search for the import patterns listed in `@references/technology-signatures.md` Section 4.

### Step 1.5 — Directory Structure Signals

Check for directory patterns that signal specific technologies (see Section 5 of technology-signatures.md):
- `src/app/` + `layout.tsx` = Next.js App Router
- `components/ui/` = shadcn/ui
- `prisma/` directory = Prisma
- `supabase/` directory = Supabase
- `trigger/` or `src/trigger/` = Trigger.dev

### Step 1.6 — Compile Technology List

Deduplicate all findings into a single list. For each technology, record:
- **Name** — canonical technology name
- **Version** — from package manifest if available, otherwise "detected"
- **Detection source** — which scan step found it (package.json, config file, docker-compose, import, directory)

Group minor packages under their parent ecosystem:
- `@radix-ui/react-dialog`, `@radix-ui/react-popover` -> just "Radix UI"
- `@sentry/node`, `@sentry/nextjs` -> just "Sentry"
- Multiple `@aws-sdk/*` packages -> just "AWS SDK"

Cap the list at the 30-40 most significant technologies. Minor utilities (linters, formatters, type checkers) can be mentioned briefly but don't need individual analysis.

---

## Phase 2: Layer Classification

Using `@references/layer-classification.md`, classify each technology into layers.

**Critical rule:** Full-stack frameworks (Next.js, Nuxt, SvelteKit, Remix, Rails, Django, Laravel) MUST appear in BOTH `logic` AND `interface`.

**Output as a table:**

```markdown
## Stack Audit Report

### Detected Technologies

| # | Technology | Version | Layer | Detection Source |
|---|-----------|---------|-------|-----------------|
| 1 | Next.js | 15.2.x | Logic, Interface | package.json, next.config.ts |
| 2 | PostgreSQL | 16 | Data | docker-compose.yml |
| 3 | Prisma | 6.x | Data | package.json, prisma/schema.prisma |
| 4 | Tailwind CSS | 4.x | Interface | package.json, tailwind.config.ts |
| 5 | Redis | 7.x | Data | docker-compose.yml |
| ... | | | | |

### Layer Summary

**Logic:** Next.js, Better Auth, Trigger.dev, tRPC, Stripe
**Interface:** Next.js, React, Tailwind CSS, shadcn/ui, Radix UI
**Data:** PostgreSQL, Prisma, Redis, Supabase
**Infrastructure:** Docker Compose, GitHub Actions, Vercel
```

---

## Phase 3: Technology Research

For each significant technology (or batched by related group), research its ecosystem online to gather information for template and plugin recommendations.

### Search Tool Fallback Chain

Try tools in this order. Move to the next only if the previous is unavailable, denied, or returns nothing useful. Reference tools by service name — find the matching tool in your available session tools:

| Priority | Service | Best for |
|----------|---------|----------|
| 1 | **Firecrawl Search** | Most powerful — supports `site:` operators, JS rendering |
| 2 | **Exa Web Search** | Code-focused, technical search |
| 3 | **Perplexity Search** | Synthesized answers about ecosystem health |
| 4 | **Jina Web Search** | Broad web search, parallel queries |
| 5 | **Context7 Query Docs** | Library documentation lookup |
| 6 | **WebSearch / WebFetch** | Always available — built-in fallback |

If an MCP search tool is denied after 1-2 attempts, immediately fall back to WebSearch/WebFetch. Do not keep retrying denied tools.

### What to Research

For each technology (batch related ones together to save queries):

1. **MCP server existence** — Search: `"{technology} MCP server"` — does an MCP server exist for this technology?
2. **Existing Claude Code plugin** — Search: `"{technology} claude code plugin agents store"` — is there already a plugin?
3. **Ecosystem health** — Is the technology actively maintained? Major version? Community size?
4. **Integration patterns** — How does this technology typically integrate with the others found in this project?

### Research Output

Record findings per technology:

```markdown
### Technology Research

| Technology | MCP Server? | Existing Plugin? | Ecosystem Status | Notes |
|-----------|-------------|-----------------|-----------------|-------|
| Next.js | No official | nextjs-dev (exists) | Active, v15 | Major framework |
| Prisma | Yes (community) | None | Active, v6 | Popular ORM |
| Redis | Yes (official) | None | Active, v7 | Standard cache |
```

---

## Phase 4: Architecture Recommendation

Based on the classified stack and research findings, provide architecture recommendations.

### Analysis Categories

1. **Consolidation opportunities** — Technologies serving the same purpose that could be unified
   - Example: "Both raw SQL queries and Prisma found — consider consolidating on Prisma"
   - Example: "Both Axios and native fetch used — standardize on one"

2. **Layer gaps** — Missing capabilities in any layer
   - Example: "No caching layer detected — consider Redis for frequently accessed data"
   - Example: "No authentication solution found — consider Better Auth or Clerk"
   - Example: "No job processing — consider Trigger.dev for background tasks"
   - Example: "No monitoring — consider Sentry for error tracking"

3. **Modern alternatives** — Technologies that have better modern replacements
   - Example: "Webpack detected — consider migrating to Vite for faster builds"
   - Example: "Express detected — consider Hono or Fastify for better performance"
   - Example: "Moment.js detected — consider date-fns or dayjs (Moment is in maintenance mode)"

4. **Integration patterns** — How the discovered technologies should work together
   - Example: "Next.js + Directus: use Directus SDK with server components for type-safe data fetching"
   - Example: "Supabase + Next.js: use Supabase Auth helpers with middleware for session management"

### Output Format

```markdown
## Architecture Recommendation

### Current Architecture
- **Logic:** [list technologies]
- **Interface:** [list technologies]
- **Data:** [list technologies]
- **Infrastructure:** [list technologies]

### Strengths
1. [what's working well about this stack]
2. [good technology choices]

### Recommended Improvements
| # | Category | Recommendation | Rationale |
|---|----------|---------------|-----------|
| 1 | Layer Gap | Add Redis for caching | Frequently accessed data without cache layer |
| 2 | Consolidation | Standardize on Prisma | Raw SQL and Prisma both used for same DB |
| 3 | Modern Alt | Migrate Webpack → Vite | 10x faster builds, native ESM |
| 4 | Integration | Use Directus SDK in server components | Type safety, automatic caching |
```

<!-- END SHARED PHASES — Phase 5 below is the Template Recommendation variant -->

---

## Phase 5: Template Recommendation

Based on discovered technologies and layer classification, generate template recommendations and a draft `stack.json`.

Reference these files for proper schema and level rules:
- `${CLAUDE_PLUGIN_ROOT}/skills/template-reference/SKILL.md` — template hierarchy rules
- `${CLAUDE_PLUGIN_ROOT}/skills/create/references/stack-json-schema.md` — stack.json schema
- `${CLAUDE_PLUGIN_ROOT}/skills/create/references/level-checklist.md` — required content per level

### Step 5.1 — Determine Template Level

Assess the project's maturity to determine the appropriate template level:

| Signal | Level |
|--------|-------|
| Just technologies, no application code | Level 1 (Stack Template) |
| Working application with sample/demo data | Level 1.5 (Demo Template) |
| Real client project with production credentials and custom business logic | Level 2 (Client Project) |

Maturity signals to check:
- Does `src/` contain substantial application code? (Level 1.5+)
- Are there seed scripts or sample data? (Level 1.5+)
- Does `.env` / `.env.local` contain real (non-example) credentials? (Level 2)
- Is there custom business logic specific to a client? (Level 2)
- Does `stack.json` already exist? (existing template — report current level)

### Step 5.2 — Generate Template Name

Follow the naming convention `project-{data}-{interface}`:
- Identify the primary **data** technology (e.g., directus, supabase, nocodb, postgresql)
- Identify the primary **interface** technology (e.g., nextjs, nuxt, svelte)
- Combine: `project-directus-nextjs`, `project-supabase-nuxt`, `project-nocodb-nuxt`

If no clear data+interface pair, use the dominant technology: `project-{dominant-tech}`

### Step 5.3 — Generate Draft stack.json

Using the layer classification from Phase 2, generate a complete `stack.json`:

```json
{
  "stack": "{data}-{interface}",
  "version": "1.0.0",
  "level": 1,
  "parent": "project-template",
  "description": "Stack template for {Data Technology} + {Interface Technology} projects",
  "layers": {
    "data": ["lowercase-tech-names"],
    "logic": ["lowercase-tech-names"],
    "interface": ["lowercase-tech-names"]
  },
  "plugins": {
    "technology": ["matching-dev-plugins"],
    "process": [],
    "stack": ["matching-stack-plugins"]
  }
}
```

Rules for `layers` values — use lowercase kebab-case identifiers:
- `nextjs` (not `Next.js`), `tailwindcss`, `trigger-dev`, `better-auth`
- Database drivers collapse to DB name: `pg` -> `postgresql`
- UI libraries use short form: `@radix-ui/*` -> `radix-ui`

Rules for `plugins` values:
- List technology plugins that exist or should be created: `{tool}-dev`, `{tool}-ops`
- List stack plugins if integration plugins exist: `stack-{name}-dev`
- Leave `process` empty unless the project uses specific business process plugins

### Step 5.4 — Identify Required Plugins

Cross-reference the `plugins` arrays with available plugins:
- Which plugins already exist in the marketplace?
- Which need to be created?

### Output Format

```markdown
## Template Recommendation

### Template Identity
- **Name:** `project-directus-nextjs`
- **Level:** 1 (Stack Template)
- **Parent:** `project-template`

### Draft stack.json

\`\`\`json
{
  "stack": "directus-nextjs",
  "version": "1.0.0",
  "level": 1,
  "parent": "project-template",
  "description": "Stack template for Directus + Next.js projects",
  "layers": {
    "data": ["directus"],
    "logic": ["nextjs", "trigger-dev"],
    "interface": ["nextjs", "tailwindcss", "shadcn"]
  },
  "plugins": {
    "technology": ["directus-dev", "nextjs-dev", "nextjs-provision"],
    "process": [],
    "stack": ["stack-directus-nextjs-dev"]
  }
}
\`\`\`

### Plugin Status
| Plugin | Status | Action |
|--------|--------|--------|
| directus-dev | Exists | Install |
| nextjs-dev | Exists | Install |
| nextjs-provision | Exists | Install |
| stack-directus-nextjs-dev | Exists | Install |
| trigger-dev-dev | Missing | Create with `/plugin-creator:create` |

### Template Creation Command

\`/project-template-creator:create Level 1 template for Directus + Next.js with Trigger.dev\`

### Suggested Stack-Specific Skills
Based on the level checklist, this template should include:
- `new-page` — scaffold a Next.js page with Directus data fetching
- `new-collection` — scaffold a Directus collection with fields
- `deploy` — deployment workflow for this stack
```
