---
name: best-practices
description: This skill should be used when the user asks to "install best practice rules", "set up project rules", "add project rules and commands", "set up project conventions", or scaffold-project reaches the rules step. Installs the proven MACSTACK rule set (.claude/rules) and core commands into a project.
---

# Install Best-Practice Rules & Commands

Every MACSTACK project ships the same battle-tested `.claude/rules/` set and core
commands (proven in a production orchestrator). Install them at scaffold time; adapt
wording to the project, never drop a rule silently.

## Mandatory `.claude/rules/`

Create each file; content = a short version of the rule + the WHY:

1. **`safety.md`** — Never: commit secrets (`.env`, tokens, `.mcp.json` with values),
   `any` in TypeScript, display names instead of resource IDs in MCP calls, deleting
   production data without confirmation, hardcoded URLs/tokens. Always: validate at
   boundaries, handle 401/404/429/500 on external calls, env vars for credentials,
   `created_at`/`updated_at` on every table, batch endpoints for >10 records.
2. **`secrets-env-sync.md`** — Infisical = the source of truth; local `.env*` are
   working copies; changed env → `/secrets-push`; before a deploy/push →
   `/env-audit`; push is an upsert (never deletes); never commit `.env*` (see the
   `infisical-env` skill).
3. **`commit-after-task.md`** — Conventional Commits (`type(scope): summary`), small
   frequent commits after each finished unit of work; body explains WHAT/WHY;
   committing ≠ pushing (pushing is a separate explicit action).
4. **`search-first.md`** — Part A: reuse before building (codebase → dependencies →
   from scratch); Part B: 2+ failed attempts / unfamiliar API → search official docs
   (Context7 → llms.txt → web), do not keep guessing.
5. **`external-api-docs.md`** — before writing code against a third-party SDK/API,
   verify usage against official docs (an llms.txt map of the stack's services);
   training data goes stale.
6. **`project-conventions.md`** — naming: TS PascalCase/camelCase/kebab files; DB
   snake_case, FK `{table}_id`, booleans `is_*/has_*`, timestamps `*_at`; workflows
   `[Domain] - [Action] - [Trigger]`; kebab API URLs.
7. **`macstack-sync.md`** (specific to the standard) — macstack.json is a living
   specification: any stack change (new software/workflow/entity/interface) is
   accompanied by a macstack.json update + `lint` in the same commit; the definition
   of done includes the spec sync.

If the project deploys to a PaaS (dokploy/coolify) — also add `deploy-verify.md`
(a deploy is done only when the build is done + containers are healthy + logs are
clean + the domain returns 200).

## Mandatory `.claude/commands/`

| Command | What it does |
|---|---|
| `commit.md` | Conventional commit per the commit-after-task rule |
| `pr.md` | Create a PR (body: what/why, work-item link) |
| `secrets-sync.md`, `secrets-push.md`, `env-audit.md`, `setup-tokens.md` | from the `infisical-env` skill |
| `update-context.md` | update macstack.json + CLAUDE.md + .env.example after stack changes (sync analog) |
| `macstack-lint.md` | run the `lint` skill |

## CLAUDE.md wiring

Ensure CLAUDE.md: (1) has the "Stack Specification" section → macstack.json;
(2) lists the rules as MANDATORY, one line each; (3) stays short (<100 lines) —
details live in rules/skills/macstack.json, not in CLAUDE.md.

## Rules for applying

- Idempotent: an existing rule file with local edits is never overwritten — show a
  diff instead.
- Rules are project files (committed); the plugin only installs their initial
  versions.
