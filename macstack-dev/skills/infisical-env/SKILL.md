---
name: infisical-env
description: This skill should be used when the user asks to "set up Infisical for this project", "create .infisical.json", "pull the env keys", "wire the env", "sync secrets", or scaffold-project reaches the env step. Creates .infisical.json, pulls .env.prod/.env.dev, ensures every key from macstack.json resources.accesses exists, and installs the mandatory secrets scripts and commands.
---

# Infisical & Env Wiring (the mandatory secrets loop)

Every MACSTACK project keeps secrets in **Infisical** (the source of truth); local
`.env*` files are working copies. macstack.json's `resources.accesses[]` is the
canonical list of key NAMES. This skill wires the three together. Values NEVER appear
in git or in macstack.json.

## Step 1 — `.infisical.json` (mandatory binding, committed)

Create in the project root:

```json
{
    "workspaceId": "<UUID of the Infisical project>",
    "defaultEnvironment": "prod",
    "gitBranchToEnvironmentMapping": null
}
```

- Workspace does not exist yet → create it in the Infisical UI/CLI (name =
  `identity.name` from macstack.json) and record its ID. `.infisical.json` is NOT a
  secret — it is a committed binding (like .dokploy.json).
- The Infisical domain comes from the organization's registry (root stack /
  projects.json, `infisical.domain`) — never hardcode it in scripts.

## Step 2 — collect the required variables from TWO sources

`.env.prod` and `.env.dev` are ALWAYS created, and their variable set is the union
of two sources (missing either source produces a stack that "deploys but breaks at
runtime"):

**Source A — the project architecture**: `macstack.json` → `resources.accesses[]`
(every key, with its `required` flag, `for`, `provided_by`).

**Source B — the project's Claude plugins (project scope)**: the plugins enabled in
`.claude/settings.json` → `enabledPlugins` need their own env tokens to work:

1. For each enabled **stack plugin**, read its `.mcp.json` and `templates/.env.example`
   — every `${VAR}` placeholder is a required variable (that's how MCP connections
   resolve).
2. Scan the project's own `.mcp.json` for `${VAR}` placeholders.
3. Read the existing env block of `.claude/settings.local.json` — keys already wired
   there stay in the set.

Cross-check the two sources: a variable required by a plugin but absent from
`resources.accesses` → **add it to macstack.json accesses** in the same run (the
spec must stay the superset — macstack.json is the registry of the stack's tokens);
an access present in macstack.json but used by nothing → warning.

Then:

1. Generate `.env.example`: one `KEY=` line per variable with a comment
   (`# required|optional — for <software|plugin>, provided_by <us|client>`). Committed.
2. Ensure every `required: true` key EXISTS in Infisical (prod AND dev envs); create
   missing ones with an empty/placeholder value and list them for the user ("fill in
   Infisical"). Keys with `provided_by: "client"` go to `lifecycle.needs_from_client`.
3. Pull: `.env.prod` ⇄ Infisical prod, `.env.dev` ⇄ Infisical dev, `.env` = the
   working copy of prod. Variables that are required but still empty after the pull
   MUST appear in the files as `KEY=''` with a `# FILL ME (required — <reason>)`
   comment right above — an empty required variable must be visible, not absent.
   All three files gitignored (`.env*` catch-all + `!.env.example`).
4. Mirror the values into the env block of `.claude/settings.local.json` so the
   `${VAR}` placeholders of the project's `.mcp.json` resolve.

## Step 3 — mandatory scripts (battle-tested pattern)

Create `scripts/setup.sh` — pulls secrets from Infisical:

- Usage: `./scripts/setup.sh [env] [.env-file] [settings-file]`
  (default: `prod .env .claude/settings.local.json`; always refreshes the
  `.env.prod` and `.env.dev` snapshots).
- Fetch as JSON (`infisical secrets -o json`) and render `KEY='value'` —
  **single quotes** keep `$ # & =`, spaces, base64, JWT dots and multiline PEM
  intact; an embedded quote is escaped the POSIX way `'\''`.
- **Instance switching**: the Infisical CLI keeps a separate login per self-hosted
  instance, but only ONE is active; before reading, check the active domain and, on
  mismatch, run `infisical login --domain=<domain>` (the --domain flag is IGNORED on
  authenticated reads!).
- **Guard**: on a failed fetch NEVER wipe the existing .env (write to a temp file
  first, then mv on success).
- Also mirrors the values into the `.claude/settings.local.json` env block (so the
  `${VAR}` placeholders in .mcp.json resolve).

Create `scripts/secrets-push.sh [--yes]` — the reverse flow: local `.env.prod`/
`.env.dev` → Infisical **upsert** (never deletes; dry-run without `--yes`).

Create `scripts/env-audit.sh` — reconciliation: macstack.json accesses ⇄ Infisical ⇄
`.env*` (+ deploy targets if any): a missing required key = error.

## Step 4 — mandatory commands and rule

`.claude/commands/`:

| Command | Body |
|---|---|
| `secrets-sync.md` | `Run ./scripts/setup.sh prod .env .claude/settings.local.json and report` (description: Pull Infisical → .env/.env.prod/.env.dev) |
| `secrets-push.md` | dry-run by default, `--yes` to write; upsert, never deletes |
| `env-audit.md` | reconcile keys macstack.json ⇄ Infisical ⇄ .env |
| `setup-tokens.md` | first-time setup: login + first pull |

`.claude/rules/secrets-env-sync.md` (installed by the `best-practices` skill):
Infisical is the truth; changed .env → `/secrets-push`; before a deploy/push →
`/env-audit`; NEVER commit `.env*`.

## Step 5 — verify

`/secrets-sync` completes; `.env.prod` contains every required key from
macstack.json (empty ones are listed for the user); `git status` shows no `.env*`
except `.env.example`; the `${VAR}` placeholders in `.mcp.json` resolve from
settings.local.json.

<example>
user: "Wire Infisical into this project"
→ .infisical.json (workspaceId of the new "nova-website" workspace)
→ .env.example from 6 accesses (MAILGUN_* marked required:false, provided_by:client)
→ scripts/setup.sh + secrets-push.sh + env-audit.sh, 4 commands
→ /secrets-sync → .env.prod: 4/6 filled, MAILGUN_* empty → into needs_from_client
</example>
