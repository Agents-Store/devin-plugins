---
name: create
description: >
  Use this skill when the user asks to "create a new template", "scaffold a Level 1
  template", "create project-{stack}", "make a new stack template", "fork
  project-template", "create a demo template", "set up a new project from template",
  or wants to create any new project template at Level 1, 1.5, or 2 from the
  universal base or a stack template.
---

# Create Project Template

Interactive workflow for creating new project templates at Level 1, 1.5, or 2 by cloning and customizing a parent template.

## Prerequisites

- **`$PROJECT_TEMPLATES_DIR`** — directory where template repos live
- **Git access** to `git@github.com:stackmakers-ai/` for cloning parent templates
- For plugin search: access to `$PLUGINS_PUBLIC_SOURCE_DIR` and `$PLUGINS_PRIVATE_SOURCE_DIR` (optional — set in `~/.claude/settings.json env`)

## Step 1: Gather Information

Ask the user (skip questions already answered):

1. **Template level** — What are you creating?
   - **Level 1** — Stack template (e.g., `project-directus-nextjs`). Reusable base for multiple demos and client projects.
   - **Level 1.5** — Demo app (e.g., `demo-directus-nextjs`). Working showcase with sample data.
   - **Level 2** — Client project (e.g., `acme-website`). Final project with real credentials.

2. **Stack name** — What technologies? (e.g., `directus-nextjs`, `supabase-n8n`, `nocodb-trigger`)
   Ask for each layer:
   - **Data layer** (database, CMS, BaaS): e.g., Directus, NocoDB, Supabase, NocoBase, PostgreSQL
   - **Logic layer** (backend, automation, jobs): e.g., Next.js, n8n, Trigger.dev, Node.js
   - **Interface layer** (frontend, UI): e.g., Next.js, Nuxt, React, Vue

3. **Parent template** — Which parent to clone from?
   - Level 1 → defaults to `project-template`
   - Level 1.5 → defaults to `project-{stack}`
   - Level 2 → defaults to `project-{stack}` (or `demo-{stack}` if forking from demo)

4. **Client name** (Level 2 only) — e.g., `acme`, `widgets-inc`, `globex`

5. **Project description** — One sentence describing the project purpose

## Step 2: Generate Template Name

Apply naming convention:

| Level | Pattern | Example |
|-------|---------|---------|
| 1 | `project-{stack}` | `project-directus-nextjs` |
| 1.5 | `demo-{stack}` | `demo-directus-nextjs` |
| 2 | `{client}-{project}` | `acme-website` |

Confirm the name with the user before proceeding.

## Step 3: Clone Parent Template

### 3a. Locate parent

```bash
PARENT_NAME="project-template"  # from Step 1

# Check local
if [ -d "$PROJECT_TEMPLATES_DIR/$PARENT_NAME" ]; then
  PARENT_DIR="$PROJECT_TEMPLATES_DIR/$PARENT_NAME"
else
  # Clone from GitHub
  echo "Cloning parent template from GitHub..."
  git clone "git@github.com:stackmakers-ai/$PARENT_NAME.git" "$PROJECT_TEMPLATES_DIR/$PARENT_NAME"
  PARENT_DIR="$PROJECT_TEMPLATES_DIR/$PARENT_NAME"
fi
```

### 3b. Create new template

```bash
NEW_NAME="project-directus-nextjs"  # from Step 2
NEW_DIR="$PROJECT_TEMPLATES_DIR/$NEW_NAME"

# Clone parent into new directory
git clone "$PARENT_DIR" "$NEW_DIR"

# Reset git for fresh history
cd "$NEW_DIR"
rm -rf .git
git init
```

### 3c. Set up remote (optional)

```bash
git remote add origin "git@github.com:stackmakers-ai/$NEW_NAME.git"
```

Ask the user if they want to create the GitHub repo now or later.

## Step 4: Customize stack.json

Generate `stack.json` based on user input from Step 1:

```json
{
  "stack": "{stack-name}",
  "version": "1.0.0",
  "level": {level},
  "parent": "{parent-name}",
  "description": "{project-description}",
  "layers": {
    "data": ["{data-layer-technologies}"],
    "logic": ["{logic-layer-technologies}"],
    "interface": ["{interface-layer-technologies}"]
  },
  "plugins": {
    "technology": [],
    "process": [],
    "stack": []
  }
}
```

The `plugins` arrays are filled in Step 7 after searching for matching plugins.

### Layer Classification for Full-Stack Frameworks

Many frameworks serve multiple layers. When a single technology handles both backend logic (API routes, server middleware) AND frontend rendering, list it in BOTH layers:

| Framework | data | logic | interface | Reason |
|-----------|------|-------|-----------|--------|
| Next.js | — | `nextjs` | `nextjs` | API routes + React SSR/CSR |
| Nuxt | — | `nuxt` | `nuxt` | Server routes + Vue SSR/CSR |
| SvelteKit | — | `sveltekit` | `sveltekit` | Endpoints + Svelte SSR |
| Remix | — | `remix` | `remix` | Loaders/actions + React |
| Rails | — | `rails` | `rails` | Controllers + views |

Dedicated backend-only or frontend-only tools go in a single layer:
- **Data only:** Directus, Supabase, NocoDB, PostgreSQL
- **Logic only:** n8n, Trigger.dev, Inngest, Express
- **Interface only:** React (SPA), Vue (SPA without Nuxt)

This matters because plugins are searched per-layer. A framework in both `logic` and `interface` ensures the right plugins are found for both backend and frontend capabilities.

See `references/stack-json-schema.md` for the complete field documentation.

## Step 5: Customize CLAUDE.md

Update CLAUDE.md for the new template level:

### Level 1 Changes
- Replace project name placeholder with stack name (e.g., "Directus + Next.js Stack Template")
- Add "Level 1 stack template. Fork this for client projects (Level 2)." at top
- Fill Tech Stack section with actual technologies and their roles
- Fill Installed Plugins section (populated in Step 7)
- Add stack-specific Quick Commands (e.g., `docker compose up dev`, `pnpm dev`)
- Add Gotchas section with known stack-specific pitfalls
- Remove all remaining placeholder comments
- Keep under 100 lines

### Level 1.5 Changes
- Same as Level 1, plus note that it's a demo
- Add demo-specific commands (seed data, reset demo)

### Level 2 Changes
- Replace with client project name
- Run the equivalent of `/init-stack` Phase 2-4 to fill project-specific content

## Step 6: Customize Template Files

### For Level 1

**`.env.example`** — Uncomment relevant variables, remove irrelevant ones:
```bash
# Keep only the variables for the selected stack
# Add stack-specific variables not in the L0 template
```

**`.mcp.json.example`** — Update with stack-specific MCP server templates:
```json
{
  "mcpServers": {
    "{data-service}": {
      "url": "${DATA_SERVICE_URL}/mcp",
      "headers": { "Authorization": "Bearer ${DATA_SERVICE_TOKEN}" }
    }
  }
}
```

**`docs/architecture.md`** — Fill with stack-specific architecture:
- Overview of the stack (what each layer does)
- Directory structure for the stack
- Data flow between layers

**`docs/code-style.md`** — Add stack-specific style rules (e.g., Next.js component patterns, Directus SDK usage patterns)

**`docs/api-conventions.md`** — Fill authentication method, pagination pattern based on the stack

**Stack-specific config files** — Use `references/stack-templates.md` for ready-made configuration snippets (nuxt.config.ts, next.config.ts, docker-compose.yml, Dockerfile, trigger.config.ts, .editorconfig). Adapt these to the specific stack rather than writing from scratch.

**Stack-specific skills** — Create skills for common stack operations. See the level checklist at `references/level-checklist.md` for suggestions per stack.

**Stack-specific config files** — Add files appropriate to the stack:
- `package.json` (if Node.js-based)
- `next.config.ts` (if Next.js)
- `docker-compose.yml` (if using Docker)
- `tsconfig.json` (if TypeScript)
- etc.

### For Level 1.5

Everything from Level 1, plus:
- Sample data / seed scripts
- Working pages consuming data
- Configured UI components
- Docker Compose for full local environment

### For Level 2

Run the init-stack command flow (Phases 2-4):
- Configure `.env` with real credentials
- Populate `project-config` skill with resource IDs
- Fill project documentation
- Create domain-specific skills if needed

## Step 7: Search for Matching Plugins

Search for Agents Store plugins that match the selected technologies:

```bash
# Search both plugin directories
for TECH in {data-layer} {logic-layer} {interface-layer}; do
  echo "=== Searching for $TECH plugins ==="

  # Public plugins
  if [ -d "$PLUGINS_PUBLIC_SOURCE_DIR" ]; then
    ls "$PLUGINS_PUBLIC_SOURCE_DIR" | grep -i "$TECH" || echo "  (none in public)"
  fi

  # Private plugins
  if [ -d "$PLUGINS_PRIVATE_SOURCE_DIR" ]; then
    ls "$PLUGINS_PRIVATE_SOURCE_DIR" | grep -i "$TECH" || echo "  (none in private)"
  fi
done
```

For each found plugin, read its `plugin.json` to get the name and classify by type (technology, process, stack).

Update `stack.json` `plugins` arrays with found plugins.

Update `CLAUDE.md` Installed Plugins section with plugin names and descriptions.

Report:
```
Plugins found:
  technology: directus-dev, nextjs-dev, nextjs-provision, vercel
  stack: stack-directus-nextjs-dev

Plugins NOT found:
  (none — all technologies have matching plugins)

  OR:

  nuxt — no plugin found. Create with: /plugin-creator:create
```

## Step 8: Validate

Run the validate skill to check the generated template:

Read `${CLAUDE_PLUGIN_ROOT}/skills/validate/SKILL.md` and execute all checks against the new template directory.

Fix any issues found before proceeding.

## Step 9: Initial Commit

```bash
cd "$NEW_DIR"
git add -A
git commit -m "feat: scaffold $NEW_NAME from $PARENT_NAME

Level $LEVEL template for $STACK_DESCRIPTION.
Technologies: $DATA_LAYER + $LOGIC_LAYER + $INTERFACE_LAYER.
Plugins: $PLUGIN_LIST."
```

Present summary:
```
Template created: {new-name}
  Location: $PROJECT_TEMPLATES_DIR/{new-name}
  Level: {level}
  Parent: {parent-name}
  Stack: {stack-name}
  Plugins: {count} found, {count} missing

Next steps:
  1. Review generated files
  2. Install listed plugins (if not already installed)
  3. Push to GitHub: git remote add origin git@github.com:stackmakers-ai/{new-name}.git && git push -u origin main
```
