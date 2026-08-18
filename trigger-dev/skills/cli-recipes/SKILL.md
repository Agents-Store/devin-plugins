---
name: cli-recipes
description: Trigger.dev CLI commands for development, deployment, MCP setup, and project management. Use when the user asks about "trigger.dev CLI", "npx trigger.dev", "trigger.dev dev server", "trigger.dev deploy command", "trigger.dev mcp install", "trigger.dev profiles", or needs ready-to-use CLI commands.
---

# Trigger.dev CLI Recipes

The CLI is bundled with the SDK — no separate install:

```bash
npx trigger.dev@latest <command>
# or: pnpm dlx trigger.dev@latest <command>
# or: yarn dlx trigger.dev@latest <command>
```

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

# With specific runtime
npx trigger.dev@latest init --runtime bun

# JavaScript (default: TypeScript)
npx trigger.dev@latest init --javascript
```

## Development Server

```bash
# Start dev server
npx trigger.dev@latest dev

# Custom config (monorepo)
npx trigger.dev@latest dev --config ./packages/jobs/trigger.config.ts

# Debug log level
npx trigger.dev@latest dev --log-level debug

# With specific profile
npx trigger.dev@latest dev --profile self-hosted
```

The dev server watches for file changes, registers tasks, and executes them locally.

## Deployment

```bash
# Deploy to production
npx trigger.dev@latest deploy

# Deploy to staging
npx trigger.dev@latest deploy --env staging

# Deploy preview branch
npx trigger.dev@latest deploy --env preview --branch feature/new-task

# Skip promotion (canary)
npx trigger.dev@latest deploy --skip-promotion
```

## MCP Server

```bash
# Interactive installer (detects installed clients and writes their configs)
npx trigger.dev@latest install-mcp

# Install for a specific client
npx trigger.dev@latest install-mcp --client claude-code
npx trigger.dev@latest install-mcp --client cursor --scope user

# Install across every supported client at once
npx trigger.dev@latest install-mcp --yolo

# Production-safe — hide deploy, trigger_task, cancel_run
npx trigger.dev@latest install-mcp --readonly

# Restrict to dev env and a single project
npx trigger.dev@latest install-mcp --dev-only --project-ref proj_abc123
```

### install-mcp Flags

| Flag | Purpose |
|------|---------|
| `--client <name...>` | claude-code, cursor, windsurf, vscode, zed, cline, gemini-cli, amp, openai-codex, crush, opencode, ruler |
| `--scope <scope>` | `user` / `project` / `local` |
| `--dev-only` | Hide deploy / list_preview_branches — only dev env tools exposed |
| `--readonly` | Hide `deploy`, `trigger_task`, `cancel_run` (AI can read but not mutate) |
| `--project-ref <ref>` | Lock MCP to one project |
| `--tag <tag>` | Pin CLI version |
| `-a, --api-url <url>` | Self-hosted API URL |
| `--log-file <path>` | Write MCP server logs to file |
| `--log-level <level>` | debug / info / log / warn / error / none |
| `--yolo` | Install into every supported client |

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

Dev-only + project-scoped example:

```json
{
  "mcpServers": {
    "trigger": {
      "command": "npx",
      "args": ["trigger.dev@latest", "mcp", "--dev-only", "--project-ref", "proj_abc123", "--readonly"]
    }
  }
}
```

### Platform Notifications

Since v4.4.4, `trigger dev` and `trigger login` fetch server-side notifications (info/warn/error/success) with color markup. Disable with `--skip-platform-notifications`:

```bash
npx trigger.dev@latest dev --skip-platform-notifications
```

## Agent Rules

```bash
# Interactive — choose AI tool and rule sets
npx trigger.dev@latest install-rules
```

| Rule Set | Tokens | Description |
|----------|--------|-------------|
| Basic tasks | 1,200 | Core task writing patterns |
| Advanced tasks | 3,000 | Complex workflows, error handling |
| Scheduled tasks | 780 | Cron/scheduled tasks |
| Configuration | 1,900 | trigger.config.ts setup |
| Realtime | 1,700 | Realtime API and React hooks |

Rules auto-update when you run `npx trigger.dev@latest dev`.

## Self-Hosted Docker

```bash
# Clone and start
git clone --depth=1 https://github.com/triggerdotdev/trigger.dev
cd trigger.dev/hosting/docker

# Start webapp
cd webapp && docker compose up -d

# Start worker (supervisor)
cd ../worker && docker compose up -d

# View logs
docker compose logs -f webapp
docker compose logs -f supervisor

# Check status
docker compose ps

# Version lock (in .env)
TRIGGER_IMAGE_TAG=v4.0.0
```

## Package.json Scripts

```json
{
  "scripts": {
    "trigger:dev": "trigger.dev dev",
    "trigger:deploy:staging": "trigger.dev deploy --env staging",
    "trigger:deploy:prod": "trigger.dev deploy --env production"
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
