---
name: cli-recipes
description: "Use when the user asks how to install or run NocoBase from the terminal — \"install nb CLI\", \"how do I bootstrap NocoBase\", \"run nb commands\", \"start/stop NocoBase\", \"backup NocoBase\", \"nb pm\". Provides install one-liner (`@nocobase/cli@beta`), the bootstrap-and-lifecycle recipes, and a routing table that hands deeper tasks to the upstream `nocobase-env-manage`, `nocobase-plugin-manage`, and `nocobase-publish-manage` skills."
---

# nb CLI — install and recipes

The `nb` CLI is the canonical way to bootstrap and operate a NocoBase v2 project from a terminal. This skill covers install, the most-used commands, and where to go for deeper topics.

## Install

```bash
npm install -g @nocobase/cli@beta
nb --version
```

Requirements: Node.js 18 or newer, npm or pnpm, and Docker if you plan to use the bundled database/storage stacks. If the install errors with `EACCES`, configure a user-level npm prefix (`npm config set prefix "$HOME/.npm-global"`) rather than running with `sudo`.

## Bootstrap a project

```bash
mkdir my-nocobase && cd my-nocobase
nb init --ui
```

`nb init --ui` opens a browser-based setup wizard. The CLI keeps the process running until the user finishes the wizard — set a 30-minute timeout and **do not interrupt** it.

In a sandboxed environment where the CLI cannot open a browser:
- Surface the URL to the user; do not auto-fill the form.
- If the agent cannot reach the URL at all, ask to elevate / step outside the sandbox.

The wizard installs core skills (the same 11 you have bundled here) into the project — that is intentional and harmless.

→ Detailed rules and edge cases live in **`nocobase-env-manage`**.

## Lifecycle

```bash
# Run / stop / restart the dev server
nb start
nb stop
nb restart

# Pull a new release without losing data
nb upgrade

# Inspect what's running
nb status
```

## Plugin manager

```bash
nb pm list              # all plugins, with enabled/disabled state
nb pm enable <name>     # e.g. nb pm enable api-keys
nb pm disable <name>
nb pm add <package>     # install from registry
nb pm remove <name>
```

→ For the full grammar and error handling, load **`nocobase-plugin-manage`**. That skill enforces "no docker/api/manual fallback chains" — only direct `nb pm` commands.

## Backup, restore, migration

```bash
# Local snapshot
nb backup ./backups/$(date +%F).nbdump

# Restore (cold; the app must be stopped)
nb stop
nb restore ./backups/2026-04-28.nbdump

# Cross-environment migration (export from staging, import to prod)
nb migration export --out staging.dump
nb migration import --in staging.dump
```

→ The full publish playbook (selective backups, partial restores, version compatibility) lives in **`nocobase-publish-manage`**.

## Declarative `nb api` surface

`nb api …` dispatches to the same FlowModel surface that the UI builder uses. It is the "configuration-as-code" entry point that the upstream skills rely on:

```bash
nb api flow-surfaces apply path/to/blueprint.yaml
nb api collections list
nb api workflows trigger --tk order-fulfilment --data '{"orderId":100}'
```

Each upstream skill documents the subcommands it owns:

| Sub-command family | Skill |
|---|---|
| `nb api flow-surfaces …` (UI authoring) | `nocobase-ui-builder` |
| `nb api collections …`, `nb api fields …` | `nocobase-data-modeling` |
| `nb api workflows …`, `nb api flow-nodes …` | `nocobase-workflow-manage` |
| `nb api roles …`, role-mode toggles | `nocobase-acl-manage` |

Always reach for the specialist skill first — it has the per-command argument tables, safety rules, and worked examples.

## Workspaces / DSL

If the user explicitly asks for a YAML/DSL "committed-to-git" build flow, hand off to **`nocobase-dsl-reconciler`** — it owns `cli push`, the `workspaces/` layout, and reconciliation logic. Do not invoke the DSL path for ad-hoc UI tweaks; use `nocobase-ui-builder` instead (live API, no commit needed).

## Quick reference

| Task | One-liner |
|---|---|
| Install | `npm install -g @nocobase/cli@beta` |
| Bootstrap (interactive) | `nb init --ui` |
| Run / stop | `nb start` / `nb stop` |
| Upgrade in place | `nb upgrade` |
| Enable a plugin | `nb pm enable <name>` |
| Backup | `nb backup ./out.nbdump` |
| Migrate environment | `nb migration export/import` |
| Apply a UI blueprint | `nb api flow-surfaces apply <yaml>` |
| Trigger a workflow | `nb api workflows trigger --tk <key> --data '{…}'` |

## When to use REST API instead

- The agent runs on a different host from NocoBase — the CLI is local-only.
- The call is part of a webhook handler, scheduled job, or another service.
- You need streaming or fine-grained pagination — those are HTTP-native.

For everything else, prefer `nb` when it is available; it carries fewer auth and CORS pitfalls than raw HTTP.
