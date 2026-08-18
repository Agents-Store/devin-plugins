# Context7 MCP Tools (2 tools)

Context7 provides **up-to-date documentation** for programming libraries and frameworks. Essential for finding current API references when building apps.

## resolve-library-id
Resolve a package/product name to a Context7-compatible library ID. Always call this first before querying docs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `libraryName` | string | Yes | Package or framework name (e.g., "react", "nextjs", "prisma") |

```
Tool: resolve-library-id
Input: { "libraryName": "nextjs" }
```

Returns a library ID like `/vercel/next.js` that you pass to `query-docs`.

## query-docs
Query documentation for a specific library. Returns relevant documentation sections. (Replaces the older `get-library-docs` tool.)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `libraryId` | string | Yes | Library ID from resolve step (format: `/org/project`) |
| `query` | string | Yes | Natural language question about the library |

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
Input: { "libraryName": "prisma" }
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

API key optional (context7.com/dashboard) — higher rate limits and private repos; keyless works with low limits.

## Remote MCP Alternative

Instead of the bundled npx server, connect to the hosted endpoint:

```
URL: https://mcp.context7.com/mcp
Header: Authorization: Bearer ${CONTEXT7_API_KEY}
```

Quick onboarding: `npx ctx7 setup` configures Context7 for your client interactively.
