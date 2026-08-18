# Stack Templates — Config File Examples

Ready-made configuration snippets for popular technology combinations. Use these as starting points when creating Level 1 templates.

## Nuxt + Supabase

### nuxt.config.ts
```typescript
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ['@nuxtjs/supabase'],
  supabase: {
    redirectOptions: {
      login: '/login',
      callback: '/confirm',
      exclude: ['/', '/about'],
    },
  },
  typescript: {
    strict: true,
  },
})
```

### .env.example
```bash
# Supabase
SUPABASE_URL=
SUPABASE_KEY=           # anon/public key
SUPABASE_SERVICE_KEY=   # service_role key (server-side only)

# Trigger.dev
TRIGGER_API_KEY=
TRIGGER_API_URL=http://localhost:3030

# App
NUXT_PUBLIC_SITE_URL=http://localhost:3000
```

### docker-compose.yml
```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
      - /app/.nuxt
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
```

---

## Next.js + Directus

### next.config.ts
```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**' },
    ],
  },
}

export default nextConfig
```

### .env.example
```bash
# Directus
NEXT_PUBLIC_DIRECTUS_URL=
DIRECTUS_ADMIN_TOKEN=

# Auth (NextAuth)
NEXTAUTH_URL=
NEXTAUTH_SECRET=

# Vercel
VERCEL_TOKEN=
VERCEL_ORG_ID=
VERCEL_PROJECT_ID=
```

### docker-compose.yml
```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
      - /app/.next
    environment:
      - NEXT_PUBLIC_DIRECTUS_URL=${NEXT_PUBLIC_DIRECTUS_URL}
      - DIRECTUS_ADMIN_TOKEN=${DIRECTUS_ADMIN_TOKEN}
      - WATCHPACK_POLLING=true  # hot-reload inside Docker
```

---

## Next.js + Supabase

### .env.example
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Auth
NEXTAUTH_URL=
NEXTAUTH_SECRET=
```

---

## NocoDB + n8n + Nuxt

### .env.example
```bash
# NocoDB
NOCODB_BASE_URL=http://localhost:8080
NOCODB_API_TOKEN=

# n8n
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=

# Trigger.dev
TRIGGER_API_KEY=
TRIGGER_API_URL=http://localhost:3030

# App
NUXT_PUBLIC_SITE_URL=http://localhost:3000
```

---

## Common Configs

### .editorconfig
```ini
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
```

### Dockerfile (Node.js)
```dockerfile
FROM node:20-alpine AS base
RUN corepack enable

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.output ./
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

### Dockerfile.dev
```dockerfile
FROM node:20-alpine
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install
COPY . .
EXPOSE 3000
CMD ["pnpm", "dev"]
```

### trigger.config.ts
```typescript
import { defineConfig } from "@trigger.dev/sdk/v3"

export default defineConfig({
  project: "<project-ref>",
  runtime: "node",
  logLevel: "log",
  retries: {
    enabledInDev: true,
    default: { maxAttempts: 3, minTimeoutInMs: 1000, maxTimeoutInMs: 10000, factor: 2 },
  },
  dirs: ["./src/trigger"],
})
```
