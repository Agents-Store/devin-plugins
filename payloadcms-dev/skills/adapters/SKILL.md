---
name: adapters
description: This skill should be used when the user asks about "Payload database adapter", "Postgres in Payload", "MongoDB Payload setup", "SQLite Payload", "S3 storage adapter", "Cloudflare R2 Payload", "Vercel Blob upload", "Payload email Resend", "Payload Nodemailer SMTP", "Payload transactions", or needs to wire Payload to a database, file storage, or email provider.
---

# PayloadCMS — Adapters

Payload is database-agnostic, storage-agnostic, and email-agnostic. Pick adapters per environment in `payload.config.ts`. This skill covers the three adapter families and the transaction model that ties them together.

## Database Adapters

Set in `payload.config.ts` under `db`. Only one per app.

### PostgreSQL (recommended for production)

```bash
pnpm add @payloadcms/db-postgres
```

```ts
import { postgresAdapter } from '@payloadcms/db-postgres'

export default buildConfig({
  // …
  db: postgresAdapter({
    pool: { connectionString: process.env.DATABASE_URI },
    push: process.env.NODE_ENV !== 'production',  // Auto-sync schema in dev
    migrationDir: path.resolve(dirname, 'migrations'),
    schemaName: 'public',
    transactionOptions: { isolationLevel: 'read committed' },
  }),
})
```

Connection string forms:
```
postgres://USER:PASS@HOST:5432/DBNAME
postgresql://USER:PASS@HOST:5432/DBNAME?sslmode=require
```

`push: true` syncs the schema automatically (great for dev). For production, **disable `push` and use migrations** — see the `cli-recipes` skill.

### MongoDB

```bash
pnpm add @payloadcms/db-mongodb
```

```ts
import { mongooseAdapter } from '@payloadcms/db-mongodb'

db: mongooseAdapter({
  url: process.env.DATABASE_URI,        // mongodb://... or mongodb+srv://...
  connectOptions: { dbName: 'my-app' },
  autoPluralization: true,
  transactionOptions: false,            // Set object to enable transactions (requires replica set)
}),
```

**MongoDB transactions require a replica set** — single-node mongod won't work. For Atlas, replica set is enabled by default. For local dev, run `mongod --replSet rs0` then `rs.initiate()` once.

### SQLite (libSQL / Turso)

```bash
pnpm add @payloadcms/db-sqlite
```

```ts
import { sqliteAdapter } from '@payloadcms/db-sqlite'

db: sqliteAdapter({
  client: {
    url: process.env.DATABASE_URI,      // file:./payload.db  or  libsql://your-db.turso.io
    authToken: process.env.DATABASE_AUTH_TOKEN,  // Turso only
  },
  push: process.env.NODE_ENV !== 'production',
  transactionOptions: { behavior: 'immediate' },
}),
```

### Vercel Postgres

```bash
pnpm add @payloadcms/db-vercel-postgres
```

```ts
import { vercelPostgresAdapter } from '@payloadcms/db-vercel-postgres'

db: vercelPostgresAdapter({
  pool: { connectionString: process.env.POSTGRES_URL },  // injected by Vercel
}),
```

Wraps `@vercel/postgres`. Same migration story as `postgresAdapter`.

### Cloudflare D1

```bash
pnpm add @payloadcms/db-d1-sqlite
```

```ts
import { sqliteD1Adapter } from '@payloadcms/db-d1-sqlite'

db: sqliteD1Adapter({
  binding: env.D1,               // the Workers D1 database binding
}),
```

For running Payload on **Cloudflare Workers** with a D1 database — see the official `with-cloudflare-d1` template (pairs with the `r2Storage` upload adapter below).

## Transactions

Postgres, SQLite (with `transactionOptions`), and MongoDB-with-replica-set provide all-or-nothing transactions. Payload uses them automatically per HTTP request. **You must thread `req` through nested ops** to keep the transaction alive:

```ts
// ❌ Breaks atomicity — new connection, separate transaction
await payload.create({ collection: 'audit', data, /* no req */ })

// ✅ Joins the parent transaction
await payload.create({ collection: 'audit', data, req })
```

When to pass `req`:
- Inside any hook (collection, field, global).
- Inside a custom endpoint that mutates multiple collections.
- In jobs/workflows where you want atomic multi-step writes.

When `req` is optional:
- Read-only top-level ops that don't depend on uncommitted writes.
- Migration scripts (each migration commits independently).

See `references/transactions.md` for the deep dive.

## Storage Adapters

Default behavior in upload collections: files written to `staticDir` on disk. That doesn't survive deploys on Vercel/Render/Fly and doesn't scale. Use a storage adapter in production.

### AWS S3 / S3-Compatible (R2, Backblaze B2, MinIO)

```bash
pnpm add @payloadcms/storage-s3
```

```ts
import { s3Storage } from '@payloadcms/storage-s3'

export default buildConfig({
  // …
  plugins: [
    s3Storage({
      collections: {
        media: true,                              // Apply to 'media' upload collection
        // Or pass options per collection:
        // media: { prefix: 'uploads/' },
      },
      bucket: process.env.S3_BUCKET,
      config: {
        endpoint: process.env.S3_ENDPOINT,        // For R2: https://<account>.r2.cloudflarestorage.com
        region: process.env.S3_REGION,            // 'auto' for R2
        credentials: {
          accessKeyId: process.env.S3_ACCESS_KEY_ID,
          secretAccessKey: process.env.S3_SECRET_ACCESS_KEY,
        },
        forcePathStyle: true,                     // Required for R2/MinIO
      },
    }),
  ],
})
```

Cloudflare R2: `endpoint` is `https://<accountId>.r2.cloudflarestorage.com`, `region: 'auto'`.

### Vercel Blob

```bash
pnpm add @payloadcms/storage-vercel-blob
```

```ts
import { vercelBlobStorage } from '@payloadcms/storage-vercel-blob'

plugins: [
  vercelBlobStorage({
    collections: { media: true },
    token: process.env.BLOB_READ_WRITE_TOKEN,
    addRandomSuffix: true,
  }),
],
```

### UploadThing

```bash
pnpm add @payloadcms/storage-uploadthing
```

```ts
import { uploadthingStorage } from '@payloadcms/storage-uploadthing'

plugins: [
  uploadthingStorage({
    collections: { media: true },
    options: {
      apiKey: process.env.UPLOADTHING_SECRET,
      acl: 'public-read',
    },
  }),
],
```

### Azure Blob

```bash
pnpm add @payloadcms/storage-azure
```

```ts
import { azureStorage } from '@payloadcms/storage-azure'

plugins: [
  azureStorage({
    collections: { media: true },
    allowContainerCreate: false,   // required — true lets the plugin create a missing container
    baseURL: process.env.AZURE_STORAGE_BASE_URL,   // required — the storage account's blob endpoint
    connectionString: process.env.AZURE_STORAGE_CONNECTION_STRING,
    containerName: process.env.AZURE_STORAGE_CONTAINER,
    // containerAccess: 'private',   // 3.90+ default for containers the plugin creates; 'blob' = anonymous reads
  }),
],
```

Since 3.87.0, client uploads support `chunkLargeFiles` for files larger than 5GB. `allowContainerCreate` and `baseURL` are required options — omitting them is a compile error. See "Upload hardening (3.90.0)" below for the private-container default.

### Google Cloud Storage

Official adapter:

```bash
pnpm add @payloadcms/storage-gcs
```

```ts
import { gcsStorage } from '@payloadcms/storage-gcs'

plugins: [
  gcsStorage({
    collections: { media: true },
    bucket: process.env.GCS_BUCKET,
    options: { /* GCS client options — keyFilename or Application Default Credentials */ },
  }),
],
```

### Cloudflare R2 (dedicated adapter — Workers)

`@payloadcms/storage-r2` exports `r2Storage()` for deployments on **Cloudflare Workers** with a native R2 bucket binding:

```bash
pnpm add @payloadcms/storage-r2
```

```ts
import { r2Storage } from '@payloadcms/storage-r2'

plugins: [
  r2Storage({
    collections: { media: true },
    bucket: env.R2_BUCKET,        // the Workers R2 bucket binding
  }),
],
```

On Node hosts (Vercel/Netlify/self-host), R2 via `s3Storage` with the S3-compatible config above remains the recommended approach.

### Upload hardening (3.90.0)

3.90.0 is a security release that tightened uploads end to end. Review each item when upgrading from 3.89 or older — they change defaults, not just options:

| Change | Affected if you | Action |
| --- | --- | --- |
| Azure containers default to **private** | `@payloadcms/storage-azure` with `allowContainerCreate: true` | Only *newly created* containers change. To keep anonymous blob URLs set `containerAccess: 'blob'` (`'container'` also allows listing); existing containers keep their access level |
| Client uploads hardened for all adapters | `clientUploads: true` on S3, GCS, Azure or a custom adapter | For GCS add `x-goog-if-generation-match` to the bucket's CORS allowed headers; custom upload clients must send the required metadata and return the headers the adapter expects |
| Client uploads stored per upload | `clientUploads` and you build file paths outside Payload | New files live at `<prefix>/<_objectKey>/<filename>` (also for generated sizes); `_objectKey` is a new upload-collection field (SQL adapters: migration adds the column). Existing files are not moved. Prefix changes must come with a file replacement |
| Multipart uploads are capped, and oversize requests are rejected with **413** | files larger than **20 MiB**, requests larger than **50 MiB**, or more than 3 files / 20 fields / 1 MiB per field in one request | The 3.90.2 defaults are `upload.requestSizeLimit: 50 * 1024 * 1024` (whole raw request) **and** `upload.limits: { fileSize: 20 * 1024 * 1024, files: 3, fields: 20, fieldSize: 1024 * 1024 }` (3.87.1 had no `limits` defaults and `abortOnLimit: false`, so oversize files were truncated instead of rejected). Raising only `requestSizeLimit` does **not** fix a single file over 20 MiB — raise `limits.fileSize` too (and keep `requestSizeLimit` above it plus metadata). `clientUploads: true` sends files straight to the bucket and bypasses these server caps |
| Strict SVG / XHTML / XML validation | you accept SVG or other XML-family files | Verify the workflow; set `allowRestrictedFileTypes: true` in the collection's `upload` config only if the previous behaviour is explicitly required |
| External files need a trusted origin | `upload.disableLocalStorage: true` with relative file URLs that need a session cookie; non-HTTP(S) URLs | Set `serverURL` or add the exact application origin to CORS/CSRF; replace non-HTTP(S) URLs with HTTP(S) |
| `externalFileHeaderFilter(headers, context)` | you use it | It can run once per redirect hop and now receives `context.isSameOrigin` — strip `cookie`/`authorization` when it is false |
| `disablePayloadAccessControl` no longer disables safe outbound fetch | you set `disablePayloadAccessControl: true` — the **storage-adapter collection option** (`collections: { media: { disablePayloadAccessControl: true } }` on `s3Storage`, `azureStorage`, …; not a root `buildConfig` option) | In 3.87.1 it forced `skipSafeFetch` to `true` for that collection; in 3.90.2 that coupling is gone and safe fetch stays on. Use a narrow `upload.skipSafeFetch` allowlist for trusted hosts; `skipSafeFetch: true` only when every URL the collection accepts is trusted |
| Upload filename hardening | a custom top-level `prefix` field on an upload collection holds ordinary data | Rename that field, or update it only from trusted server code — `prefix` is now treated as a storage field |

```ts
// src/payload.config.ts — raise the multipart caps (both: a single file is limited by `limits.fileSize`,
// the whole request by `requestSizeLimit`)
export default buildConfig({
  upload: {
    requestSizeLimit: 120 * 1024 * 1024,   // whole raw multipart request, in bytes (default 50 MiB)
    limits: {
      fileSize: 100 * 1024 * 1024,         // one file (default 20 MiB) — over the limit => HTTP 413
      // files: 3, fields: 20, fieldSize: 1024 * 1024,   // other defaults, raise only if needed
    },
  },
  // …
})

// src/collections/Media.ts
upload: {
  allowRestrictedFileTypes: true,   // only if SVG/XML must keep working as before
  skipSafeFetch: [{ hostname: 'cdn.example.com' }],   // narrow allowlist, never `true` for untrusted input
  externalFileHeaderFilter: (headers, context) => {
    if (!context?.isSameOrigin) {
      delete headers.cookie
      delete headers.authorization
    }
    return headers
  },
}
```

After upgrading run `pnpm payload generate:types`; on SQL adapters also `pnpm payload migrate:create` and `pnpm payload migrate`.

**After enabling a storage adapter** — you'll usually drop `upload.staticDir` from the collection because the files live in the bucket, not on disk:

```ts
// src/collections/Media.ts
export const Media: CollectionConfig = {
  slug: 'media',
  upload: {
    // staticDir: undefined  (default — files routed through the adapter)
    mimeTypes: ['image/*', 'application/pdf'],
    imageSizes: [/*…*/],
  },
  fields: [{ name: 'alt', type: 'text', required: true }],
}
```

The plugin auto-routes `doc.url` to the bucket's public URL (or signed URL if private).

## Email Adapters

Default: emails are logged to the console. Wire a real provider for `forgotPassword`, `verify`, and your own outgoing mail.

### Resend (transactional, simplest)

```bash
pnpm add @payloadcms/email-resend
```

```ts
import { resendAdapter } from '@payloadcms/email-resend'

export default buildConfig({
  // …
  email: resendAdapter({
    defaultFromAddress: 'no-reply@example.com',
    defaultFromName: 'My App',
    apiKey: process.env.RESEND_API_KEY,
  }),
})
```

### Nodemailer (SMTP — any provider with SMTP creds)

```bash
pnpm add @payloadcms/email-nodemailer
```

```ts
import { nodemailerAdapter } from '@payloadcms/email-nodemailer'

email: nodemailerAdapter({
  defaultFromAddress: 'no-reply@example.com',
  defaultFromName: 'My App',
  transportOptions: {
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT || 587),
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  },
}),
```

Send mail programmatically:
```ts
await payload.sendEmail({
  to: user.email,
  subject: 'Welcome',
  html: '<p>Hi!</p>',
})
```

## Switching Adapters

When swapping databases (e.g., SQLite dev → Postgres prod):
1. Run `payload migrate:create` on Postgres to generate a fresh migration set.
2. Export data with a one-off script using the Local API on the old adapter, then import on the new one.
3. Don't try to run the same migration files across DB types — adapter-specific.

## See Also

- `references/transactions.md` — full transaction semantics, isolation levels, gotchas.
- The `setup` skill — initial DB adapter selection during scaffolding.
- The `cli-recipes` skill — `migrate:create`, `migrate`, `migrate:down`.
- The `hooks` skill — req threading inside hooks.

After changing a DB adapter, restart `pnpm dev` — Payload caches the schema at boot.
