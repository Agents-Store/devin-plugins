---
name: access-control
description: This skill should be used when the user asks about "Payload access control", "RBAC in Payload", "row-level security", "isAdmin function", "field access control", "global access control", "overrideAccess", "multi-tenant Payload", "filter by user role", "Payload Access function", or needs to decide who can create/read/update/delete documents.
---

# PayloadCMS — Access Control

Access control in Payload is type-safe, declarative, and lives next to the data it protects. Three layers:

1. **Collection access** — coarse `create / read / update / delete / admin / unlock / readVersions` rules per collection. Return `boolean` OR a `Where` query.
2. **Field access** — per-field `read / create / update` gates. Boolean return only.
3. **Global access** — `read / update / readVersions` on singleton globals.

The trick that unlocks everything: a function returning `boolean` is a global allow/deny, but a function returning a `Where` clause is a row-level filter — Payload merges it into every query against the collection.

## Anatomy of an Access Function

```ts
import type { Access } from 'payload'

type Access = (args: {
  req: PayloadRequest          // contains user, locale, payload, headers
  id?: string | number          // present on update/delete/read-by-id
  data?: Partial<TypeWithID>    // present on create/update (incoming data)
}) => boolean | Where | Promise<boolean | Where>
```

Return values:
- `true` — allow unconditionally.
- `false` — deny unconditionally.
- `Where` object — allow only rows matching this query. Payload AND-merges it with whatever the user passed.

## Common Helpers

Stamp these in a `src/access/` folder once and reuse:

```ts
// src/access/anyone.ts
import type { Access } from 'payload'
export const anyone: Access = () => true

// src/access/authenticated.ts
export const authenticated: Access = ({ req: { user } }) => Boolean(user)

// src/access/isAdmin.ts
import type { User } from '@/payload-types'
export const isAdmin: Access = ({ req: { user } }) =>
  (user as User | null)?.roles?.includes('admin') ?? false

// src/access/isAdminOrSelf.ts
export const isAdminOrSelf: Access = ({ req: { user } }) => {
  if (!user) return false
  if ((user as User).roles?.includes('admin')) return true
  return { id: { equals: user.id } }
}

// src/access/publishedOrOwn.ts
export const publishedOrOwn: Access = ({ req: { user } }) => {
  if (!user) return { _status: { equals: 'published' } }
  if ((user as User).roles?.includes('admin')) return true
  return {
    or: [
      { _status: { equals: 'published' } },
      { author: { equals: user.id } },
    ],
  }
}
```

## Collection Access

```ts
import { isAdmin, authenticated, publishedOrOwn, isAdminOrSelf } from '../access'

export const Posts: CollectionConfig = {
  slug: 'posts',
  access: {
    read: publishedOrOwn,
    create: authenticated,
    update: isAdminOrSelf,
    delete: isAdmin,
    admin: isAdmin,               // Can see the collection in the admin sidebar?
    readVersions: isAdmin,        // Can browse version history?
  },
  fields: [/* … */],
}
```

If `access` is omitted on a collection, the defaults are:
- `read` — `() => true` (public).
- `create / update / delete` — `({ req: { user } }) => Boolean(user)` (logged-in users).
- `admin` — same as `update`.

## Field Access

Field access returns boolean only — no Where filtering:

```ts
{
  name: 'salary',
  type: 'number',
  access: {
    read:   ({ req: { user } }) => user?.roles?.includes('admin') ?? false,
    update: ({ req: { user } }) => user?.roles?.includes('admin') ?? false,
    create: ({ req: { user } }) => user?.roles?.includes('admin') ?? false,
  },
}
```

If `read` returns false, the field is stripped from the response (the document is still returned).
If `update`/`create` returns false, attempts to write the field are silently ignored.

## Global Access

```ts
import { isAdmin, anyone } from '../access'

export const SiteSettings: GlobalConfig = {
  slug: 'site-settings',
  fields: [/* … */],
  access: {
    read: anyone,
    update: isAdmin,
    readVersions: isAdmin,
  },
}
```

## Row-Level Security (the killer feature)

Return a Where clause and Payload auto-filters every list query. Multi-tenant in 4 lines:

```ts
// src/access/sameTenant.ts
export const sameTenant: Access = ({ req: { user } }) => {
  if (!user) return false
  if ((user as User).roles?.includes('super-admin')) return true
  return { tenant: { equals: (user as User).tenant } }
}

// Posts collection
access: {
  read: sameTenant,
  create: sameTenant,
  update: sameTenant,
  delete: sameTenant,
}
```

For a more complex policy (members of a team OR admins):

```ts
export const teamMemberOrAdmin: Access = ({ req: { user } }) => {
  if (!user) return false
  if ((user as User).roles?.includes('admin')) return true
  return {
    'team.members': { contains: user.id },
  }
}
```

The dot syntax (`team.members`) joins through the relationship — see the `queries` skill for nested-property queries.

## CRITICAL: Local API and `overrideAccess`

**Local API operations bypass ALL access control by default**, even when you pass `user`:

```ts
// ❌ SECURITY BUG — access control is bypassed
await payload.find({
  collection: 'posts',
  user: someUser,
})

// ✅ SECURE — actually enforces the user's permissions
await payload.find({
  collection: 'posts',
  user: someUser,
  overrideAccess: false,         // REQUIRED
})
```

Default behavior is the bypass because most Local API callers are trusted server code (cron jobs, hooks, migrations). When you're proxying a user request, you must opt in.

| Context | Use |
| --- | --- |
| Cron job, system task, migration | `overrideAccess: true` (default) |
| API route handling a user request | `overrideAccess: false` + pass `user: req.user` |
| Webhook handler | `overrideAccess: false` if acting on behalf of a user |

## RBAC Setup

There's no built-in role model — wire it yourself on the auth collection:

```ts
export const Users: CollectionConfig = {
  slug: 'users',
  auth: true,
  admin: { useAsTitle: 'email' },
  fields: [
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      saveToJWT: true,            // CRITICAL: makes roles available in JWT for access fns
      options: [
        { label: 'Super Admin', value: 'super-admin' },
        { label: 'Admin', value: 'admin' },
        { label: 'Editor', value: 'editor' },
        { label: 'User', value: 'user' },
      ],
      defaultValue: ['user'],
      required: true,
    },
  ],
}
```

`saveToJWT: true` writes roles into the JWT payload — that's how `req.user.roles` is populated on every authenticated request without re-fetching the user.

## Filter Options on Relationships

Closely related — `filterOptions` on a relationship field is access control for "what's selectable":

```ts
{
  name: 'editor',
  type: 'relationship',
  relationTo: 'users',
  filterOptions: ({ user }) => ({
    roles: { in: ['editor', 'admin'] },
  }),
}
```

This narrows the dropdown to qualified users without touching their actual access rules.

## Auth Operations & Cookies

When `auth: true` is set:
- `POST /api/users/login` returns a JWT and sets an HTTP-only cookie.
- `POST /api/users/logout` clears the cookie.
- `req.user` is populated from the JWT on every authenticated request.

Cookie config:
```ts
auth: {
  cookies: {
    secure: true,         // HTTPS only (production)
    sameSite: 'Strict',   // CSRF protection
    domain: '.example.com', // Cross-subdomain
  },
}
```

## Where to Put Access Functions

```txt
src/
├── access/
│   ├── anyone.ts
│   ├── authenticated.ts
│   ├── isAdmin.ts
│   ├── isAdminOrSelf.ts
│   ├── sameTenant.ts
│   └── publishedOrOwn.ts
├── collections/
│   └── Posts.ts          # imports from '../access'
```

## See Also

- `references/advanced-patterns.md` — context-aware access, time-based access, subscription gating, access function factories, multi-tenant deep dive.
- The `hooks` skill — for stamping `req.user.id` into `author` automatically.
- The `queries` skill — for the Where syntax used inside row-level filters.

Always run `pnpm generate:types` after changing `roles` options — the generated `User['roles']` union narrows access functions.
