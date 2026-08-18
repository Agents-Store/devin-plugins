---
name: examples
description: End-to-end scenario walkthroughs for the Directus + Next.js + Trigger.dev stack. This skill should be used when the user asks for "directus nextjs trigger.dev examples", "how to build a blog with directus + next.js", "ai enrichment pipeline example", "scheduled data sync example", "show me a complete example with background tasks", or needs implementation references for common application types on this stack.
---

# Examples: Directus + Next.js + Trigger.dev Scenarios

Complete walkthroughs for building common application types with this stack. Each scenario shows the full flow from Directus data model through Next.js rendering, and — where applicable — through Trigger.dev background work and back to Directus.

## Available Scenarios

| Scenario | Description | Key Patterns |
|----------|-------------|--------------|
| [Blog](references/scenarios/blog-with-directus.md) | Content blog with posts, authors, and categories | M2O relations, images, ISR, SEO metadata, RSS feed |
| [Product Catalog](references/scenarios/product-catalog.md) | E-commerce catalog with products, categories, and filtering | M2M relations, search params, image gallery, dynamic filters |
| [AI Enrichment Pipeline](references/scenarios/ai-enrichment-pipeline.md) | Directus article created → background LLM enrichment → write tags/summary back → revalidate | Directus Flow webhook, `tasks.trigger()`, idempotency, Directus SDK in task, close-the-loop revalidation |
| [Scheduled Data Sync](references/scenarios/scheduled-data-sync.md) | Daily cron pulls from external API → upserts into Directus → revalidates dashboard | `schedules.task()`, cron strings, upsert patterns, dashboard revalidation |

## How to Use

1. Pick the scenario closest to what you are building
2. Read the full walkthrough in `references/scenarios/`
3. Adapt the collections, fields, and page structure to your needs
4. Follow the `full-feature` template for each new feature you add
5. If your feature needs background work, also read `background-tasks` (for event-driven) or `scheduled-tasks` (for cron)

Each scenario includes:
- Directus collection schema (fields, relations, permissions)
- TypeScript interfaces
- Complete Next.js page code (listing, detail, metadata)
- Trigger.dev task definition (for AI/schedule scenarios)
- Image handling patterns
- Revalidation strategy
