---
name: troubleshoot
description: This skill should be used when the user asks about "Payload error", "Payload not working", "Payload TypeError", "access bypass in Local API", "Payload hook infinite loop", "Payload transaction rollback", "Cannot find module payload", "Payload import map missing", "Payload type generation fails", "Could not resolve component", or sees a stack trace from Payload they want decoded.
---

# PayloadCMS — Troubleshooting

The recurring failure modes. Each entry: symptom → cause → fix → why.

## Security: Local API Access Control Bypassed

**Symptom**: A user can fetch records they shouldn't. `payload.find` returns rows their access function should filter out.

**Cause**: You passed `user` to the Local API call but didn't set `overrideAccess: false`. Local API operations bypass ALL access control by default.

**Fix**:
```ts
// ❌ BUG
await payload.find({ collection: 'posts', user: someUser })

// ✅ CORRECT
await payload.find({ collection: 'posts', user: someUser, overrideAccess: false })
```

**Why**: Most Local API callers are trusted server code (cron jobs, system tasks). Default-bypass keeps those simple. When proxying a user request, you must opt in. (This is the v3 default; the Payload 4 canary flips it to `overrideAccess: false` — canary, not for production — so state `overrideAccess: true` explicitly in trusted server code you want to keep working.)

See the `access-control` skill for the full pattern.

## Transactions: Atomic Operations Break

**Symptom**: A hook does multiple writes. One fails. You expect a clean rollback but find half-committed data (e.g., the parent record rolled back, the audit-log row persisted).

**Cause**: Nested operations missing `req` — they opened separate transactions.

**Fix**: Always pass `req` to nested calls inside a hook or endpoint:
```ts
// ❌ Separate transaction
await req.payload.create({ collection: 'audit', data })

// ✅ Same transaction
await req.payload.create({ collection: 'audit', data, req })
```

**Why**: Without `req`, the call doesn't know which transaction to join — it grabs a new connection. The parent's rollback can't reach across connections.

## Infinite Hook Loops

**Symptom**: Hook fires, fires again, again, until a stack overflow / DB connection exhaustion.

**Cause**: An `afterChange` (or any hook) writes back to the same document, re-triggering itself.

**Fix**: Set a context flag:
```ts
hooks: {
  afterChange: [
    async ({ doc, req, context }) => {
      if (context?.skipHooks) return doc          // bail re-entry
      await req.payload.update({
        collection: 'posts',
        id: doc.id,
        data: { viewCount: (doc.viewCount || 0) + 1 },
        context: { skipHooks: true },              // skip on the recursive call
        req,
      })
      return doc
    },
  ],
}
```

**Why**: `req.context` is a per-request object you control. Use it to short-circuit recursive paths.

## TypeScript: Types out of sync

**Symptom**: TS errors like `Property 'newField' does not exist on type 'Post'`.

**Cause**: Forgot to regenerate types after changing a collection.

**Fix**:
```bash
pnpm generate:types
```

**Why**: `payload-types.ts` is the source of truth for typed Local API responses. Add to git pre-commit hook or CI to enforce freshness.

## Admin: "Could not resolve component"

**Symptom**: Admin panel renders with a red error: `Could not resolve component <path>`.

**Cause**: The import map is stale. You added a string-path component reference but didn't regenerate `src/app/(payload)/admin/importMap.js`.

**Fix**:
```bash
pnpm payload generate:importmap
git add src/app/\(payload\)/admin/importMap.js
```

**Why**: Payload uses static import maps so Next.js can split admin bundles. Strings only resolve via the map — they're not regular imports.

## Migrations: "Schema is out of sync"

**Symptom**: Postgres / SQLite: app boots but errors during writes about missing columns. Or `migrate` says nothing pending but the prod DB is missing columns.

**Cause**: Mixing `db.push: true` with migrations — only one strategy should manage the schema per environment.

**Fix**:
- Dev: `push: true`, never call `migrate:create`.
- Staging/Prod: `push: false`, manage schema **only** through migrations.
- If migrations diverged, in staging: `pnpm migrate:reset && pnpm migrate` (only on a non-prod DB).

**Why**: `push` and migrations both mutate schema. If both run, they fight.

## "Module not found: payload"

**Symptom**: `Cannot find module 'payload'` or `'@payload-config'`.

**Cause**: `tsconfig.json` paths not picked up by the runner, or fresh clone without `pnpm install`.

**Fix**: Run install. Verify `tsconfig.json`:
```json
{
  "compilerOptions": {
    "paths": {
      "@payload-config": ["./src/payload.config.ts"],
      "@/*": ["./src/*"]
    }
  }
}
```

## MongoDB: "Transaction numbers are only allowed on a replica set"

**Symptom**: `MongoServerError: Transaction numbers are only allowed on a replica set member or mongos`.

**Cause**: You set `transactionOptions: {...}` on the Mongo adapter but the DB isn't a replica set.

**Fix**: Either disable transactions for local dev:
```ts
mongooseAdapter({ url, transactionOptions: false })
```
Or run a single-node replica set:
```bash
mongod --replSet rs0
mongosh --eval 'rs.initiate()'
```

**Why**: Mongo transactions require multi-document atomicity, which requires the replica-set oplog.

## Postgres: "relation does not exist"

**Symptom**: First request after schema change errors `relation "posts" does not exist`.

**Cause**: Forgot to apply migrations on the target DB.

**Fix**:
```bash
pnpm migrate
```

For first-time setup of a new DB and you're still in dev with `push: true`, restart `pnpm dev` — Payload only pushes on cold boot.

## Logger: "TypeError: Cannot read properties of undefined (reading 'msg')"

**Symptom**: Logging an error throws.

**Cause**: Wrong logger argument shape.

**Fix**:
```ts
// ❌ Don't pass error as second arg
req.payload.logger.error('Failed', err)

// ❌ Don't use 'error'/'message' keys
req.payload.logger.error({ message: 'Failed', error: err })

// ✅ Use 'msg' + 'err'
req.payload.logger.error({ msg: 'Failed', err })
// ✅ Plain string also works
req.payload.logger.error('Failed')
```

**Why**: Payload uses Pino under the hood — Pino expects `err` for Error objects and `msg` for the message.

## After upgrading to 3.89 / 3.90: what broke

3.90.0 (2026-09-18) is a security release and 3.89.0 closed the jobs collection. After `pnpm up payload @payloadcms/*`, run `pnpm payload generate:types`; on SQL databases also `pnpm payload migrate:create upgrade-3-90 && pnpm payload migrate`.

| Symptom | Cause | Fix |
| --- | --- | --- |
| `payload-jobs` REST/GraphQL returns 403, admin Jobs view empty (3.89) | Collection access is `() => false` by default | Local API with `overrideAccess: true`, or open read-only via `jobs.jobsCollectionOverrides` — see `jobs-queue` |
| TS error `Type 'boolean' is not assignable to type 'StripeRESTConfig'`; or startup throws "requires an object with a non-empty allowedMethods array" | A boolean `rest` option on `stripePlugin` (older examples set it to `false`) | Delete `rest` to keep the proxy off, or pass `{ allowedMethods: ['customers.list'], access? }` — see `official-plugins` |
| API key no longer readable in admin / API | Keys are shown once since 3.90 | Regenerate and store it; `auth: { useAPIKey: { reveal: true } }` restores revealing — see `authentication` |
| SQL error about a missing column for `resetPasswordRequestedAt` (auth collections) or `_objectKey` (upload collections) | Migration for the new auth / upload fields not run | `pnpm payload migrate:create` then `pnpm payload migrate` |
| Users on other devices got signed out | Password change now revokes other sessions | Expected; no action |
| Scheduled publish events from before the upgrade never fire | `schedulePublish` now records the user's auth collection | Re-create pending scheduled publish/unpublish events |
| Upload fails with 413 ("File size limit has been reached", "Multipart request size limit has been reached" or "Multipart limit has been reached") | 3.90 multipart defaults: a single file over 20 MiB (`upload.limits.fileSize`), the whole request over 50 MiB (`upload.requestSizeLimit`), more than 3 files / 20 fields / 1 MiB per field | Raise the one that tripped in the root config — `upload: { requestSizeLimit, limits: { fileSize } }`; raising only `requestSizeLimit` leaves the 20 MiB per-file cap. See `adapters` |
| SVG / XML upload rejected | Strict validation | Verify the file; `upload.allowRestrictedFileTypes: true` only if required |
| External image URL / paste-URL fetch fails | External files need a trusted origin; non-HTTP(S) URLs refused | Set `serverURL` or add the origin to CORS/CSRF; use HTTP(S) |
| GCS client upload fails CORS preflight | New required header | Add `x-goog-if-generation-match` to the bucket's CORS allowed headers |
| Azure files no longer public | Plugin-created containers are private by default | `containerAccess: 'blob'` if anonymous reads are intended |
| Secondary auth collection can't read form submissions | Form Builder defaults read to the admin collection | Set `formSubmissionOverrides.access.read` — see `official-plugins` |
| `QueryError` on a polymorphic join | Unsupported `where` (localized fields, arrays/blocks, paths through relationship/upload/json, `near/within/intersects/all`) | Rewrite the filter / the read access rule to use direct, compatible fields |
| Custom Lexical feature fails to compile | Lexical 0.50 removed old APIs; direct `lexical` dependency | Drop `lexical` / `@lexical/*` deps, import from `@payloadcms/richtext-lexical/lexical` |
| `peer dependency` error on `next` | `@payloadcms/next` 3.90 needs `next >=16.3.3 <17` (or a patched 15.2–15.4 line) | Upgrade Next — see `nextjs-integration` |

## Upload: "Cannot read file" after deploy

**Symptom**: Files uploaded locally don't appear on production.

**Cause**: Using local `staticDir` on a serverless/ephemeral host (Vercel, Render, Fly).

**Fix**: Add a storage adapter (S3, R2, Vercel Blob, UploadThing). See the `adapters` skill.

**Why**: Containers don't share writable disk across deploys.

## Live Preview Iframe Empty

**Symptom**: Admin's Live Preview tab shows a blank page.

**Cause(s)**:
1. Wrong `admin.livePreview.url` — points to a 404.
2. Frontend route doesn't render content from `data` prop.
3. CSP / `X-Frame-Options` blocks the iframe.

**Fix**: Visit the URL directly. If 404, fix slug/path. If empty, ensure the page accepts `?live-preview=true` and renders. If CSP-blocked, add the admin origin to `frame-ancestors`.

## "Maximum call stack size exceeded" inside a hook

**Symptom**: Stack overflow during admin save.

**Cause**: Either an infinite hook loop (see above) or a recursive component import in a custom field.

**Fix**: Add `context.skipHooks` guards. If component-related, isolate the component to verify which import chain recurses.

## Migration File Won't Compile

**Symptom**: `payload migrate` errors during TS compile.

**Cause(s)**:
1. A type imported from `@/payload-types` references a collection that no longer exists.
2. A migration import points outside `src/`.

**Fix**: Migrations should import types lazily or use plain JS types. Keep them self-contained — don't import app code that may change.

## "Sharp" or image processing fails

**Symptom**: Uploads fail with `Error: Input file contains unsupported image format` or sharp install errors.

**Cause(s)**:
1. Image too large — bump `payload.config.ts`'s `serverURL` body limit, or Next.js `bodySizeLimit`.
2. `sharp` not installed on the deploy target architecture.

**Fix**:
```bash
pnpm add sharp
# On Vercel, set NODE_OPTIONS="--no-warnings" and ensure pnpm's lockfile commits sharp's arch-specific deps
```

## See Also

- The `access-control` skill — overrideAccess details.
- The `hooks` skill — `req` threading and `context` flags.
- The `cli-recipes` skill — migration commands.
- The `adapters` skill — DB and storage gotchas.
