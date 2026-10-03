# nextjs-dev (Devin plugin)

Next.js development plugin. Knowledge base for building modern Next.js 16 applications with App Router, Server/Client Components, data fetching, Cache Components, performance optimization, and the next-devtools-mcp toolchain.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (18)

- `api-design` — Next.js API design patterns for Route Handlers and Server Actions. Use when the user asks about "Route Handlers", "API routes in App Router", "Server Actions vs API routes", "input validation", "API response patterns", "streaming responses", "SSE", "webhooks in Next.js", "CORS", "API versioning", or needs guidance on building APIs with Next.js.

- `api-reference` — Next.js framework API quick reference — key functions, configuration options, and TypeScript types. This skill should be used when the user asks about "Next.js API", "Next.js functions", "next.config options", "generateMetadata API", "Next.js TypeScript types", or needs a quick lookup of Next.js framework APIs.
- `app-router-patterns` — Next.js App Router patterns and file conventions. This skill should be used when the user asks about "Next.js routing", "App Router", "layouts and pages", "route groups", "parallel routes", "intercepting routes", "proxy", "metadata", "route handlers", or needs guidance on Next.js file-based routing architecture.
- `auth-patterns` — Next.js authentication and authorization patterns. Use when the user asks about "authentication in Next.js", "NextAuth.js", "Auth.js", "Better Auth", "middleware auth guards", "protected routes", "session management", "role-based access", "login page", "signup form", "JWT sessions", "cookies auth", or needs guidance on implementing auth in App Router applications.

- `cli-recipes` — Next.js CLI commands and common development scripts. This skill should be used when the user asks about "Next.js CLI", "next dev command", "next build", "create-next-app", "Turbopack", "Next.js command line", or needs to run Next.js commands from the terminal.
- `data-fetching` — Next.js data fetching, caching, and mutation patterns. This skill should be used when the user asks about "data fetching in Next.js", "Server Actions", "server-side data fetching", "caching strategies", "'use cache' directive", "revalidation", "ISR", "streaming with Suspense", "fetch in Server Components", or needs guidance on how to load and mutate data in Next.js App Router.
- `docker-patterns` — Docker configuration patterns for Next.js applications. This skill should be used when the user asks to "dockerize Next.js", "create a Dockerfile for Next.js", "set up Docker for Next.js", "docker compose for Next.js", "build Next.js with Docker", "deploy Next.js in Docker", "Next.js standalone Docker", or needs to containerize a Next.js application for development or production.

- `error-handling` — Next.js error handling patterns and error boundaries. Use when the user asks about "error.tsx", "global-error.tsx", "not-found.tsx", "error boundaries", "error handling", "loading.tsx", "loading states", "fallback UI", "error recovery", "catchError", "retry", or needs guidance on graceful error handling in App Router applications.

- `examples` — Next.js development scenario walkthroughs and code patterns. This skill should be used when the user asks for "Next.js examples", "Next.js project walkthrough", "how to build a dashboard in Next.js", "Next.js e-commerce example", "Next.js code patterns", or needs end-to-end implementation guidance for common Next.js application types.
- `form-handling` — Next.js form handling with Server Actions and validation. Use when the user asks about "forms in Next.js", "Server Action forms", "useActionState", "form validation", "Zod validation", "useFormStatus", "optimistic updates", "useOptimistic", "progressive enhancement", "file uploads", or needs guidance on building forms in App Router.

- `mcp-tools` — Next.js DevTools MCP server tools and integration patterns. This skill should be used when the user asks about "next-devtools-mcp", "Next.js MCP tools", "MCP server for Next.js", "runtime diagnostics", "Next.js dev server MCP", or needs to set up or use the official Next.js MCP toolchain for AI-assisted development.
- `performance-optimization` — Next.js performance optimization patterns for images, fonts, bundles, and Core Web Vitals. This skill should be used when the user asks about "Next.js performance", "optimize Next.js app", "Core Web Vitals", "bundle size", "next/image optimization", "next/font", "lazy loading", "dynamic imports", or needs to improve the speed and efficiency of their Next.js application.
- `project-structure` — Next.js project architecture and file organization patterns. Use when the user asks about "Next.js project structure", "folder organization", "feature-based structure", "where to put shared code", "naming conventions", "barrel exports", "modular architecture", "colocation", "route groups for organization", or needs guidance on organizing a scalable Next.js codebase.

- `security-patterns` — Next.js security best practices for production applications. Use when the user asks about "Next.js security", "CSRF protection", "CSP headers", "Content Security Policy", "XSS prevention", "environment variable safety", "server-only", "security headers", "CORS", "rate limiting", "input sanitization", or needs guidance on securing a Next.js app.

- `server-client-components` — Server and Client Component patterns in Next.js App Router. This skill should be used when the user asks about "Server Components", "Client Components", "'use client' directive", "when to use Server vs Client components", "component boundaries", "interleaving components", "context providers in Next.js", or needs guidance on the server/client rendering split.
- `setup` — Verify Next.js project environment and readiness. This skill should be used when the user asks to "verify Next.js setup", "check Next.js project", "is my Next.js app configured correctly", "test Next.js environment", or needs to confirm their project is ready for development.
- `testing-patterns` — Next.js testing patterns with Vitest and Playwright. Use when the user asks about "testing Next.js", "unit tests", "integration tests", "E2E tests", "Vitest with Next.js", "Playwright", "testing Server Components", "testing Server Actions", "testing Route Handlers", "mocking next/navigation", "mocking next/headers", or needs guidance on test setup and patterns for App Router applications.

- `troubleshoot` — Next.js common errors, debugging techniques, and solutions. This skill should be used when the user asks about "Next.js errors", "hydration error", "Next.js not working", "build errors", "debug Next.js", "'use client' errors", "deployment issues", or encounters problems during Next.js development.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/nextjs-dev
