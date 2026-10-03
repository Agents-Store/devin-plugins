---
name: full-feature
description: This skill should be used when the user wants to "build a complete feature with directus nextjs and trigger.dev", "create an end-to-end feature with background tasks", "implement a full crud feature with async processing", "build a new section of the site that uses background jobs", "add a page backed by directus with a background task", or needs a step-by-step recipe for building features that span Directus, Next.js, and Trigger.dev.
---

# Full Feature Recipe

Build end-to-end features across Directus (data), Next.js (interface and logic) and Trigger.dev (background work) with a repeatable seven-step pattern. Follow the template in `template.md` for each new feature.

## Pattern Overview

Every feature in this stack follows the same flow:

1. **Data Model**: create or extend the Directus collection, its fields and its permissions
2. **TypeScript Types**: mirror the collection in `types/directus.ts`
3. **Reads and Pages**: one tagged read function per query in `lib/content/`, then Server Component pages that call it
4. **Mutations**: Server Actions that authenticate, authorize, write, then expire the tag (if needed)
5. **Background Work**: a Trigger.dev task for what is slow or can fail, started by the action, a Directus Flow or a schedule (if needed)
6. **Register for Revalidation**: add the collection to the Directus Flow and to the Route Handler's allow-list
7. **Verify**: types compile, the page renders, an edit in Directus reaches the page, the task runs and its result reaches the page

## Prerequisites

- `init-project` completed (client, schema type, environment variables, Trigger.dev project)
- The revalidation pipeline from `deployment` exists (Flow and `/api/revalidate`)
- Directus MCP and Trigger.dev MCP connections working
- The dev servers running: Next.js (`npm run dev`) and Trigger.dev (`npx trigger.dev dev --env-file .env.trigger.local`)

## How to Use

Read `template.md` and fill in the placeholders for each new feature. It gives the file paths, code patterns and verification steps, including the task stub when background work is needed.

For data modeling defer to `directus-dev`; for page patterns defer to `nextjs-dev`; for task API depth (retries, queues, waits, realtime) defer to `trigger-dev`. The rules at the boundaries (token, cache, assets, types; ids across the task boundary) are in `directus-to-nextjs`, `background-tasks` and `directus-to-trigger`; this recipe applies them in order.

## Decide: Does This Feature Need a Task?

Before step 5, ask whether anything in the feature runs slowly, calls a third party, or must be retried:

| Signal | Task? |
|--------|-------|
| Renders from Directus data in under 200 ms | No: stay in the Server Component |
| A user mutates data through a Server Action in under a second, deterministically | No: inline in the action |
| An AI call, image or PDF processing, an email | **Yes** |
| An external call that can fail (webhook, payment, third-party API) | **Yes** |
| A bulk operation over many records | **Yes** |
| Must run on a schedule | **Yes**: `schedules.task` (`trigger-dev` → `scheduled-tasks`) |
| Needs retries, or runs longer than the serverless limit | **Yes** |

If any "Yes" applies, do step 5. Otherwise skip it.

## Quick Reference

| Step | Where | What |
|------|-------|------|
| Data Model | Directus Studio or MCP tools | Create the collection, add fields, give the server token's policy read; give the task user's policy only the result fields |
| TypeScript | `types/directus.ts` | Add the interface, update `Schema` (tasks import the same file) |
| Reads | `lib/content/{collection}.ts` | `requestTagged(readItems(...), [collection], seconds)` inside `cache()` |
| Pages | `app/{route}/page.tsx`, `app/{route}/[slug]/page.tsx` | Server Components calling the read functions, plus `generateStaticParams` and `generateMetadata` |
| Actions | `app/{route}/actions.ts` | `requireUser()`, then the write with the user's token (`withToken`) or a role check, then `updateTag`; when a task is needed, `tasks.trigger` with ids |
| Task | `trigger/{feature}.ts` | `task({ id, run })` reading the record, skipping what is done, writing results, `onFailure` marking `failed` |
| Revalidation | Directus Flow, `app/api/revalidate/route.ts` | The collection name in both lists |
| Verify | `npx tsc --noEmit`, browser, Directus, Trigger.dev dashboard | Types, rendering, images, an edit reaching the page, a run that ends `done` |

## Fresh Pages After a Task

When a task changes Directus content, the revalidation Flow (step 6) expires the tag for the task's write like it does for an editor's save, so the page refreshes without code in the task. The task calls `/api/revalidate` itself only when the Flow does not cover the collection (`background-tasks` → "Closing the Loop"). A page that shows task state (`processing_status`) can subscribe to the run in the browser (`background-tasks` → "Show the Run in the Browser").
