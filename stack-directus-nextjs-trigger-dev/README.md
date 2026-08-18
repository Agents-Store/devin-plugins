# stack-directus-nextjs-trigger-dev (Devin plugin)

Directus + Next.js + Trigger.dev stack dev plugin. Adds self-hosted Trigger.dev as a workflow engine for AI agents, durable async logic, and scheduled jobs on top of the Directus + Next.js App Router stack.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (9)

- `authentication` — This skill should be used when the user wants to "add authentication to Directus + Next.js", "implement Directus login in Next.js", "use NextAuth with Directus", "protect Next.js pages with Directus auth", "set up cookie-based auth for Directus SSR", or needs patterns for authenticating users across Directus and Next.js.
- `background-tasks` — This skill should be used when the user wants to "offload work to trigger.dev from next.js", "run background job from a server action", "trigger a task from a route handler", "call tasks.trigger from next.js app router", "delegate slow work to trigger.dev", "show realtime task status in next.js", "fix force-dynamic error with trigger.dev", "handle onclick trigger.dev server action", or needs the integration patterns between Next.js (App Router) and Trigger.dev for event-driven background work.
- `deployment` — This skill should be used when the user wants to "set up Docker for Directus locally", "deploy trigger.dev tasks", "run local dev for the 3-service stack", "configure content-change webhooks with trigger.dev", "CI/CD for trigger tasks", "production checklist for directus + nextjs + trigger.dev", or needs local dev and integration deployment patterns. For platform-specific hosting (Vercel, Dokploy, etc.), see the respective deployment plugin.
- `directus-to-nextjs` — This skill should be used when the user wants to "fetch Directus data in Next.js", "display Directus content in Next.js pages", "render Directus images in Next.js", "use Directus SDK with Server Components", "create Next.js pages from Directus collections", "add TypeScript types for Directus", or needs integration patterns between Directus data and Next.js rendering.
- `directus-to-trigger` — This skill should be used when the user wants to "trigger a task from a directus flow", "run a background task when a directus item is created or updated", "forward directus webhooks to trigger.dev", "process directus items asynchronously", "build a directus automate → next.js → trigger pipeline", "have a task write back to directus after processing", or needs the pattern for wiring Directus Flow events through Next.js into Trigger.dev tasks and back.
- `examples` — End-to-end scenario walkthroughs for the Directus + Next.js + Trigger.dev stack. This skill should be used when the user asks for "directus nextjs trigger.dev examples", "how to build a blog with directus + next.js", "ai enrichment pipeline example", "scheduled data sync example", "show me a complete example with background tasks", or needs implementation references for common application types on this stack.
- `full-feature` — This skill should be used when the user wants to "build a complete feature with directus nextjs and trigger.dev", "create an end-to-end feature with background tasks", "implement a full crud feature with async processing", "build a new section of the site that uses background jobs", "add a page backed by directus with a background task", or needs a step-by-step recipe for building features that span Directus, Next.js, AND Trigger.dev.
- `init-project` — This skill should be used when the user asks to "set up Directus + Next.js + Trigger.dev project", "initialize directus nextjs trigger.dev stack", "bootstrap the 3-service stack", "configure directus next.js and trigger.dev together", "connect trigger.dev to a directus nextjs app", "scaffold stack with background tasks", "start a new project with background jobs", or needs to set up environment variables and verify connections for the Directus + Next.js + Trigger.dev stack.
- `scheduled-tasks` — This skill should be used when the user wants to "create a scheduled task with trigger.dev", "add a cron job", "run a daily task", "sync directus on a schedule", "build a cron that reads from directus", "attach a schedule to production", "timezone-aware cron", or needs patterns for defining `schedules.task()` cron jobs that interact with Directus from the Directus + Next.js + Trigger.dev stack.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/stack-directus-nextjs-trigger-dev
