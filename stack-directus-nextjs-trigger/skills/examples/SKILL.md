---
name: examples
description: End-to-end scenario walkthroughs for the Directus + Next.js + Trigger.dev stack. This skill should be used when the user asks for "directus nextjs trigger.dev examples", "how to build a blog with directus + next.js", "ai enrichment pipeline example", "scheduled data sync example", "show me a complete example with background tasks", or needs implementation references for common application types on this stack.
---

# Examples: Directus + Next.js + Trigger.dev Scenarios

Complete walkthroughs for building common application types with this stack. Each scenario shows the flow from the Directus data model through Next.js rendering, and where it applies through Trigger.dev work and back to Directus. They use the rules of `directus-to-nextjs` (tagged reads, no token in asset URLs), `directus-to-trigger` and `background-tasks`, and the pipelines of `deployment`.

## Available Scenarios

| Scenario | Description | Key Patterns |
|----------|-------------|--------------|
| [Blog](references/scenarios/blog-with-directus.md) | Content blog with posts, authors, and categories | M2O and M2M relations, images, tagged reads, SEO metadata, RSS feed |
| [Product Catalog](references/scenarios/product-catalog.md) | E-commerce catalog with products, categories, and filtering | Decimal fields, search params, typed filters, image gallery, uncached search |
| [AI Enrichment Pipeline](references/scenarios/ai-enrichment-pipeline.md) | An article is created or edited in Directus, a task adds an AI summary and tags, the page shows them | Flow with a loop-guard condition, receiver, debounced `tasks.trigger`, source-hash skip, `onFailure`, task-side client |
| [Scheduled Data Sync](references/scenarios/scheduled-data-sync.md) | A daily cron pulls rates from a provider and upserts them into Directus | `schedules.task` with `environments`, upsert on a unique key, tagged dashboard read |

## How to Use

1. Pick the scenario closest to what you are building
2. Read the full walkthrough in `references/scenarios/`
3. Adapt the collections, fields, and page structure to your needs
4. Follow the `full-feature` template for each new feature you add
5. If the feature needs work off the request path, also read `background-tasks` (started by a user), `directus-to-trigger` (started by a Directus change) or `trigger-dev` → `scheduled-tasks` (started by the clock)

Each scenario includes:
- The Directus collection schema (fields, relations, permissions), including the policy of the task's own user where there is a task
- TypeScript interfaces (or a pointer to the shared ones in `directus-dev`)
- The Next.js page code (listing, detail, metadata, dashboard)
- The Trigger.dev task and the Flow settings (for the AI and schedule scenarios)
- The revalidation strategy: which tags, which collections the Flow lists
