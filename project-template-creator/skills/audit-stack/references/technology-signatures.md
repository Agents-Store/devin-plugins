# Technology Detection Signatures

How to detect technologies in a project. Scan these sources in order.

---

## 1. Package Manifest Detection

### Node.js — package.json `dependencies` / `devDependencies`

| Package | Technology | Layer |
|---------|-----------|-------|
| `next` | Next.js | Logic, Interface |
| `nuxt` | Nuxt | Logic, Interface |
| `@sveltejs/kit` | SvelteKit | Logic, Interface |
| `remix` / `@remix-run/node` | Remix | Logic, Interface |
| `react` | React | Interface |
| `react-dom` | React | Interface |
| `vue` | Vue | Interface |
| `svelte` | Svelte | Interface |
| `@angular/core` | Angular | Interface |
| `solid-js` | SolidJS | Interface |
| `express` | Express | Logic |
| `fastify` | Fastify | Logic |
| `hono` | Hono | Logic |
| `@nestjs/core` | NestJS | Logic |
| `koa` | Koa | Logic |
| `tailwindcss` | Tailwind CSS | Interface |
| `@radix-ui/*` | Radix UI | Interface |
| `@shadcn/ui` / presence of `components/ui/` | shadcn/ui | Interface |
| `@mui/material` | MUI (Material UI) | Interface |
| `@headlessui/react` | Headless UI | Interface |
| `antd` | Ant Design | Interface |
| `@chakra-ui/react` | Chakra UI | Interface |
| `styled-components` | styled-components | Interface |
| `@emotion/react` | Emotion | Interface |
| `prisma` / `@prisma/client` | Prisma | Data |
| `drizzle-orm` | Drizzle ORM | Data |
| `typeorm` | TypeORM | Data |
| `sequelize` | Sequelize | Data |
| `mongoose` | Mongoose (MongoDB) | Data |
| `@directus/sdk` | Directus SDK | Data |
| `nocodb-sdk` | NocoDB SDK | Data |
| `@supabase/supabase-js` | Supabase | Data |
| `firebase` / `firebase-admin` | Firebase | Data |
| `@appwrite.io/sdk` | Appwrite | Data |
| `redis` / `ioredis` | Redis | Data |
| `bullmq` | BullMQ | Logic |
| `@trigger.dev/sdk` | Trigger.dev | Logic |
| `inngest` | Inngest | Logic |
| `next-auth` / `@auth/core` | NextAuth / Auth.js | Logic |
| `better-auth` | Better Auth | Logic |
| `lucia` / `lucia-auth` | Lucia Auth | Logic |
| `@clerk/nextjs` | Clerk | Logic |
| `stripe` | Stripe | Logic |
| `@sanity/client` | Sanity | Data |
| `contentful` | Contentful | Data |
| `@trpc/server` | tRPC | Logic |
| `graphql` / `@apollo/server` | GraphQL / Apollo | Logic |
| `socket.io` | Socket.IO | Logic |
| `zod` | Zod | Logic |
| `@tanstack/react-query` | TanStack Query | Interface |
| `swr` | SWR | Interface |
| `zustand` | Zustand | Interface |
| `@reduxjs/toolkit` | Redux Toolkit | Interface |
| `vite` | Vite | Interface |
| `webpack` | Webpack | Interface |
| `esbuild` | esbuild | Logic |
| `turbo` | Turborepo | Logic |
| `jest` | Jest | Logic |
| `vitest` | Vitest | Logic |
| `playwright` | Playwright | Logic |
| `cypress` | Cypress | Logic |
| `storybook` | Storybook | Interface |
| `@sentry/node` / `@sentry/nextjs` | Sentry | Logic |
| `pino` / `winston` | Logging (Pino/Winston) | Logic |
| `nodemailer` / `@sendgrid/mail` | Email (Nodemailer/SendGrid) | Logic |
| `amqplib` | RabbitMQ | Data |
| `kafkajs` | Kafka | Data |
| `nats` | NATS | Data |
| `minio` | MinIO | Data |
| `@aws-sdk/client-s3` | AWS S3 | Data |
| `@qdrant/js-client-rest` | Qdrant | Data |
| `@pinecone-database/pinecone` | Pinecone | Data |
| `chromadb` | ChromaDB | Data |
| `weaviate-ts-client` | Weaviate | Data |
| `pg` / `postgres` | PostgreSQL (driver) | Data |
| `mysql2` | MySQL | Data |
| `better-sqlite3` | SQLite | Data |
| `@anthropic-ai/sdk` | Anthropic Claude API | Logic |
| `openai` | OpenAI API | Logic |
| `langchain` / `@langchain/core` | LangChain | Logic |
| `ai` / `@ai-sdk/core` | Vercel AI SDK | Logic |

### Python — requirements.txt / pyproject.toml / Pipfile

| Package | Technology | Layer |
|---------|-----------|-------|
| `django` | Django | Logic, Interface |
| `flask` | Flask | Logic |
| `fastapi` | FastAPI | Logic |
| `uvicorn` | Uvicorn | Logic |
| `sqlalchemy` | SQLAlchemy | Data |
| `alembic` | Alembic (migrations) | Data |
| `celery` | Celery | Logic |
| `redis` | Redis (Python) | Data |
| `psycopg2` / `asyncpg` | PostgreSQL (Python) | Data |
| `pymongo` | MongoDB (Python) | Data |
| `pydantic` | Pydantic | Logic |
| `httpx` / `requests` | HTTP client | Logic |
| `pytest` | Pytest | Logic |
| `langchain` | LangChain | Logic |
| `anthropic` | Anthropic Claude API | Logic |
| `openai` | OpenAI API | Logic |
| `streamlit` | Streamlit | Interface |
| `gradio` | Gradio | Interface |
| `jinja2` | Jinja2 | Interface |

### Go — go.mod

| Module | Technology | Layer |
|--------|-----------|-------|
| `github.com/gin-gonic/gin` | Gin | Logic |
| `github.com/gofiber/fiber` | Fiber | Logic |
| `github.com/labstack/echo` | Echo | Logic |
| `gorm.io/gorm` | GORM | Data |
| `github.com/jackc/pgx` | PostgreSQL (Go) | Data |
| `github.com/redis/go-redis` | Redis (Go) | Data |

### Rust — Cargo.toml

| Crate | Technology | Layer |
|-------|-----------|-------|
| `actix-web` | Actix Web | Logic |
| `axum` | Axum | Logic |
| `rocket` | Rocket | Logic |
| `diesel` | Diesel ORM | Data |
| `sqlx` | SQLx | Data |
| `tokio` | Tokio | Logic |
| `leptos` | Leptos | Logic, Interface |
| `yew` | Yew | Interface |

### Ruby — Gemfile

| Gem | Technology | Layer |
|-----|-----------|-------|
| `rails` | Ruby on Rails | Logic, Interface |
| `sinatra` | Sinatra | Logic |
| `pg` | PostgreSQL (Ruby) | Data |
| `redis` | Redis (Ruby) | Data |
| `sidekiq` | Sidekiq | Logic |

### PHP — composer.json

| Package | Technology | Layer |
|---------|-----------|-------|
| `laravel/framework` | Laravel | Logic, Interface |
| `symfony/*` | Symfony | Logic |
| `doctrine/orm` | Doctrine ORM | Data |

### Java/Kotlin — build.gradle / pom.xml

| Dependency | Technology | Layer |
|-----------|-----------|-------|
| `org.springframework.boot` | Spring Boot | Logic |
| `io.quarkus` | Quarkus | Logic |
| `org.jetbrains.exposed` | Exposed (Kotlin) | Data |

---

## 2. Configuration File Detection

| File Pattern | Technology | Layer |
|-------------|-----------|-------|
| `next.config.*` | Next.js | Logic, Interface |
| `nuxt.config.*` | Nuxt | Logic, Interface |
| `svelte.config.*` | SvelteKit | Logic, Interface |
| `angular.json` | Angular | Interface |
| `vue.config.*` / `vite.config.*` + vue | Vue | Interface |
| `remix.config.*` | Remix | Logic, Interface |
| `astro.config.*` | Astro | Interface |
| `gatsby-config.*` | Gatsby | Interface |
| `tailwind.config.*` | Tailwind CSS | Interface |
| `postcss.config.*` | PostCSS | Interface |
| `tsconfig.json` | TypeScript | Logic |
| `vite.config.*` | Vite | Interface |
| `webpack.config.*` | Webpack | Interface |
| `turbo.json` | Turborepo | Logic |
| `nx.json` | Nx | Logic |
| `prisma/schema.prisma` | Prisma | Data |
| `drizzle.config.*` | Drizzle ORM | Data |
| `trigger.config.*` | Trigger.dev | Logic |
| `.env.example` / `.env.local` | Environment config | — |
| `.mcp.json` | MCP server integration | — |
| `docker-compose.yml` / `docker-compose.yaml` | Docker Compose | — |
| `Dockerfile` / `Dockerfile.*` | Docker | — |
| `.github/workflows/*.yml` | GitHub Actions CI/CD | — |
| `vercel.json` | Vercel | Logic |
| `netlify.toml` | Netlify | Logic |
| `fly.toml` | Fly.io | Logic |
| `railway.json` / `railway.toml` | Railway | Logic |
| `terraform/*.tf` | Terraform | — |
| `k8s/` / `kubernetes/` | Kubernetes | — |
| `.storybook/` | Storybook | Interface |
| `jest.config.*` | Jest | Logic |
| `vitest.config.*` | Vitest | Logic |
| `playwright.config.*` | Playwright | Logic |
| `cypress.config.*` | Cypress | Logic |
| `eslint.config.*` / `.eslintrc.*` | ESLint | — |
| `prettier.config.*` / `.prettierrc` | Prettier | — |
| `sentry.*.config.*` | Sentry | Logic |
| `.sentryclirc` | Sentry CLI | Logic |

---

## 3. Docker Compose Service Detection

Parse `docker-compose.yml` for `image:` or `build:` directives:

| Image Pattern | Technology | Layer |
|--------------|-----------|-------|
| `postgres:*` / `postgis:*` | PostgreSQL | Data |
| `mysql:*` / `mariadb:*` | MySQL/MariaDB | Data |
| `mongo:*` | MongoDB | Data |
| `redis:*` / `valkey:*` | Redis/Valkey | Data |
| `rabbitmq:*` | RabbitMQ | Data |
| `confluentinc/cp-kafka:*` / `bitnami/kafka:*` | Kafka | Data |
| `nats:*` | NATS | Data |
| `elasticsearch:*` / `opensearchproject/*` | Elasticsearch/OpenSearch | Data |
| `meilisearch:*` | Meilisearch | Data |
| `typesense:*` | Typesense | Data |
| `minio:*` | MinIO | Data |
| `qdrant/qdrant:*` | Qdrant | Data |
| `chromadb/chroma:*` | ChromaDB | Data |
| `directus/directus:*` | Directus | Data |
| `nocodb/nocodb:*` | NocoDB | Data |
| `nocobase/nocobase:*` | NocoBase | Data |
| `supabase/*` | Supabase | Data |
| `n8nio/n8n:*` | n8n | Logic |
| `nginx:*` / `traefik:*` / `caddy:*` | Reverse Proxy | Logic |
| `grafana/grafana:*` | Grafana | Interface |
| `prom/prometheus:*` | Prometheus | Logic |
| `henrygd/beszel:*` | Beszel | Logic |
| `mailhog/*` / `mailpit/*` | Mail testing | Logic |

---

## 4. Import Pattern Detection

Grep source files (`src/**/*.{ts,tsx,js,jsx,py,go,rs}`) for distinctive imports:

| Pattern (regex) | Technology |
|----------------|-----------|
| `from ['"]@directus/sdk['"]` | Directus SDK |
| `from ['"]nocodb-sdk['"]` | NocoDB SDK |
| `from ['"]@supabase/` | Supabase |
| `from ['"]firebase/` / `from ['"]firebase-admin` | Firebase |
| `from ['"]@clerk/` | Clerk |
| `from ['"]better-auth` | Better Auth |
| `from ['"]@trigger\.dev/` | Trigger.dev |
| `from ['"]@anthropic-ai/sdk['"]` | Anthropic API |
| `from ['"]openai['"]` | OpenAI API |
| `from ['"]@langchain/` | LangChain |
| `from ['"]@trpc/` | tRPC |
| `from ['"]@tanstack/` | TanStack |
| `from ['"]next-auth` / `from ['"]@auth/` | Auth.js |
| `from ['"]@sentry/` | Sentry |
| `from ['"]@stripe/` / `from ['"]stripe['"]` | Stripe |

---

## 5. Directory Structure Signals

| Directory/File | Technology Signal |
|---------------|-----------------|
| `src/app/` + `layout.tsx` | Next.js App Router |
| `src/pages/` + `_app.tsx` | Next.js Pages Router |
| `pages/` + `_app.vue` | Nuxt 2 |
| `app/` + `app.vue` | Nuxt 3 |
| `src/routes/` + `+page.svelte` | SvelteKit |
| `components/ui/` | shadcn/ui |
| `prisma/` | Prisma |
| `drizzle/` | Drizzle |
| `supabase/` | Supabase |
| `terraform/` / `*.tf` | Terraform |
| `k8s/` / `kubernetes/` / `helm/` | Kubernetes |
| `.github/workflows/` | GitHub Actions |
| `trigger/` / `src/trigger/` | Trigger.dev |
| `jobs/` + trigger imports | Trigger.dev |
