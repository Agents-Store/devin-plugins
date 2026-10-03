# SDK in Server-Side Apps (Next.js and other SSR frameworks)

How to wire `@directus/sdk` into an app that calls Directus from server code: Server Components, Route Handlers, Server Actions, loaders. Checked against `@directus/sdk` 26.0.0 and `next@16.3.8` types with `tsc --strict`, and against a Directus 12.4.1 instance. Client variants, login modes and CRUD are in `SKILL.md`; relations, typing and reading patterns are in [content-queries.md](content-queries.md). This file covers what is specific to a server-rendered app.

## Server-only client module

```typescript
// lib/directus.ts
import 'server-only';
import { createDirectus, rest, staticToken } from '@directus/sdk';
import type { Schema } from '@/types/directus';

const directus = createDirectus<Schema>(process.env.DIRECTUS_URL!)
  .with(staticToken(process.env.DIRECTUS_TOKEN!))
  .with(rest());

export default directus;
```

```typescript
// types/directus.ts: start with a stub, add one interface per collection as you create it
export interface Schema {
  // posts: Post[];
}
```

- `import 'server-only'` makes the build fail when a Client Component imports the module, so the token cannot end up in a browser bundle. Never give the token variable a `NEXT_PUBLIC_` prefix.
- Use the variable names your project's `.env` already has. A Next.js app that also needs the Directus address in the browser (for image URLs, for example) reads the URL from a `NEXT_PUBLIC_` variable and keeps the token in a plain one.
- The token belongs to a dedicated Directus user whose policy grants only what the server code reads and writes. A token of an administrator turns every bug in your app into full access to the instance.
- Keep `types/directus.ts` in step with the real schema: list it with the MCP `schema` tool or `readCollections()` and `readFieldsByCollection()`. `tsc` then flags drift in the fields your queries name.

## Fetch options: `rest()` has no `cache`

```typescript
// Does not compile: TS2353 'cache' does not exist in type 'Partial<RestConfig>'
createDirectus<Schema>(url).with(rest({ cache: 'no-store' }));
```

`RestConfig` is `{ credentials, onRequest, onResponse }`. The SDK hands whatever `onRequest` (client wide) or `withOptions` (one command) returns to `fetch`, so framework fetch options travel through those two. Verified: `cache` and `next` reach `fetch` unchanged.

```typescript
// lib/directus-no-store.ts: every request of this client
import { createDirectus, rest } from '@directus/sdk';
import type { Schema } from '@/types/directus';

export const noStoreClient = createDirectus<Schema>(process.env.DIRECTUS_URL!).with(
  rest({ onRequest: (options) => ({ ...options, cache: 'no-store' }) }),
);
```

```typescript
// lib/directus-tagged.ts: one command, with Next.js cache tags and a lifetime
import 'server-only';
import { withOptions, type RestCommand } from '@directus/sdk';
import directus from '@/lib/directus';
import type { Schema } from '@/types/directus';

export function requestTagged<Output>(
  command: RestCommand<Output, Schema>,
  tags: string[],
  revalidate: number | 'no-store', // seconds, or 'no-store' to bypass the cache for this one request
) {
  const options =
    revalidate === 'no-store'
      ? { cache: 'no-store' as const }
      : { cache: 'force-cache' as const, next: { tags, revalidate } };
  return directus.request(withOptions(command, options));
}
```

Build the command inside the call (`requestTagged(readItems('posts', { ... }), ...)`), not in a variable of its own: a `readItems(...)` stored in a `const` has no client to take the schema from, and TypeScript rejects the collection name (`'posts'` is not assignable to `never`).

`next` is declared on `RequestInit` by Next's global types (`next-env.d.ts`). For another framework pass its own fetch options. Which caching model applies, and what `revalidateTag` needs, is covered by the `nextjs-dev` plugin (`data-fetching`).

## System collections

`readItems('directus_collections')` is a type error, and untyped JavaScript throws `Cannot use readItems for core collections` at runtime. Every `directus_*` collection has its own commands:

| You want | Command |
|----------|---------|
| Is the server up (public, answers `pong`) | `serverPing()` |
| Project info, version, license, `mcp_enabled` | `serverInfo()` |
| Dependency health (needs a token in Directus 12) | `serverHealth()` |
| Collections and fields | `readCollections()`, `readFieldsByCollection(collection)` |
| Current user | `readMe()` |
| Users, roles, policies, permissions | `readUsers()`, `readRoles()`, `readPolicies()`, `readPermissions()` |
| Files (metadata) | `readFiles()` |

`serverPing()` is the right connection check for a bootstrap script: it needs no token and no permission.

## A different token for one request

`withToken(token, command)` sends that token for the one command, whatever the client was built with (verified: it wins over a static token):

```typescript
// lib/me.ts
import { readMe, withToken } from '@directus/sdk';
import directus from '@/lib/directus';

export async function getMe(userAccessToken: string) {
  return directus.request(withToken(userAccessToken, readMe({ fields: ['id', 'email'] })));
}
```

Use it to act as the signed-in user: the request runs with that user's policies, not the server token's. Never put such a call inside a cached function (`'use cache'` or a tagged `fetch`): the cache entry is shared by every visitor who hits the same key.

## Signing in end users from server code

A session library (NextAuth, Better Auth with a custom provider, your own cookie) calls the Directus REST auth endpoints itself:

| Call | Body | Answer (`data`) |
|------|------|-----------------|
| `POST /auth/login` | `{ email, password, mode: 'json' }` | `access_token`, `refresh_token`, `expires` |
| `POST /auth/refresh` | `{ refresh_token, mode: 'json' }` | the same three fields, new values |
| `GET /users/me` with `Authorization: Bearer <access_token>` | | the user |

- `expires` is **milliseconds** until the access token ends (`900000`, 15 minutes, by default).
- A refresh token is **single use**. Verified on 12.4.1: after a refresh the old token answers `401 INVALID_CREDENTIALS`, and the new token works. Two parallel refreshes with the same token race, and the loser fails. Refresh in one place only (the session library's token callback) and treat a failure as "sign in again".
- Keep both tokens on the server (an encrypted httpOnly session cookie). The `refresh_token` must never reach browser JavaScript.
- For a code example against NextAuth see `nextjs-dev` (`auth-patterns`).

## CORS and cookies

Server-to-server calls from your Next.js server to Directus are not subject to CORS. You need it only when the **browser** talks to Directus (SDK in a Client Component, `authentication('session')`, WebSockets):

```bash
CORS_ENABLED=true
CORS_ORIGIN=http://localhost:3000,https://app.example.com   # exact origins, comma separated
```

With `credentials: 'include'` the origin must be listed exactly (no wildcard). Since Directus 12.1 the same list is enforced for WebSocket connections. Cookie-based sessions across two domains also need the `SESSION_COOKIE_*` settings (domain, secure, same-site) on the server.
