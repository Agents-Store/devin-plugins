---
name: infisical-env
description: This skill should be used when the user asks to "set up Infisical for this project", "create .infisical.json", "pull the env keys", "wire the env", "sync secrets", or scaffold-project reaches the env step. Creates .infisical.json, pulls .env.prod/.env.dev, ensures every key from macstack.json resources.accesses exists, and installs the mandatory secrets scripts and slash-command skills.
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
- **Instance selection — one named profile per instance** (Infisical CLI >= 0.43.134).
  A profile is one login: an account on one instance plus the organization it uses.
  Do not check "which instance is active" and re-login; keep every instance logged in
  as its own profile and let the CLI pick:
  - once per instance: `infisical login --save-as <profile> --domain=<domain>` (the
    domain is `infisical.domain` from the organization's registry);
  - once per project, in the project root: `infisical profile bind <profile>` — every
    command under that directory then selects the profile by itself. The binding lives
    in the user's CLI config, never in the repository;
  - `infisical profile current` prints which profile applies here and why — the
    script's pre-flight line, and what to run when a pull reads the wrong vault;
  - one terminal: `eval "$(infisical profile pin <profile>)"`; one command or a
    script: `--profile <profile>` or `INFISICAL_PROFILE` (`pin` only prints an
    `export` line). Order of precedence: `--profile`, `INFISICAL_PROFILE`, a bound
    directory, the default profile (`infisical profile use`).
- **Wrong-instance guard**: the instance itself is chosen by `--domain`, then
  `INFISICAL_DOMAIN`, then a `domain` field in `.infisical.json`, then US Cloud. After
  a user login a `--domain` / `INFISICAL_DOMAIN` that names a different instance than
  the profile in use makes the command FAIL instead of reading the wrong vault — so
  the script sets `INFISICAL_DOMAIN` (or passes `--domain`) from the registry value on
  every read; never a literal in the script. Keep `domain` out of the committed
  `.infisical.json` unless the team wants it there: anyone who can edit that file can
  redirect the CLI, and the CLI prints a warning naming the host each time it uses it.
- A CLI older than 0.43.134 has no `profile` command or `--profile` flag
  (`unknown command "profile"`) — upgrade it (`infisical --version`). Everything else
  about the Infisical CLI: the `infisical-dev` plugin, skill `cli-reference`.
- **No profile applies**: `infisical profile current` exits 1 with "No profile is
  selected" (a pinned name that does not exist prints `Status: profile does not exist`
  and exits 0 — treat that as no profile too). `setup.sh` then stops BEFORE the fetch,
  prints the two one-time commands above (`login --save-as …`, then `profile bind …`)
  and leaves the existing `.env` untouched; it never starts an interactive login itself.
- **Guard**: on a failed fetch NEVER wipe the existing .env (write to a temp file
  first, then mv on success).
- Also mirrors the values into the `.claude/settings.local.json` env block (so the
  `${VAR}` placeholders in .mcp.json resolve).

Create `scripts/secrets-push.sh [--yes]` — the reverse flow: local `.env.prod`/
`.env.dev` → Infisical **upsert** (never deletes; dry-run without `--yes`).

Create `scripts/env-audit.sh` — reconciliation: macstack.json accesses ⇄ Infisical ⇄
`.env*` (+ deploy targets if any): a missing required key = error.

## Step 4 — mandatory slash-command skills and rule

`.claude/skills/<name>/SKILL.md` — frontmatter `name` and `description`, then the body;
still typed as `/<name>`. The ones that write are manual and carry
`disable-model-invocation: true` (only the user types them); `env-audit` only reads, so
it stays model-invocable and Claude can run it when the rule below asks:

| Skill | Invocation | Body |
|---|---|---|
| `secrets-sync` | manual | `Run ./scripts/setup.sh prod .env .claude/settings.local.json and report` (description: Pull Infisical → .env/.env.prod/.env.dev) |
| `secrets-push` | manual | dry-run by default, `--yes` to write; upsert, never deletes |
| `env-audit` | model-invocable | reconcile keys macstack.json ⇄ Infisical ⇄ .env |
| `setup-tokens` | manual | first-time setup: named profile (`login --save-as`) + `profile bind` + first pull |

A project that already has these as `.claude/commands/<name>.md` keeps them (same
behaviour) — never add a second skill with the same name beside one.

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
→ .infisical.json (workspaceId of the new "acme-website" workspace)
→ .env.example from 6 accesses (MAILGUN_* marked required:false, provided_by:client)
→ scripts/setup.sh + secrets-push.sh + env-audit.sh, 4 skills under .claude/skills/
→ /secrets-sync → .env.prod: 4/6 filled, MAILGUN_* empty → into needs_from_client
</example>
