# stack.json Schema Reference

## Full Schema

```json
{
  "stack": "string | null",
  "version": "string (semver)",
  "level": "number (0 | 1 | 1.5 | 2)",
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

## Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `stack` | Yes | Stack identifier. `null` at Level 0, `"{data}-{interface}"` at Level 1+ |
| `version` | Yes | Semver version (e.g., `"1.0.0"`) |
| `level` | Yes | Template hierarchy level: `0`, `1`, `1.5`, or `2` |
| `parent` | Yes | Parent template name. `null` at Level 0 only |
| `description` | Yes | Human-readable description of this template |
| `layers.data` | Yes | Data layer technologies as lowercase strings |
| `layers.logic` | Yes | Logic layer technologies as lowercase strings |
| `layers.interface` | Yes | Interface layer technologies as lowercase strings |
| `plugins.technology` | Yes | Required Technology plugin names (e.g., `"directus-dev"`) |
| `plugins.process` | Yes | Required Process plugin names |
| `plugins.stack` | Yes | Required Stack plugin names (e.g., `"stack-directus-nextjs-dev"`) |

## Examples

### Level 0 — Empty

```json
{
  "stack": null,
  "version": "1.0.0",
  "level": 0,
  "parent": null,
  "description": "Universal project template",
  "layers": {
    "data": [],
    "logic": [],
    "interface": []
  },
  "plugins": {
    "technology": [],
    "process": [],
    "stack": []
  }
}
```

### Level 1 — Directus + Next.js

```json
{
  "stack": "directus-nextjs",
  "version": "1.0.0",
  "level": 1,
  "parent": "project-template",
  "description": "Stack-specific template for Directus + Next.js projects",
  "layers": {
    "data": ["directus"],
    "logic": ["nextjs"],
    "interface": ["nextjs"]
  },
  "plugins": {
    "technology": ["directus-dev", "nextjs-dev", "nextjs-provision", "vercel"],
    "process": [],
    "stack": ["stack-directus-nextjs-dev"]
  }
}
```

### Level 1 — NocoDB + n8n + Nuxt

```json
{
  "stack": "nocodb-nuxt",
  "version": "1.0.0",
  "level": 1,
  "parent": "project-template",
  "description": "Stack template for NocoDB + n8n + Nuxt projects",
  "layers": {
    "data": ["nocodb"],
    "logic": ["nuxt", "n8n", "trigger-dev"],
    "interface": ["nuxt"]
  },
  "plugins": {
    "technology": ["nocodb-dev", "n8n-ops", "trigger-dev-dev"],
    "process": [],
    "stack": []
  }
}
```

Note: Nuxt appears in both `logic` and `interface` because it handles server routes/API endpoints (logic) and Vue SSR rendering (interface).

### Level 2 — Client Project

```json
{
  "stack": "directus-nextjs",
  "version": "1.0.0",
  "level": 2,
  "parent": "project-directus-nextjs",
  "description": "ACME corporate website built on Directus + Next.js",
  "layers": {
    "data": ["directus"],
    "logic": ["nextjs"],
    "interface": ["nextjs"]
  },
  "plugins": {
    "technology": ["directus-dev", "nextjs-dev", "nextjs-provision", "vercel"],
    "process": ["plane-ops"],
    "stack": ["stack-directus-nextjs-dev"]
  }
}
```

## Validation Rules

1. `stack` must be `null` if and only if `level` is `0`
2. `parent` must be `null` if and only if `level` is `0`
3. At Level 1+, at least one layer must have technologies
4. At Level 1+, `plugins.technology` should list at least one plugin
5. Plugin names must match Agents Store naming: `{tool}-{process}` for technology, `stack-{name}-{process}` for stack
6. Layer values should be lowercase technology identifiers
7. Full-stack frameworks (Next.js, Nuxt, SvelteKit, Remix) must appear in BOTH `logic` and `interface` layers — they serve as backend (API routes, server middleware) and frontend (SSR/CSR rendering) simultaneously
