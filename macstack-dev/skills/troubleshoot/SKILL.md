---
name: troubleshoot
description: This skill should be used when the user reports "macstack lint fails", "prototype does not resolve", "env keys missing", "scaffold broke my files", "cross-stack reference does not work", or any macstack-dev skill errors out. Diagnoses the common failure modes of the macstack.json toolchain.
---

# Troubleshoot macstack-dev

## Lint failures

| Symptom | Cause → fix |
|---|---|
| `entity master problem` | master does not appear in stores exactly once with role=master → add a store with the master role or fix the `master` field |
| `category not in registry` | typo or a new niche → check `references/software-categories.json`; a new category = a kebab-case slug + a registry proposal (PR), never a silent custom value |
| `rating mismatch` | agentic.rating disagrees with the channels → rule: 3×true=full, 2=good, 1=basic, only "partial"=partial |
| `trigger unknown` | a workflow references a trigger code missing from `triggers[]` → triggers live ONLY in the collection, never inline |
| `delegation not downward` | an orchestrator appears in a worker's delegates_to → the hierarchy is strictly control_plane → orchestrator → worker |
| `cross-stack not declared` | the `foo:` prefix is not declared → add the stack to `stacks.root/substacks/links` |

## Prototype resolution

- `github:owner/repo` fails to clone → check `gh auth status` / repo visibility;
  private repos need a PAT. Fallback: ask the user for a local absolute path.
- The repo has no `macstack.json` → it is a legacy prototype (only `stack.json`):
  use its files for scaffolding, but there is nothing to inherit — record it in
  open_questions.
- A prototype cycle (A→B→A) → an error by design; break the chain.
- A local path inside a cloud-synced folder (iCloud/Drive) may hang on first read
  (file materialization) — retry, or copy the prototype to a regular folder.

## Infisical / env

- `infisical secrets` reads the wrong instance → the CLI ignores `--domain` on
  authenticated reads; only one instance is active — run
  `infisical login --domain=…` first.
- `.env` got wiped empty → setup.sh lacks the guard: fetch into a temp file, mv
  only on success. Restore by pulling from Infisical again.
- A required key exists in macstack.json but is empty after sync → it is missing in
  Infisical: create it there; `provided_by: client` → move to
  `lifecycle.needs_from_client`.
- Values with `$`/spaces break `source .env` → render `KEY='value'` in single
  quotes (embedded quote → `'\''`).

## Scaffold

- A user file got overwritten → an idempotency violation: an existing file with
  differences = diff + question, never a silent overwrite. Restore from git.
- Generated files contradict the architecture → the source order was violated:
  prototype → stack plugins → dev plugins; redo starting from the prototype.
- `${VAR}` from .mcp.json does not resolve → values must live in the env block of
  `.claude/settings.local.json` (filled by scripts/setup.sh), not inside .mcp.json.

## Discovery

- `curl raw.githubusercontent.com/...marketplace.json` → 404: the branch is not
  `main` or the repo is private → use
  `gh api repos/agents-store/claude-plugins/contents/...`.
- No plugin exists for a software → record the gap in open_questions + suggest
  creating it via plugin-creator; do NOT put a non-existent name into
  context.plugins.
