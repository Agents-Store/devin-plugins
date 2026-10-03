# Context7 MCP Tools (2 tools)

Context7 provides **up-to-date documentation** for programming libraries and frameworks. Essential for finding current API references when building apps.

## resolve-library-id
Resolve a package/product name to a Context7-compatible library ID. Always call this first before querying docs, unless the user already gave an ID in `/org/project` or `/org/project/version` form.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | What you want to look up in the docs — used to rank the candidate libraries |
| `libraryName` | string | Yes | Official library name **with proper punctuation**: `Next.js` (not `nextjs`), `Three.js`, `Customer.io` |

```
Tool: resolve-library-id
Input: { "query": "server actions with form validation", "libraryName": "Next.js" }
```

Returns candidates (library ID, description, snippet count, source reputation, benchmark score, available versions); pick by name match, reputation and snippet coverage. A library ID such as `/vercel/next.js` goes to `query-docs`; for a specific version use `/org/project/version` from the returned version list. Do not call this tool more than 3 times per question — if nothing fits, use the best result you have. Never put secrets or proprietary code in `query` — it is sent to the Context7 API.

## query-docs
Query documentation for a specific library. Returns relevant documentation sections. (Replaces the older `get-library-docs` tool.) Keep each query to one concept — make a separate call per concept — and do not call it more than 3 times per question.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `libraryId` | string | Yes | Library ID from resolve step (format: `/org/project`) |
| `query` | string | Yes | Natural-language question scoped to one concept (specific: "React useEffect cleanup examples", not "hooks") |

```
Tool: query-docs
Input: {
  "libraryId": "/vercel/next.js",
  "query": "How to implement server actions with form validation"
}
```

## Typical Workflow

```
Step 1 — Resolve library name:
Tool: resolve-library-id
Input: { "query": "many-to-many relations", "libraryName": "Prisma" }
→ Returns: "/prisma/prisma"

Step 2 — Query docs:
Tool: query-docs
Input: {
  "libraryId": "/prisma/prisma",
  "query": "How to set up many-to-many relations"
}
→ Returns: relevant documentation sections with code examples
```

## When to Use Context7

- **Bug fixing**: search for current API signatures when something changed between versions
- **Feature implementation**: find up-to-date patterns instead of relying on training data
- **Migration**: check new API when upgrading a framework
- **Verification**: confirm a code pattern is correct for the current version

## Supported Libraries

Context7 covers most popular programming libraries and frameworks. If `resolve-library-id` returns a result, the library is supported. Common examples:

- **Frontend**: React, Next.js, Vue, Svelte, Angular, Solid
- **Backend**: Express, Fastify, NestJS, Hono, Django, FastAPI, Rails
- **Database**: Prisma, Drizzle, TypeORM, Sequelize, Mongoose
- **Styling**: Tailwind CSS, shadcn/ui, Chakra UI
- **Testing**: Jest, Vitest, Playwright, Cypress
- **Tools**: Vite, Webpack, ESBuild, Turbopack

API key optional (context7.com/dashboard) — higher rate limits and private repos; keyless works with low limits. The bundled server passes the key as `--api-key` (which takes priority over the `CONTEXT7_API_KEY` environment variable). `@upstash/context7-mcp` 4.x needs Node.js >= 20.18.1.

## Remote MCP Alternative

Instead of the bundled npx server, connect to the hosted endpoint:

```
URL: https://mcp.context7.com/mcp
Header: Authorization: Bearer ${CONTEXT7_API_KEY}
```

Quick onboarding: `npx ctx7 setup` configures Context7 for your client interactively.
