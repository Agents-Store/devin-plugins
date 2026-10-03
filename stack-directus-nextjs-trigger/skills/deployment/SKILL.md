---
name: deployment
description: This skill should be used when the user wants to "run the Directus Next.js Trigger.dev stack locally", "deploy trigger.dev tasks next to a Next.js app", "set environment variables for trigger.dev tasks", "configure content-change webhooks with trigger.dev", "revalidate the site when a task changes Directus content", "CI/CD for trigger tasks", "production checklist for directus + nextjs + trigger.dev", or needs the pipelines that connect the three services and the checks before production. For platform-specific hosting (Vercel, Dokploy, etc.), see the respective deployment plugin.
---

# Deployment: Pipelines, Environments and Production Checklist

What connects the three services when they run for real: the local setup, the paths from an editor's save, a schedule or a user's click to a fresh page, the environment variables each service needs, and the list to check before production. Hosting platform specifics (Vercel, Dokploy, Netlify) belong to the deployment plugin for that platform; how a task is built and deployed belongs to `trigger-dev` → `deployment`.

## Local Development

Three terminals:

```bash
# 1. Directus, from the Compose file of directus-dev (docker-local-dev: pinned image, loopback port)
docker compose up -d
curl http://localhost:8055/server/ping          # pong; the health endpoint needs a token in Directus 12

# 2. Trigger.dev dev server: tasks run on this machine, against your self-hosted server
npx trigger.dev dev --env-file .env.trigger.local

# 3. Next.js
npm run dev
```

Two environment files, because the services read them differently:

| File | Read by | Holds |
|------|---------|-------|
| `.env.local` (from `templates/.env.example`) | Next.js | Directus, auth, revalidation and Trigger.dev SDK variables. Next.js expands `${VAR}` in it, which is how `DIRECTUS_URL=${NEXT_PUBLIC_DIRECTUS_URL}` works |
| `.env.trigger.local` (from `templates/.env.trigger.example`) | `trigger dev` | The variables the **tasks** read, with literal values |

The Trigger.dev CLI loads `.env`, `.env.local` and the other dotenv files of the project into the dev run, but it does **not** expand `${VAR}`. Checked with the dotenv loader of `trigger.dev` 4.7.2 (`resolveDotEnvVars`, run against an aliased `.env.local`): a task that read `DIRECTUS_URL` from it would get the literal text `${NEXT_PUBLIC_DIRECTUS_URL}`, and every call would fail with `Failed to parse URL`. `--env-file` makes the CLI read that one file only. The name `.env.trigger.local` matches the `.env*.local` and `.env*` ignore patterns of a Next.js project, so the task token stays out of git.

In `dev` the tasks run locally, so a task can call `http://localhost:3000/api/revalidate`. A Directus Flow cannot: its `request` operation runs inside the Directus container, where `localhost` is the container (`directus-dev` → `flow-automation` → `references/notify-external-app.md`). A schedule fires in `dev` only while the dev server runs.

## Four Pipelines, One Revalidation Route

```
1. editor saves in Directus
     -> Flow -> POST /api/revalidate (header secret, body {"collection":"posts"})
     -> revalidateTag(collection) -> the next visitor gets the new page

2. editor saves, a task does work on it
     -> Flow -> POST /api/directus-webhook/<collection> (header secret, body: event, collection, keys)
     -> receiver starts the task with ids -> task reads, works, writes back to Directus
     -> the revalidation Flow (pipeline 1) sees the write and expires the tag -> fresh page   (directus-to-trigger)

3. a schedule fires
     -> task reads or fetches, writes to Directus
     -> the revalidation Flow expires the tag -> fresh page   (trigger-dev -> scheduled-tasks)

4. a user acts
     -> Server Action authenticates, authorizes, starts the task with ids, returns the run id and token
     -> the browser subscribes to the run                   (background-tasks, trigger-dev -> realtime)
     -> when the task wrote to Directus, the revalidation Flow expires the tag
```

Each piece is taught where its tool lives:

| Piece | Where |
|-------|-------|
| Flow with a `request` operation, the secret in a header read from `$env` (`FLOWS_ENV_ALLOW_LIST`), where the request is made from | `directus-dev` → `flow-automation` → `references/notify-external-app.md` |
| Flow that sends item keys to a worker, the write-back loop guard | `directus-dev` → `flow-automation` → `references/send-items-to-a-worker.md` |
| The Route Handler `/api/revalidate`: secret check, tag allow-list, `revalidateTag` | `nextjs-dev` → `data-fetching` → `references/headless-cms.md` |
| Which tag each Directus read carries | "Cache" in `directus-to-nextjs` |
| The receiver that starts tasks, the task-side Directus client, the call back to `/api/revalidate` | `directus-to-trigger`, `background-tasks` |

Two things only the stack can tell you:

- **The names must agree.** A tag is a Directus collection name. The revalidation Flow lists collections, the Route Handler allows the same list, and `lib/content.ts` tags reads with them (including expanded relations). A collection missing from one of them never refreshes, whoever wrote to it: an editor, a task or an import. A task that calls the route itself sends the same collection name.
- **`REVALIDATION_SECRET` lives in two places, three when a task calls the route**: the Directus container (with `FLOWS_ENV_ALLOW_LIST`), the Next.js hosting environment, and the Trigger.dev environment of a task that calls `/api/revalidate` itself. Different values give `401` and a stale site, and nothing shows it unless the Flow logs its reject path and the task checks the response of its call.

Hosting platforms that rebuild on a deploy hook can use that hook as the Flow's URL instead; configure it through the platform's own plugin.

## Environment Variables: Four Places

| Where | Variables |
|-------|-----------|
| **Next.js host** (build and runtime) | `NEXT_PUBLIC_DIRECTUS_URL`, `DIRECTUS_ADMIN_TOKEN`, the aliases `DIRECTUS_URL`, `DIRECTUS_TOKEN`, `NEXT_PUBLIC_CMS_URL` (a platform may not expand `${...}` the way `.env.local` does: give each name its value), the auth secrets, `REVALIDATION_SECRET`, `DIRECTUS_WEBHOOK_SECRET`, `TRIGGER_API_URL`, `TRIGGER_SECRET_KEY` (the key of the environment you run in), `NEXT_PUBLIC_TRIGGER_API_URL` |
| **Directus container** | `REVALIDATION_SECRET`, `DIRECTUS_WEBHOOK_SECRET`, and `FLOWS_ENV_ALLOW_LIST=REVALIDATION_SECRET,DIRECTUS_WEBHOOK_SECRET` |
| **Trigger.dev environment**, one set per environment (dev, staging, prod) | `DIRECTUS_URL`, `DIRECTUS_TOKEN` (the **task** user's token), every third-party key a task uses, and `NEXT_PUBLIC_SITE_URL` with `REVALIDATION_SECRET` for a task that calls `/api/revalidate` itself |
| **CI that deploys tasks** | `TRIGGER_ACCESS_TOKEN`, `TRIGGER_API_URL`, and the registry login of a self-hosted instance (`trigger-dev` → `deployment`) |

A task runs on the Trigger.dev workers, not on the Next.js host, and sees none of the host's variables. How to set them per environment (dashboard, `trigger env set`, the `syncEnvVars` build extension) is in `trigger-dev` → `deployment` ("Self-Hosted Runtime Environment Variables"). A missing one shows up as `Failed to parse URL from undefined/...` inside the run; the task-side client in `directus-to-trigger` checks them up front and names the missing variable.

`DIRECTUS_TOKEN` of the Trigger.dev environment belongs to its own Directus user, whose policy grants exactly what the tasks read and write. Do not reuse the token of the Next.js server or of an administrator.

## Deploying Tasks

Tasks deploy **separately** from the Next.js app, with the CLI, to the environment you target (`trigger-dev` → `deployment` has the flags, the self-hosted registry login and the CI recipes; none of it is repeated here). What belongs to this stack:

- **One version line.** `trigger.dev` (CLI), `@trigger.dev/sdk`, `@trigger.dev/react-hooks` and the server are the same version. Keep `trigger.dev` in `devDependencies` and deploy through an npm script, not `@latest`.
- **The app and the tasks share payload types** (`import type` from `trigger/`). When a change adds a field the app sends, deploy the tasks first, or pin every run to the deployment built with the app: `deploy --external-id <commit sha>` together with `TRIGGER_EXTERNAL_DEPLOYMENT_ID` in the app's environment (server 4.5.12 or later; see "Version Skew Protection" in `trigger-dev` → `deployment`).
- **Check the tasks in CI with the app.** `npx tsc --noEmit` covers `trigger/` too, so a renamed Directus field fails the build instead of failing a run at 02:00.
- **Run Node 22 or later** in the CI job: the Directus SDK needs it, and Node 20 is end of life.
- **Test a run per task after each deploy** with the MCP `trigger_task` tool (`trigger-dev` → "Post-Deploy Verification"). A successful deploy does not prove the environment variables are right.

## Production Checklist

Directus:

- [ ] Image tag pinned to an exact 12.x version, not `latest`; `PUBLIC_URL` is the address editors open
- [ ] SSL in front of it. `IP_TRUST_PROXY` set when Directus sits behind a reverse proxy (default `false`)
- [ ] Persistent PostgreSQL with backups, and file storage that survives the container (volume or S3-compatible), backed up too
- [ ] The token in `DIRECTUS_ADMIN_TOKEN` belongs to a dedicated user with a narrow policy, not an administrator; the tasks use a different user's token
- [ ] Public policy: only what the public site needs. If it reads `directus_files`, every file is downloadable and listable (see "Assets" in `directus-to-nextjs`)
- [ ] `CORS_ORIGIN` lists the exact production origin, only if browser code or WebSockets talk to Directus
- [ ] The license tier fits the features you use (SSO, custom permission rules). An instance that stays over its limits after the grace period loses GraphQL, WebSockets and MCP
- [ ] The Flows are active: revalidation lists every collection the pages read, **including the ones tasks write to**; the task Flows list their collections and carry the loop-guard condition; secrets are in `FLOWS_ENV_ALLOW_LIST`

Next.js:

- [ ] `next@^16.3.8`, Node 22 or later, `proxy.ts` (the middleware file is deprecated in Next.js 16)
- [ ] All variables set in the hosting platform (table above), including `TRIGGER_API_URL`: without it the SDK sends the key to Trigger.dev Cloud
- [ ] `images.remotePatterns` names the production Directus host with `pathname: '/assets/**'` (or `localPatterns` for the proxy route), and `dangerouslyAllowLocalIP` is off in production
- [ ] No token in any URL a browser sees (images, links, query strings); no `TRIGGER_SECRET_KEY` in client code
- [ ] `/api/revalidate` rejects a wrong secret (`401`) and an unknown collection (`400`); `/api/directus-webhook/*` does the same
- [ ] `NEXTAUTH_SECRET` or `BETTER_AUTH_SECRET` is a strong random value, not the development placeholder
- [ ] `npx tsc --noEmit` passes in CI against the production schema

Trigger.dev:

- [ ] Server, SDK, CLI and react-hooks on one version; `trigger.dev` pinned in `devDependencies`
- [ ] Tasks deployed to the production environment, by CI with a secret `TRIGGER_ACCESS_TOKEN`, at least one test run per task afterwards
- [ ] Task environment variables set for production (table above), with the task user's own Directus token
- [ ] Declarative schedules that must not run in dev or staging carry `environments`; the `window` is chosen on purpose (`trigger-dev` → `scheduled-tasks`)
- [ ] Alerts for failed runs are configured in the project
- [ ] After a first publish in Directus, the page changes within seconds. If not, check the Flow's reject-path log first, then the receiver's `401`, then the run in the Trigger.dev dashboard
