# Conventions — Naming, stack.json, CLAUDE.md

## Naming Conventions

| Entity | Pattern | Examples |
|--------|---------|---------|
| Universal base (L0) | `project-template` | `project-template` |
| Stack template (L1) | `project-{stack}` | `project-directus-nextjs`, `project-nocodb-saas` |
| Demo (L1.5) | `demo-{stack}` | `demo-directus-nextjs` |
| Client project (L2) | `{client}-{project}` | `acme-website`, `globex-portal` |

### Prefix Rationale

- `project-*` — reusable stack templates, no client data
- `demo-*` — working showcase apps with sample data
- No prefix — client projects (unique, private)

### Stack Naming

The `{stack}` portion uses the primary technologies joined by hyphens: `{data}-{interface}` or `{primary-technology}`.

Examples: `directus-nextjs`, `nocodb-saas`, `supabase-nuxt`, `nocobase-crm`

---

## stack.json Schema

```json
{
  "stack": "string | null",
  "version": "semver string",
  "level": "0 | 1 | 1.5 | 2",
  "parent": "string | null",
  "description": "string",
  "layers": {
    "data": ["string"],
    "logic": ["string"],
    "interface": ["string"]
  },
  "plugins": {
    "technology": ["string"],
    "process": ["string"],
    "stack": ["string"]
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `stack` | string/null | Stack identifier (null at Level 0) |
| `version` | string | Semver version of this template |
| `level` | number | Hierarchy level: 0, 1, 1.5, or 2 |
| `parent` | string/null | Name of the parent template (null at Level 0) |
| `description` | string | Human-readable description |
| `layers.data` | string[] | Data layer technologies (e.g., ["directus"]) |
| `layers.logic` | string[] | Logic layer technologies (e.g., ["nextjs"]) |
| `layers.interface` | string[] | Interface layer technologies (e.g., ["nextjs"]) |
| `plugins.technology` | string[] | Required Technology plugins (e.g., ["directus-dev", "nextjs-dev"]) |
| `plugins.process` | string[] | Required Process plugins |
| `plugins.stack` | string[] | Required Stack plugins (e.g., ["stack-directus-nextjs-dev"]) |

### Examples by Level

**Level 0:**
```json
{
  "stack": null,
  "version": "1.0.0",
  "level": 0,
  "parent": null,
  "layers": { "data": [], "logic": [], "interface": [] },
  "plugins": { "technology": [], "process": [], "stack": [] }
}
```

**Level 1:**
```json
{
  "stack": "directus-nextjs",
  "version": "1.0.0",
  "level": 1,
  "parent": "project-template",
  "layers": { "data": ["directus"], "logic": ["nextjs"], "interface": ["nextjs"] },
  "plugins": {
    "technology": ["directus-dev", "nextjs-dev", "nextjs-provision", "vercel"],
    "process": [],
    "stack": ["stack-directus-nextjs-dev"]
  }
}
```

**Level 1.5:**
```json
{
  "stack": "directus-nextjs",
  "level": 1.5,
  "parent": "project-directus-nextjs",
  ...
}
```

**Level 2:**
```json
{
  "stack": "directus-nextjs",
  "level": 2,
  "parent": "project-directus-nextjs",
  ...
}
```

---

## CLAUDE.md Structure

CLAUDE.md serves as the project memory for Claude Code. Keep it under 100 lines.

### Required Sections

| Section | L0 | L1 | L1.5 | L2 |
|---------|----|----|------|----|
| Tech Stack | Placeholders | Filled | Inherited | Inherited |
| Architecture | `@docs/architecture.md` | `@docs/architecture.md` | Same | Same |
| Code Style | `@docs/code-style.md` | `@docs/code-style.md` | Same | Same |
| API Conventions | `@docs/api-conventions.md` | `@docs/api-conventions.md` | Same | Same |
| Installed Plugins | Placeholders | Listed with descriptions | Inherited | Extended |
| Quick Commands | Generic list | Stack-specific additions | Inherited | Custom additions |
| Project Config | Reference to skill | Reference to skill | Same | Same |
| Gotchas | — | Stack-specific warnings | Inherited | Extended |
| Critical Rules | Generic | Stack-specific additions | Inherited | Inherited |

### CLAUDE.md Quality Rules

- Under 100 lines total
- No placeholder text remaining ("TBD", "TODO", "fill in", "[e.g.,")
- Technologies in Tech Stack match stack.json `layers`
- Plugins in Installed Plugins match stack.json `plugins`
- Commands in Quick Commands exist as files in `.claude/commands/`
- Reference `@docs/` files rather than inlining long content

---

## GitHub Conventions

All template repos live under the `stackmakers-ai` GitHub organization:
- `git@github.com:stackmakers-ai/project-template.git`
- `git@github.com:stackmakers-ai/project-directus-nextjs.git`
- `git@github.com:stackmakers-ai/demo-directus-nextjs.git`
- `git@github.com:stackmakers-ai/{client}-{project}.git` (private repos)

### Commit Convention for Templates

```
feat({category}): {description}     # new skill, command, agent, rule
fix({category}): {description}      # fix existing content
chore({category}): {description}    # update deps, configs, docs
```

Categories: skill, command, agent, rule, docs, env, claude-md, readme, config
