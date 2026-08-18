# Local API — Method Reference

All methods are on the Payload instance returned by `getPayload({ config })`. They run in-process — no HTTP overhead.

## Setup

```ts
import { getPayload } from 'payload'
import config from '@payload-config'

const payload = await getPayload({ config })
```

## Universal Options

Most methods accept these options:

| Option | Default | Effect |
| --- | --- | --- |
| `req` | — | Pass the active `PayloadRequest` to join its transaction & user context |
| `user` | — | Acting user (for access control) |
| `overrideAccess` | `true` | Set `false` to enforce access rules with the passed `user` |
| `locale` | default locale | Read/write localized data |
| `fallbackLocale` | default | Fallback when current locale empty |
| `depth` | `2` | Populate depth (`0` = IDs only) |
| `draft` | `false` | Include drafts (versions:drafts enabled) |
| `disableErrors` | `false` | Resolve instead of throw on not-found |
| `context` | — | Per-op flag bag passed to hooks (`req.context`) |
| `showHiddenFields` | `false` | Bypass field-level `read` access |
| `trash` | `false` | Include soft-deleted docs (collections with `trash: true`) — supported by find/findByID/update/delete and version ops |
| `select` | — | Return only the listed fields |
| `populate` | — | Per-relationship field selection on populated docs |

## Collections

### `payload.find`

```ts
payload.find<T extends keyof Collections>({
  collection: T,
  where?: Where<Collections[T]>,
  sort?: string,           // 'createdAt' | '-createdAt' | 'priority,-createdAt'
  limit?: number,
  page?: number,
  pagination?: boolean,
  select?: SelectType,
  depth?: number,
  locale?: string,
  fallbackLocale?: string,
  user?: User,
  overrideAccess?: boolean,
  req?: PayloadRequest,
}): Promise<PaginatedDocs<Collections[T]>>
```

Returns:
```ts
interface PaginatedDocs<T> {
  docs: T[]
  totalDocs: number
  limit: number
  totalPages: number
  page: number
  pagingCounter: number
  hasPrevPage: boolean
  hasNextPage: boolean
  prevPage: number | null
  nextPage: number | null
}
```

### `payload.findByID`

```ts
payload.findByID({
  collection: T,
  id: string | number,
  depth?: number,
  locale?: string,
  draft?: boolean,
  disableErrors?: boolean,         // returns null instead of throwing
  user?: User,
  overrideAccess?: boolean,
  req?: PayloadRequest,
}): Promise<Collections[T] | null>
```

### `payload.count`

```ts
payload.count({
  collection: T,
  where?: Where,
  locale?: string,
  user?: User,
  overrideAccess?: boolean,
  req?: PayloadRequest,
}): Promise<{ totalDocs: number }>
```

### `payload.findDistinct`

Distinct values of a single field:

```ts
payload.findDistinct({
  collection: T,
  field: string,
  where?: Where,
  limit?: number,
  page?: number,
  sort?: string,
}): Promise<PaginatedDistinctDocs<Record<string, unknown>>>
```

### `payload.create`

```ts
payload.create({
  collection: T,
  data: Partial<Collections[T]>,
  file?: PayloadFile,              // For upload collections
  locale?: string,
  draft?: boolean,
  user?: User,
  overrideAccess?: boolean,
  context?: Record<string, any>,
  req?: PayloadRequest,
  disableVerificationEmail?: boolean,  // auth collections
}): Promise<Collections[T]>
```

`PayloadFile`:
```ts
{ data: Buffer, mimetype: string, name: string, size: number }
```

### `payload.update`

Single doc by ID:
```ts
payload.update({
  collection: T,
  id: string | number,
  data: Partial<Collections[T]>,
  draft?: boolean,
  autosave?: boolean,
  locale?: string,
  user?: User,
  overrideAccess?: boolean,
  context?: Record<string, any>,
  req?: PayloadRequest,
}): Promise<Collections[T]>
```

Many docs by `where`:
```ts
payload.update({
  collection: T,
  where: Where,
  data: Partial<Collections[T]>,
  // …same other options
}): Promise<{ docs: Collections[T][]; errors: { message: string; id: string }[] }>
```

### `payload.delete`

```ts
payload.delete({
  collection: T,
  id?: string | number,
  where?: Where,
  user?: User,
  overrideAccess?: boolean,
  req?: PayloadRequest,
}): Promise<Collections[T] | { docs: Collections[T][]; errors: any[] }>
```

### `payload.duplicate`

```ts
payload.duplicate({
  collection: T,
  id: string | number,
  user?: User,
  req?: PayloadRequest,
}): Promise<Collections[T]>
```

## Globals

### `payload.findGlobal`

```ts
payload.findGlobal({
  slug: G,
  depth?: number,
  locale?: string,
  draft?: boolean,
  user?: User,
  overrideAccess?: boolean,
  req?: PayloadRequest,
}): Promise<Globals[G]>
```

### `payload.updateGlobal`

```ts
payload.updateGlobal({
  slug: G,
  data: Partial<Globals[G]>,
  draft?: boolean,
  locale?: string,
  user?: User,
  overrideAccess?: boolean,
  context?: Record<string, any>,
  req?: PayloadRequest,
}): Promise<Globals[G]>
```

## Versions

### `payload.findVersions`

```ts
payload.findVersions({
  collection: T,
  where?: Where,
  sort?: string,
  limit?: number,
  page?: number,
  depth?: number,
  user?: User,
  overrideAccess?: boolean,
  req?: PayloadRequest,
}): Promise<PaginatedDocs<{ id: string; version: Collections[T]; createdAt: string; ... }>>
```

### `payload.findVersionByID`

```ts
payload.findVersionByID({
  collection: T,
  id: string,                       // Version ID, not doc ID
  depth?: number,
  user?: User,
  req?: PayloadRequest,
}): Promise<TypeWithVersion<T>>
```

### `payload.restoreVersion`

```ts
payload.restoreVersion({
  collection: T,
  id: string,                       // Version ID to restore
  user?: User,
  req?: PayloadRequest,
}): Promise<Collections[T]>
```

### `payload.restoreGlobalVersion`

```ts
payload.restoreGlobalVersion({
  slug: G,
  id: string,                       // Global version ID to restore
  user?: User,
  req?: PayloadRequest,
}): Promise<Globals[G]>
```

## Auth

For auth-enabled collections:

### `payload.login`

```ts
payload.login({
  collection: 'users',
  data: { email: string, password: string },
  req?: PayloadRequest,
}): Promise<{ user, token, exp }>
```

> **No `payload.logout` method exists.** Logout and token refresh are server functions imported from `@payloadcms/next/auth` (`logout`, `refresh`) — see the `authentication` skill.

### `payload.forgotPassword`

```ts
payload.forgotPassword({
  collection: 'users',
  data: { email: string },
  disableEmail?: boolean,
  expiration?: number,              // ms
  req?: PayloadRequest,
}): Promise<string>                  // Returns reset token
```

### `payload.resetPassword`

```ts
payload.resetPassword({
  collection: 'users',
  data: { token: string, password: string },
  overrideAccess?: boolean,
  req?: PayloadRequest,
}): Promise<{ user, token }>
```

### `payload.verifyEmail`

```ts
payload.verifyEmail({
  collection: 'users',
  token: string,
}): Promise<boolean>
```

### `payload.auth`

Authenticate an incoming Request (used in custom routes):
```ts
payload.auth({ headers: Request['headers'] })
  : Promise<{ user: User | null, responseHeaders: Headers, permissions: Permissions }>
```

### `payload.unlock`

Manually clear `loginAttempts` / `lockUntil`:
```ts
payload.unlock({ collection: 'users', data: { email }, req? }): Promise<boolean>
```

## Jobs

### `payload.jobs.queue`

```ts
payload.jobs.queue({
  task?: TaskSlug,                  // For one-off tasks
  workflow?: WorkflowSlug,          // For workflows
  input: Record<string, any>,
  queue?: string,
  waitUntil?: Date,
  req?: PayloadRequest,
}): Promise<Job>
```

### `payload.jobs.run`

```ts
payload.jobs.run({
  queue?: string,
  limit?: number,
  where?: Where,
  silent?: boolean,
}): Promise<{ noJobsRemaining: boolean, results: JobResult[] }>
```

### `payload.jobs.runByID`

```ts
payload.jobs.runByID({ id: string | number }): Promise<RunJobsResult>
```

### `payload.jobs.cancel` / `payload.jobs.cancelByID`

```ts
payload.jobs.cancel({ where: Where }): Promise<void>
payload.jobs.cancelByID({ id: string | number }): Promise<void>
```

### `payload.jobs.handleSchedules`

Enqueue due scheduled jobs (see the `jobs-queue` skill):

```ts
payload.jobs.handleSchedules({ queue?: string, allQueues?: boolean }): Promise<HandleSchedulesResult>
```

## Email

### `payload.sendEmail`

```ts
payload.sendEmail({
  to: string | string[],
  from?: string,                    // Falls back to defaultFromAddress
  subject: string,
  html?: string,
  text?: string,
  cc?: string | string[],
  bcc?: string | string[],
  attachments?: any[],
  headers?: Record<string, string>,
}): Promise<any>                    // Provider-specific response
```

## Database Adapter

### Direct transactions

```ts
payload.db.beginTransaction({ /* options */ }): Promise<string | number>
payload.db.commitTransaction(txID): Promise<void>
payload.db.rollbackTransaction(txID): Promise<void>
```

Wrap multi-step orchestration in a try/catch/rollback. See `adapters/references/transactions.md`.

## Logger

```ts
payload.logger.info(msg: string | object)
payload.logger.warn(msg: string | object)
payload.logger.error(msg: string | object)
payload.logger.debug(msg: string | object)
payload.logger.trace(msg: string | object)
payload.logger.fatal(msg: string | object)
```

Object form: `{ msg: 'message', err: Error, ...customKeys }`. **Use `err`, not `error`.**

## Hooks Programmatic API

Most callers don't need these — they live on `payload.collections.<slug>.config.hooks` for advanced introspection.

## Where Type

```ts
type Where = {
  [field: string]: {
    equals?: any
    not_equals?: any
    greater_than?: number | string
    greater_than_equal?: number | string
    less_than?: number | string
    less_than_equal?: number | string
    like?: string
    contains?: string
    in?: any[]
    not_in?: any[]
    all?: any[]
    exists?: boolean
    near?: [number, number, number?, number?]   // [lng, lat, maxDistance?, minDistance?]
    within?: GeoJSON
    intersects?: GeoJSON
  } | Where
} & {
  and?: Where[]
  or?: Where[]
}
```
