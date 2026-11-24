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

### Admin-panel users only: `defaultAdminPanelUserAccess` (3.94+)

A plain `Boolean(user)` check lets in any logged-in user from **any** auth collection — an admin `users` collection and a storefront `customers` collection both pass. `payload` exports a ready-made check for the case where only users of the collection named in `admin.user` should get through:

```ts
import { defaultAdminPanelUserAccess } from 'payload'
import type { CollectionConfig } from 'payload'

export const Settings: CollectionConfig = {
  slug: 'settings',
  access: {
    admin: defaultAdminPanelUserAccess,   // who may open it in the admin panel
    read: defaultAdminPanelUserAccess,
    update: defaultAdminPanelUserAccess,
  },
  fields: [/* … */],
}
```

It returns `true` only when there is a user and `user.collection === config.admin.user`; it never returns a `Where`. Use it instead of hand-writing that comparison in each project or plugin; combine it with a role check when you need more than collection membership. Sources: release v3.94.0, `payload@3.94.1` (`dist/auth/defaultAdminPanelUserAccess.js`).

If `access` is omitted on a collection, the defaults are:
- `read / create / update / delete` — `({ req: { user } }) => Boolean(user)` (logged-in users only). Nothing is public by
  default: a collection the site reads anonymously needs an explicit `read: () => true` (or a `Where`). Source:
  `payload@3.94.1` (`dist/collections/config/defaults.js`, `dist/auth/defaultAccess.js`).
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

### Field access knows the document `id` (3.92+)

Field access functions receive `id` (the document being read or updated; `undefined` on `create`), alongside `req`, `data`, `doc`, `siblingData` and `blockData`. The argument was always in the types, but document-level permission evaluation did not fill it in; 3.92.0 does, so you can authorize against the current document without reaching into `doc.id`:

```ts
{
  name: 'internalNotes',
  type: 'textarea',
  access: {
    // owner of this very document, or an admin
    read: async ({ req, id }) => {
      if (!req.user) return false
      if (req.user.roles?.includes('admin')) return true
      if (!id) return false
      const doc = await req.payload.findByID({
        collection: 'projects',
        id,
        depth: 0,
        select: { owner: true },
        req,                      // same transaction as the request
      })
      return doc.owner === req.user.id
    },
    update: ({ req }) => req.user?.roles?.includes('admin') ?? false,
  },
}
```

Field access runs per field and per document, so keep the lookup cheap (`select`, `depth: 0`) or compare against `doc`/`siblingData` when they already hold what you need. Sources: release v3.92.0 (PR "pass document id to field access"), [Field-level access docs](https://payloadcms.com/docs/access-control/fields).

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

## Security Checklist After 3.93

3.93.0 (2026-11-04) is a security release. Three of its fixes touch access control and change what a config can rely on. Upgrade, then check each against your collections:

| Check | Since 3.93 | What to review |
| --- | --- | --- |
| Field read access inside `blocks` | Queries now check field-level `read` access on fields inside a `blocks` field before running; before, a query on a restricted block field could leak limited information while the field was still removed from the response | Any `blocks` field whose blocks carry fields with `access.read`; expect queries filtering on those fields to be refused for users who cannot read them (advisory GHSA-j4q6-g29w-5cmg) |
| Block rows limited to the field's own block types | A row whose `blockType` is not among the blocks configured for that field is rejected as invalid, and hooks run only for configured block types | Code or imports that write blocks across fields (a `blockType` valid on one field, not on the other) now fail validation with `The following field is invalid: <field label>` |
| `pasteURL` restrictions on remote uploads | Remote-URL uploads now honor the collection's `upload.pasteURL` (`false`, or `{ allowList }`) consistently; before, the restriction could be skipped under some configurations and let a user with create/update access make the server fetch URLs it should not reach (advisory GHSA-wc63-5fg7-7r49) | Upload collections writable by untrusted users: set `pasteURL: false` or a tight `allowList` — see the `collections` skill (upload hardening) |

Until you can upgrade, the advisories advise limiting query access on affected collections to users who may read the restricted block fields, restricting create/update on upload collections to trusted users, or rejecting the `url` field in a `beforeOperation` hook. Sources: release v3.93.0, GitHub security advisories of `payloadcms/payload` (published 2026-11-09).

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
