---
name: plugin-development
description: This skill should be used when the user asks to "build a Payload plugin", "create payload-plugin package", "write a Payload plugin from scratch", "add fields via plugin", "preserve hooks in plugin", "publish payload-plugin to npm", "plugin architecture in Payload", or needs to author or maintain a reusable PayloadCMS plugin.
---

# PayloadCMS — Plugin Development

The official `templates/plugin` starter in the payloadcms/payload repo is the canonical scaffold for `payload-plugin-*` packages — clone it to start with build config, dev app, and tests pre-wired.

A Payload plugin is a curried function that takes user options and returns a config transformer:

```ts
type Plugin = (incomingConfig: Config) => Config
type PluginFactory<O> = (options: O) => Plugin

export const myPlugin: PluginFactory<MyOptions> = (options) => (config) => {
  // mutate or return a new config
  return { ...config /* … */ }
}
```

User wires it up:
```ts
import { myPlugin } from 'payload-plugin-my-thing'

export default buildConfig({
  // …
  plugins: [
    myPlugin({ collections: ['posts'], featureFlag: true }),
  ],
})
```

Plugins run **in order** during config sanitization. They can:
- Add or modify collections, globals, fields.
- Inject hooks (always **append**, never replace).
- Register endpoints, custom components, jobs, email handlers.
- Register their own admin views.

## Minimal Plugin

```ts
// src/plugin.ts
import type { Config } from 'payload'

export interface MyPluginConfig {
  /** Collections to enable plugin for */
  collections?: string[]
  /** Disable without uninstalling */
  disabled?: boolean
}

export const myPlugin =
  (options: MyPluginConfig) =>
  (config: Config): Config => {
    if (options.disabled) return config

    return {
      ...config,
      collections: config.collections?.map((collection) => {
        if (!options.collections?.includes(collection.slug)) return collection
        return {
          ...collection,
          fields: [
            ...(collection.fields ?? []),
            {
              name: 'pluginField',
              type: 'text',
              admin: { description: 'Added by my-plugin' },
            },
          ],
        }
      }),
    }
  }
```

## Adding Hooks (Without Stomping)

Hooks are arrays. Spread the existing ones and append yours:

```ts
collections: config.collections?.map((collection) => ({
  ...collection,
  hooks: {
    ...collection.hooks,
    afterChange: [
      ...(collection.hooks?.afterChange ?? []),
      myAfterChangeHook,
    ],
    beforeDelete: [
      ...(collection.hooks?.beforeDelete ?? []),
      myBeforeDeleteHook,
    ],
  },
})),
```

**Never replace** the array — you'd destroy user hooks and other plugins' hooks. Same rule for `access`, `endpoints`, `admin.components`.

## Adding Root Endpoints

```ts
return {
  ...config,
  endpoints: [
    ...(config.endpoints ?? []),
    {
      path: '/my-plugin/healthcheck',
      method: 'get',
      handler: (req) => Response.json({ ok: true }),
    },
  ],
}
```

Mounted at `/api/my-plugin/healthcheck`.

## Adding Admin Components

Components are referenced by import-map path strings:

```ts
return {
  ...config,
  admin: {
    ...config.admin,
    components: {
      ...config.admin?.components,
      beforeDashboard: [
        ...(config.admin?.components?.beforeDashboard ?? []),
        'payload-plugin-my-thing/rsc#WelcomeBanner',
        'payload-plugin-my-thing/client#StatsClient',
      ],
    },
  },
}
```

Expose those components in your package's `package.json` `exports`:

```json
{
  "exports": {
    ".":        { "import": "./dist/index.js", "types": "./dist/index.d.ts" },
    "./rsc":    { "import": "./dist/rsc.js",   "types": "./dist/rsc.d.ts" },
    "./client": { "import": "./dist/client.js","types": "./dist/client.d.ts" },
    "./types":  { "types": "./dist/types.d.ts" }
  }
}
```

## Adding Collections

```ts
return {
  ...config,
  collections: [
    ...(config.collections ?? []),
    {
      slug: 'my-plugin-records',
      admin: { group: 'My Plugin' },
      fields: [{ name: 'label', type: 'text' }],
    },
  ],
}
```

Always namespace your slugs (`my-plugin-records`) so they can't collide with user collections.

## Adding Jobs / Tasks

```ts
return {
  ...config,
  jobs: {
    ...config.jobs,
    tasks: [
      ...(config.jobs?.tasks ?? []),
      myBackgroundTask,
    ],
  },
}
```

## Package Structure (production-grade)

```txt
payload-plugin-my-thing/
├── src/
│   ├── index.ts                 # Main entry — exports plugin factory
│   ├── plugin.ts                # Implementation
│   ├── types.ts                 # PublicAPI types
│   ├── exports/
│   │   ├── client.ts            # 'use client' barrel
│   │   └── rsc.ts               # Server components barrel
│   ├── components/
│   │   ├── WelcomeBanner.tsx    # RSC
│   │   └── StatsClient.tsx      # 'use client'
│   ├── endpoints/
│   │   └── healthcheck.ts
│   ├── fields/
│   │   └── pluginField.ts
│   └── hooks/
│       └── afterChange.ts
├── dev/                          # A real Payload app for development
│   ├── payload.config.ts        # Imports plugin via 'workspace:*' or relative
│   ├── package.json
│   └── int.spec.ts              # Integration tests (Vitest)
├── .swcrc
├── tsconfig.json
├── vitest.config.ts
├── playwright.config.ts          # If you ship admin UI
├── package.json
└── README.md
```

### package.json

```json
{
  "name": "payload-plugin-my-thing",
  "version": "0.1.0",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".":        { "import": "./dist/index.js", "types": "./dist/index.d.ts" },
    "./client": { "import": "./dist/exports/client.js", "types": "./dist/exports/client.d.ts" },
    "./rsc":    { "import": "./dist/exports/rsc.js",    "types": "./dist/exports/rsc.d.ts" }
  },
  "files": ["dist"],
  "scripts": {
    "build": "pnpm clean && pnpm build:types && pnpm build:swc",
    "build:swc": "swc ./src -d ./dist --strip-leading-paths",
    "build:types": "tsc --emitDeclarationOnly --outDir ./dist",
    "clean": "rm -rf dist",
    "dev": "cd dev && pnpm dev",
    "test:int": "vitest run",
    "test:e2e": "playwright test",
    "prepublishOnly": "pnpm clean && pnpm build"
  },
  "peerDependencies": {
    "payload": "^3.0.0"
  },
  "devDependencies": {
    "@swc/cli": "^0.5.0",
    "@swc/core": "^1.7.0",
    "payload": "^3.0.0",
    "typescript": "^5.5.0"
  }
}
```

### .swcrc

```json
{
  "$schema": "https://json.schemastore.org/swcrc",
  "jsc": {
    "target": "es2022",
    "parser": { "syntax": "typescript", "tsx": true, "decorators": true },
    "transform": { "react": { "runtime": "automatic" } }
  },
  "module": { "type": "es6" }
}
```

### Why SWC + tsc?

- **SWC** compiles fast and outputs runnable JS.
- **tsc --emitDeclarationOnly** writes `.d.ts` files but skips JS emit.
- Run both for a clean dist/ with both types and code.

## Local Development with `dev/`

The `dev/` folder is a fully functional Payload app that imports your plugin:

```ts
// dev/payload.config.ts
import { myPlugin } from '../src'
import { postgresAdapter } from '@payloadcms/db-postgres'

export default buildConfig({
  // …
  plugins: [myPlugin({ collections: ['posts'] })],
  db: postgresAdapter({ pool: { connectionString: process.env.DATABASE_URI } }),
})
```

Run `pnpm --filter dev dev` to start a real admin UI against your local plugin code.

## Testing

### Integration (Vitest)

```ts
// dev/int.spec.ts
import { getPayload, type Payload } from 'payload'
import { describe, it, expect, beforeAll } from 'vitest'
import config from './payload.config'

let payload: Payload

beforeAll(async () => {
  payload = await getPayload({ config })
})

describe('plugin field is added', () => {
  it('exists on the posts collection', () => {
    const posts = payload.collections.posts.config.fields
    expect(posts.some((f) => 'name' in f && f.name === 'pluginField')).toBe(true)
  })

  it('persists data', async () => {
    const created = await payload.create({
      collection: 'posts',
      data: { title: 't', pluginField: 'v' },
    })
    expect(created.pluginField).toBe('v')
  })
})
```

### E2E (Playwright)

If your plugin renders admin components, run Playwright against `dev/`:
```bash
pnpm --filter dev dev &
pnpm test:e2e
```

## Options Patterns

### Per-collection overrides

```ts
type CollectionOptions = boolean | {
  fields?: Field[]
  hooks?: CollectionConfig['hooks']
}

interface MyPluginConfig {
  collections?: Record<string, CollectionOptions>
}

// usage:
myPlugin({
  collections: {
    posts: true,
    pages: { fields: [/* extra fields */] },
  },
})
```

### Disable without uninstall

```ts
if (options.disabled) {
  // Keep DB schema (don't strip fields) but skip side effects
  return config
}
```

This is the convention: never silently drop fields when disabled, otherwise users lose data.

### Conditional behavior per environment

```ts
if (process.env.NODE_ENV === 'production') {
  // Only attach prod-only endpoints
}
```

## Publishing

```bash
pnpm changeset                    # If using changesets
pnpm build
npm publish --access public
```

Suggest `payload-plugin-<slug>` naming so users can `pnpm add payload-plugin-stripe`.

Tag the GitHub release with the version, attach a CHANGELOG, link the plugin in the Payload community list (`payloadcms/payload-plugins`).

## See Also

- The `hooks` skill — patterns to wrap when injecting hooks.
- The `fields` skill — field type guards for safely modifying user fields.
- The `nextjs-integration` skill — components must be RSC- or client-explicit.
- Real-world plugins to study: `@payloadcms/plugin-seo`, `@payloadcms/plugin-nested-docs`, `@payloadcms/plugin-form-builder`, `@payloadcms/plugin-search`, `@payloadcms/plugin-stripe`, `@payloadcms/plugin-multi-tenant`.
