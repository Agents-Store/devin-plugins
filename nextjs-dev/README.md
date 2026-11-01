# nextjs-dev (Devin plugin)

Next.js development plugin. Knowledge base for building modern Next.js 16 applications with App Router, Server/Client Components, data fetching, Cache Components, performance optimization, and the next-devtools-mcp toolchain.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (18)

- `api-design` — Next.js API design patterns for Route Handlers (app/api/**/route.ts): input validation, response and error shapes, streaming and SSE, webhooks, CORS, versioning, caching GET handlers, and choosing between a Route Handler and a Server Action. Not for form handling with Server Actions (form-handling) or for fetching data in Server Components (data-fetching).

- `api-reference` — Next.js framework API quick reference — key functions, configuration options, and TypeScript types. This skill should be used when the user asks about "Next.js API", "Next.js functions", "next.config options", "generateMetadata API", "Next.js TypeScript types", or needs a quick lookup of Next.js framework APIs.
- `app-router-patterns` — Next.js 16 App Router routing conventions — layouts and templates, route groups, dynamic routes with async params and generateStaticParams, parallel routes (every slot needs default.tsx), intercepting routes for modals, proxy.ts replacing middleware.ts, and the Metadata API. Use when creating, restructuring or migrating routes. Error and loading files belong to error-handling, Route Handlers to api-design.
- `auth-patterns` — Next.js authentication and authorization patterns. Use when the user asks about "authentication in Next.js", "NextAuth.js", "Auth.js", "Better Auth", "middleware auth guards", "protected routes", "session management", "role-based access", "login page", "signup form", "JWT sessions", "cookies auth", or needs guidance on implementing auth in App Router applications.

- `cli-recipes` — Next.js 16 command-line recipes — create-next-app, next dev and next build with Turbopack as the default (--webpack to opt out), next start, the built-in bundle analyzer, next upgrade with codemods, and linting now that next lint is removed. Use when the question is which next command, flag or package script to run. Docker packaging is docker-patterns.
- `data-fetching` — Next.js 16 data fetching and caching in the App Router — Server Component fetching, parallel requests and Suspense streaming, Server Action mutations, revalidation with revalidatePath, revalidateTag, updateTag and refresh, ISR, and the use cache directive with cacheLife and cacheTag under cacheComponents. Use when loading, caching or invalidating data. Forms and validation are form-handling.
- `docker-patterns` — Docker configuration patterns for Next.js applications. This skill should be used when the user asks to "dockerize Next.js", "create a Dockerfile for Next.js", "set up Docker for Next.js", "docker compose for Next.js", "build Next.js with Docker", "deploy Next.js in Docker", "Next.js standalone Docker", or needs to containerize a Next.js application for development or production.

- `error-handling` — Next.js error handling patterns and error boundaries. Use when the user asks about "error.tsx", "global-error.tsx", "not-found.tsx", "error boundaries", "error handling", "loading.tsx", "loading states", "fallback UI", "error recovery", "catchError", "retry", or needs guidance on graceful error handling in App Router applications.

- `examples` — Next.js development scenario walkthroughs and code patterns. This skill should be used when the user asks for "Next.js examples", "Next.js project walkthrough", "how to build a dashboard in Next.js", "Next.js e-commerce example", "Next.js code patterns", or needs end-to-end implementation guidance for common Next.js application types.
- `form-handling` — Next.js forms with Server Actions — useActionState, useFormStatus, useOptimistic, zod validation with field errors, progressive enhancement, file uploads and the Form component. Use when building or fixing a form in the App Router. Choosing a Route Handler for an endpoint is api-design, refreshing data after a mutation is data-fetching.
- `mcp-tools` — Next.js DevTools MCP server tools and integration patterns. This skill should be used when the user asks about "next-devtools-mcp", "Next.js MCP tools", "MCP server for Next.js", "runtime diagnostics", "Next.js dev server MCP", or needs to set up or use the official Next.js MCP toolchain for AI-assisted development.
- `performance-optimization` — Next.js 16 performance — next/image and next/font setup, dynamic imports, bundle analysis, the React Compiler (stable in 16, experimental Rust compiler in 16.3), prefetching and Partial Prefetching, third-party scripts and Core Web Vitals (LCP, INP, CLS). Use when a page is slow or heavy. Caching strategy belongs to data-fetching.
- `project-structure` — Next.js project architecture and file organization patterns. Use when the user asks about "Next.js project structure", "folder organization", "feature-based structure", "where to put shared code", "naming conventions", "barrel exports", "modular architecture", "colocation", "route groups for organization", or needs guidance on organizing a scalable Next.js codebase.

- `security-patterns` — Next.js 16 security for production apps — security headers, nonce-based Content Security Policy in proxy.ts, CSRF and allowed origins for Server Actions, CORS for Route Handlers, rate limiting, server-only data access layers, environment variable safety, and keeping next patched against current security advisories. Use when hardening an app. Login and sessions belong to auth-patterns.
- `server-client-components` — Server and Client Components in the Next.js App Router — where to put 'use client', which props can cross the boundary, passing server components as children, context providers, wrapping third-party components, and keeping server-only code out of the client bundle with the server-only and client-only packages. Use when deciding or fixing component boundaries.
- `setup` — Verify Next.js project environment and readiness. This skill should be used when the user asks to "verify Next.js setup", "check Next.js project", "is my Next.js app configured correctly", "test Next.js environment", or needs to confirm their project is ready for development.
- `testing-patterns` — Next.js testing patterns with Vitest and Playwright. Use when the user asks about "testing Next.js", "unit tests", "integration tests", "E2E tests", "Vitest with Next.js", "Playwright", "testing Server Components", "testing Server Actions", "testing Route Handlers", "mocking next/navigation", "mocking next/headers", or needs guidance on test setup and patterns for App Router applications.

- `troubleshoot` — Diagnose Next.js 16 errors — hydration mismatches, 'use client' and server-only errors, build failures such as dynamic server usage, Cache Components errors like blocking-prerender and next-request-in-use-cache, next/image host errors, slow dev or build, and deployment problems. Use when something fails or behaves unexpectedly in a Next.js app.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/nextjs-dev
