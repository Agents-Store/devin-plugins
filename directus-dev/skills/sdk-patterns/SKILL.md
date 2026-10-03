---
name: sdk-patterns
description: "@directus/sdk patterns \u2014 composable client, TypeScript types, CRUD operations, authentication, real-time subscriptions, server-side use in Next.js (fetch options, per-request tokens, relations in queries). This skill should be used when the user asks about \"Directus SDK\", \"@directus/sdk\", \"Directus client library\", \"Directus TypeScript\", \"Directus in Next.js\", or needs code patterns for integrating Directus into a JavaScript/TypeScript project."
---

# @directus/sdk Patterns

The official Directus SDK uses a composable architecture. Install:

```bash
npm install @directus/sdk
```

Requirements and versioning (verified against `@directus/sdk` 26.0.0, built for Directus 12.4.x):

- Node.js 22 or later (`engines.node >= 22`). The SDK needs global `fetch` and `URL`; `WebSocket` only for `realtime()`.
- Use the SDK release that belongs to your server release: 26.x for Directus 12.4.x. A typed client from another generation can send calls the server no longer has.
- Every snippet below reads the server address and token from the environment: `DIRECTUS_URL` and `DIRECTUS_TOKEN` (server-side), never hardcode them.

## Client Setup

### Basic Client (Static Token, server-side)

```typescript
import { createDirectus, rest, staticToken } from '@directus/sdk';

const client = createDirectus(process.env.DIRECTUS_URL!)
  .with(staticToken(process.env.DIRECTUS_TOKEN!))
  .with(rest());
```

A static token belongs to one Directus user and carries that user's permissions. Keep it on the server, in an environment variable (`${DIRECTUS_TOKEN}` in `.env`), and give the user a policy with only the access the code needs.

### Client with Login (Node.js scripts and servers)

```typescript
import { createDirectus, rest, authentication } from '@directus/sdk';

// 'json' mode: the refresh token comes back in the response body and the client keeps it,
// so auto-refresh works outside a browser. The default mode is 'cookie': in Node it returns no refresh token, so the session cannot be refreshed.
const client = createDirectus(process.env.DIRECTUS_URL!)
  .with(authentication('json'))
  .with(rest());

// Login takes ONE payload object, then optional options
await client.login({
  email: process.env.DIRECTUS_EMAIL!,
  password: process.env.DIRECTUS_PASSWORD!,
});

// Token is managed automatically (refresh handled internally)

// One-shot scripts: the client schedules the next token refresh with a timer,
// which keeps Node alive. Stop it when the script is done (or build the client
// with authentication('json', { autoRefresh: false })).
client.stopRefreshing();
```

`login(payload, options)`. The payload is `{ email, password }`, or `{ identifier, password }` for an LDAP provider. Options (all optional):

```typescript
await client.login(
  { email, password },
  {
    otp: '123456',        // one-time password when the user has 2FA
    mode: 'json',         // 'json' | 'cookie' | 'session'; overrides the mode given to authentication()
    provider: 'default',  // pick an auth provider (not for redirect-based SSO)
  },
);

await client.login({ identifier: 'username', password }, { provider: 'ldap' });
```

The positional form `login(email, password)` was replaced in SDK 20. It is a type error in TypeScript and throws at runtime in JavaScript. `refresh` and `logout` take an options object too (`{ mode, refresh_token }`), not positional arguments:

```typescript
await client.refresh();                  // uses the stored session
await client.logout();
// as a standalone REST command: client.request(refresh({ mode: 'json', refresh_token }))
```

### Client with Login (browser app, session cookie)

```typescript
import { createDirectus, rest, authentication } from '@directus/sdk';

const client = createDirectus(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
  .with(authentication('session', { credentials: 'include' }))
  .with(rest({ credentials: 'include' }));

await client.login({ email, password });
```

Directus and the app on different domains need `credentials: 'include'` on both composables, plus matching CORS (`CORS_ORIGIN`) and cookie settings on the server. For SSO providers that redirect in the browser (Google, GitHub, Okta), `login()` does not apply: send the user to `/auth/login/<provider>?redirect=<app-url>` and call `client.refresh()` after they return. SSO needs a licensed tier on Directus 12.

### Reading and Setting the Token

```typescript
const token = await client.getToken();   // current access token or null
await client.setToken(accessToken);      // use a token you obtained elsewhere
```

### Reusable Client Module

One module per app keeps the typed schema and the auth choice in a single place. Use a static-token client for server code and a token-less client for public reads that the Public policy allows:

```typescript
// lib/directus.ts
import { createDirectus, rest, staticToken } from '@directus/sdk';
import type { Schema } from './directus-schema'; // your MySchema interface

const url = process.env.DIRECTUS_URL!;

/** Server-only: acts as the token's user. */
export function serverClient() {
  return createDirectus<Schema>(url)
    .with(staticToken(process.env.DIRECTUS_TOKEN!))
    .with(rest());
}

/** Anonymous: only what the Public policy grants. */
export const publicClient = createDirectus<Schema>(url).with(rest());
```

Build a fresh client inside background jobs and serverless handlers instead of importing a shared singleton, so every invocation reads its own environment.

## Type-Safe Schema

Define your schema for TypeScript autocompletion:

```typescript
interface Post {
  id: string;
  title: string;
  content: string;
  status: 'draft' | 'published' | 'archived';
  author: string | Author;
  categories: string[] | PostCategory[];
  date_created: string;
}

interface Author {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

interface Category {
  id: string;
  name: string;
  slug: string;
}

interface PostCategory {
  id: string;
  posts_id: string | Post;
  categories_id: string | Category;
}

interface MySchema {
  posts: Post[];
  authors: Author[];
  categories: Category[];
  posts_categories: PostCategory[];
}

const client = createDirectus<MySchema>(process.env.DIRECTUS_URL!)
  .with(staticToken(process.env.DIRECTUS_TOKEN!))
  .with(rest());
```

Match the schema to the real collection. The string `status` above is the classic draft/published/archived pattern; collections created in Directus 12 get a boolean `archived` field instead (`archived: boolean`), and existing `status` fields keep working. For publish workflows prefer content versions (below) over a status flag.

System collections are typed by the SDK itself (`DirectusUser`, `DirectusRole`, `DirectusPolicy` and so on). Since SDK 26 several of their fields are nullable (`DirectusRole.parent`, `DirectusVersion.hash`, `DirectusRelation.meta` and `.schema`) and `DirectusPolicy.ip_access` is `string[] | null`: add null checks when you read them.

## CRUD Operations

### Read Items

```typescript
import { readItems } from '@directus/sdk';

// List with filter and sort
const posts = await client.request(
  readItems('posts', {
    fields: ['id', 'title', 'status', { author: ['first_name', 'last_name'] }],
    filter: { status: { _eq: 'published' } },
    sort: ['-date_created'],
    limit: 25,
  })
);
```

### Read Single Item

```typescript
import { readItem } from '@directus/sdk';

const post = await client.request(
  readItem('posts', 'item-uuid', {
    fields: ['*', { author: ['*'] }],
  })
);
```

### Create Item

```typescript
import { createItem } from '@directus/sdk';

const newPost = await client.request(
  createItem('posts', {
    title: 'New Post',
    content: 'Post content...',
    status: 'draft',
    author: 'author-uuid',
  })
);
```

### Create Multiple Items

```typescript
import { createItems } from '@directus/sdk';

const newPosts = await client.request(
  createItems('posts', [
    { title: 'Post 1', status: 'draft' },
    { title: 'Post 2', status: 'draft' },
  ])
);
```

### Update Item

```typescript
import { updateItem } from '@directus/sdk';

const updated = await client.request(
  updateItem('posts', 'item-uuid', {
    status: 'published',
  })
);
```

### Update Multiple Items

```typescript
import { updateItems } from '@directus/sdk';

const updated = await client.request(
  updateItems('posts', ['uuid-1', 'uuid-2'], {
    status: 'archived',
  })
);
```

### Delete Item

```typescript
import { deleteItem, deleteItems } from '@directus/sdk';

// Single
await client.request(deleteItem('posts', 'item-uuid'));

// Multiple
await client.request(deleteItems('posts', ['uuid-1', 'uuid-2']));
```

## Filtering

```typescript
const results = await client.request(
  readItems('products', {
    filter: {
      _and: [
        { status: { _eq: 'active' } },
        {
          _or: [
            { price: { _lt: 50 } },
            { featured: { _eq: true } },
          ],
        },
      ],
    },
  })
);
```

## Aggregation

```typescript
import { aggregate } from '@directus/sdk';

const stats = await client.request(
  aggregate('orders', {
    aggregate: { count: '*', sum: 'total', avg: 'total' },
    groupBy: ['status'],
  })
);
```

## Search

```typescript
const results = await client.request(
  readItems('articles', {
    search: 'machine learning',
    fields: ['id', 'title', 'excerpt'],
    limit: 20,
  })
);
```

## Deep Queries

```typescript
const posts = await client.request(
  readItems('posts', {
    fields: ['title', { comments: ['text', { author: ['name'] }] }],
    deep: {
      comments: {
        _filter: { status: { _eq: 'approved' } },
        _sort: ['-date_created'],
        _limit: 5,
      },
    },
  })
);
```

## File Operations

```typescript
import { uploadFiles, importFile } from '@directus/sdk';

// Upload from form data
const formData = new FormData();
formData.append('file', fileBlob);
formData.append('title', 'My Image');

const uploaded = await client.request(uploadFiles(formData));

// Import from URL
const imported = await client.request(
  importFile('https://example.com/image.jpg', {
    title: 'Imported Image',
    folder: 'folder-uuid',
  })
);
```

## Schema Operations

```typescript
import {
  readCollections, createCollection,
  readFields, createField,
  readRelations, createRelation,
  schemaSnapshot, schemaDiff, schemaApply,
} from '@directus/sdk';

// Read all collections
const collections = await client.request(readCollections());

// Get schema snapshot for migration (admin token required)
const snapshot = await client.request(schemaSnapshot());

// Partial snapshot: pass exactly one of includeCollections / excludeCollections
const partial = await client.request(schemaSnapshot({ includeCollections: ['posts'] }));

// Compare against a snapshot from another environment.
// SDK 26: the second argument is an options object, not a boolean.
const diff = await client.request(
  schemaDiff(snapshotFromStaging, { force: false, mode: 'mirror' }), // 'merge' = additive, no deletions
);

// Apply the diff
if (diff && Object.keys(diff.diff).length > 0) {
  await client.request(schemaApply(diff));
}
```

`schemaDiff(snapshot, true)` (positional `force`) was replaced by `schemaDiff(snapshot, { force: true })` in Directus 12.2.0 so that `mode` could be added. Snapshots sent to the server are limited by `IMPORT_MAX_FILE_SIZE` (default `50mb`).

SDK 26 validates some parameters before sending: `readRelationByCollection`, `createField`, `deleteCollection`, `utilsExport`, `utilsImport`, `utilitySort`, `triggerFlow` and `readShareInfo` throw immediately when given an empty collection, key or id. Check values that come from user input or config before you call them.

## Server-Side Apps (Next.js and Other SSR Frameworks)

Calling Directus from Server Components, Route Handlers or Server Actions has its own rules. They live in two files, loaded on demand:

- **Client and runtime** (server-only module, fetch options such as `cache` and `next.tags` through `onRequest` / `withOptions` because `rest({ cache })` does not exist, system collections need their own commands, `withToken` for a per-request user token, the login and refresh REST contract, CORS): [references/ssr-client.md](references/ssr-client.md)
- **Reading content** (relations as nested objects in `fields`, many-to-many through the junction, `readSingleton`, typed filters from URL parameters): [references/content-queries.md](references/content-queries.md)

## Content Versions and Access Policies

Two larger topics live in their own files, loaded on demand:

- **Content versions** (draft and publish workflows: `readItem(..., { version: 'draft' })`, `createContentVersion`, `compareContentVersion`, `promoteContentVersion`; a missing version key answers `403`): [references/content-versions.md](references/content-versions.md)
- **Access policies** (`createPolicy`, `createPermission`, `createRole`, attaching a policy through `/access`, `readUserPermissions()`; a role no longer holds `admin_access` or `app_access`): [references/access-policies.md](references/access-policies.md)

## Real-Time (WebSocket)

```typescript
import { createDirectus, realtime, staticToken } from '@directus/sdk';

const client = createDirectus(process.env.DIRECTUS_URL!)
  .with(staticToken(process.env.DIRECTUS_TOKEN!))
  .with(realtime());

// Connect
await client.connect();

// Subscribe to collection changes
const { subscription } = await client.subscribe('posts', {
  event: 'create',
  query: { fields: ['id', 'title', 'status'] },
});

for await (const event of subscription) {
  console.log('New post:', event.data);
}
```

WebSockets must be enabled on the server (`WEBSOCKETS_ENABLED=true`). Since Directus 12.1.0 the browser origin of a WebSocket connection must be listed in `CORS_ORIGIN`, or the connection is rejected. Instances locked down after a license grace period have WebSockets disabled.

## Error Handling

```typescript
try {
  const result = await client.request(readItem('posts', 'nonexistent'));
} catch (error) {
  if (error.errors) {
    for (const err of error.errors) {
      console.error(`[${err.extensions?.code}] ${err.message}`);
    }
  }
}
```

Common error codes: `FORBIDDEN`, `RECORD_NOT_UNIQUE`, `FAILED_VALIDATION`, `INVALID_PAYLOAD`, `ROUTE_NOT_FOUND`, and since Directus 12.4 `COLLECTION_INACTIVE` (403, collection status Inactive).

## Environment Variables

Always use env vars for configuration:

```typescript
const client = createDirectus(process.env.DIRECTUS_URL!)
  .with(staticToken(process.env.DIRECTUS_TOKEN!))
  .with(rest());
```

```bash
# .env (never commit real values)
DIRECTUS_URL=https://directus.example.com
DIRECTUS_TOKEN=<static-token-of-a-dedicated-user>
```

For local development against the Docker Compose stack, `DIRECTUS_URL` is the local address of the container (see the `docker-local-dev` skill).

## Migrating Older SDK Code

| Older code | SDK 26 |
|------------|--------|
| Positional `login(email, password)` | `client.login({ email, password }, options?)` (SDK 20+); LDAP: `{ identifier, password }` |
| Positional `mode` and `refresh_token` arguments to `refresh` and `logout` | `refresh({ mode, refresh_token })`, `logout({ mode, refresh_token })` |
| `schemaDiff(snapshot, true)` | `schemaDiff(snapshot, { force: true })` |
| `readItem(..., { version: 'main' })` | still works; prefer `'published'` |
| `authentication()` in a Node script, then refresh fails | `authentication('json')`: the default `'cookie'` mode needs a browser cookie jar |
