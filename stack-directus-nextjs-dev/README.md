# stack-directus-nextjs-dev (Devin plugin)

Directus + Next.js stack dev plugin. Integrates Directus headless CMS with Next.js App Router for content-driven applications.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (6)

- `authentication` — This skill should be used when the user wants to "add authentication to Directus + Next.js", "implement Directus login in Next.js", "use NextAuth with Directus", "protect Next.js pages with Directus auth", "set up cookie-based auth for Directus SSR", or needs patterns for authenticating users across Directus and Next.js.
- `deployment` — This skill should be used when the user wants to "set up Docker for Directus", "run Directus locally with Docker", "configure content-change webhooks", "set up ISR revalidation with Directus", "auto-rebuild on content change", "production checklist for Directus + Next.js", or needs local dev and integration patterns for the Directus + Next.js stack. For platform-specific deployment (Vercel, Dokploy, etc.), see the respective deployment plugin.
- `directus-to-nextjs` — This skill should be used when the user wants to "fetch Directus data in Next.js", "display Directus content in Next.js pages", "render Directus images in Next.js", "use Directus SDK with Server Components", "create Next.js pages from Directus collections", "add TypeScript types for Directus", or needs integration patterns between Directus data and Next.js rendering.
- `examples` — End-to-end scenario walkthroughs for the Directus + Next.js stack. This skill should be used when the user asks for "Directus Next.js examples", "how to build a blog with Directus and Next.js", "Directus Next.js product catalog", "show me a complete example", or needs implementation references for common application types.
- `full-feature` — This skill should be used when the user wants to "build a complete feature with Directus and Next.js", "create an end-to-end page from Directus data", "implement a full CRUD feature across Directus and Next.js", "build a new section of the site", "create a page that shows Directus data", "build a dashboard with Directus content", "display Directus collection in Next.js", "add a new page with CMS data", or needs a step-by-step recipe for building features that span both Directus and Next.js.
- `init-project` — This skill should be used when the user asks to "set up Directus + Next.js project", "initialize Directus Next.js stack", "configure Directus with Next.js", "connect Directus to Next.js", "bootstrap Directus Next.js app", "create Next.js app with Directus", "scaffold Directus + Next.js", "start new project with Directus", "create a new Directus Next.js project", or needs to set up environment variables and verify connections for the Directus + Next.js stack.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/stack-directus-nextjs-dev
