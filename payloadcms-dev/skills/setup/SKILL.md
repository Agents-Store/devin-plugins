---
name: setup
description: This skill should be used when the user asks to "install PayloadCMS", "create a Payload project", "set up Payload v3", "scaffold Payload app", "initialize Payload with Next.js", "pick a Payload database adapter", "configure payload.config.ts", or needs to bootstrap a fresh Payload project from zero to a running admin panel.
---

# PayloadCMS — Setup

Bootstrap a PayloadCMS v3 project from zero. Five steps: install Node, scaffold with `create-payload-app`, configure the database adapter, set up `payload.config.ts`, run the admin panel.

## 1. Prerequisites

- **Node.js `^18.20.2 || >=20.9.0`** (the `payload` engines field); use 20 LTS+ in practice.
- **pnpm 9+**, npm 10+, yarn 4+, or bun 1+ for installing dependencies. pnpm is the project default.
- A database. Pick one before scaffolding:
  - **MongoDB** — simplest local dev (Docker, Atlas free tier, mongodb-memory-server).
  - **PostgreSQL** — most production deployments (Supabase, Neon, Railway, RDS, local Postgres).
  - **SQLite** — single-file local dev, no server. Backed by libSQL/Turso for prod.

## 2. Scaffold with `create-payload-app`

Use the official scaffolder — it sets up a Next.js App Router project with `(frontend)` and `(payload)` route groups already wired:

```bash
pnpm create payload-app@latest my-app
```

Interactive prompts:
- **Template**: `blank` (recommended for custom builds) or `website` / `ecommerce` (full demo apps).
- **Database**: `mongodb` / `postgres` / `sqlite`.
- **Project name**: kebab-case slug.

The payload repo also ships additional starter templates beyond the scaffolder prompts: `plugin` (for plugin authors), `with-cloudflare-d1` (Workers + D1), `with-vercel-*`, and the experimental `blank-tanstack`.

Non-interactive form (CI-friendly):
```bash
pnpm create payload-app@latest my-app \
  --template blank \
  --db postgres \
  --no-deps=false \
  --use-pnpm
```

The scaffolder writes:
- `src/app/(frontend)/` — your public Next.js frontend.
- `src/app/(payload)/` — the Payload admin panel at `/admin`.
- `src/payload.config.ts` — central Payload configuration.
- `src/collections/Users.ts`, `src/collections/Media.ts` — starter collections.
- `.env` — `PAYLOAD_SECRET` and `DATABASE_URI` placeholders.

## 3. Set environment variables

Open the generated `.env` and replace placeholders:

```bash
# .env
PAYLOAD_SECRET=replace-with-a-long-random-string-min-32-chars
DATABASE_URI=postgres://user:pass@localhost:5432/mydb
# For MongoDB:
# DATABASE_URI=mongodb://127.0.0.1/my-app
# For SQLite:
# DATABASE_URI=file:./payload.db
```

**Generate `PAYLOAD_SECRET`** — never commit a real one:
```bash
openssl rand -hex 32
```

The secret signs JWTs, password reset tokens, and version drafts. Rotating it logs every user out. Keep `.env` out of git (the scaffolder already adds it to `.gitignore`).

## 4. Inspect `payload.config.ts`

The minimal config the scaffolder produces:

```ts
import { buildConfig } from 'payload'
import { postgresAdapter } from '@payloadcms/db-postgres'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import path from 'path'
import { fileURLToPath } from 'url'
import { Users } from './collections/Users'
import { Media } from './collections/Media'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: {
    user: Users.slug,
    importMap: {
      baseDir: path.resolve(dirname),
    },
  },
  collections: [Users, Media],
  editor: lexicalEditor(),
  secret: process.env.PAYLOAD_SECRET || '',
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
  db: postgresAdapter({
    pool: { connectionString: process.env.DATABASE_URI || '' },
  }),
})
```

Key fields:
- `admin.user` — slug of the auth collection used to sign into `/admin`. Usually `users`.
- `admin.importMap.baseDir` — Payload's compile target for custom components. Must point at `src/`.
- `collections` — array of imported collection configs.
- `editor` — default rich text editor for every `richText` field. `lexicalEditor()` is the default and recommended editor; the legacy Slate adapter (`@payloadcms/richtext-slate`) exists only for v2 migration.
- `secret` — read from `process.env.PAYLOAD_SECRET`.
- `typescript.outputFile` — where to emit generated types. Re-run `pnpm generate:types` after editing collections.
- `db` — database adapter. Swap `postgresAdapter` for `mongooseAdapter` / `sqliteAdapter` if you picked a different DB.

## 5. Run the dev server

```bash
pnpm dev
```

Visit:
- `http://localhost:3000` — your Next.js frontend.
- `http://localhost:3000/admin` — Payload admin. First request shows the **"Create first user"** form. Fill it in to create the initial admin account.

If the admin panel hangs or shows database errors, run the diagnostics from the `troubleshoot` skill.

## 6. Generate TypeScript types

Every time you change a collection or field, regenerate types:

```bash
pnpm generate:types
```

This writes `src/payload-types.ts`. Import generated types in app code:

```ts
import type { User, Media, Post } from '@/payload-types'
```

Set up a watch task (optional):
```json
// package.json
{
  "scripts": {
    "generate:types": "payload generate:types",
    "generate:importmap": "payload generate:importmap"
  }
}
```

## 7. Generate the import map

When you reference custom React components (custom fields, custom views, custom admin components) by string path in `payload.config.ts`, Payload needs an import map so Next.js can resolve them at build time. Regenerate it after adding any custom component:

```bash
pnpm payload generate:importmap
```

The output lives in `src/app/(payload)/admin/importMap.js`. Commit it.

## What this skill does NOT cover

- **Designing collections** — see the `collections` skill.
- **Picking field types** — see the `fields` skill.
- **Database adapter deep dives, transactions, storage adapters** — see the `adapters` skill.
- **Migrating from another CMS** — see the `cms-migration` skill.
- **Common errors during install** — see the `troubleshoot` skill.

After `pnpm dev` succeeds and you can log into `/admin`, the next likely step is designing your first content collection — invoke the `collections` skill.
