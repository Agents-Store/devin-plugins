# Scenario — Auth-Only Headless API

Payload as a typed user/role/permission backend for a mobile/SPA frontend. No CMS content. Custom endpoints. JWT + API-key auth.

## Collections

### `src/collections/Users.ts`

```ts
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  auth: {
    tokenExpiration: 60 * 60,                           // 1h
    maxLoginAttempts: 5,
    lockTime: 10 * 60 * 1000,
    cookies: { secure: true, sameSite: 'Strict' },
    useAPIKey: true,                                     // each user gets an API key
    verify: true,
  },
  admin: { useAsTitle: 'email' },
  fields: [
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      saveToJWT: true,
      options: ['super-admin', 'admin', 'user'],
      defaultValue: ['user'],
      required: true,
    },
    { name: 'fullName', type: 'text' },
    {
      name: 'permissions',
      type: 'select',
      hasMany: true,
      saveToJWT: true,
      options: [
        'read:resources', 'write:resources', 'delete:resources',
        'admin:users', 'admin:billing',
      ],
      defaultValue: ['read:resources'],
    },
    {
      name: 'apiQuotaPerMinute',
      type: 'number',
      defaultValue: 60,
      admin: { description: 'Rate limit cap' },
    },
  ],
}
```

### `src/collections/Resources.ts`

```ts
import type { CollectionConfig } from 'payload'

const hasPermission = (perm: string) => ({ req: { user } }: any) => {
  if (!user) return false
  if (user.roles?.includes('super-admin')) return true
  return user.permissions?.includes(perm) ?? false
}

export const Resources: CollectionConfig = {
  slug: 'resources',
  access: {
    read:   hasPermission('read:resources'),
    create: hasPermission('write:resources'),
    update: hasPermission('write:resources'),
    delete: hasPermission('delete:resources'),
  },
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'data', type: 'json' },
    { name: 'owner', type: 'relationship', relationTo: 'users', required: true },
  ],
}
```

## `payload.config.ts`

```ts
import { buildConfig } from 'payload'
import { postgresAdapter } from '@payloadcms/db-postgres'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import path from 'path'
import { fileURLToPath } from 'url'
import { Users } from './collections/Users'
import { Resources } from './collections/Resources'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: { user: 'users', importMap: { baseDir: path.resolve(dirname) } },
  collections: [Users, Resources],
  editor: lexicalEditor(),                              // unused but required
  db: postgresAdapter({ pool: { connectionString: process.env.DATABASE_URI } }),
  secret: process.env.PAYLOAD_SECRET || '',
  typescript: { outputFile: path.resolve(dirname, 'payload-types.ts') },
  cors: ['https://app.example.com', 'https://admin.example.com'],
  csrf: ['https://app.example.com', 'https://admin.example.com'],
  rateLimit: { window: 60_000, max: 1000, trustProxy: true },
  endpoints: [
    {
      path: '/whoami',
      method: 'get',
      handler: async (req) => {
        if (!req.user) return new Response('Unauthorized', { status: 401 })
        return Response.json({
          id: req.user.id,
          email: (req.user as any).email,
          roles: req.user.roles,
          permissions: (req.user as any).permissions,
        })
      },
    },
    {
      path: '/quota',
      method: 'get',
      handler: async (req) => {
        if (!req.user) return new Response('Unauthorized', { status: 401 })
        const used = await req.payload.count({
          collection: 'request-log',
          where: {
            user: { equals: req.user.id },
            createdAt: { greater_than: new Date(Date.now() - 60_000).toISOString() },
          },
        })
        return Response.json({
          quota: (req.user as any).apiQuotaPerMinute,
          used: used.totalDocs,
          remaining: (req.user as any).apiQuotaPerMinute - used.totalDocs,
        })
      },
    },
  ],
})
```

## Auth Patterns

### JWT login (browser)

```bash
curl -X POST 'https://api.example.com/api/users/login' \
  -H 'Content-Type: application/json' \
  -d '{"email":"…","password":"…"}'
# → { token, exp, user }
```

Send subsequent requests with `Authorization: JWT <token>` or rely on the cookie.

### API-key auth (server/server)

```bash
curl 'https://api.example.com/api/resources' \
  -H "Authorization: users API-Key $USER_API_KEY"
```

Format: `Authorization: <auth-collection-slug> API-Key <key>`.

### Refresh token

```bash
curl -X POST 'https://api.example.com/api/users/refresh-token' \
  -H "Authorization: JWT $TOKEN"
# → { token, exp, refreshedToken }
```

### Forgot / reset

```bash
curl -X POST 'https://api.example.com/api/users/forgot-password' \
  -d '{"email":"…"}'

# (token arrives by email)
curl -X POST 'https://api.example.com/api/users/reset-password' \
  -d '{"token":"…","password":"…"}'
```

## Custom Permissions Pattern

Centralize permission checks:

```ts
// src/access/hasPermission.ts
import type { Access, AccessArgs } from 'payload'

export const hasPermission =
  (perm: string): Access =>
  ({ req: { user } }: AccessArgs) => {
    if (!user) return false
    if (user.roles?.includes('super-admin')) return true
    return (user as any).permissions?.includes(perm) ?? false
  }
```

Use everywhere:
```ts
access: {
  read:   hasPermission('read:resources'),
  update: hasPermission('write:resources'),
  delete: hasPermission('delete:resources'),
}
```

## Disabling the Admin UI

Some headless deployments don't want `/admin` exposed. Drop the admin route group:
```bash
rm -r src/app/\(payload\)/admin
```

Keep `/api/*` routes — they're independent. The admin is just a Next.js page that uses the same Local API. Removing it doesn't break anything outside the UI.

## Rate Limiting

Payload ships built-in IP-based rate limiting on auth endpoints via `rateLimit` config. For per-user quotas, log every request and check before serving:

```ts
endpoints: [
  {
    path: '/resources',
    method: 'get',
    handler: async (req) => {
      if (!req.user) return new Response('Unauthorized', { status: 401 })

      const used = await req.payload.count({
        collection: 'request-log',
        where: {
          user: { equals: req.user.id },
          createdAt: { greater_than: new Date(Date.now() - 60_000).toISOString() },
        },
      })
      if (used.totalDocs >= ((req.user as any).apiQuotaPerMinute || 60)) {
        return new Response('Rate limit exceeded', { status: 429 })
      }

      await req.payload.create({
        collection: 'request-log',
        data: { user: req.user.id, path: '/resources' },
        req,
      })

      const data = await req.payload.find({
        collection: 'resources',
        user: req.user,
        overrideAccess: false,
      })
      return Response.json(data)
    },
  },
],
```

## What This Demonstrates

- Multi-mechanism auth: JWT, API key, refresh.
- `permissions` array on the auth collection with `saveToJWT: true`, then a tiny `hasPermission` helper.
- Custom endpoints at root (`/api/whoami`) and per-collection.
- Server-side rate limiting backed by a `request-log` collection.
- Headless deployment with `/admin` removed.
- `overrideAccess: false` to enforce per-user permissions on Local API calls inside custom endpoints.
