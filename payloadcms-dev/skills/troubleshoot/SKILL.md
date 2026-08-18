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

**Why**: Most Local API callers are trusted server code (cron jobs, system tasks). Default-bypass keeps those simple. When proxying a user request, you must opt in.

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
