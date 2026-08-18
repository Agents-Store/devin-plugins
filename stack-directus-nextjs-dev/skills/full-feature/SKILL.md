---
name: full-feature
description: This skill should be used when the user wants to "build a complete feature with Directus and Next.js", "create an end-to-end page from Directus data", "implement a full CRUD feature across Directus and Next.js", "build a new section of the site", "create a page that shows Directus data", "build a dashboard with Directus content", "display Directus collection in Next.js", "add a new page with CMS data", or needs a step-by-step recipe for building features that span both Directus and Next.js.
---

# Full Feature Recipe

Build end-to-end features across Directus (data) and Next.js (interface) using a repeatable 5-step pattern. Follow the template in `template.md` for each new feature.

## Pattern Overview

Every feature in this stack follows the same flow:

1. **Data Model** — Create or extend Directus collections and fields
2. **TypeScript Types** — Define interfaces matching the new/updated collections
3. **Next.js Pages** — Build Server Components that fetch and render the data
4. **Mutations** — Add Server Actions for create/update operations (if needed)
5. **Verify** — Test the complete data flow from Directus to rendered page

## Prerequisites

- init-project completed (SDK client, TypeScript schema, env vars configured)
- Directus MCP connection working
- Next.js dev server running

## How to Use

Read `template.md` and fill in the placeholders for each new feature. The template provides the exact file paths, code patterns, and verification steps.

For data modeling guidance, defer to the `directus-dev` plugin. For Next.js page patterns, defer to the `nextjs-dev` plugin. This recipe coordinates both.

## Quick Reference

| Step | Where | What |
|------|-------|------|
| Data Model | Directus Admin or MCP tools | Create collection, add fields, set permissions |
| TypeScript | `types/directus.ts` | Add interface, update Schema type |
| Pages | `app/{route}/page.tsx` | Server Component with `readItems` |
| Detail | `app/{route}/[slug]/page.tsx` | Dynamic route with `generateStaticParams` + `generateMetadata` |
| Actions | `app/{route}/actions.ts` | Server Actions with `createItem`/`updateItem` |
| Verify | Browser + Directus | Check rendering, images, mutations, revalidation |
