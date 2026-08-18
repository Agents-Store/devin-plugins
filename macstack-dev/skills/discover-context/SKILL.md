---
name: discover-context
description: This skill should be used when the user asks to "find plugins for this stack", "discover context for the project", "which plugins should I install", "find a prototype", "pick a stack prototype", or when init-project/generate-stack need context.plugins and prototype candidates. Searches Agents Store plugins and stackmakers-ai prototypes on GitHub.
---

# Discover Context: Plugins & Prototypes

Find the context a project needs: reusable blocks from the MACSTACK registry, Claude
plugins in the Agents Store, and prototype repositories in stackmakers-ai. The output
fills `software[]`, `context.plugins` and `prototype` in macstack.json.

## Source 0 — the MACSTACK registry (reusable blocks)

Before writing any `software[]`/`entities[]`/`triggers[]` entry by hand, check
`https://github.com/macstacks/registry` — copying a maintained block beats retyping
(fewer taxonomy mistakes, ratings already consistent):

```bash
# A software passport (stack-independent half of a software[] entry):
curl -fsSL https://raw.githubusercontent.com/macstacks/registry/main/software/directus.json
# Entity/trigger/agent templates:
curl -fsSL https://raw.githubusercontent.com/macstacks/registry/main/entities/client.json
curl -fsSL https://raw.githubusercontent.com/macstacks/registry/main/triggers/trg-nightly-cron.json
curl -fsSL https://raw.githubusercontent.com/macstacks/registry/main/agents/support-agent.json
# What exists:
gh api repos/macstacks/registry/contents/software -q '.[].name'
```

Copy the passport into macstack.json and add only the stack-specific half (role,
value, hosting, instances, cost); for entities add stores + master; in trigger/agent
presets replace the `<placeholders>`. Full examples of finished files live in
`https://github.com/macstacks/macstack/tree/main/examples`.

## Source 1 — Agents Store plugins

Registry: `https://github.com/agents-store/claude-plugins` (public marketplace).
The machine-readable index is `.claude-plugin/marketplace.json` in the repo root:

```bash
# Full list of marketplace plugins (name, description, keywords, category)
curl -s https://raw.githubusercontent.com/agents-store/claude-plugins/main/.claude-plugin/marketplace.json \
  | jq -r '.plugins[] | "\(.name)\t\(.description)"'
# Or via gh (when private access is configured):
gh api repos/agents-store/claude-plugins/contents/.claude-plugin/marketplace.json \
  -q .content | base64 -d | jq '.plugins[].name'
```

Matching rule — derive plugin names from macstack.json `software[]`:

- For every software look for `{tool}-dev` (development), `{tool}-ops` (data
  operations), `{tool}-provision` (schema/roles/setup). Example: directus →
  `directus-dev`.
- For the layer bundle look for a stack plugin `stack-{name}-{process}` (e.g.
  `stack-directus-nextjs-trigger-dev`, `stack-composable-stack-v1`) — it carries
  `.mcp.json`, `.env.example` and the integration skills.
- Plugin not found → record the gap in `lifecycle.open_questions` ("no plugin X —
  create it via plugin-creator"); NEVER invent a name inside context.plugins.

Fill `context.plugins`: `{technology: [...], process: [...], stack: [...]}` and
`context.marketplaces: ["agents-store-claude-plugins"]`.

## Source 2 — stackmakers-ai prototypes

Registry: `https://github.com/orgs/stackmakers-ai/repositories`.

```bash
gh api "orgs/stackmakers-ai/repos?per_page=100" -q '.[] | .name + "\t" + (.description // "")'
```

Prototype naming convention:

| Pattern | What it is |
|---|---|
| `project-template` | universal base (Level 0) |
| `project-{stack}` | stack template: project-composable-stack-v1, project-directus-nextjs, project-directus-nextjs-trigger-dev, project-flask-sqlalchemy |
| `demo-{stack}` | demo with seed data |
| `{client}-{stack}` | client projects (examples of real assemblies) |
| `*-workspace-*` | Agents Workspace (root-stack candidate) |

Selection rule: pick the prototype whose stack matches the chosen software layers;
prefer `project-*` templates over client repos. Set in macstack.json:
`"prototype": "github:stackmakers-ai/<repo>"`. A local clone works too:
`"prototype": "/Users/<me>/STACKS/<repo>"` — both forms are valid.

Check whether the prototype repo has its own `macstack.json` (the new standard) —
inherit via merge-by-id; if it only has a legacy `stack.json`, treat it as a
scaffold source only and note that in open_questions.

## Output

Report a compact table: software → found dev/ops/provision plugins → stack plugin →
selected prototype (+ alternatives). Then update macstack.json (`context.plugins`,
`prototype`) and validate with `lint`.

<example>
user: "Pick the context for a directus+nextjs+trigger-dev stack"
→ marketplace.json: directus-dev ✓, nextjs-dev ✓, nextjs-provision ✓, trigger-dev ✓, seo-dev ✓,
  stack-directus-nextjs-trigger-dev ✓
→ prototypes: project-directus-nextjs-trigger-dev (template) — selected; demo: demo-directus-nextjs
→ macstack.json: prototype + context.plugins filled, lint OK
</example>
