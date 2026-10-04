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

### Plugin Naming

The names listed in `stack.json` `plugins` are Agents Store plugin names:

| Plugin type | Pattern | Examples |
|-------------|---------|----------|
| Technology | `{tool}-{process}` (`dev`, `ops`, `provision`) | `directus-dev`, `vercel-dev`, `trigger-dev` |
| Stack | `stack-{name}` — no process suffix | `stack-directus-nextjs` |

Take names from the marketplace listing or the plugin's `plugin.json`, never from memory: renamed plugins keep working through the marketplace `renames` map, but new templates should use the current name.

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
| `plugins.stack` | string[] | Required Stack plugins (e.g., ["stack-directus-nextjs"]; named `stack-{name}`, no process suffix) |

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
    "technology": ["directus-dev", "nextjs-dev", "nextjs-provision", "vercel-dev"],
    "process": [],
    "stack": ["stack-directus-nextjs"]
  }
}
```

**Level 1.5:**
```jsonc
{
  "stack": "directus-nextjs",
  "level": 1.5,
  "parent": "project-directus-nextjs",
  ...
}
```

**Level 2:**
```jsonc
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

The 100-line limit is this template system's own rule; Anthropic's guidance is under 200 lines per CLAUDE.md file. Count the content CLAUDE.md imports too (`@AGENTS.md`): imported files load at launch together with the importing file.

### AGENTS.md and CLAUDE.md

One source of truth. `AGENTS.md` holds the rules every coding tool reads (Cursor, Gemini, Codex, ...). `CLAUDE.md` starts with an `@AGENTS.md` import and adds the Claude-specific lines below it; a symlink (`ln -s AGENTS.md CLAUDE.md`) also works when there is nothing Claude-specific. Claude Code reads `AGENTS.md` directly only when no `CLAUDE.md` exists, so the import or symlink is what makes it load. Do not generate `AGENTS.md` from `CLAUDE.md`. `scripts/sync-context.sh` stays only to mirror the rules into `.cursor/`.

The section table below applies to the combined content: `CLAUDE.md` plus the `AGENTS.md` it imports.

### Required Sections

| Section | L0 | L1 | L1.5 | L2 |
|---------|----|----|------|----|
| Tech Stack | Placeholders | Filled | Inherited | Inherited |
| Architecture | `docs/architecture.md` (plain path) | `docs/architecture.md` (plain path) | Same | Same |
| Code Style | `docs/code-style.md` (plain path) | `docs/code-style.md` (plain path) | Same | Same |
| API Conventions | `docs/api-conventions.md` (plain path) | `docs/api-conventions.md` (plain path) | Same | Same |
| Installed Plugins | Placeholders | Listed with descriptions | Inherited | Extended |
| Quick Commands | Generic list | Stack-specific additions | Inherited | Custom additions |
| Project Config | Reference to skill | Reference to skill | Same | Same |
| Gotchas | — | Stack-specific warnings | Inherited | Extended |
| Critical Rules | Generic | Stack-specific additions | Inherited | Inherited |

### CLAUDE.md Quality Rules

- Under 100 lines total, imports included (internal rule; the official target is under 200)
- No placeholder text remaining ("TBD", "TODO", "fill in", "[e.g.,")
- Technologies in Tech Stack match stack.json `layers`
- Plugins in Installed Plugins match stack.json `plugins`
- Workflows in Quick Commands exist as `.claude/skills/<name>/SKILL.md` (older templates: `.claude/commands/<name>.md`)
- Point to long content by plain path (`docs/architecture.md`, read on demand) rather than inlining it. An `@docs/...` import does not save context: imported files load at launch with CLAUDE.md
- Rules that matter only for some files go in `.claude/rules/<name>.md` with a `paths:` frontmatter, which loads them only when Claude reads a matching file; CLAUDE.md and rules without `paths:` load every session

---

## .mcp.json and Claude Code Settings

| File | Committed | Content |
|------|-----------|---------|
| `.mcp.json` | yes | MCP servers with `${VAR}` references only (`${VAR:-default}` is allowed); empty `mcpServers` at Level 0 |
| `.claude/settings.json` | yes | `enabledPlugins` and `extraKnownMarketplaces`, derived from `stack.json` `plugins` |
| `.env`, `.env.local` | no | Real values for every `${VAR}` — shell tooling reads them |
| `.claude/settings.local.json` | no | `env` block with the same values for Claude Code; `settings.local.json.example` documents the keys |

Claude Code expands `${VAR}` in `command`, `args`, `env`, `url` and `headers` of `.mcp.json`. A literal URL is acceptable only for a published product endpoint that is the same for every user; a deployment host, token or key is always a `${VAR}`.

`.claude/settings.json` example (the marketplace entry is keyed by the marketplace's own name, plugins are `<plugin>@<marketplace>`):

```json
{
  "extraKnownMarketplaces": {
    "agents-store-claude-plugins": {
      "source": { "source": "github", "repo": "Agents-Store/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "directus-dev@agents-store-claude-plugins": true,
    "stack-directus-nextjs@agents-store-claude-plugins": true
  }
}
```

Committing `enabledPlugins` turns the plugins on for collaborators but does not download them: each collaborator runs `claude plugin install <name>@<marketplace> --scope project` once, and Claude Code asks to trust the repository before it registers the marketplace.

---

## GitHub Conventions

All template repos live under one GitHub organization, `$PROJECT_TEMPLATES_GITHUB_ORG` (here the fictional `acme-templates`):
- `git@github.com:acme-templates/project-template.git`
- `git@github.com:acme-templates/project-directus-nextjs.git`
- `git@github.com:acme-templates/demo-directus-nextjs.git`
- `git@github.com:acme-templates/{client}-{project}.git` (private repos)

### Commit Convention for Templates

```
feat({category}): {description}     # new skill, command, agent, rule
fix({category}): {description}      # fix existing content
chore({category}): {description}    # update deps, configs, docs
```

Categories: skill, command, agent, rule, docs, env, claude-md, readme, config
