---
name: scaffold-project
description: This skill should be used when the user asks to "scaffold the project from macstack.json", "create the project working files", "generate project files from the spec", "build the project from macstack.json", or after a macstack.json is validated and the working tree must be built. Creates project files strictly in the prototype → stack plugins → dev plugins order.
---

# Scaffold Project Files From macstack.json

Turn a validated macstack.json into a working Claude project. The knowledge-source
order below is MANDATORY — it prevents reinventing what the ecosystem already
standardized. Each source overrides generic defaults; later sources fill what earlier
ones did not.

## THE ORDER (never violate)

### 1. PROTOTYPE FIRST — `macstack.json.prototype`

If `prototype` is set, resolve and study it BEFORE writing any file:

- `github:owner/repo[#ref]` or an https URL → shallow clone:
  `git clone --depth 1 https://github.com/owner/repo "$TMP/proto"`
- An absolute path (`/Users/...`) → a local folder, read it directly.
- Folder/repo → the root `macstack.json`; merge-by-id yields the inherited content.

From the prototype take (copy, then adapt): directory layout, `docker-compose.yml`,
config files (trigger.config.ts, next.config.ts…), `scripts/`, `.claude/`
(rules/commands/skills), `.env.example`, the CLAUDE.md skeleton, `.gitignore`.
The prototype is the ground truth for HOW this stack is assembled — its files beat
any generic template. Prototype chains resolve recursively (the child wins).

### 2. STACK PLUGINS SECOND — `context.plugins.stack[]`

Plugins with the **stack** prefix describe the ARCHITECTURE of the bundle: layers,
integration patterns (a-to-b data flows), decision frameworks, `.mcp.json` with
`${VAR}`, `templates/.env.example`, `templates/CLAUDE.md.template`.

- Install/enable them in `.claude/settings.json` → `enabledPlugins`
  (`"<plugin>@<marketplace>": true`).
- Generate the project's `.mcp.json` from the stack plugin's template (or from
  `connections.mcp` in macstack.json when no stack plugin exists) — `${VAR}`
  placeholders, NEVER values.
- Architecture rules from the stack plugin's CLAUDE.md.template merge into the
  project CLAUDE.md.

### 3. DEV PLUGINS THIRD — `context.plugins.technology[]`

`{tool}-dev` plugins define HOW to build with each software in the architecture
(SDK patterns, API usage, gotchas). Enable them, and follow their conventions when
writing the initial code stubs (e.g.: Directus SDK `cache: 'no-store'`; Trigger.dev
v4 imports from `@trigger.dev/sdk/v3`). Do not copy their content into the project —
plugins own tool knowledge; the project only references them.

### 4. Only then — generate project files

Backed by sources 1→3, create:

| Artifact | Source |
|---|---|
| Software skeletons (`nextjs` listed → Next.js scaffold; `trigger-dev` → trigger.config.ts + `src/trigger/`) | prototype, then dev plugins |
| `CLAUDE.md` ("Stack Specification" section → macstack.json; Tech Stack from software; Installed Plugins from context.plugins) | prototype + stack plugin template |
| `.mcp.json` (`${VAR}`) | stack plugin / connections |
| `.env.example`, **`.env.prod`, `.env.dev`** (always created), `.infisical.json` | the `infisical-env` skill (mandatory to invoke) — variables = union of macstack.json `resources.accesses` AND the `${VAR}` tokens required by the project's enabled Claude plugins (settings.json → stack plugin `.mcp.json`/`.env.example`); required-but-empty keys appear as `KEY=''` with a FILL ME comment |
| `.claude/rules/`, `.claude/commands/`, `scripts/` | the `best-practices` skill (mandatory to invoke) |
| `macstack/` (README.md, client/OVERVIEW.md, USER-CASES.md, UX-UI.md, AUTOMATION.md, HANDBOOK.md, OPEN-QUESTIONS.md, history/DECISIONS.md, ledger.jsonl) | the `documents` skill (mandatory to invoke) |
| Workflow stubs (from `workflows[]` + `triggers[]`) and entity schemas/migrations | macstack.json + dev plugins |

## Rules

- **`"$schema"` first**: ensure macstack.json starts with `"$schema":
  "https://raw.githubusercontent.com/macstacks/macstack/main/schema/macstack.schema.json"`
  so editors validate live.
- **Idempotency**: a re-run only adds what is missing and NEVER overwrites user
  code (existing file with differences → show a diff and ask).
- **`macstack/` is never overwritten by a prototype**: a prototype may seed
  `macstack/README.md` and nothing else — a parent's cases and open questions
  belong to the parent project, not this one.
- **No secrets in files**: key names only; values arrive via `infisical-env`.
- Every generated piece must trace to macstack.json (a software/workflow/entity id) —
  a file bound to nothing is "coding for coding's sake"; do not create it.
- After scaffolding run `lint` again and report: files created, what came from the
  prototype / stack plugin / dev plugins, what remains manual (open_questions).

<example>
user: "Scaffold the project from macstack.json"
→ prototype github:<owner>/project-directus-nextjs-trigger-dev → clone, copy
  compose/scripts/.claude/layout
→ stack plugin stack-directus-nextjs-trigger-dev → enabledPlugins + .mcp.json (${VAR}) + CLAUDE.md merge
→ dev plugins directus-dev, nextjs-dev, trigger-dev → enable, follow their conventions in stubs
→ files: src/trigger/<wf-id>.ts per workflows[], collection schemas per entities[]
→ infisical-env → best-practices → documents → lint → report
</example>
