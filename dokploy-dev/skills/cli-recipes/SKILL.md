---
name: cli-recipes
description: "This skill should be used when running Dokploy operations from the terminal with the @dokploy/cli — authenticating, creating projects/apps, deploying, managing environment variables, provisioning databases, or reading logs via command line. Triggers: \"dokploy cli\", \"dokploy command\", \"dokploy auth\", \"dokploy application deploy\", \"dokploy read-logs from terminal\", \"deploy dokploy from terminal\"."
---

# Dokploy CLI Recipes

Common commands and workflows for the official Dokploy CLI (`@dokploy/cli`). Use these when operating Dokploy from a terminal or CI, alongside the MCP tools.

> **The CLI was completely rewritten (0.29.x):** it is now **auto-generated 1:1 from the OpenAPI spec** — 546 commands in 50 kebab-case groups, in the shape `dokploy <group> <action> [--param value…]`. It version-locks to Dokploy releases (e.g. CLI 0.29.14 ↔ Dokploy v0.29.14). The old `dokploy authenticate`, `dokploy verify`, `dokploy app *`, `dokploy project list/info`, `dokploy env pull/push`, and `dokploy database postgresql *` commands are **gone**.

> **The CLI now READS LOGS.** Every `read-logs` operation from the API is a CLI command (`dokploy deployment read-logs`, `dokploy application read-logs`, `dokploy compose read-logs`, all six `{db} read-logs` — including `dokploy libsql read-logs`). For guided multi-container debugging still prefer `/dokploy-dev:logs`, `/dokploy-dev:compose-logs`, `/dokploy-dev:debug`.

---

## Installation

```bash
npm install -g @dokploy/cli
dokploy --version        # versions in lockstep with Dokploy, e.g. 0.29.14
```

---

## Authentication (three ways — env vars take precedence)

1. **Persisted config:**
   ```bash
   dokploy auth -u https://dokploy.example.com -t <API_KEY>
   ```
   Non-interactive. Validates against `/api/trpc/user.get` and saves `config.json`.

2. **Environment variables** — the SAME vars as MCP/REST, so one env block feeds all three interfaces:
   ```bash
   export DOKPLOY_URL=https://dokploy.example.com     # base URL, no /api
   export DOKPLOY_API_KEY=<API_KEY>                   # alias: DOKPLOY_AUTH_TOKEN
   ```

3. **A `.env` file in the working directory** — auto-loaded; does not override already-set env vars.

- **Server URL** — the Dokploy base URL, e.g. `https://dokploy.example.com` (do NOT include `/api`).
- **Access token** — generate in the dashboard under **Settings > Profile** (or **Settings > API/Tokens**); tokens don't expire by default. The **same token** works for CLI, MCP, and REST.

---

## Command model

```
dokploy <group> <action> [--param value…] [--json]
```

- **546 commands** auto-generated 1:1 from the OpenAPI spec across **50 kebab-case groups**: `admin`, `ai`, `application`, `audit-log`, `backup`, `bitbucket`, `certificates`, `cluster`, `compose`, `custom-role`, `deployment`, `destination`, `docker`, `domain`, `environment`, `forward-auth`, `gitea`, `github`, `gitlab`, `git-provider`, `libsql`, `license-key`, `mariadb`, `mongo`, `mounts`, `mysql`, `notification`, `organization`, `patch`, `port`, `postgres`, `preview-deployment`, `project`, `redirects`, `redis`, `registry`, `rollback`, `schedule`, `scim`, `security`, `server`, `settings`, `ssh-key`, `sso`, `stripe`, `swarm`, `tag`, `user`, `volume-backups`, `whitelabeling` — plus `auth`.
- **Actions** are the kebab-cased operation names: `read-logs`, `save-build-type`, `get-containers-by-app-label`, …
- **Flags** are the API params: `--applicationId`, `--tail`, `--environmentId`, …
- `--help` works at every level; `--json` on every command for raw machine-readable output.

---

## Provisioning Recipes

```bash
# List projects
dokploy project all

# Create a project
dokploy project create --name my-saas

# Resolve the target environment (resources live under an environment, default "production")
dokploy project one --projectId <id> --json    # read environments[] → environmentId

# Create an application
dokploy application create --name web --environmentId <envId>

# Deploy it
dokploy application deploy --applicationId <id>

# Set environment variables (all four companion flags required by the API)
dokploy application save-environment --applicationId <id> \
  --env "KEY=VALUE" --buildArgs "" --buildSecrets "" --createEnvFile false

# Provision + start a PostgreSQL database
dokploy postgres create --name main-db --databaseName main --databaseUser postgres \
  --databasePassword <pw> --environmentId <envId>
dokploy postgres deploy --postgresId <id>
```

All six database groups exist — `postgres`, `mysql`, `mariadb`, `mongo`, `redis`, and `libsql` (`dokploy libsql create` works; LibSQL is no longer API/MCP-only).

---

## Reading logs from the CLI

```bash
# Build log of a deployment
dokploy deployment read-logs --deploymentId <id> --tail 500

# App runtime log with filters
dokploy application read-logs --applicationId <id> --tail 200 --since 1h --search error

# Compose stack: enumerate containers first, then read per container
dokploy docker get-containers-by-app-name-match --appName <name> --appType docker-compose --json
dokploy compose read-logs --composeId <id> --containerId <cid> --tail 200

# Databases — all six types
dokploy postgres read-logs --postgresId <id> --tail 200
dokploy libsql read-logs --libsqlId <id> --tail 200
```

Same filter model as the API: `tail` 1–10000 (default 100), `since` `all` or `<n>{s|m|h|d}`, `search` substring.

---

## Workflow Recipes

### Deploy an app

```bash
dokploy auth -u https://dokploy.example.com -t <API_KEY>   # one-time (or export env vars)
dokploy project create --name my-saas
dokploy project one --projectId <id> --json                # → environmentId
dokploy application create --name web --environmentId <envId>
dokploy application save-environment --applicationId <appId> --env "NODE_ENV=production" --buildArgs "" --buildSecrets "" --createEnvFile false
dokploy application deploy --applicationId <appId>
dokploy deployment read-logs --deploymentId <deployId> --tail 500   # watch the build
```

### Provision a PostgreSQL database

```bash
dokploy project one --projectId <id> --json    # or reuse a known environmentId
dokploy postgres create --name main-db --databaseName main --databaseUser postgres --databasePassword <pw> --environmentId <envId>
dokploy postgres deploy --postgresId <pgId>
```

### Full-stack (app + database)

```bash
dokploy postgres create --name main-db --databaseName main --databaseUser postgres --databasePassword <pw> --environmentId <envId>
dokploy postgres deploy --postgresId <pgId>
dokploy application create --name web --environmentId <envId>
dokploy application save-environment --applicationId <appId> --env "DATABASE_URL=postgres://…" --buildArgs "" --buildSecrets "" --createEnvFile false
dokploy application deploy --applicationId <appId>
```

---

## Useful Flags

| Flag | Commands | Description |
|------|----------|-------------|
| `--help` | all | Show help for any command/group |
| `--json` | all | Machine-readable output for scripting |

---

## CLI vs MCP vs REST API

| Method | Best for | Logs/debug? |
|--------|----------|-------------|
| CLI | Terminal/CI provisioning + deploys, scripting | ✅ `<group> read-logs` commands (mirrors the API) |
| MCP tools | Claude Code automation, multi-step orchestration, guided debugging | ✅ `*-readLogs`, `ai-analyzeLogs`, docker introspection |
| REST API | Custom integrations, external scripts, monitoring | ✅ `GET /api/*.readLogs` |

All three use the same base URL + access token (`DOKPLOY_URL` / `DOKPLOY_API_KEY`) against the same Dokploy instance.
