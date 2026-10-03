# stack-directus-nextjs-trigger (Devin plugin)

Directus + Next.js + Trigger.dev architecture plugin. How Directus (content, files, access), a Next.js App Router frontend and self-hosted Trigger.dev (durable and scheduled work) fit together: who holds which token, how the cache is invalidated, how a Directus change reaches a task and the result reaches the page, who owns the session, and a production checklist. Tool knowledge comes from its dependencies.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (8)

- `authentication` — This skill should be used when the user wants to "add authentication to Directus + Next.js", "implement Directus login in Next.js", "use NextAuth with Directus", "use Better Auth with Directus", "protect Next.js pages with Directus auth", "choose an auth approach for Directus and Next.js", "decide who owns the session", "act as the signed-in user inside a trigger.dev task", or needs to decide who owns the end-user session and the tokens across Directus and Next.js.
- `background-tasks` — This skill should be used when the user wants to "offload work to trigger.dev from next.js", "run a background job from a server action", "trigger a task from a route handler", "delegate slow work to trigger.dev", "decide what runs in a Server Action and what in a task", "show a task's progress in next.js", "give the browser a token for a trigger.dev run", "keep task environment variables apart from next.js", "fix a TRIGGER_SECRET_KEY build error", or needs the rules where a Next.js App Router app hands work to Trigger.dev and gets the result back.
- `deployment` — This skill should be used when the user wants to "run the Directus Next.js Trigger.dev stack locally", "deploy trigger.dev tasks next to a Next.js app", "set environment variables for trigger.dev tasks", "configure content-change webhooks with trigger.dev", "revalidate the site when a task changes Directus content", "CI/CD for trigger tasks", "production checklist for directus + nextjs + trigger.dev", or needs the pipelines that connect the three services and the checks before production. For platform-specific hosting (Vercel, Dokploy, etc.), see the respective deployment plugin.
- `directus-to-nextjs` — This skill should be used when the user wants to "fetch Directus data in Next.js", "display Directus content in Next.js pages", "render Directus images in Next.js", "use Directus SDK with Server Components", "create Next.js pages from Directus collections", "add TypeScript types for Directus", "cache Directus data in Next.js", "revalidate after Directus content changes", "fix 403 on Directus images", or needs the rules where Directus data meets Next.js rendering: who holds the token, what is cached, how files are served, and how types follow the schema.
- `directus-to-trigger` — This skill should be used when the user wants to "trigger a task from a directus flow", "run a background task when a directus item is created or updated", "forward directus webhooks to trigger.dev", "process directus items asynchronously", "build a directus flow to next.js to trigger pipeline", "have a task write back to directus", "stop a directus flow and task from looping", "read and write directus from a trigger.dev task", or needs the pattern for wiring Directus Flow events through Next.js into Trigger.dev tasks and back.
- `examples` — End-to-end scenario walkthroughs for the Directus + Next.js + Trigger.dev stack. This skill should be used when the user asks for "directus nextjs trigger.dev examples", "how to build a blog with directus + next.js", "ai enrichment pipeline example", "scheduled data sync example", "show me a complete example with background tasks", or needs implementation references for common application types on this stack.
- `full-feature` — This skill should be used when the user wants to "build a complete feature with directus nextjs and trigger.dev", "create an end-to-end feature with background tasks", "implement a full crud feature with async processing", "build a new section of the site that uses background jobs", "add a page backed by directus with a background task", or needs a step-by-step recipe for building features that span Directus, Next.js, and Trigger.dev.
- `init-project` — This skill should be used when the user asks to "set up Directus + Next.js + Trigger.dev project", "initialize directus nextjs trigger.dev stack", "bootstrap the 3-service stack", "configure directus next.js and trigger.dev together", "connect trigger.dev to a directus nextjs app", "scaffold stack with background tasks", "start a new project with background jobs", or needs to set up environment variables, versions and verify connections for the Directus + Next.js + Trigger.dev stack.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/stack-directus-nextjs-trigger
