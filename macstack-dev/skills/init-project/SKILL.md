---
name: init-project
description: This skill should be used when the user asks to "create macstack.json in this project", "add macstack.json", "init macstack", "describe this existing project as macstack.json", or an existing codebase has no macstack.json. Audits the existing project and produces a validated macstack.json draft.
---

# Init macstack.json in an Existing Project

Create macstack.json for a project that already has code. The file must describe
reality, not aspiration: audit first, write second, ask the user only what cannot be
derived.

## Step 1 — Audit the codebase (evidence, not guesses)

Scan in this order and map findings to macstack.json sections:

| Source | What it yields |
|---|---|
| `package.json` / `requirements.txt` / `pyproject.toml` / `composer.json` | `software[]` candidates (frameworks, libraries) |
| `docker-compose.yml` (services + images) | self-hosted `software[]` + `instances[]` (ports, env names) |
| `.mcp.json` | `connections.mcp[]` (servers, transports, `${VAR}` → url_env). SECURITY: any HARDCODED token/key found here → flag as an open_question (rotate + move to `${VAR}`) |
| `.env.example` / `.env` (key NAMES only, NEVER values) | `resources.accesses[]` |
| `.claude/settings.json` enabledPlugins | `context.plugins` |
| `.infisical.json`, `.dokploy.json`, `.plane.json` | `resources.bindings` |
| DB schemas / Directus collections / NocoBase collections / migrations | `entities[]` (attributes, master) |
| `src/trigger/`, n8n exports, Flows | `workflows[]` + `triggers[]` |
| App Router pages / admin panels / bots | `interfaces[]` (path relative to the instance!) |
| README, CLAUDE.md, docs/ | description, goals/results draft |

Classification rules for layers: full-stack frameworks (nextjs, django) → logic +
interface; BaaS/headless CMS (directus, nocodb, supabase) → data; job runners
(trigger-dev, n8n, bullmq) → logic; Docker/CI/Terraform → infrastructure.

## Step 2 — Ask the user ONLY the business gaps

The audit yields the technical half. The business half must come from the user —
ask in ONE compact message:

1. What are the project's **goals** (1–3, with a horizon)?
2. What **results** must it produce (measurable: $, leads/mo, hours saved)?
   What **problem** does each result close?
3. Who is the **client/organization** (`identity.client`, `identity.organization`)?
   Is there an organization root stack (→ `stacks.role: substack`)?
4. What **prototype** (parent template) was the project built from, if any?

## Step 3 — Write the draft

- Fill sections in the schema's canonical order. Mark everything not confirmed by
  code or user as `"status": "planned"` and list uncertainties in
  `lifecycle.open_questions[]`.
- Every entity MUST get `master` (which software/instance owns it). If two stores
  exist and the master is unclear — that is an open question for the user, never a
  silent guess (a wrong master means data corruption later).
- `software[].category` — from the bundled registry; `type` — mandatory;
  slugs kebab-case (`trigger-dev`, not `trigger.dev`; `postgresql`, not `postgres`).
- Triggers: extract cron/webhook/db-event configs into the top-level `triggers[]`
  collection; workflows reference them by id.
- Do NOT invent goals/results the user did not confirm — a spec that lies is worse
  than an incomplete one.

## Step 4 — Validate and wire

1. Run the `lint` skill (schema + referential integrity). Fix every error.
2. Add the CLAUDE.md reference section (see the `setup` skill).
3. Offer next steps: `infisical-env` (if accesses exist), `best-practices`
   (rules/commands), `discover-context` (find plugins for the detected software).

<example>
user: "Add macstack.json to this project (a Directus + Next.js website)"
→ audit: docker-compose (directus, postgres), package.json (next), .mcp.json (directus mcp),
  src/trigger absent → no trigger-dev
→ ask: goals/results/client/prototype
→ write macstack.json: software [directus (cms/constructor/data), nextjs (frontend-frameworks/framework/logic+interface)],
  entities from Directus collections with master=directus, interfaces site (path "/") + cms-admin (path "/admin")
→ lint → CLAUDE.md section → offer infisical-env
</example>
