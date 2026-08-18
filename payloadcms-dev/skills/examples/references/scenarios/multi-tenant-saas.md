# Scenario — Multi-Tenant SaaS

A B2B SaaS where every tenant has isolated data: users, projects, settings, billing. One Payload instance, strict per-tenant access on every collection. Subdomain routing.

## Tenant Model

### `src/collections/Tenants.ts`

```ts
import type { CollectionConfig } from 'payload'

export const Tenants: CollectionConfig = {
  slug: 'tenants',
  admin: { useAsTitle: 'name', group: 'Platform' },
  access: {
    // Only platform admins manage tenants
    read:   ({ req: { user } }) => user?.roles?.includes('platform-admin') ?? false,
    create: ({ req: { user } }) => user?.roles?.includes('platform-admin') ?? false,
    update: ({ req: { user } }) => user?.roles?.includes('platform-admin') ?? false,
    delete: ({ req: { user } }) => user?.roles?.includes('platform-admin') ?? false,
  },
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'slug', type: 'text', required: true, unique: true, index: true },
    { name: 'subdomain', type: 'text', unique: true, index: true },
    {
      name: 'plan',
      type: 'select',
      options: ['free', 'pro', 'enterprise'],
      defaultValue: 'free',
      required: true,
    },
    {
      name: 'limits',
      type: 'group',
      fields: [
        { name: 'projectsMax', type: 'number', defaultValue: 3 },
        { name: 'seatsMax', type: 'number', defaultValue: 5 },
      ],
    },
  ],
}
```

## Tenant-Aware Users

### `src/collections/Users.ts`

```ts
import type { CollectionConfig } from 'payload'
import type { User } from '@/payload-types'

export const Users: CollectionConfig = {
  slug: 'users',
  auth: { cookies: { secure: true, sameSite: 'Strict' } },
  admin: { useAsTitle: 'email' },
  access: {
    read: ({ req: { user } }) => {
      if (!user) return false
      const u = user as User
      if (u.roles?.includes('platform-admin')) return true
      // Tenant members see other users in the same tenant
      return { tenant: { equals: u.tenant } }
    },
    create: ({ req: { user } }) => {
      if (!user) return false
      const u = user as User
      if (u.roles?.includes('platform-admin')) return true
      return u.roles?.includes('tenant-admin') ?? false
    },
    update: ({ req: { user } }) => {
      if (!user) return false
      const u = user as User
      if (u.roles?.includes('platform-admin')) return true
      // Tenant admins can update users in their tenant; anyone can update self
      if (u.roles?.includes('tenant-admin')) return { tenant: { equals: u.tenant } }
      return { id: { equals: u.id } }
    },
    delete: ({ req: { user } }) => user?.roles?.includes('platform-admin') ?? false,
  },
  fields: [
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      saveToJWT: true,
      options: ['platform-admin', 'tenant-admin', 'member'],
      defaultValue: ['member'],
      required: true,
    },
    {
      name: 'tenant',
      type: 'relationship',
      relationTo: 'tenants',
      saveToJWT: true,
      required: true,
      // Members can't reassign their tenant
      access: {
        update: ({ req: { user } }) => user?.roles?.includes('platform-admin') ?? false,
      },
    },
    { name: 'displayName', type: 'text' },
  ],
}
```

`saveToJWT: true` on `tenant` puts the tenant ID in the JWT so access functions read it without hitting the DB.

## Tenant-Scoped Helpers

### `src/access/tenant.ts`

```ts
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
  if (!u.roles?.includes('tenant-admin') && !u.roles?.includes('member')) return false
  return { tenant: { equals: u.tenant } }
}

export const tenantDelete: Access = ({ req: { user } }) => {
  if (!user) return false
  const u = user as User
  if (u.roles?.includes('platform-admin')) return true
  if (!u.roles?.includes('tenant-admin')) return false
  return { tenant: { equals: u.tenant } }
}
```

## Tenant-Stamping Hook

Every tenant-scoped collection needs a `beforeChange` hook that stamps `data.tenant` from `req.user.tenant` on create. Otherwise users could pass a foreign tenant ID.

### `src/hooks/stampTenant.ts`

```ts
import type { CollectionBeforeChangeHook } from 'payload'
import type { User } from '@/payload-types'

export const stampTenant: CollectionBeforeChangeHook = ({ data, req, operation }) => {
  if (operation === 'create' && req.user) {
    const u = req.user as User
    // Platform admins can set tenant explicitly; others always inherit
    if (!u.roles?.includes('platform-admin')) {
      data.tenant = u.tenant
    }
  }
  return data
}
```

## Tenant-Scoped Content Collection

### `src/collections/Projects.ts`

```ts
import type { CollectionConfig } from 'payload'
import { tenantRead, tenantWrite, tenantDelete } from '../access/tenant'
import { stampTenant } from '../hooks/stampTenant'

export const Projects: CollectionConfig = {
  slug: 'projects',
  access: {
    read:   tenantRead,
    create: tenantWrite,
    update: tenantWrite,
    delete: tenantDelete,
  },
  admin: { useAsTitle: 'name' },
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'slug', type: 'text' },
    {
      name: 'tenant',
      type: 'relationship',
      relationTo: 'tenants',
      required: true,
      index: true,
      // Only platform-admin can reassign
      access: {
        update: ({ req: { user } }) => user?.roles?.includes('platform-admin') ?? false,
      },
    },
    { name: 'description', type: 'textarea' },
    {
      name: 'owner',
      type: 'relationship',
      relationTo: 'users',
      filterOptions: ({ user }) => ({
        tenant: { equals: (user as any)?.tenant },
      }),
    },
  ],
  hooks: { beforeChange: [stampTenant] },
}
```

The hook stamps tenant on create, the field-level access prevents reassignment, the row-level Where filters reads/writes — three layers, defense in depth.

## Plan-Limit Enforcement

Block creates above the plan limit:

```ts
// src/collections/Projects.ts (enhanced)
hooks: {
  beforeChange: [
    stampTenant,
    async ({ data, req, operation }) => {
      if (operation !== 'create') return data
      if (!req.user) return data
      const u = req.user as any
      if (u.roles?.includes('platform-admin')) return data

      const tenant = await req.payload.findByID({ collection: 'tenants', id: u.tenant, req })
      const limit = tenant?.limits?.projectsMax ?? 0
      const current = await req.payload.count({
        collection: 'projects',
        where: { tenant: { equals: u.tenant } },
        req,
      })
      if (current.totalDocs >= limit) {
        throw new Error(`Project limit reached for plan ${tenant?.plan}. Upgrade to add more.`)
      }
      return data
    },
  ],
}
```

## Subdomain → Tenant Resolution (Frontend)

```ts
// src/app/(frontend)/page.tsx
import { headers } from 'next/headers'
import { getPayload } from 'payload'
import config from '@payload-config'

async function resolveTenant() {
  const host = (await headers()).get('host') || ''
  const subdomain = host.split('.')[0]
  const payload = await getPayload({ config })
  const { docs } = await payload.find({
    collection: 'tenants',
    where: { subdomain: { equals: subdomain } },
    limit: 1,
  })
  return docs[0] ?? null
}

export default async function HomePage() {
  const tenant = await resolveTenant()
  if (!tenant) return <div>Tenant not found</div>
  return <h1>Welcome to {tenant.name}</h1>
}
```

## Multi-Tenant Plugin

For complex needs, `@payloadcms/plugin-multi-tenant` ships with admin UI improvements (tenant switcher in the sidebar, tenant-scoped queries everywhere). Worth considering before reinventing.

```bash
pnpm add @payloadcms/plugin-multi-tenant
```

```ts
import { multiTenantPlugin } from '@payloadcms/plugin-multi-tenant'

plugins: [
  multiTenantPlugin({
    collections: {
      projects: {},
      'project-files': {},
    },
    tenantField: { name: 'tenant' },
    tenantsArrayField: { rowFields: [{ name: 'roles', type: 'select', options: ['tenant-admin', 'member'], hasMany: true }] },
  }),
],
```

The plugin handles a lot of plumbing the manual approach in this scenario writes by hand.

## What This Demonstrates

- Three-layer tenant isolation (access function + stamp hook + field-level update gate).
- `saveToJWT: true` on both `roles` and `tenant` so access fns are pure / no DB read.
- Plan-limit enforcement in `beforeChange`.
- Filter relationships to tenant peers via `filterOptions`.
- Subdomain → tenant resolution in Next.js server component.
- Trade-off note: roll-your-own vs `@payloadcms/plugin-multi-tenant`.
