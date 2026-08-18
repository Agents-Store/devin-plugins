# directus-dev (Devin plugin)

Directus development plugin. Knowledge base for working with Directus MCP tools (12 tools), REST API, and @directus/sdk. Covers collections, items, fields, relations, files, flows, operations, and schema design.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (10)

- `api-reference` — Directus REST API endpoints, curl examples, authentication patterns, schema migration pipeline. This skill should be used when the user asks for "Directus API endpoints", "Directus REST API", "Directus curl examples", "Directus API documentation", "Directus HTTP requests", or needs specific endpoint details for scripting.
- `examples` — End-to-end workflow examples, tool call patterns, and scenario walkthroughs for Directus MCP. This skill should be used when the user needs complete working examples, reference implementations, step-by-step walkthroughs, or tool call patterns for Directus.
- `field-relations` — Field types, relationship configuration — M2O, O2M, M2M, M2A, translations, files. This skill should be used when the user asks to add fields, configure field types, set up relations, create relationships between Directus collections, or design M2O/O2M/M2M/M2A structures.
- `file-management` — File and asset management — upload via URL, organize folders, query file metadata, retrieve base64 assets. This skill should be used when the user asks to manage files, upload images, import files from URLs, organize folders, query file metadata, or retrieve assets in Directus.
- `flow-automation` — Flow automation — triggers, operations, data chains, event hooks, webhooks, schedules. This skill should be used when the user asks to create automation flows, set up triggers, configure operations, build event-driven workflows, schedule tasks, or trigger flows programmatically in Directus.
- `item-operations` — Item CRUD operations — create, read, update, delete items, filtering, sorting, deep queries, aggregation, batch operations. This skill should be used when the user asks to create, read, update, or delete items, filter or search data, query with relations, aggregate values, or perform batch operations in Directus.
- `mcp-tools` — All Directus MCP tools reference — action patterns, parameters, query system. This skill should be used when the user asks about "Directus MCP tools", "which Directus tools are available", "how to use Directus MCP", "Directus tool parameters", or needs to know which MCP operations are available for Directus and how to use them correctly.
- `schema-design` — Schema design best practices — data modeling, collection planning, system fields, display templates, singletons, folders, versioning. This skill should be used when the user asks to design a data model, plan collections, create a database schema, or build a CMS/e-commerce/project database structure in Directus.
- `sdk-patterns` — @directus/sdk patterns — composable client, TypeScript types, CRUD operations, authentication, real-time subscriptions. This skill should be used when the user asks about "Directus SDK", "@directus/sdk", "Directus client library", "Directus TypeScript", or needs code patterns for integrating Directus into a JavaScript/TypeScript project.
- `troubleshoot` — Directus troubleshooting — common errors, diagnostics, MCP connection issues, permission problems, schema conflicts. This skill should be used when the user encounters "Directus errors", "Directus not working", "Directus connection issues", "Directus 403/422/500 errors", or needs to diagnose and fix problems.

## Not carried over

- 2 agent(s) — Devin plugins do not support agents
- 10 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/directus-dev
