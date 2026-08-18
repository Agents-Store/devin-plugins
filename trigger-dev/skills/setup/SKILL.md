---
name: setup
description: Set up Trigger.dev in a project, connect to a self-hosted instance, verify MCP connection, authenticate the CLI, or configure dev/staging/production environments. Use when the user asks to "set up trigger.dev", "init trigger project", "connect to self-hosted trigger", "verify trigger connection", "install trigger.dev", or "configure trigger environments".
---

# Trigger.dev Setup

Get Trigger.dev running in your project — self-hosted or cloud — and verify the connection.

## When to Use

- Adding Trigger.dev to an existing project
- Creating your first task
- Connecting to a self-hosted Trigger.dev v4 instance
- Verifying MCP or CLI connection
- Configuring environments (dev / staging / production)

## Prerequisites

- Node.js 18.20+ (or Bun runtime)
- TypeScript 5.0.4+
- A Trigger.dev account — cloud or self-hosted instance
- For self-hosted: running webapp + supervisor Docker Compose stacks

## Step 1: Install the SDK

```bash
npm install @trigger.dev/sdk
```

## Step 2: Authenticate the CLI

### Cloud

```bash
npx trigger.dev@latest login
```

### Self-Hosted

```bash
npx trigger.dev@latest login -a https://trigger.example.com
```

The `-a` flag tells the CLI where your instance lives. The CLI remembers this URL for all subsequent commands.

### Multiple Instances (Profiles)

```bash
# Login with a named profile
npx trigger.dev@latest login -a https://trigger.example.com --profile self-hosted

# Use the profile for dev/deploy
npx trigger.dev@latest dev --profile self-hosted
npx trigger.dev@latest deploy --profile self-hosted

# List all saved profiles
npx trigger.dev@latest list-profiles

# Switch between profiles
npx trigger.dev@latest switch self-hosted

# Verify who you're logged in as
npx trigger.dev@latest whoami
```

## Step 3: Initialize Project

```bash
npx trigger.dev@latest init
```

This creates:
- `trigger.config.ts` — project configuration
- `src/trigger/` directory — where your tasks live
- A sample task file

### Self-Hosted Init

```bash
npx trigger.dev@latest init -p <project-ref> -a https://trigger.example.com
```

### Init Flags

| Flag | Description |
|------|-------------|
| `-p, --project-ref` | Project ref (proj_xxx) from dashboard |
| `-a, --api-url` | API URL for self-hosted |
| `--runtime` | Runtime: node or bun |
| `--skip-package-install` | Skip SDK install |
| `--javascript` | Use JavaScript instead of TypeScript |

## Step 4: Configure trigger.config.ts

```ts
import { defineConfig } from "@trigger.dev/sdk";

export default defineConfig({
  project: "proj_xxxxx",  // From your dashboard
  dirs: ["./src/trigger"],
});
```

## Step 5: Create Your First Task

```ts
// src/trigger/my-task.ts
import { task } from "@trigger.dev/sdk";

export const myFirstTask = task({
  id: "my-first-task",
  run: async (payload: { name: string }) => {
    console.log(`Hello, ${payload.name}!`);
    return { message: `Processed ${payload.name}` };
  },
});
```

## Step 6: Start Dev Server

```bash
npx trigger.dev@latest dev
```

The dev server watches for file changes, registers tasks with the dev environment, and executes tasks locally.

## Step 7: Trigger Your Task

From your app code:

```ts
import { tasks } from "@trigger.dev/sdk";
import type { myFirstTask } from "./trigger/my-task";

await tasks.trigger<typeof myFirstTask>("my-first-task", {
  name: "World",
});
```

Or use the **Test** tab in the Trigger.dev dashboard.

## Environment Variables

| Variable | Description | Format |
|----------|-------------|--------|
| `TRIGGER_DEV_SECRET_KEY` | Dev environment secret key | `tr_dev_xxx` |
| `TRIGGER_STAGE_SECRET_KEY` | Staging environment secret key | `tr_dev_xxx` (different key) |
| `TRIGGER_PROD_SECRET_KEY` | Production environment secret key | `tr_prod_xxx` |
| `TRIGGER_API_URL` | Self-hosted instance URL | `https://trigger.example.com` |
| `TRIGGER_PROJECT_REF` | Project identifier from dashboard | `proj_xxxxx` |
| `TRIGGER_ACCESS_TOKEN` | Personal access token for CI/CD | `tr_pat_xxx` |

Each environment has its own secret key. Pass the appropriate one to the SDK via `configure()`.

Set in `.env`:

```bash
TRIGGER_PROJECT_REF=proj_xxxxx
TRIGGER_DEV_SECRET_KEY=tr_dev_xxxxxxxxxxxxxx
TRIGGER_STAGE_SECRET_KEY=tr_dev_yyyyyyyyyyyyyy
TRIGGER_PROD_SECRET_KEY=tr_prod_zzzzzzzzzzzzzz
TRIGGER_API_URL=https://trigger.your-domain.com
```

For the full reference, see @references/environment-setup.md.

## MCP Server Setup

Trigger.dev provides an **official MCP server** shipped with the CLI. As of v4.4.4 the supported install flow is the `install-mcp` command:

```bash
# Install for a specific AI client (writes the client's MCP config for you)
npx trigger.dev@latest install-mcp --client claude-code

# Or — install into every supported client automatically
npx trigger.dev@latest install-mcp --yolo
```

Manual config:

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

Common flag combinations:

```bash
# Dev-only — hides deploy and list_preview_branches
npx trigger.dev@latest install-mcp --dev-only

# Read-only — hides deploy, trigger_task, cancel_run (agent can read but not mutate)
npx trigger.dev@latest install-mcp --readonly

# Scoped to one project
npx trigger.dev@latest install-mcp --project-ref proj_abc123
```

> **Production tip:** pass `--readonly` when wiring MCP into an agent that must not mutate a production instance. All write tools are hidden server-side, not just filtered by the client.

See https://trigger.dev/docs/mcp-introduction for the per-client config file locations.

## Agent Rules Installation

```bash
npx trigger.dev@latest install-rules
```

Available rule sets: Basic tasks (1,200 tokens), Advanced tasks (3,000), Scheduled tasks (780), Configuration (1,900), Realtime (1,700). Rules auto-update when you run `npx trigger.dev@latest dev`.

## Verification Checklist

1. **CLI auth**: `npx trigger.dev@latest whoami` returns your user info
2. **Dev server**: `npx trigger.dev@latest dev` starts without errors
3. **Tasks registered**: Dashboard shows your tasks under the dev environment
4. **If MCP**: MCP tool `list_orgs` returns your organizations

## Self-Hosted v4 Health Check

```bash
# Check webapp services
cd trigger.dev/hosting/docker/webapp
docker compose ps

# Check supervisor
cd trigger.dev/hosting/docker/worker
docker compose ps

# View logs
docker compose logs -f webapp
docker compose logs -f supervisor
```

## Deeper Reference

- @references/project-structure.md — project layout conventions
- @references/environment-setup.md — complete environment and self-hosted configuration
