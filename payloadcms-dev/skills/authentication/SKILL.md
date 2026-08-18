---
name: authentication
description: This skill should be used when the user asks to "add login to Payload", "set up OAuth/SSO", "write a custom auth strategy", "use API keys", "configure auth cookies", "customize verification emails", "refresh a JWT", or "handle forgot-password" — anything about Payload v3 authentication strategies, operations, or auth emails beyond the basics covered in collections.
---

# PayloadCMS — Authentication

Auth in Payload is a property of a collection, not a separate subsystem. Set `auth: true` (or an `AuthConfig` object) on any collection and it gains a login source, auto-generated `email`/`password`/`resetPasswordToken`/`loginAttempts`/`lockUntil` fields, a full set of auth REST endpoints, Local API methods, and `req.user` population on every request. The `collections` skill covers turning it on; this skill goes deeper — the four strategies, every operation, auth emails, token data, and locking down cookies.

## The Four Strategies

Payload ships four built-in ways to identify a user. They are not mutually exclusive — a collection can accept cookies, bearer JWTs, and API keys at once.

| Strategy | How the client authenticates | Enable with | Use for |
| --- | --- | --- | --- |
| HTTP-only Cookie | Browser sends the `payload-token` cookie automatically after login | On by default with `auth: true` | Admin panel, same-site frontends |
| JWT (bearer) | `Authorization: JWT <token>` header | On by default; token returned by login/refresh/me | Mobile apps, server-to-server, cross-origin |
| API Key | `Authorization: <slug> API-Key <key>` header | `useAPIKey: true` | Service accounts, third-party integrations |
| Custom | Your `authenticate` function resolves a user | `strategies: [...]` | OAuth/SSO, SAML, header-forwarded identity |

Cookies are immune to XSS (JavaScript cannot read them); JWTs are convenient for non-browser clients. Both carry the same signed payload.

## AuthConfig Reference

```ts
// src/collections/Users.ts
import type { CollectionConfig } from 'payload'

export const Users: CollectionConfig = {
  slug: 'users',
  admin: { useAsTitle: 'email' },
  auth: {
    tokenExpiration: 7200,              // Seconds the session/JWT stays valid (2h)
    verify: true,                       // Require email verification before login
    maxLoginAttempts: 5,                // Failed logins before lockout (0 disables)
    lockTime: 600 * 1000,               // Lockout duration in ms (10 min)
    useAPIKey: false,                   // Per-user API keys on this collection
    useSessions: true,                  // Default true; false => stateless JWT
    depth: 0,                           // Relationship depth when building the JWT
    removeTokenFromResponses: false,    // Strip token from auth-op responses
    cookies: { secure: true, sameSite: 'Lax' },
    // disableLocalStrategy: true,      // Advanced: turn off email/password entirely
    // loginWithUsername: { ... },      // Username login (see below)
    // strategies: [ ... ],            // Custom strategies (see below)
    // forgotPassword: { ... },        // Reset-email customization (see below)
    // verify: { ... },                // Verify-email customization (see below)
  },
  fields: [
    {
      name: 'roles',
      type: 'select',
      hasMany: true,
      saveToJWT: true,                  // Read roles from req.user without a DB hit
      options: ['admin', 'editor', 'user'],
      defaultValue: ['user'],
      required: true,
    },
  ],
}
```

Run `pnpm generate:types` after editing the collection so the generated `User` type stays in sync.

## Auth Operations

Every auth collection exposes these. REST paths are relative to `/api/<slug>`; Local API methods take `{ collection: '<slug>', ... }`.

| Operation | REST | Local API |
| --- | --- | --- |
| Login | `POST /<slug>/login` | `payload.login({ collection, data: { email, password } })` |
| Logout | `POST /<slug>/logout?allSessions=false` | `logout` server function (from `@payloadcms/next/auth`) |
| Me (current user) | `GET /<slug>/me` | read `req.user` |
| Refresh token | `POST /<slug>/refresh-token` | `refresh` server function |
| Forgot password | `POST /<slug>/forgot-password` | `payload.forgotPassword({ collection, data: { email }, disableEmail })` |
| Reset password | `POST /<slug>/reset-password` | `payload.resetPassword({ collection, data: { token, password }, overrideAccess })` |
| Verify email | `POST /<slug>/verify/<token>` | `payload.verifyEmail({ collection, token })` |
| Unlock | `POST /<slug>/unlock` | `payload.unlock({ collection, data: { email } })` |

Login (Local API):
```ts
// src/app/(auth)/actions.ts
const { user, token, exp } = await payload.login({
  collection: 'users',
  data: { email, password },
})
```

Login (REST) returns the user and sets the `payload-token` cookie; the JSON body also carries `token` for non-browser clients:
```ts
const res = await fetch('/api/users/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
})
const { user, token } = await res.json()
```

Kick off a reset and let Payload email the link, or suppress the email to handle delivery yourself:
```ts
const token = await payload.forgotPassword({
  collection: 'users',
  data: { email: 'jane@example.com' },
  disableEmail: false,   // true => you get the token back, no email sent
})
// Later, with the token from the email link:
await payload.resetPassword({
  collection: 'users',
  data: { token, password: 'new-secret' },
  overrideAccess: true,
})
```

## Auth Emails: Verify & Forgot-Password

Customize the verification and reset emails inside `auth`. Both objects accept `generateEmailHTML` and `generateEmailSubject`. `generateEmailHTML` receives `{ req, token, user }`; `generateEmailSubject` receives `{ req, user }`. Point the link at your own frontend route — not Payload's API.

```ts
// src/collections/Users.ts
auth: {
  verify: {
    generateEmailHTML: ({ token, user }) =>
      `<p>Hi ${user.email}, confirm your account:</p>
       <a href="${process.env.NEXT_PUBLIC_SITE_URL}/verify?token=${token}">Verify email</a>`,
    generateEmailSubject: ({ user }) => `Verify your account, ${user.email}`,
  },
  forgotPassword: {
    expiration: 3600 * 1000,   // Reset-token validity in ms (1h)
    generateEmailHTML: ({ token, user }) =>
      `<p>Reset your password:</p>
       <a href="${process.env.NEXT_PUBLIC_SITE_URL}/reset-password?token=${token}">Choose a new password</a>`,
    generateEmailSubject: ({ user }) => `Hey ${user.email}, reset your password`,
  },
}
```

These emails only send if an email transport is configured at the root `email:` key. SMTP, Resend, Nodemailer, etc. live in the `adapters` skill — without one, Payload logs the email to the console in dev and silently no-ops in prod.

## Token Data & `saveToJWT`

The JWT/cookie carries a small signed payload, read back as `req.user` on every request with no extra DB query. By default it holds `id`, `email`, and `collection`. Opt fields in per-field:

```ts
{ name: 'roles', type: 'select', hasMany: true, saveToJWT: true }
{ name: 'tenant', type: 'relationship', relationTo: 'tenants', saveToJWT: true }
{ name: 'internalNote', type: 'text', saveToJWT: false }   // explicit exclude
{ name: 'plan', type: 'text', saveToJWT: 'subscriptionPlan' }  // alternate JWT key
```

`group` and `tabs` fields store the whole object when `saveToJWT: true`, and child fields can override individually. Anything you need inside access functions or hooks (`req.user.roles`, `req.user.tenant`) must be marked `saveToJWT: true` — otherwise it's absent from `req.user` until you re-fetch the document.

Read it anywhere a `req` is in scope:
```ts
// In an access function, hook, or custom endpoint
if (req.user?.roles?.includes('admin')) return true
```

Tune `tokenExpiration` for session length, `maxLoginAttempts` + `lockTime` for brute-force protection (Payload increments `loginAttempts` and stamps `lockUntil` automatically), and `removeTokenFromResponses: true` when you only want cookie-based auth and never want the raw token in JSON.

## Cookies, CSRF & Cross-Domain

```ts
auth: {
  cookies: {
    secure: true,            // HTTPS only — keep false in local dev over http
    sameSite: 'Lax',         // 'Strict' | 'Lax' | 'None'
    domain: '.example.com',  // Share the cookie across subdomains
  },
}
```

Cookies are read from the responses of `login`, `logout`, `refresh`, and `me`. For a cross-origin frontend you must set `sameSite: 'None'` **and** `secure: true`, then whitelist origins for CSRF in the root config (`csrf`) and CORS (`cors`) — wildcards are not allowed once `sameSite: 'None'` is in play:

```ts
// src/payload.config.ts
export default buildConfig({
  serverURL: process.env.PAYLOAD_URL,
  cors: ['https://app.example.com'],
  csrf: ['https://app.example.com'],   // serverURL is added automatically
  collections: [Users],
})
```

## `loginWithUsername` & `disableLocalStrategy`

Swap email-as-identifier for a username (with optional email fallback):
```ts
auth: {
  loginWithUsername: {
    allowEmailLogin: true,   // Accept username OR email at the login form
    requireEmail: false,     // Make email optional at signup
  },
}
```

Turn off email/password entirely when a collection authenticates only via API key or a custom strategy:
```ts
auth: {
  useAPIKey: true,
  disableLocalStrategy: true,   // No password fields, no login op
}
```

## Custom Strategies (OAuth / SSO)

A custom strategy is the integration point for OAuth, SAML, or a reverse-proxy that forwards a trusted identity header. Add objects to `auth.strategies`. Each has a `name` and an `authenticate` function receiving `{ payload, headers, canSetHeaders, isGraphQL }`. It must resolve to `{ user }` where `user` is `{ collection: '<slug>', ...userDoc }` (or `null` to fall through to the next strategy), optionally with `responseHeaders`.

```ts
// src/auth/headerStrategy.ts
import type { AuthStrategy } from 'payload'

export const headerStrategy: AuthStrategy = {
  name: 'forwarded-identity',
  authenticate: async ({ payload, headers }) => {
    const email = headers.get('x-forwarded-user')   // set by a trusted proxy
    if (!email) return { user: null }

    const { docs } = await payload.find({
      collection: 'users',
      where: { email: { equals: email } },
      limit: 1,
    })

    const found = docs[0]
    return {
      user: found ? { collection: 'users', ...found } : null,
    }
  },
}
```

Wire it in, usually alongside `disableLocalStrategy`:
```ts
// src/collections/Users.ts
auth: {
  disableLocalStrategy: true,
  strategies: [headerStrategy],
}
```

## Protecting Next.js Routes

In the App Router, resolve the user from headers via the Local API and gate server components or route handlers:
```ts
// src/app/(app)/dashboard/page.tsx
import { headers as nextHeaders } from 'next/headers'
import { getPayload } from 'payload'
import config from '@payload-config'
import { redirect } from 'next/navigation'

export default async function Dashboard() {
  const payload = await getPayload({ config })
  const { user } = await payload.auth({ headers: await nextHeaders() })
  if (!user) redirect('/login')
  return <h1>Welcome {user.email}</h1>
}
```
See the `nextjs-integration` skill for the full server-component, middleware, and route-handler patterns.

<example>
**User**: "Add Google sign-in to my Payload users via a custom strategy."

**Solution**: Verify the Google ID token in `authenticate`, upsert the user, return it tagged with the collection slug. Keep the local strategy on so password users still work.
```ts
// src/auth/googleStrategy.ts
import type { AuthStrategy } from 'payload'
import { OAuth2Client } from 'google-auth-library'

const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID)

export const googleStrategy: AuthStrategy = {
  name: 'google-oauth',
  authenticate: async ({ payload, headers }) => {
    const idToken = headers.get('authorization')?.replace('Bearer ', '')
    if (!idToken) return { user: null }

    const ticket = await client.verifyIdToken({
      idToken,
      audience: process.env.GOOGLE_CLIENT_ID,
    })
    const email = ticket.getPayload()?.email
    if (!email) return { user: null }

    const { docs } = await payload.find({
      collection: 'users',
      where: { email: { equals: email } },
      limit: 1,
    })
    const user =
      docs[0] ??
      (await payload.create({
        collection: 'users',
        data: { email, roles: ['user'] },
      }))

    return { user: { collection: 'users', ...user } }
  },
}

// src/collections/Users.ts
auth: { strategies: [googleStrategy] }
```
</example>

<example>
**User**: "I need a machine-to-machine service account that only uses an API key, no password."

**Solution**: A dedicated collection with `useAPIKey` and `disableLocalStrategy`. Generate the key per document in the admin panel, then send it in the `Authorization` header.
```ts
// src/collections/ServiceAccounts.ts
export const ServiceAccounts: CollectionConfig = {
  slug: 'service-accounts',
  auth: { useAPIKey: true, disableLocalStrategy: true },
  fields: [
    { name: 'label', type: 'text', required: true },
    { name: 'scopes', type: 'select', hasMany: true, saveToJWT: true,
      options: ['read', 'write'] },
  ],
}
```
```ts
// Caller — header is case-sensitive: "<slug> API-Key <key>"
await fetch('https://cms.example.com/api/posts', {
  headers: { Authorization: `service-accounts API-Key ${process.env.CMS_API_KEY}` },
})
```
Keys are encrypted at rest, so a database leak does not expose them.
</example>

## What this skill does NOT cover

- `collections` — auth field basics and the `auth: true` toggle in context of modeling a collection.
- `access-control` — who can create/read/update/delete once a user is authenticated (`overrideAccess`, row-level Where filters, field access).
- `adapters` — the email transport (SMTP/Resend/Nodemailer) that actually delivers verify and reset emails.
- `nextjs-integration` — full server-component, middleware, and route-handler patterns for using `req.user` in a Next.js app.
