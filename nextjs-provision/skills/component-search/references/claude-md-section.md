## Component & Template Search

When creating UI — ALWAYS search for existing components before building from scratch.

### How to search
The official `shadcn` MCP server is configured. It searches across all registries listed in components.json (populate them with the registries from the official directory — skip `unavailable` and hidden ones). Without the MCP use the CLI: `npx shadcn@latest search @registry -q "<term>"` and `npx shadcn@latest view @registry/item`.

### How to install
- Official components: `npx shadcn@latest add [component]` (forms: `field` + React Hook Form; date picker: `popover` + `calendar` — there are no `form` or `date-picker` items)
- From any registry: `npx shadcn@latest add @[registry]/[component]`
- From a GitHub repo: `npx shadcn@latest add <user>/<repo>/<item>`

### Key registries by category

**Animated components & effects:**
- @magicui, @aceternity (degraded), @animate-ui, @cult-ui, @motion-primitives

**Extra UI components:**
- @coss (ex-Origin UI), @diceui, @basecn, @8bitcn, @boldkit, @8starlabs-ui, @cardcn

**Blocks & sections (marketing, landing pages, dashboards):**
- @bundui, @blocks-so, @efferd (degraded)

**E-commerce:**
- @commercn

**AI components:**
- @ai-elements, @assistant-ui, @tool-ui

**Editors & kits:**
- @plate, @kibo-ui, @kokonutui, @reui

**File upload:**
- @better-upload

Full list: https://ui.shadcn.com/docs/directory

### Workflow
1. User asks for a page/template/component
2. Search via MCP for existing components and blocks across all registries
3. If found — install via `npx shadcn@latest add @registry/component`
4. If not found — build from shadcn/ui primitives + Tailwind CSS
5. Always prefer existing components over building from scratch
