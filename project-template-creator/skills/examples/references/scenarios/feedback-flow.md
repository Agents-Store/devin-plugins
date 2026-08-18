# Scenario: Push an Improvement to Parent Template

## Setup

You're working in `acme-website` (Level 2), which was forked from `project-directus-nextjs` (Level 1).

While building a page, you discover that `next.config.ts` needs `images.remotePatterns` configured for Directus image URLs. This is something every Directus + Next.js project needs.

## Walkthrough

### 1. User invokes feedback

```
/project-template-creator:feedback Add images.remotePatterns for Directus URLs to next.config.ts
```

### 2. Plugin identifies the improvement

From conversation context, it extracts:
- **What:** Add `images.remotePatterns` config to `next.config.ts` for Directus image hosting
- **Category:** config
- **Target:** Level 1 (stack-specific — only Directus + Next.js needs this)
- **Why:** Every project using Directus images through Next.js Image component needs this
- **Severity:** Major (images break without it)

### 3. Plugin reads stack.json

```json
// acme-website/stack.json
{
  "stack": "directus-nextjs",
  "level": 2,
  "parent": "project-directus-nextjs"
}
```

Parent is `project-directus-nextjs`.

### 4. Plugin locates parent template

```bash
# Found at $PROJECT_TEMPLATES_DIR/project-directus-nextjs/
```

### 5. Plugin applies the fix

Edits `project-directus-nextjs/next.config.ts` to add:

```typescript
const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
}
```

Also adds to `project-directus-nextjs/CLAUDE.md` Gotchas:
```
- `next.config.ts` needs `images.remotePatterns` — Next.js Image blocks external URLs by default
```

### 6. Plugin records in LEARNINGS.md

```markdown
## 2026-03-30 — config: Add images.remotePatterns for Directus URLs

**Problem:** Next.js Image component blocks Directus-hosted images without remotePatterns config
**Fix:** Added images.remotePatterns to next.config.ts, added gotcha to CLAUDE.md
**Source:** Discovered in acme-website (Level 2)
**Affected files:** next.config.ts, CLAUDE.md
**Severity:** Major
```

### 7. Plugin commits

```bash
cd project-directus-nextjs
git commit -m "fix(config): add images.remotePatterns for Directus URLs

Discovered in acme-website (Level 2).
Improves template for all derivative projects."
```

### 8. Plugin notes children

> "Fix applied to **project-directus-nextjs**. The following child projects should pull/merge:
> - demo-directus-nextjs
> - acme-website
> - globex-portal"
