---
name: cli-recipes
description: Trigger.dev CLI commands for development, deployment, MCP setup, agent skills, env vars, runs and project management. Use when the user asks about "trigger.dev CLI", "npx trigger.dev", "trigger.dev dev server", "trigger.dev deploy command", "trigger.dev mcp install", "trigger.dev mcp readonly", "trigger.dev skills", "trigger.dev profiles", or needs ready-to-use CLI commands.
---

# Trigger.dev CLI Recipes

The CLI is bundled with the SDK — no separate install:

```bash
npx trigger.dev@latest <command>
# or: pnpm dlx trigger.dev@latest <command>
# or: yarn dlx trigger.dev@latest <command>
```

`@latest` is fine for ad-hoc commands. For `dev` and `deploy` in a project (and always in CI) use the version of `@trigger.dev/sdk` — and on self-hosted the version of the server: `npx trigger.dev@<version> <command>`, or the `trigger.dev` devDependency. `npx trigger.dev@<version> update` aligns every `@trigger.dev/*` package with that version.

## Authentication

```bash
# Login to cloud
npx trigger.dev@latest login

# Login to self-hosted
npx trigger.dev@latest login -a https://trigger.example.com

# Login with named profile
npx trigger.dev@latest login -a https://trigger.example.com --profile self-hosted

# Verify
npx trigger.dev@latest whoami
```

## Profile Management

```bash
# List all profiles
npx trigger.dev@latest list-profiles

# Switch profile interactively
npx trigger.dev@latest switch

# Switch to specific profile
npx trigger.dev@latest switch self-hosted

# Remove a profile
npx trigger.dev@latest logout --profile self-hosted
```

## Project Initialization

```bash
# Interactive init
npx trigger.dev@latest init

# Self-hosted with project ref
npx trigger.dev@latest init -p proj_xxx -a https://trigger.example.com

# Agent / CI (no TTY): --yes needs --project-ref, or --project-name with --org-name
npx trigger.dev@latest init --yes --project-ref proj_xxx -a https://trigger.example.com --no-browser

# Specific runtime: node, node-22, node-24 (default), node-26, bun
npx trigger.dev@latest init --runtime node-24

# JavaScript (default: TypeScript)
npx trigger.dev@latest init --javascript
```

Other `init` flags: `--project-name`, `--org-name`, `--pkg-args <csv>`, `--tag <sdk version>`, `--override-config`, `--skip-package-install`, `--profile`. Without a TTY and without `--yes`, `init` exits with an error.

## Development Server

```bash
# Start dev server (`dev` is a command group; `start` is the default sub-command)
npx trigger.dev@latest dev

# Custom config (monorepo)
npx trigger.dev@latest dev --config ./packages/jobs/trigger.config.ts

# Debug log level
npx trigger.dev@latest dev --log-level debug

# With specific profile
npx trigger.dev@latest dev --profile self-hosted

# Dev branch (CLI 4.5.0+) and cap on local concurrency
npx trigger.dev@latest dev --branch my-feature --max-concurrent-runs 4

# Archive a dev branch (--branch defaults to $TRIGGER_DEV_BRANCH)
npx trigger.dev@latest dev archive --branch my-feature
```

`dev start` options: `-c/--config`, `-p/--project-ref`, `-b/--branch`, `--env-file`, `--max-concurrent-runs`, `--keep-tmp-files`, `--debug-otel`, `--skip-update-check`, `--profile`, `-a/--api-url`. Hidden flags: `--skip-mcp-install`, `--skip-rules-install`, `--skip-platform-notifications`.

The dev server watches for file changes, registers tasks, and executes them locally. It runs in the foreground and blocks a shell tool; from an agent use the MCP tools `start_dev_server`, `dev_server_status`, `stop_dev_server` instead.

## Deployment

```bash
# Deploy to production (default env is prod)
npx trigger.dev@<version> deploy

# Deploy to staging
npx trigger.dev@<version> deploy --env staging

# Deploy preview branch
npx trigger.dev@<version> deploy --env preview --branch feature/new-task

# Skip promotion (canary), then promote later
npx trigger.dev@<version> deploy --skip-promotion
npx trigger.dev@<version> promote 20260101.1

# Tag the deploy with a commit SHA (version skew protection, max 128 characters)
npx trigger.dev@<version> deploy --env prod --external-id "$GITHUB_SHA"  # requires CLI/SDK and server >= 4.5.12; drop it on older
```

`--env` accepts `prod`, `staging` and `preview` (`production` is coerced to `prod`). More flags: `--force` (rebuild an already deployed `--external-id`; both need server ≥ 4.5.12, CLI/SDK must match), `--dry-run`, `--skip-sync-env-vars`, `--env-file`, `--config`, `--project-ref`, `--profile`, `-a/--api-url`, `--local-build`, `--native-build`, `--depot-build`, `--local-bundle` (experimental, needs `--native-build`), `--detach` (needs `--native-build`), `--build-logs compact|full`. See the **deployment** skill for the full table and self-hosted specifics.

## Environment Variables

```bash
npx trigger.dev@<version> env list --env prod
npx trigger.dev@<version> env get MY_VAR --env prod
npx trigger.dev@<version> env set MY_VAR some-value --env prod
npx trigger.dev@<version> env set MY_SECRET some-value --env prod --secret   # cannot be read back
npx trigger.dev@<version> env pull --env prod                                # to a local file
```

`env` needs CLI 4.6.1 or newer. `--env` is `prod`, `staging` or `preview`.

## Runs, Projects, Reports (CLI 4.5-4.7)

```bash
npx trigger.dev@latest runs list --env prod --status FAILED --limit 20
npx trigger.dev@latest runs get run_xxx
npx trigger.dev@latest runs replay run_xxx          # same payload, latest version
npx trigger.dev@latest runs cancel run_xxx
npx trigger.dev@latest projects list
npx trigger.dev@latest projects create
npx trigger.dev@latest projects rename proj_xxx "New name"
npx trigger.dev@latest orgs create
npx trigger.dev@latest report health --env prod --period 24h   # is work flowing, is it my code, is telemetry fresh
npx trigger.dev@latest mint-token --ttl 3600                    # short-lived read-only tr_uat_ token
npx trigger.dev@latest preview archive                          # archive a preview branch
```

These commands exist in CLI 4.7.2 and were added across 4.5-4.7; use a CLI whose version matches your server.

## MCP Server

```bash
# Interactive installer (detects installed clients and writes their configs)
npx trigger.dev@latest install-mcp

# Install for a specific client
npx trigger.dev@latest install-mcp --client claude-code
npx trigger.dev@latest install-mcp --client cursor --scope user

# Install across every supported client at once
npx trigger.dev@latest install-mcp --yolo

# Restrict to dev env and a single project
npx trigger.dev@latest install-mcp --dev-only --project-ref proj_abc123
```

### install-mcp Flags

| Flag | Purpose |
|------|---------|
| `--client <name...>` | claude-code, cursor, windsurf, vscode, zed, cline, gemini-cli, amp, openai-codex, crush, opencode, ruler |
| `--scope <scope>` | `user`, `project` or `local` (which of them a client supports depends on the client; the CLI help text lists only user and project) |
| `--dev-only` | Dev environment only: `deploy`, `list_preview_branches` and any non-dev `environment` argument are rejected |
| `--project-ref <ref>` | Lock MCP to one project |
| `--tag <tag>` | Pin the CLI version the MCP server runs |
| `-a, --api-url <url>` | Self-hosted API URL |
| `--log-file <path>` | Write MCP server logs to file |
| `--log-level <level>` | debug / info / log / warn / error / none |
| `--yolo` | Install into every supported client |

`install-mcp` has no read-only switch.

### mcp Flags (the server itself)

| Flag | Purpose |
|------|---------|
| `--readonly` | Hide the 15 write tools (`deploy`, `trigger_task`, `cancel_run`, `create_project_in_org`, `initialize_project`, 5 prompt writers, `start_agent_chat`, `send_agent_message`, `close_agent_chat`, `write_session_channel`, `submit_feedback`). Does not hide `start_dev_server`, `stop_dev_server`, `switch_profile` |
| `--dev-only` | Same restriction as above |
| `-p, --project-ref <ref>` | Project to use |
| `--profile <name>` | Login profile (default `default`) |
| `-a, --api-url <url>` | Override the API URL |
| `--log-file <path>`, `-l, --log-level` | Logging |
| `--skip-telemetry` | Opt out of telemetry (also hides `submit_feedback`) |
| `--install` | Run the interactive install wizard instead of starting the server |

### Manual Config

```json
{
  "mcpServers": {
    "trigger": {
      "command": "npx",
      "args": ["trigger.dev@latest", "mcp"]
    }
  }
}
```

Read-only, dev-only, project-scoped example (production-safe for an agent):

```json
{
  "mcpServers": {
    "trigger": {
      "command": "npx",
      "args": ["trigger.dev@latest", "mcp", "--readonly", "--dev-only", "--project-ref", "proj_abc123"]
    }
  }
}
```

### Platform Notifications

`trigger dev` and `trigger login` fetch server-side notifications (info/warn/error/success) with color markup. Disable with the hidden `--skip-platform-notifications` flag:

```bash
npx trigger.dev@latest dev --skip-platform-notifications
```

## Agent Skills

Agent rules were replaced by agent skills. The canonical command is `skills`; `install-rules` is just an alias.

```bash
# Interactive — choose the coding agent
npx trigger.dev@latest skills

# Non-interactive: targets are claude-code, cursor, vscode, agents.md
npx trigger.dev@latest skills --target claude-code --target cursor -y
```

Installed skills: trigger-authoring-tasks, trigger-realtime-and-frontend, trigger-authoring-chat-agent, trigger-chat-agent-advanced, trigger-cost-savings (placed in `.claude/skills/` and the equivalent folders of other agents). `npx trigger.dev@latest dev` offers the install on its first run.

## Self-Hosted Docker

```bash
# Clone
git clone --depth=1 https://github.com/triggerdotdev/trigger.dev
cd trigger.dev/hosting/docker

# First time: create .env and generate secrets (no shared defaults since 4.5.6)
cp .env.example .env && ./generate-secrets.sh

# Start webapp
cd webapp && docker compose up -d

# Start worker (supervisor)
cd ../worker && docker compose up -d

# View logs
docker compose logs -f webapp
docker compose logs -f supervisor

# Check status
docker compose ps

# Version lock (in .env): use the version you run; the default is `latest`
TRIGGER_IMAGE_TAG=v4.7.2
```

## Package.json Scripts

Keep `trigger.dev` in `devDependencies` at the SDK version so these scripts run the matching CLI:

```json
{
  "scripts": {
    "trigger:dev": "trigger.dev dev",
    "trigger:deploy:staging": "trigger.dev deploy --env staging",
    "trigger:deploy:prod": "trigger.dev deploy --env prod"
  }
}
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Cannot find trigger.config.ts | Run from project root or pass `--config` |
| Authentication failed | Check TRIGGER_SECRET_KEY or re-login |
| Connection refused | Verify TRIGGER_API_URL and instance health |
| No tasks found | Ensure task files are in configured `dirs` |
| Redirected to cloud | Use `login -a <url>` or set TRIGGER_API_URL |
| Registry push fails | `docker login -u user registry:5000` |
