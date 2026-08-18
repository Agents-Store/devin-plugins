# Community shadcn Registries

## Dynamic Source (Always Current)

The authoritative, always-up-to-date list of all shadcn-compatible registries:

```
https://ui.shadcn.com/r/registries.json
```

Returns a JSON array of 267 registries (Aug 2026). Each entry: `name`, `url`, `homepage`, `description`.

**To populate components.json with all registries**, use the `/add-registries` command — it fetches this endpoint and adds every registry automatically.

**Browse online**: https://ui.shadcn.com/docs/directory

---

## Category Guide (For Quick Reference)

The tables below organize notable registries by category. This is a curated subset — the dynamic endpoint above has the complete list.

---

## Animation & Motion

| Registry | URL | Description |
|----------|-----|-------------|
| @magicui | `https://magicui.design/r/{name}` | 50+ animated components — shimmer buttons, animated beams, globe, particles, meteors, marquee |
| @aceternity | `https://ui.aceternity.com/registry/{name}.json` | Motion-heavy effects — parallax scroll, moving border, spotlight, aurora background, 3D cards |
| @animate-ui | `https://animate-ui.com/r/{name}.json` | Smooth transition components — animated accordion, fade-in, slide, reveal effects |
| @cult-ui | `https://cult-ui.com/r/{name}.json` | Creative animations — flyout menus, hover reveals, morphing shapes |
| @motion-primitives | `https://motion-primitives.com/c/{name}.json` | Motion building blocks — transition, animate-presence, gesture primitives |
| @chamaac | `https://chamaac.com/r/{name}.json` | Animation effects — glow, ripple, magnetic cursor, tilt effects |

## Extended UI Components

| Registry | URL | Description |
|----------|-----|-------------|
| @coss | `https://coss.com/ui/r/{name}.json` | COSS UI (successor to Origin UI — originui.com now redirects to coss.com/ui) — 100+ styled component variants |
| @diceui | `https://diceui.com/r/{style}/{name}.json` | Interactive components — combobox, tags input, editable text, kanban board |
| @basecn | `https://basecn.dev/r/{name}.json` | Base component extensions — enhanced select, multi-select, command palette |
| @8bitcn | `https://www.8bitcn.com/r/{name}.json` | Retro pixel-style UI components — 8-bit buttons, pixel cards, retro badges |
| @boldkit | `https://boldkit.dev/r/{name}.json` | Bold design system — distinctive buttons, cards, layouts |
| @8starlabs-ui | `https://ui.8starlabs.com/r/{name}.json` | Additional UI components and variants |
| @cardcn | `https://cardcn.dev/r/{name}.json` | Card-focused components — pricing cards, profile cards, feature cards, stat cards |
| @unlumen-ui | `https://ui.unlumen.com/r/{name}.json` | Minimalist UI components |

## Blocks & Sections

| Registry | URL | Description |
|----------|-----|-------------|
| @bundui | `https://bundui.io/r/{name}.json` | Landing page blocks — hero sections, feature grids, pricing tables, testimonials |
| @blocks-so | `https://blocks.so/r/{name}.json` | Marketing blocks — CTA sections, navigation, footers, content sections |
| @efferd | `https://efferd.com/r/{name}.json` | Pre-built page sections — headers, footers, feature sections |
| @doras-ui | `https://ui.doras.to/r/{name}.json` | Dashboard and application blocks |
| @creative-tim | `https://www.creative-tim.com/ui/r/{name}.json` | Professional UI blocks — admin dashboards, landing pages, e-commerce sections |

## E-Commerce

| Registry | URL | Description |
|----------|-----|-------------|
| @commercn | `https://commercn.com/r/{name}.json` | shadcn blocks for e-commerce sites — product cards, shopping cart, checkout flow, reviews |

## AI Components

| Registry | URL | Description |
|----------|-----|-------------|
| @ai-elements | `https://ai-sdk.dev/elements/api/registry/{name}.json` | Vercel AI SDK UI elements — chat interfaces, streaming response displays |
| @assistant-ui | `https://r.assistant-ui.com/{name}.json` | AI assistant UIs — chat bubbles, thread views, suggested prompts, tool call displays |
| @tool-ui | `https://www.tool-ui.com/r/{name}.json` | Tool/function call UIs for AI agents — tool result cards, execution status |
| @ai-blocks | `https://webllm.org/r/{name}.json` | WebLLM blocks — browser-based LLM interfaces, local inference UIs |

## File Upload

| Registry | URL | Description |
|----------|-----|-------------|
| @better-upload | `https://better-upload.com/r/{name}.json` | Upload components — drag-and-drop zones, progress indicators, file previews |

## Other

| Registry | URL | Description |
|----------|-----|-------------|
| @arc | `https://witharc.co/r/{name}.json` | Design system components |
| @abui | `https://abui.io/r/{name}.json` | Additional UI component library |
| @aevr | `https://ui.aevr.space/r/{name}.json` | UI component variants |
| @einui | `https://ui.eindev.ir/r/{name}.json` | Extended UI components |
| @billingsdk | `https://billingsdk.com/r/{name}.json` | Billing and payment form components — subscription management, plan selectors |

## Notable Additions (2026)

Registries recently added to the directory worth knowing (exact URL templates come from `registries.json` — fetch the endpoint at setup time):

| Registry | Description |
|----------|-------------|
| @kibo-ui | Advanced composite components (Gantt, kanban, editors) |
| @kokonutui | Modern animated components |
| @reui | Extended UI component collection |
| @plate | Rich text editor framework components |
| @paceui (+ @paceui-gsap) | Animated/GSAP-powered components |
| @intentui | Design-system component kit |
| @hextaui | Modern UI components |
| @skiper-ui | Animated showcase components |
| @smoothui | Smooth micro-interaction components |
| @neobrutalism | Neobrutalism-styled components |
| @retroui | Retro-styled components |
| @tailark | Marketing blocks |
| @shadcnblocks | Large block collection |
| @shadcn-editor | Lexical-based editor for shadcn |
| @clerk | Clerk auth UI components |
| @supabase | Supabase UI library components |

(@tweakcn is NOT in the directory.)

---

## Populating components.json

Use the `/add-registries` command to automatically fetch all 267 registries from `https://ui.shadcn.com/r/registries.json` and add them to `components.json`.

The command:
1. Fetches the JSON endpoint
2. Parses each entry's `name` and `url`
3. Adds them to the `"registries"` field in `components.json`
4. Merges with existing entries — never overwrites
