---
name: setup
description: This skill should be used when the user asks "what is macstack.json", "set up macstack", "check macstack setup", "verify macstack.json", "explain the macstack standard", or before any other macstack-dev skill runs in a project for the first time. Explains the standard, locates the schema and category registry, and verifies tooling.
---

# MACSTACK Setup & Orientation

macstack.json is the standardized JSON file of the MACSTACK framework (Multi-Agent
Composable Stacks). It lives in the **root of a Claude project** and is at once: the
business spec (goals, results), the technical spec (software, entities, interfaces,
workflows) and the meta-config from which project files are scaffolded. `CLAUDE.md`
references it — never duplicates it.

## Canonical resources (GitHub-first, bundled fallback)

The standard is hosted on GitHub — always prefer the live copies (they may be newer
than the bundled ones); fall back to the bundled copies offline:

| Resource | Live (canonical) | Bundled fallback |
|---|---|---|
| JSON Schema | `https://raw.githubusercontent.com/macstacks/macstack/main/schema/macstack.schema.json` | `${CLAUDE_PLUGIN_ROOT}/skills/lint/references/macstack.schema.json` |
| Category registry | `https://raw.githubusercontent.com/macstacks/registry/main/software-categories.json` | `${CLAUDE_PLUGIN_ROOT}/skills/lint/references/software-categories.json` |
| Reusable blocks (software passports, entity/trigger/agent templates) | `https://github.com/macstacks/registry` (`software/`, `entities/`, `triggers/`, `agents/`) | — |
| Full examples + reference linter | `https://github.com/macstacks/macstack` (`examples/`, `scripts/lint.py`) | — |

Every macstack.json should start with `"$schema":
"https://raw.githubusercontent.com/macstacks/macstack/main/schema/macstack.schema.json"`
— editors then autocomplete and validate live.

Read the schema's top-level `description` first — it encodes the section order
(result-first): goals → results → processes → triggers → workflows → software →
entities → interfaces → connections → agents → context → resources.

## Core concepts (30 seconds)

- **Result-first**: every stack starts from goals/results in money terms; a process
  without a result is "coding for coding's sake".
- **prototype**: a parent macstack.json (GitHub repo `github:owner/repo` or a local
  absolute path). The child extends/overrides it — merge by `id`.
- **stacks**: organization composition — one `root` stack + `substacks`.
  Cross-stack refs use `<stack-id>:<element-id>`.
- **software[]**: every piece of software with mandatory `category` (registry) and
  `type` (ready_made | constructor | framework | library | custom), strict layers
  (data | logic | interface | infrastructure), `instances[]` with URLs.
- **agents**: `stack_agents` (orchestrate the whole stack, read `.claude/`, may modify
  the stack) and `managed_agents` (model + instructions + tools; invoked via
  interface / workflow / trigger / api).
- **Secrets are NAMES only**: `resources.accesses[]` lists env keys (with `required`
  flag); values live in Infisical.

## Verification steps

1. **Tooling**: `python3 -c "import jsonschema"` (fallback: structural checks only),
   `jq --version`, `gh --version` (needed for discover-context and GitHub prototypes).
2. **Project state**: does `./macstack.json` exist?
   - Yes → validate it (`lint` skill) and report the stage (`lifecycle.stage`).
   - No → offer `init-project` (existing codebase) or `generate-stack` (from scratch).
3. **CLAUDE.md link**: check that CLAUDE.md contains a "Stack Specification" section
   pointing to macstack.json. If missing, offer to add:

```markdown
## Stack Specification
The business and technical specification of this project is **`macstack.json`**
(MACSTACK standard). Read it first: goals → results → processes → workflows →
software → entities → interfaces.
Never write code that contradicts macstack.json — update the specification first.
```

## Skill routing

| Task | Skill |
|---|---|
| macstack.json for an existing project | `init-project` |
| New stack from scratch from a request | `generate-stack` |
| Find plugins/prototypes | `discover-context` |
| Create the project's working files | `scaffold-project` |
| .infisical.json + .env.prod/.env.dev | `infisical-env` |
| Project rules and commands | `best-practices` |
| Validation | `lint` |
