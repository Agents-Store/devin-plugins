---
name: full-feature
description: This skill should be used when the user wants to "build a complete feature with Directus and Next.js", "create an end-to-end page from Directus data", "implement a full CRUD feature across Directus and Next.js", "build a new section of the site", "create a page that shows Directus data", "build a dashboard with Directus content", "display Directus collection in Next.js", "add a new page with CMS data", or needs a step-by-step recipe for building features that span both Directus and Next.js.
---

# Full Feature Recipe

Build end-to-end features across Directus (data) and Next.js (interface) with a repeatable six-step pattern. Follow the template in `template.md` for each new feature.

## Pattern Overview

Every feature in this stack follows the same flow:

1. **Data Model** — Create or extend the Directus collection, its fields and its permissions
2. **TypeScript Types** — Mirror the collection in `types/directus.ts`
3. **Reads** — One tagged read function per query in `lib/content/`, then Server Component pages that call it
4. **Mutations** — Server Actions that authenticate, authorize, write, then expire the tag (if needed)
5. **Register for Revalidation** — Add the collection to the Directus Flow and to the Route Handler's allow-list
6. **Verify** — Types compile, the page renders, an edit in Directus reaches the page

## Prerequisites

- `init-project` completed (client, schema type, environment variables)
- The revalidation pipeline from `deployment` exists (Flow and `/api/revalidate`)
- Directus MCP connection working
- Next.js dev server running

## How to Use

Read `template.md` and fill in the placeholders for each new feature. It gives the file paths, code patterns and verification steps.

For data modeling guidance defer to `directus-dev`; for page patterns defer to `nextjs-dev`. The rules at the boundary (token, cache, assets, types) are in `directus-to-nextjs`; this recipe applies them in order.

## Quick Reference

| Step | Where | What |
|------|-------|------|
| Data Model | Directus Studio or MCP tools | Create collection, add fields, give the server token's policy read (and write if needed) |
| TypeScript | `types/directus.ts` | Add the interface, update `Schema` |
| Reads | `lib/content/{collection}.ts` | `requestTagged(readItems(...), [collection], seconds)` inside `cache()` |
| Pages | `app/{route}/page.tsx`, `app/{route}/[slug]/page.tsx` | Server Components calling the read functions, plus `generateStaticParams` and `generateMetadata` |
| Actions | `app/{route}/actions.ts` | `requireUser()`, then `createItem` / `updateItem` with the user's token (`withToken`), then `updateTag` |
| Revalidation | Directus Flow, `app/api/revalidate/route.ts` | The collection name in both lists |
| Verify | `npx tsc --noEmit`, browser, Directus | Types, rendering, images, an edit reaching the page |
