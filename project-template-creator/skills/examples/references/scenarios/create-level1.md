# Scenario: Create a Level 1 Stack Template

## Setup

You want to create a new stack template for Supabase + Nuxt projects. No such template exists yet.

## Walkthrough

### 1. User invokes create

```
/project-template-creator:create Level 1 template for Supabase + Nuxt
```

### 2. Plugin gathers information

From the request and follow-up questions:
- **Level:** 1 (stack template)
- **Stack:** `supabase-nuxt`
- **Technologies:**
  - Data: Supabase
  - Logic: Nuxt (server routes), Trigger.dev (background jobs)
  - Interface: Nuxt (Vue frontend)
- **Parent:** `project-template` (default for Level 1)

### 3. Plugin generates name

Name: `project-supabase-nuxt`
User confirms.

### 4. Plugin clones parent

```bash
# Parent found at $PROJECT_TEMPLATES_DIR/project-template/
git clone "$PROJECT_TEMPLATES_DIR/project-template" "$PROJECT_TEMPLATES_DIR/project-supabase-nuxt"
cd "$PROJECT_TEMPLATES_DIR/project-supabase-nuxt"
rm -rf .git && git init
git remote add origin git@github.com:stackmakers-ai/project-supabase-nuxt.git
```

### 5. Plugin customizes stack.json

```json
{
  "stack": "supabase-nuxt",
  "version": "1.0.0",
  "level": 1,
  "parent": "project-template",
  "description": "Stack template for Supabase + Nuxt projects",
  "layers": {
    "data": ["supabase"],
    "logic": ["nuxt", "trigger-dev"],
    "interface": ["nuxt"]
  },
  "plugins": {
    "technology": ["trigger-dev-dev"],
    "process": [],
    "stack": []
  }
}
```

### 6. Plugin customizes CLAUDE.md

```markdown
# Supabase + Nuxt Stack Template

Level 1 stack template. Fork this for client projects (Level 2).

## Tech Stack
- Data: Supabase (PostgreSQL, Auth, Storage, Realtime)
- Logic: Nuxt (server routes, API endpoints), Trigger.dev (background jobs)
- Interface: Nuxt (Vue 3, SSR/SSG)

## Installed Plugins
### Technology
- trigger-dev-dev — task definitions, SDK patterns, deployment

### Stack
- (none yet — create with /plugin-creator:create)

## Gotchas
- Supabase RLS: always enable Row Level Security on tables — open tables are a security risk
- Nuxt `useFetch` uses caching by default — use `{ server: true, lazy: false }` for fresh data
...
```

### 7. Plugin customizes .env.example

```bash
# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=

# Trigger.dev
TRIGGER_DEV_API_URL=http://localhost:3030
TRIGGER_DEV_API_KEY=
```

### 8. Plugin searches for matching plugins

```
Plugins found:
  technology: trigger-dev-dev

Plugins NOT found:
  supabase — no plugin found. Create with: /plugin-creator:create
  nuxt — no plugin found. Create with: /plugin-creator:create
```

### 9. Plugin validates

Runs validate skill. Passes with note about missing plugins.

### 10. Plugin commits

```bash
git add -A
git commit -m "feat: scaffold project-supabase-nuxt from project-template

Level 1 template for Supabase + Nuxt projects.
Technologies: Supabase + Nuxt + Trigger.dev.
Plugins: trigger-dev-dev (2 missing: supabase, nuxt)."
```

### 11. Summary

```
Template created: project-supabase-nuxt
  Location: $PROJECT_TEMPLATES_DIR/project-supabase-nuxt
  Level: 1
  Parent: project-template
  Plugins: 1 found, 2 missing (supabase, nuxt)

Next steps:
  1. Create missing plugins: supabase-dev, nuxt-dev
  2. Add stack-specific skills (new-page, new-api-route)
  3. Push to GitHub: git push -u origin main
```
