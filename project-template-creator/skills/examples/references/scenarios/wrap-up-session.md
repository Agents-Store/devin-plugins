# Scenario: End-of-Session Wrap-Up

## Setup

You've spent 3 hours working in `demo-directus-nextjs` (Level 1.5). During the session you:
- Added a `deploy.sh` script for Vercel deployment
- Discovered that shadcn v4 uses `@base-ui/react` instead of Radix
- Created a reusable `useDirectus` composable for data fetching
- Manually fixed Docker hot-reload by adding a volume mount

## Walkthrough

### 1. User invokes wrap-up

```
/project-template-creator:wrap-up
```

### 2. Plugin reviews session

```
## Session Review

**Current project:** demo-directus-nextjs (Level 1.5)
**Parent templates:** project-directus-nextjs (L1) → project-template (L0)

### Template Improvements Found

#### Push to Level 0 (all stacks)
  (none found this session)

#### Push to Level 1 (project-directus-nextjs)
1. deploy.sh — Vercel deployment script is generic to all Directus + Next.js projects
2. shadcn v4 gotcha — Important warning about @base-ui/react vs Radix
3. Docker hot-reload fix — volume mount for next.js hot reload in Docker

#### Project-only (skip)
4. useDirectus composable — Demo-specific data patterns, not generic enough for template
```

### 3. Plugin categorizes

| # | Description | Target | Category | Priority |
|---|-------------|--------|----------|----------|
| 1 | deploy.sh for Vercel | Level 1 | script | Must-have |
| 2 | shadcn v4 @base-ui gotcha | Level 1 | CLAUDE.md | Must-have |
| 3 | Docker hot-reload volume | Level 1 | config | Nice-to-have |

### 4. User decides

> "Found 3 template improvements for Level 1. Should I:
> (a) Apply fixes to project-directus-nextjs and commit
> (b) Create GitHub Issue
> (c) Just record in LEARNINGS.md
> (d) Skip"

User picks **(a)**.

### 5. Plugin applies fixes

Delegates to feedback skill for each item, targeting `project-directus-nextjs`:

**Fix 1:** Copies `deploy.sh` to parent template, updates CLAUDE.md Quick Commands
**Fix 2:** Adds gotcha to CLAUDE.md: "shadcn v4 uses `@base-ui/react`, not Radix — `asChild` doesn't exist, use `render`"
**Fix 3:** Adds volume mount to `docker-compose.yml` for hot reload

All three applied in one commit:

```bash
cd project-directus-nextjs
git add deploy.sh docker-compose.yml CLAUDE.md LEARNINGS.md
git commit -m "fix(template): deploy script, shadcn v4 gotcha, Docker hot-reload

3 improvements discovered in demo-directus-nextjs session:
- Added deploy.sh for Vercel deployment
- Added shadcn v4 @base-ui/react gotcha to CLAUDE.md
- Fixed Docker hot-reload with volume mount in docker-compose.yml"
```

### 6. Summary

```
Session wrap-up complete:
  - Applied 3 fixes to project-directus-nextjs (committed)
  - Skipped 1 project-only item (useDirectus composable)

Child projects that should merge from project-directus-nextjs:
  - demo-directus-nextjs (current project)
  - acme-website
  - globex-portal
```
