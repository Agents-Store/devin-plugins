# Access Control — Advanced Patterns

Beyond the basics in the main SKILL.md. Patterns from production multi-tenant SaaS, subscription apps, and audit-driven systems.

## Access Function Factories

When you need to parameterize behavior across many collections, write a factory:

```ts
import type { Access } from 'payload'

export const isOwner =
  (ownerField: string): Access =>
  ({ req: { user } }) => {
    if (!user) return false
    if (user.roles?.includes('admin')) return true
    return { [ownerField]: { equals: user.id } }
  }

// Reuse across collections
export const Posts: CollectionConfig = {
  slug: 'posts',
  access: { update: isOwner('author'), delete: isOwner('author') },
  fields: [/*…*/],
}

export const Orders: CollectionConfig = {
  slug: 'orders',
  access: { update: isOwner('customer'), read: isOwner('customer') },
  fields: [/*…*/],
}
```

## Context-Aware Access

You can read `req.headers`, `req.context`, or any custom property:

```ts
export const internalOnly: Access = ({ req }) => {
  const apiKey = req.headers.get('x-internal-key')
  return apiKey === process.env.INTERNAL_API_KEY
}
```

Useful for server-to-server endpoints, webhooks, build-time generation.

## Time-Based Access

```ts
export const duringPublishWindow: Access = () => ({
  and: [
    { publishedAt: { less_than_equal: new Date().toISOString() } },
    {
      or: [
        { expiresAt: { exists: false } },
        { expiresAt: { greater_than: new Date().toISOString() } },
      ],
    },
  ],
})
```

Now drafts before `publishedAt` and expired content after `expiresAt` are invisible to public callers.

## Subscription-Gated Access

```ts
import type { User } from '@/payload-types'

export const proSubscribersOnly: Access = ({ req: { user } }) => {
  if (!user) return false
  const u = user as User
  if (u.roles?.includes('admin')) return true
  if (u.subscriptionTier !== 'pro') return false
  if (u.subscriptionExpiresAt && new Date(u.subscriptionExpiresAt) < new Date()) {
    return false
  }
  return true
}
```

Combine with Stripe webhooks (`afterChange` on a `subscriptions` collection) to flip `subscriptionTier` automatically.

## Multi-Tenant: Strict Isolation

```ts
// src/access/tenantIsolation.ts
import type { Access } from 'payload'
import type { User } from '@/payload-types'

export const tenantRead: Access = ({ req: { user } }) => {
  if (!user) return false
  const u = user as User
  if (u.roles?.includes('platform-admin')) return true
  return { tenant: { equals: u.tenant } }
}

export const tenantWrite: Access = ({ req: { user } }) => {
  if (!user) return false
  const u = user as User
  if (u.roles?.includes('platform-admin')) return true
  // Only tenant admins can write
  if (!u.roles?.includes('tenant-admin')) return false
  return { tenant: { equals: u.tenant } }
}
```

Pair with a `beforeChange` hook that stamps `data.tenant = req.user.tenant` on create so users can't smuggle in a foreign tenant:

```ts
hooks: {
  beforeChange: [
    ({ data, req, operation }) => {
      if (operation === 'create' && req.user) {
        data.tenant = (req.user as User).tenant
      }
      return data
    },
  ],
}
```

And a field-level `update` block to prevent reassignment:
```ts
{
  name: 'tenant',
  type: 'relationship',
  relationTo: 'tenants',
  required: true,
  access: {
    update: ({ req: { user } }) => (user as User)?.roles?.includes('platform-admin') ?? false,
  },
}
```

## Read vs. Write Asymmetry

Often the right policy: anyone in the team can read, only owners/admins can write.

```ts
access: {
  read: ({ req: { user } }) => {
    if (!user) return false
    if (user.roles?.includes('admin')) return true
    return { 'team.members': { contains: user.id } }
  },
  update: ({ req: { user } }) => {
    if (!user) return false
    if (user.roles?.includes('admin')) return true
    return { owner: { equals: user.id } }
  },
}
```

## Templates for Common Domains

### Blog (public read + author write)
```ts
access: {
  read: ({ req: { user } }) =>
    user ? true : { _status: { equals: 'published' } },
  create: ({ req: { user } }) => Boolean(user),
  update: ({ req: { user } }) => {
    if (!user) return false
    if (user.roles?.includes('admin')) return true
    return { author: { equals: user.id } }
  },
  delete: isAdmin,
}
```

### Documents per-user
```ts
access: {
  read:   isOwnerOrAdmin('owner'),
  create: authenticated,
  update: isOwnerOrAdmin('owner'),
  delete: isOwnerOrAdmin('owner'),
}
```

### Comments (public read + author update + admin moderate)
```ts
access: {
  read: anyone,
  create: ({ req: { user } }) => Boolean(user),
  update: ({ req: { user } }) => {
    if (!user) return false
    if (user.roles?.some(r => ['admin', 'moderator'].includes(r))) return true
    return { and: [{ author: { equals: user.id } }, { moderationStatus: { equals: 'pending' } }] }
  },
  delete: ({ req: { user } }) =>
    user?.roles?.some(r => ['admin', 'moderator'].includes(r)) ?? false,
}
```

## Performance Considerations

- Avoid hitting the DB inside an access function — it runs on every request. Memoize via `req.context` if you must.
- Where clauses with deep joins (`team.members.contains`) generate complex SQL on Postgres; verify with `EXPLAIN ANALYZE` and add indexes (`tenant`, `author`, `team`).
- Return `true` early for admins to skip Where-clause merging entirely on hot paths.

## Testing Access Functions Locally

```ts
import { getPayload } from 'payload'
import config from '@payload-config'

const payload = await getPayload({ config })

// Simulate a request from a specific user
const fakeUser = await payload.findByID({ collection: 'users', id: 'user_123' })
const docs = await payload.find({
  collection: 'posts',
  user: fakeUser,
  overrideAccess: false,
})
console.log(docs.docs.length, 'visible to user_123')
```

This is the canonical way to verify your access rules in a Vitest test or in a one-off script.
