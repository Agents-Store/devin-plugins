---
name: hooks
description: This skill should be used when the user asks about "Payload hooks", "beforeChange", "afterChange", "afterRead", "beforeDelete", "field hooks", "global hooks", "prevent hook loops", "Next.js revalidation in Payload", "transaction safe hooks", "auto-set author from req.user", or needs to wire up lifecycle automation in PayloadCMS.
---

# PayloadCMS — Hooks

Hooks let you inject logic at every step of a document's lifecycle. They live on collections, globals, and individual fields. Use them for slug generation, audit logs, cache invalidation, side effects (email, webhooks), and computed values — without forking the admin or the API.

## Hook Categories

| Where | Available hooks |
| --- | --- |
| **Collection** | `beforeOperation`, `beforeValidate`, `beforeChange`, `afterChange`, `beforeRead`, `afterRead`, `beforeDelete`, `afterDelete`, `afterOperation`, `afterError`, plus auth-only: `beforeLogin`, `afterLogin`, `afterLogout`, `afterForgotPassword`, `afterMe`, `afterRefresh` |
| **Global** | `beforeValidate`, `beforeChange`, `afterChange`, `beforeRead`, `afterRead` |
| **Field** | `beforeValidate`, `beforeChange`, `afterChange`, `afterRead` |

Every hook is an array — Payload runs them in order. Plugins **append** to these arrays; never overwrite.

## Hook Argument Shape

Every collection hook receives roughly the same args (precise shape varies per hook). Common keys:

```ts
{
  doc,            // Current document (after change for afterChange, before for beforeChange)
  data,           // Incoming data (beforeChange) or null
  previousDoc,    // Document state before update
  operation,      // 'create' | 'update'
  req,            // Payload Request — contains payload, user, locale, transactionID, context, headers
  context,        // req.context — your own flags
  collection,     // SanitizedCollectionConfig
  originalDoc,    // Doc as fetched from DB (pre-mutation)
}
```

`req.payload` is the Payload instance — use it for nested DB calls. Always pass `req` through:
```ts
await req.payload.update({ collection: 'audit', data: {/*…*/}, req })
```

## beforeChange — runs on create + update

The most common hook. Use it to:
- Normalize / sanitize values.
- Generate derived fields (slugs, search-index strings).
- Set `author = req.user.id` automatically.
- Reject invalid combinations with a thrown error.

```ts
import slugify from 'slugify'

hooks: {
  beforeChange: [
    async ({ data, operation, req }) => {
      // Auto-slugify title on create
      if (operation === 'create' && data.title && !data.slug) {
        data.slug = slugify(data.title, { lower: true, strict: true })
      }

      // Stamp the author from the authenticated user
      if (operation === 'create' && req.user) {
        data.author = req.user.id
      }

      return data                       // Always return data
    },
  ],
}
```

Throwing inside `beforeChange` aborts the operation. Use `APIError` for proper HTTP responses:
```ts
import { APIError } from 'payload'

if (data.price < 0) {
  throw new APIError('Price cannot be negative.', 400, undefined, true)
}
```

## afterChange — runs after persist

Side effects only. The change is already saved.

```ts
hooks: {
  afterChange: [
    async ({ doc, previousDoc, operation, req, collection }) => {
      // Cache invalidation (see Next.js Revalidation section)
      if (doc._status === 'published') {
        revalidatePath(`/${collection.slug}/${doc.slug}`)
      }

      // Write to audit log — pass req to keep the same transaction
      await req.payload.create({
        collection: 'audit-log',
        data: {
          action: operation,
          collection: collection.slug,
          docId: doc.id,
          userId: req.user?.id,
        },
        req,
      })

      return doc
    },
  ],
}
```

## afterRead — transform on every fetch

Runs on every find / findByID / REST / GraphQL response. Heavy compute here can wreck performance — cache when possible.

```ts
hooks: {
  afterRead: [
    ({ doc }) => {
      doc.computedExcerpt = (doc.content || '').slice(0, 200)
      return doc
    },
  ],
}
```

Common use cases: hide sensitive fields, decorate with derived values, populate from external APIs.

## beforeDelete — cascading cleanup

```ts
hooks: {
  beforeDelete: [
    async ({ id, req }) => {
      // Cascade: delete all comments belonging to this post
      await req.payload.delete({
        collection: 'comments',
        where: { post: { equals: id } },
        req,
      })
    },
  ],
}
```

## beforeValidate — coerce / normalize

Runs before field validators. Last chance to fix incoming data.

```ts
hooks: {
  beforeValidate: [
    ({ data }) => {
      if (typeof data.tags === 'string') {
        data.tags = data.tags.split(',').map((t) => t.trim())
      }
      return data
    },
  ],
}
```

## afterError — capture failures

```ts
hooks: {
  afterError: [
    async ({ error, req }) => {
      req.payload.logger.error({ msg: 'collection error', err: error })
      // Optional: forward to Sentry, etc.
    },
  ],
}
```

## Auth-only Hooks

For collections with `auth: true`:

```ts
hooks: {
  beforeLogin: [
    async ({ user, req }) => {
      if (user.disabled) {
        throw new APIError('Account disabled', 403)
      }
    },
  ],
  afterLogin: [
    async ({ user, req }) => {
      await req.payload.update({
        collection: 'users',
        id: user.id,
        data: { lastLoginAt: new Date().toISOString() },
        req,
      })
    },
  ],
  afterForgotPassword: [
    async ({ args }) => {
      // Custom email or webhook
    },
  ],
}
```

## Field Hooks

Same shapes as collection hooks but scoped to one field:

```ts
{
  name: 'slug',
  type: 'text',
  hooks: {
    beforeValidate: [
      ({ data, value }) => value || slugify(data?.title || ''),
    ],
    afterRead: [
      ({ value }) => value?.toLowerCase(),
    ],
  },
}
```

Field hooks fire **inside** the surrounding collection hook step — i.e., all field `beforeChange` hooks run during the collection's `beforeChange` phase.

## Global Hooks

Globals have a single document, so there's no `beforeDelete`. Otherwise same args:

```ts
export const Header: GlobalConfig = {
  slug: 'header',
  fields: [/* … */],
  hooks: {
    afterChange: [
      async ({ doc }) => {
        revalidateTag('global-header')
      },
    ],
  },
}
```

## Critical Patterns

### Thread `req` through nested ops to keep transactions atomic

```ts
// ❌ BREAKS TRANSACTION — runs in its own transaction
afterChange: [
  async ({ doc, req }) => {
    await req.payload.create({
      collection: 'audit',
      data: { /*…*/ },
      // missing req!
    })
  },
]

// ✅ ATOMIC — joins the calling transaction
afterChange: [
  async ({ doc, req }) => {
    await req.payload.create({
      collection: 'audit',
      data: { /*…*/ },
      req,
    })
  },
]
```

Without `req`, the nested write commits separately — if the parent rolls back, your "side effect" doesn't.

### Prevent infinite hook loops with `context`

```ts
afterChange: [
  async ({ doc, req, context }) => {
    if (context?.skipHooks) return doc           // Bail out re-entrant

    await req.payload.update({
      collection: 'posts',
      id: doc.id,
      data: { viewCount: (doc.viewCount || 0) + 1 },
      context: { skipHooks: true },               // Tell ourselves not to re-fire
      req,
    })

    return doc
  },
]
```

`req.context` is a plain object passed through the whole request — your skip flags, cache keys, or correlation IDs live here.

### Next.js revalidation with context control

```ts
import { revalidatePath, revalidateTag } from 'next/cache'

hooks: {
  afterChange: [
    ({ doc, req, context }) => {
      if (context?.disableRevalidate) return doc
      if (doc._status === 'published') {
        revalidatePath(`/posts/${doc.slug}`)
        revalidateTag('posts')
      }
      return doc
    },
  ],
  afterDelete: [
    ({ doc }) => {
      revalidatePath(`/posts/${doc.slug}`)
      revalidateTag('posts')
    },
  ],
}
```

When you want to bulk-write without triggering ISR: `payload.update({ ..., context: { disableRevalidate: true }, req })`.

## Logger Usage

Use `payload.logger` for structured logs that survive transactions:
```ts
req.payload.logger.error({ msg: 'sync failed', err })  // ✅ object form
req.payload.logger.info('cache warmed')                 // ✅ string form

// ❌ Invalid: don't pass the error as a 2nd arg
// req.payload.logger.error('something failed', err)
```

## Where Hooks Live

```txt
src/collections/
├── Posts.ts
├── Posts.hooks/
│   ├── slugify.ts
│   ├── stampAuthor.ts
│   ├── revalidate.ts
│   └── index.ts
```

Importing from a sibling folder keeps the collection file readable:
```ts
import { slugify, stampAuthor, revalidate } from './Posts.hooks'

export const Posts: CollectionConfig = {
  // …
  hooks: {
    beforeChange: [slugify, stampAuthor],
    afterChange: [revalidate],
  },
}
```

After every hooks change run `pnpm generate:types` only if you changed field shapes — hook code is plain TS, not stored in the config.
