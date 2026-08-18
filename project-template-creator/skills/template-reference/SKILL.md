---
name: template-reference
description: >
  Use this skill when the user asks about "template hierarchy", "template levels",
  "project template conventions", "what files go in a template", "Level 0 vs Level 1",
  "template structure", "what belongs in the parent template", or needs reference
  documentation for the project template system and its 4-level hierarchy.
disable-model-invocation: true
---

# Project Template Hierarchy Reference

Quick reference for the 4-level project template system. For detailed docs, see the `references/` files linked below.

## Levels Overview

| Level | Pattern | Parent | Purpose |
|-------|---------|--------|---------|
| 0 | `project-template` | none | Universal base — structure, rules, commands, conventions |
| 1 | `project-{stack}` | `project-template` | Stack-specific — stack.json filled, plugins declared, stack docs |
| 1.5 | `demo-{stack}` | `project-{stack}` | Working demo app — sample data, seed scripts, showcases |
| 2 | `{client}-{project}` | `project-{stack}` | Client project — real IDs/URLs, .env, .mcp.json configured |

Each level inherits everything from its parent and adds level-specific content.

## What Lives Where

- **Level 0 owns:** Process skills (brainstorming, TDD, debugging, planning, verification), core commands (commit, pr, plan, review, retro, sync), generic rules (safety, search-before-building, conventions), docs templates, project-config template
- **Level 1 owns:** Stack-specific skills (e.g., `new-page` for Next.js), stack-specific .env.example vars, stack-specific CLAUDE.md gotchas, stack plugin references, stack-specific docs (architecture, code-style)
- **Level 1.5 owns:** Sample data, seed scripts, working pages, demo deployment configs
- **Level 2 owns:** Client resource IDs, real credentials (.env), domain-specific skills, custom business logic

## Key Files

Every template has: `stack.json`, `CLAUDE.md`, `AGENTS.md`, `README.md`, `.env.example`, `.mcp.json.example`, `.gitignore`, `docs/` (architecture, code-style, api-conventions), `.claude/` (skills, commands, agents, rules, settings).

## Detailed References

- @references/hierarchy.md — Detailed level descriptions with examples
- @references/file-inventory.md — Complete file-by-file inventory per template level
- @references/conventions.md — Naming conventions, stack.json schema, CLAUDE.md structure
