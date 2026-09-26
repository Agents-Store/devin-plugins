# Layer Classification Reference

Canonical mapping of technologies to the 3-layer model used in `stack.json`.

---

## Classification Rules

1. **Full-stack frameworks** (Next.js, Nuxt, SvelteKit, Remix, Rails, Django, Laravel, Leptos) appear in BOTH `logic` AND `interface` — they handle server routes (logic) and rendering (interface)
2. **BaaS/headless CMS** (Supabase, Firebase, Directus, NocoDB, NocoBase, Sanity, Contentful, Strapi, Appwrite) are always `data` — even if they have UI, the plugin consumer uses them as data sources
3. **ORMs and database drivers** are always `data`
4. **Auth libraries** are `logic` — they implement business logic (session management, token validation)
5. **Job runners and automation** (Trigger.dev, Inngest, BullMQ, Celery, Sidekiq, n8n) are `logic`
6. **UI component libraries** (shadcn, Radix, MUI, Ant Design, Headless UI) are `interface`
7. **CSS frameworks** (Tailwind, styled-components, Emotion) are `interface`
8. **State management** (Redux, Zustand, Pinia, SWR, TanStack Query) is `interface`
9. **Build tools** (Vite, Webpack, esbuild, Turbo) are `interface` when they serve frontend, `logic` when they build backend
10. **Infrastructure** (Docker, Terraform, Kubernetes, CI/CD) are not classified into layers — report them under "Infrastructure" separately

---

## Canonical Mapping Table

### Logic Layer

| Technology | Category | Notes |
|-----------|----------|-------|
| Next.js | Full-stack framework | Also in Interface |
| Nuxt | Full-stack framework | Also in Interface |
| SvelteKit | Full-stack framework | Also in Interface |
| Remix | Full-stack framework | Also in Interface |
| Astro | Static/hybrid framework | Also in Interface if SSR |
| Express | Backend framework | |
| Fastify | Backend framework | |
| Hono | Backend framework | |
| NestJS | Backend framework | |
| Koa | Backend framework | |
| Django | Full-stack framework | Also in Interface |
| Flask | Backend framework | |
| FastAPI | Backend framework | |
| Ruby on Rails | Full-stack framework | Also in Interface |
| Sinatra | Backend framework | |
| Laravel | Full-stack framework | Also in Interface |
| Symfony | Backend framework | |
| Spring Boot | Backend framework | |
| Gin | Backend framework | |
| Fiber | Backend framework | |
| Echo | Backend framework | |
| Actix Web | Backend framework | |
| Axum | Backend framework | |
| Leptos | Full-stack framework | Also in Interface |
| NextAuth / Auth.js | Auth | |
| Better Auth | Auth | |
| Lucia Auth | Auth | |
| Clerk | Auth | |
| Passport.js | Auth | |
| Trigger.dev | Job runner | |
| Inngest | Job runner | |
| BullMQ | Job queue | |
| Celery | Task queue | |
| Sidekiq | Job queue | |
| n8n | Workflow automation | |
| tRPC | API layer | |
| GraphQL / Apollo | API layer | |
| Socket.IO | Real-time | |
| Stripe | Payments | |
| Sentry | Monitoring | |
| Anthropic Claude API | AI/LLM | |
| OpenAI API | AI/LLM | |
| LangChain | AI orchestration | |
| Vercel AI SDK | AI/LLM | |
| Zod | Validation | |

### Interface Layer

| Technology | Category | Notes |
|-----------|----------|-------|
| Next.js | Full-stack framework | Also in Logic |
| Nuxt | Full-stack framework | Also in Logic |
| SvelteKit | Full-stack framework | Also in Logic |
| Remix | Full-stack framework | Also in Logic |
| Astro | Static/hybrid framework | |
| Gatsby | Static site generator | |
| React | Frontend framework | |
| Vue | Frontend framework | |
| Svelte | Frontend framework | |
| Angular | Frontend framework | |
| SolidJS | Frontend framework | |
| Django | Full-stack framework | Also in Logic |
| Ruby on Rails | Full-stack framework | Also in Logic |
| Laravel | Full-stack framework | Also in Logic |
| Leptos | Full-stack framework | Also in Logic |
| Yew | Frontend framework (Rust) | |
| Tailwind CSS | CSS framework | |
| styled-components | CSS-in-JS | |
| Emotion | CSS-in-JS | |
| PostCSS | CSS tooling | |
| shadcn/ui | UI component library | |
| Radix UI | UI primitives | |
| MUI (Material UI) | UI component library | |
| Ant Design | UI component library | |
| Headless UI | UI primitives | |
| Chakra UI | UI component library | |
| TanStack Query | Data fetching | |
| SWR | Data fetching | |
| Zustand | State management | |
| Redux Toolkit | State management | |
| Pinia | State management (Vue) | |
| Vite | Build tool | |
| Storybook | Component dev | |
| Streamlit | Python UI | |
| Gradio | Python UI | |
| Grafana | Dashboard UI | |

### Data Layer

| Technology | Category | Notes |
|-----------|----------|-------|
| PostgreSQL | Relational DB | |
| MySQL / MariaDB | Relational DB | |
| SQLite | Embedded DB | |
| MongoDB | Document DB | |
| DynamoDB | Key-value/document DB | |
| Prisma | ORM | |
| Drizzle ORM | ORM | |
| TypeORM | ORM | |
| Sequelize | ORM | |
| SQLAlchemy | ORM (Python) | |
| GORM | ORM (Go) | |
| Diesel | ORM (Rust) | |
| Mongoose | ODM (MongoDB) | |
| Directus | Headless CMS / BaaS | |
| NocoDB | BaaS | |
| NocoBase | BaaS | |
| Supabase | BaaS | |
| Firebase | BaaS | |
| Appwrite | BaaS | |
| Sanity | Headless CMS | |
| Contentful | Headless CMS | |
| Strapi | Headless CMS | |
| Redis / Valkey | Cache / KV store | |
| Memcached | Cache | |
| RabbitMQ | Message broker | |
| Kafka | Event streaming | |
| NATS | Message system | |
| AWS S3 | Object storage | |
| MinIO | Object storage | |
| Cloudflare R2 | Object storage | |
| Qdrant | Vector DB | |
| Pinecone | Vector DB | |
| ChromaDB | Vector DB | |
| Weaviate | Vector DB | |
| pgvector | Vector extension (PG) | |
| Elasticsearch | Search engine | |
| OpenSearch | Search engine | |
| Meilisearch | Search engine | |
| Typesense | Search engine | |

### Infrastructure (not classified into layers)

| Technology | Category |
|-----------|----------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Kubernetes | Container orchestration |
| Terraform | Infrastructure as Code |
| GitHub Actions | CI/CD |
| Vercel | Deployment platform |
| Netlify | Deployment platform |
| Fly.io | Deployment platform |
| Railway | Deployment platform |
| Nginx / Traefik / Caddy | Reverse proxy |
| Prometheus | Monitoring |
| Beszel | Server monitoring |
| Turborepo / Nx | Monorepo tools |

---

## stack.json Layer Format

When generating `stack.json`, use lowercase identifiers:

```json
{
  "layers": {
    "data": ["postgresql", "prisma", "redis"],
    "logic": ["nextjs", "trigger-dev", "better-auth"],
    "interface": ["nextjs", "tailwindcss", "shadcn"]
  }
}
```

Naming conventions for layer values:
- Use kebab-case: `trigger-dev`, `better-auth`, `ruby-on-rails`
- Use official short names: `nextjs` (not `next.js`), `vuejs` (not `vue.js`), `tailwindcss`
- Database drivers collapse to the DB name: `pg` package -> `postgresql`
- UI library groups collapse: `@radix-ui/*` -> `radix-ui`
