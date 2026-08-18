---
name: examples
description: This skill should be used when the user asks "show me a complete Payload example", "give me a working Payload blog", "Payload ecommerce example", "Payload auth-only API example", "Payload jobs worker example", "Payload multi-tenant example", or wants end-to-end scenario walkthroughs instead of isolated snippets.
---

# PayloadCMS — Complete Examples

Index of end-to-end scenario walkthroughs. Each scenario lives in `references/scenarios/` as a fully runnable reference — collections, hooks, access rules, frontend pages — copy/paste ready.

| Scenario | What it shows | File |
| --- | --- | --- |
| Blog CMS | Posts with drafts, autosave, live preview, Lexical content, tags, categories, public frontend with ISR + revalidation | `references/scenarios/blog-cms.md` |
| E-commerce product catalog | Products, variants via blocks, inventory, Stripe price IDs, customer auth, Resend confirmation email queued as a job | `references/scenarios/ecommerce-product-catalog.md` |
| Auth-only API (headless) | User/role/permission model, custom endpoints, no admin UI for clients, JWT + API-key auth, rate-limited login | `references/scenarios/auth-only-api.md` |
| Jobs worker | Background image resize on upload + nightly cleanup workflow + Vercel cron trigger | `references/scenarios/jobs-worker.md` |
| Multi-tenant SaaS | `tenants` collection, `tenant`-scoped access on every collection, sub-domain routing, per-tenant settings global | `references/scenarios/multi-tenant-saas.md` |

## When to Use This Skill vs Others

| Want | Use |
| --- | --- |
| Smallest reproducible example for one feature | This skill — open the right scenario file |
| Reference for a specific method signature | `api-reference` |
| Idiomatic patterns explained | `collections` / `fields` / `hooks` / `access-control` / `queries` |
| Building 3rd-party plugins | `plugin-development` |
| Why something is broken | `troubleshoot` |
| Moving content from another CMS | `cms-migration` |

## Reading Order if You're New to Payload

1. `references/scenarios/blog-cms.md` — covers ~60% of typical Payload usage.
2. `references/scenarios/auth-only-api.md` — see auth + custom endpoints without admin distraction.
3. `references/scenarios/ecommerce-product-catalog.md` — fields composition, jobs, email.
4. `references/scenarios/multi-tenant-saas.md` — access control at scale.
5. `references/scenarios/jobs-worker.md` — background processing.

Each scenario is self-contained — you can lift any single file into a fresh project and adapt.
