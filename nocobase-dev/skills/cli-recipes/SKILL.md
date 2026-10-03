---
name: cli-recipes
description: "Use when the user asks how to install or run NocoBase from the terminal — \"install nb CLI\", \"how do I bootstrap NocoBase\", \"run nb commands\", \"start/stop/upgrade NocoBase\", \"add an environment\", \"backup NocoBase\", \"enable a plugin\". Provides the install one-liner (`@nocobase/cli`, stable channel), the env, lifecycle, plugin and backup recipes in their `nb` 2.2 canonical forms, and a routing table that hands deeper tasks to the upstream `nocobase-env-manage`, `nocobase-plugin-manage`, and `nocobase-publish-manage` skills."
---

# nb CLI — install and recipes

The `nb` CLI is the canonical way to bootstrap and operate a NocoBase v2 project from a terminal. This skill covers install, the most-used commands in their canonical (2.2) spelling, and where to go for deeper topics. Command forms below were checked against `@nocobase/cli` 2.2.20; always confirm an exact flag with `nb <group> <command> --help` before relying on it.

## Install

```bash
npm install -g @nocobase/cli      # stable channel (`latest`)
nb --version
```

Requirements: **Node.js 22 or newer**, Yarn 1.x, npm, and Docker if you choose the Docker install source or the built-in database. pnpm is needed only when developing an AI Portal. To connect an agent to an existing NocoBase, the app must be **2.1.0 or newer**. If the install errors with `EACCES`, configure a user-level npm prefix (`npm config set prefix "$HOME/.npm-global"`) rather than running with `sudo`.

Channels: the stable `@nocobase/cli` (`latest`) is the default for everything in this plugin. The `@alpha` channel is needed only for `nb portal` (Portal lifecycle), which stable and beta do not contain — see `overview`. Update the CLI itself with `nb self check` / `nb self update`.

## Bootstrap a project

```bash
mkdir my-nocobase && cd my-nocobase
nb init --ui
```

`nb init --ui` opens a browser-based setup wizard. Its first step chooses *install a new app*, *manage a local app*, or *connect a remote app*. The CLI keeps the process running until the user finishes the wizard — set a 30-minute timeout and **do not interrupt** it. Terminal-only variants: `nb init` (interactive prompts) and `nb init --env <name> -y` (defaults, no prompts; add `--setup-mode connect-remote --api-base-url <https://host/api> --auth-type oauth` to connect an existing app instead of installing).

In a sandboxed environment where the CLI cannot open a browser:
- Surface the URL to the user; do not auto-fill the form.
- If the agent cannot reach the URL at all, ask to elevate / step outside the sandbox.

`nb init` also installs the upstream NocoBase skills (the same set bundled here) — that is intentional and harmless; skip it with `--skip-skills`, and manage them later with `nb skills check|install|update|remove`.

→ Detailed rules and edge cases live in **`nocobase-env-manage`**.

## Environments

An *env* is a named NocoBase endpoint plus its credential, stored by the CLI. Every runtime command takes `-e, --env <name>` and defaults to the current env.

```bash
# Save an endpoint (the URL includes the /api prefix) and sign in
nb env add prod --api-base-url https://app.example.com/api --auth-type oauth
nb env auth prod                      # re-authenticate: --auth-type basic|token|oauth

nb env list                           # all envs
nb env use prod                       # switch the current env
nb env current
nb env info prod                      # app, database, API and auth details (secrets masked)
nb env status                         # runtime status; `nb env status --all` for every env
nb env update prod                    # re-sync the env and refresh generated `nb api` commands
nb env remove prod
```

`--auth-type oauth` uses the OAuth device flow when the server supports it (it prints a verification URL and code, so it works on a headless server) and falls back to a browser loopback flow otherwise; it needs the IdP: OAuth plugin. `--auth-type token` takes an API key (`--access-token`), `--auth-type basic` takes `--username` / `--password`. When an explicit `--env` differs from the current env in a non-interactive session, add `--yes` (or run `nb env use <name>` first).

## Lifecycle

```bash
# Run / stop / restart the app of the current env (or pass --env <name>)
nb app start
nb app stop
nb app restart

# Pull a new release without losing data
nb app upgrade                        # --force skips the confirmation; --version <tag> pins one

# Inspect what's running
nb env status                         # runtime status
nb env info                           # full details
nb app logs --tail 200 --no-follow    # recent logs (pm2 logs for local installs, docker logs for Docker)
```

The flat forms (`start`, `stop`, `restart`, `upgrade`, `logs`) still run as hidden aliases, but write the canonical `nb app …` forms. There is no flat status command — use `nb env status`, `nb env info` or `nb app logs`.

## Plugin manager

```bash
nb plugin list                                        # all plugins, with enabled/disabled state
nb plugin enable @nocobase/plugin-api-keys            # one or more package names
nb plugin disable @nocobase/plugin-api-keys
nb plugin import <archive.tgz | https-url | npm-spec> # unpack a packaged plugin into storage/plugins (does not enable it)
```

`nb plugin` takes full package names (`@nocobase/plugin-…`). `nb pm` is a hidden alias that only offers `list`, `enable` and `disable`; there is no install-from-registry or remove command — bring a plugin in with `nb plugin import`, then `nb plugin enable`. Built-in plugins (API keys, IdP: OAuth, MCP server, …) need no import.

→ For the full grammar and error handling, load **`nocobase-plugin-manage`**. That skill enforces "no docker/api/manual fallback chains" — only direct `nb plugin` commands.

## Backup, restore, migration

```bash
# Create a backup on the env and download it
nb backup create --output ./backups/ --json-output

# Restore a local backup file into an env (overwrites application data — confirm with the user first)
nb backup restore --file ./backups/<file>.nbdump --env <env> --force

# Server-side backups and cross-environment migrations are `nb api` groups
nb api backup list -e staging
nb api migration rules list -e staging
nb api migration create --help        # then: get, check, execute, download, logs, list
```

`nb backup {create,restore}` is the file-based front door. The server-side surface is `nb api backup {create,list,status,download,remove,restore,restore-upload,restore-status}` and `nb api migration {rules,create,check,execute,download,logs,list,get,remove}` — those groups are generated from the app's OpenAPI, so confirm exact flags with `-h`.

→ The full publish playbook (selective backups, partial restores, version compatibility, dev→prod migration order) lives in **`nocobase-publish-manage`**.

## Declarative `nb api` surface

`nb api …` has two parts: the built-in `nb api resource list|get|create|update|destroy|query` for any collection, and **generated groups** built from the connected app's OpenAPI schema when you run `nb env add` / `nb env update`. The available groups therefore depend on the app version and its enabled plugins — inspect them with `nb api --help` and `nb api <group> --help`.

```bash
nb api data-modeling collections list -j
nb api data-modeling collections get --filter-by-tk posts --appends fields -j
nb api resource list --resource users --filter '{}' --page-size 20 -j
nb api workflow workflows list -j
nb api flow-surfaces apply-blueprint --body-file blueprint.json -j
nb api acl roles list -e prod -j
```

Shared conventions: `-e/--env`, `--api-base-url`, `-t/--token` (API key override), `--role` (sent as `X-Role`), and `-j/--json-output` (raw JSON, on by default; `--no-json-output` for tables). Query parameters become kebab-case flags (`--filter-by-tk`, `--page-size`, `--appends`); write bodies go in `--body '<json>'` or `--body-file <path>` (mutually exclusive — prefer the file for anything non-trivial).

Each upstream skill documents the subcommands it owns:

| Sub-command family | Skill |
|---|---|
| `nb api flow-surfaces …` (UI authoring) | `nocobase-portal-manage` → `nocobase-ui-builder` |
| `nb api data-modeling collections|fields|db-views …` | `nocobase-data-modeling` |
| `nb api workflow workflows|flow-nodes|executions|jobs …` | `nocobase-workflow-manage` |
| `nb api acl roles|data-sources …`, role-mode toggles | `nocobase-acl-manage` |
| `nb api ai …` (LLM providers/services, employees), `nb api kb …` | `nocobase-ai-manager`, `nocobase-ai-employee`, `nocobase-ai-knowledge-base-manager` |
| `nb api backup …`, `nb api migration …` | `nocobase-publish-manage` |

Always reach for the specialist skill first — it has the per-command argument tables, safety rules, and worked examples. A manual workflow run is the one case where the REST call is the documented portable path: `POST /api/workflows:execute?filterByTk=<workflowId>` (see `examples`).

## Workspaces / DSL

If the user explicitly asks for a YAML/DSL "committed-to-git" build flow, hand off to **`nocobase-dsl-reconciler`** — it owns `cli push`, the `workspaces/` layout, and reconciliation logic. Do not invoke the DSL path for ad-hoc UI tweaks; use `nocobase-portal-manage` instead (live API, no commit needed).

## Quick reference

| Task | One-liner |
|---|---|
| Install | `npm install -g @nocobase/cli` |
| Bootstrap (interactive) | `nb init --ui` |
| Add and sign in to an env | `nb env add <name> --api-base-url <url>/api --auth-type oauth` |
| Run / stop | `nb app start` / `nb app stop` |
| Upgrade in place | `nb app upgrade` |
| Status / logs | `nb env status` / `nb app logs` |
| Enable a plugin | `nb plugin enable @nocobase/plugin-<name>` |
| Backup | `nb backup create --output <dir>` |
| Restore | `nb backup restore --file <path> --force` |
| Migrate environments | `nb api migration …` (see `nocobase-publish-manage`) |
| Apply a UI blueprint | `nb api flow-surfaces apply-blueprint --body-file <payload>.json -j` |
| Run a workflow manually | `POST /api/workflows:execute?filterByTk=<id>` |

## When to use REST API instead

- The agent runs on a different host from NocoBase and has no `nb` env — the CLI keeps its envs locally.
- The call is part of a webhook handler, scheduled job, or another service.
- You need streaming or fine-grained pagination — those are HTTP-native.

For everything else, prefer `nb` when it is available; it carries fewer auth and CORS pitfalls than raw HTTP.
