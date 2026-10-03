---
name: init-project
description: This skill should be used when the user asks to "set up Directus + Next.js + Trigger.dev project", "initialize directus nextjs trigger.dev stack", "bootstrap the 3-service stack", "configure directus next.js and trigger.dev together", "connect trigger.dev to a directus nextjs app", "scaffold stack with background tasks", "start a new project with background jobs", or needs to set up environment variables, versions and verify connections for the Directus + Next.js + Trigger.dev stack.
---

# Initialize Directus + Next.js + Trigger.dev Stack

Bootstrap checklist: versions, environment, dependencies, client, Trigger.dev project, verification. How each tool works is in `directus-dev`, `nextjs-dev` and `trigger-dev`; this skill says which of their pieces to use and in what order, and where the three meet.

## 1. Versions

| Piece | Version | Why |
|-------|---------|-----|
| Directus | 12 (MCP needs 11.12 or later) | MCP is switched on in Settings → AI. The health endpoint needs a token in 12, use `/server/ping` |
| `@directus/sdk` | 26 | Needs Node 22 or later |
| Next.js | `^16.3.8` | `proxy.ts` replaces the deprecated middleware file; earlier 16.3 patches miss security fixes |
| Node.js | 22 or later | The SDK's floor (Next.js itself needs 20.9) |
| Trigger.dev server | 4.x, self-hosted | `trigger-dev` targets 4.4.4 as its baseline and marks newer features with the server version they need (spread window for schedules: 4.6.0) |
| `@trigger.dev/sdk`, `@trigger.dev/react-hooks`, `trigger.dev` (CLI) | **the version of the server** | One line for all four. A CLI or SDK that differs from the server makes `deploy` fail or behave unpredictably (`trigger-dev` → `deployment`) |

## 2. Environment File

```bash
cp templates/.env.example .env.local
```

| Variable | How to obtain |
|----------|---------------|
| `NEXT_PUBLIC_DIRECTUS_URL` | Directus address (`http://localhost:8055` for the local Docker stack) |
| `DIRECTUS_ADMIN_TOKEN` | Create a dedicated user in Directus with a policy that grants only what the server code reads and writes, then generate a static token on the user's page. The name is historical: an administrator token is for local development only |
| `DIRECTUS_URL`, `DIRECTUS_TOKEN`, `NEXT_PUBLIC_CMS_URL` | Already in `.env.example` as `${...}` references to the two rows above. The recipes of `directus-dev` and `nextjs-dev` read these names (client, NextAuth, the images block of `next.config.ts`), so do not delete them |
| `NEXTAUTH_URL`, `NEXTAUTH_SECRET` | NextAuth path only: `http://localhost:3000`, and `openssl rand -base64 32` |
| `REVALIDATION_SECRET` | `openssl rand -base64 32`; sent in a header by the Directus Flow, and by a task that calls the route itself (see `deployment`) |
| `DIRECTUS_WEBHOOK_SECRET` | `openssl rand -base64 32`; sent by the Directus Flow that starts a task. A different value from `REVALIDATION_SECRET`: starting tasks costs money, expiring a cache does not (see `directus-to-trigger`) |
| `TRIGGER_API_URL` | Address of the self-hosted Trigger.dev. Set it wherever `tasks.trigger()` runs: without it the SDK falls back to Trigger.dev Cloud and sends your key there |
| `TRIGGER_SECRET_KEY` | Trigger.dev dashboard → project → API keys → the **environment** secret key (`tr_dev_…` for dev). The SDK in the Next.js server triggers tasks with it |
| `TRIGGER_ACCESS_TOKEN` | Trigger.dev dashboard → Account → Personal Access Tokens (`tr_pat_…`). The MCP server and `trigger deploy` use it, the SDK does not |
| `TRIGGER_PROJECT_REF` | Project page → `proj_…` |
| `NEXT_PUBLIC_TRIGGER_API_URL` | Already in `.env.example` as `${TRIGGER_API_URL}`: the address that browser hooks (`baseURL`) need. An address, never a key |

`.env.local` is not committed. A variable with the `NEXT_PUBLIC_` prefix is shipped to the browser: only addresses may have it, never a token or a key.

## 3. Local Directus (optional)

Follow `directus-dev` → skill `docker-local-dev` (Compose file, `.env`, `/server/ping` check). Set `LOCAL_FRONTEND_ORIGIN=http://localhost:3000` there so CORS and Live Preview accept the Next.js dev server, then use the local address as `NEXT_PUBLIC_DIRECTUS_URL`. The self-hosted Trigger.dev server is set up with `trigger-dev` → `deployment` → `references/self-hosted-infrastructure.md`; this stack assumes it is already running.

## 4. Dependencies

```bash
npm install @directus/sdk@26 server-only
npm install @trigger.dev/sdk@<server-version> @trigger.dev/react-hooks@<server-version>
npm install --save-dev trigger.dev@<server-version>
```

`server-only` makes the build fail when a Client Component imports the Directus client. `trigger.dev` is a development dependency, called through `npx trigger.dev` or an npm script, so the CLI is the version of the SDK instead of whatever `@latest` is today. Add `next-auth@4` or `better-auth` only when you build login (see `authentication`).

## 5. Client and Types

Create `lib/directus.ts` and `types/directus.ts` as described in `directus-dev` → skill `sdk-patterns` → `references/ssr-client.md`, reading `DIRECTUS_URL` and `DIRECTUS_TOKEN` (they expand to this stack's `NEXT_PUBLIC_DIRECTUS_URL` and `DIRECTUS_ADMIN_TOKEN`). Two things from that file decide how the rest works:

- `rest()` has **no `cache` option** (passing `cache` to `rest()` is TS2353). Caching is set per request: see "Cache" in `directus-to-nextjs`.
- Core collections are read with their own commands (`readCollections()`; `readItems` refuses `directus_*` collections).

Fill `types/directus.ts` from the real schema: call the Directus MCP `schema` tool and mirror each collection. Tasks import the same `types/directus.ts` but not `lib/directus.ts`, which carries `import 'server-only'` and throws outside Next.js (`directus-to-trigger` has the task-side client).

## 6. Images

Allow the Directus host in `next.config.ts` (`images.remotePatterns`, and `dangerouslyAllowLocalIP` for a local Directus): see `nextjs-dev` → skill `data-fetching` → `references/headless-cms.md`. How file URLs are built, and why they carry no token, is in "Assets" of `directus-to-nextjs`.

## 7. The Trigger.dev Project

Initialize with the CLI at the server's version, pointing at your instance (`trigger-dev` → `setup` has the flags, including the non-interactive form). Step 4 already installed the packages at the server's version, and `init` would install the newest SDK by default, so skip its install:

```bash
npx trigger.dev@<server-version> init --project-ref "$TRIGGER_PROJECT_REF" --api-url "$TRIGGER_API_URL" --skip-package-install
```

Then check three things that belong to this stack, not to Trigger.dev in general:

- `trigger.config.ts` takes the project from `TRIGGER_PROJECT_REF` (not a literal `proj_…`), sets `maxDuration`, and lists `./trigger` in `dirs`. The options are in `trigger-dev` → `config-and-build`.
- Task files live in `trigger/` and import `@trigger.dev/sdk` (no `/v3` path). The task-side Directus client is created inside the task, not imported from `lib/directus.ts`.
- Environment variables for **deployed** tasks are set in the Trigger.dev project, per environment. They do not come from `.env.local` and not from the Next.js host (`deployment` lists them).

Log the CLI in against your instance once (`npx trigger.dev@<server-version> login --api-url "$TRIGGER_API_URL"`), then start the dev server in its own terminal: `npx trigger.dev@<server-version> dev`.

## 8. Verify Connections

| Service | How to verify |
|---------|---------------|
| **Directus MCP** | Call the `schema` tool with no parameters: it lists the collections. If it fails, check Settings → AI → Model Context Protocol and the token |
| **Directus SDK** | A temporary route (below) |
| **Trigger.dev MCP** | Call `whoami` or `list_projects`; with `--dev-only` in `.mcp.json` only the dev environment answers |
| **Trigger.dev tasks** | `npx trigger.dev dev` lists the tasks of `trigger/`; trigger the example task with the MCP `trigger_task` tool and read it with `get_run_details` |
| **Next.js to Trigger.dev** | A Server Action or route that calls `tasks.trigger()` returns a run id (see `background-tasks`) |

```typescript
// app/api/directus-check/route.ts: temporary, delete it after the check
import directus from '@/lib/directus';
import { readCollections, serverPing } from '@directus/sdk';

export async function GET() {
  const [pong, collections] = await Promise.all([
    directus.request(serverPing()),
    directus.request(readCollections()),
  ]);
  return Response.json({ pong, collections: collections.length });
}
```

Open `/api/directus-check` with `npm run dev`. A `401` or `403` from Directus means the token is wrong or its user may not read the schema.

## 9. Project CLAUDE.md

Copy `templates/CLAUDE.md.template` to the project root as `CLAUDE.md` and replace `[PROJECT_NAME]`, `[DIRECTUS_URL]` and `[TRIGGER_API_URL]`.
