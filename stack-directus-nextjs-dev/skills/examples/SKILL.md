---
name: examples
description: End-to-end scenario walkthroughs for the Directus + Next.js stack. This skill should be used when the user asks for "Directus Next.js examples", "how to build a blog with Directus and Next.js", "Directus Next.js product catalog", "show me a complete example", or needs implementation references for common application types.
---

# Examples: Directus + Next.js Scenarios

Complete walkthroughs for building common application types with this stack. Each scenario shows the full flow from Directus data model to rendered Next.js pages.

## Available Scenarios

| Scenario | Description | Key Patterns |
|----------|-------------|--------------|
| [Blog](references/scenarios/blog-with-directus.md) | Content blog with posts, authors, and categories | M2O relations, images, ISR, SEO metadata, RSS feed |
| [Product Catalog](references/scenarios/product-catalog.md) | E-commerce catalog with products, categories, and filtering | M2M relations, search params, image gallery, dynamic filters |

## How to Use

1. Pick the scenario closest to what you are building
2. Read the full walkthrough in `references/scenarios/`
3. Adapt the collections, fields, and page structure to your needs
4. Follow the `full-feature` template for each new feature you add

Each scenario includes:
- Directus collection schema (fields, relations, permissions)
- TypeScript interfaces
- Complete Next.js page code (listing, detail, metadata)
- Image handling patterns
- Revalidation strategy
