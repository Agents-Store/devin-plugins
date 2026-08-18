---
name: full-feature
description: This skill should be used when the user wants to "build a complete feature with directus nextjs and trigger.dev", "create an end-to-end feature with background tasks", "implement a full crud feature with async processing", "build a new section of the site that uses background jobs", "add a page backed by directus with a background task", or needs a step-by-step recipe for building features that span Directus, Next.js, AND Trigger.dev.
---

# Full Feature Recipe

Build end-to-end features across Directus (data), Next.js (interface + logic), and Trigger.dev (background work) using a repeatable 6-step pattern. Follow the template in `template.md` for each new feature.

## Pattern Overview

Every feature in this stack follows the same flow:

1. **Data Model** — Create or extend Directus collections and fields
2. **TypeScript Types** — Define interfaces matching the new/updated collections
3. **Next.js Pages** — Build Server Components that fetch and render the data
4. **Mutations** — Add Server Actions for create/update operations (if needed)
5. **Background Work** — Delegate slow/flaky operations to Trigger.dev tasks (if needed)
6. **Verify** — Test the complete data flow end-to-end: Directus → Next.js → Trigger task → back to Directus → rendered page

## Prerequisites

- `init-project` completed (SDK client, TypeScript schema, env vars, Trigger.dev initialized)
- Directus MCP connection working
- Trigger.dev dev server running (`npx trigger.dev@latest dev`)
- Next.js dev server running (`npm run dev`)

## How to Use

Read `template.md` and fill in the placeholders for each new feature. The template provides the exact file paths, code patterns, and verification steps — including the Trigger.dev task stub if background work is needed.

For Directus data modeling, defer to the `directus-dev` plugin. For Next.js page patterns, defer to the `nextjs-dev` plugin. For Trigger.dev task API depth (retries, queues, waits, realtime), defer to the `trigger-dev` plugin. This recipe coordinates all three.

## Decide: Does this feature need a background task?

Before step 5, ask: does anything in this feature run slowly, call a third party, or need to retry on failure?

| Signal | Delegate to Trigger? |
|--------|----------------------|
| Directly renders from Directus data in <200ms | No — stay in Server Component |
| User mutates data via Server Action, <1s, deterministic | No — inline in Server Action |
| AI/LLM call, image processing, PDF generation, email send | **Yes — Trigger task** |
| External API call that can fail (webhook, payment, third-party) | **Yes — Trigger task** |
| Bulk operation over many records | **Yes — Trigger task** |
| Must run on a schedule (cron) | **Yes — `schedules.task()`** (see `scheduled-tasks` skill) |
| Needs retries or long-running (>30s serverless timeout) | **Yes — Trigger task** |

If any "Yes" applies, add step 5. Otherwise, skip it.

## Quick Reference

| Step | Where | What |
|------|-------|------|
| Data Model | Directus Admin or MCP tools | Create collection, add fields, set permissions |
| TypeScript | `types/directus.ts` | Add interface, update Schema type |
| Pages | `app/{route}/page.tsx` | Server Component with `readItems` |
| Detail | `app/{route}/[slug]/page.tsx` | Dynamic route with `generateStaticParams` + `generateMetadata` |
| Actions | `app/{route}/actions.ts` | Server Actions with `createItem`/`updateItem` |
| Task | `trigger/{feature}.ts` | `task({ id, run })` with Directus SDK + third-party calls |
| Trigger point | Server Action / route handler / Directus Flow webhook | `tasks.trigger<typeof myTask>(...)` with `force-dynamic` |
| Verify | Browser + Directus + Trigger dashboard | Check rendering, mutations, task runs, revalidation |

## The Close-the-Loop Pattern

For features where a Trigger task mutates Directus, always close the loop back to the Next.js ISR cache:

1. Next.js page reads from Directus
2. User action → Server Action → `tasks.trigger(myTask, { itemId })` → immediate return with run handle
3. (Optional) Client Component subscribes via `useRealtimeRun(handle.id)` to show progress
4. Task runs → calls Directus SDK → updates item
5. Task calls `revalidatePath()` or POSTs to `/api/revalidate` → Next.js cache invalidates
6. Next fetch returns updated data

Without step 5, users see stale content until the next ISR interval or manual revalidation. See `background-tasks` skill for the full wiring, and `directus-to-trigger` for the Directus-event-driven variant.
