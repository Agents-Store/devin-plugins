# directus-dev (Devin plugin)

Directus development plugin. Knowledge base for working with Directus MCP tools (12 tools), REST API, and @directus/sdk. Covers collections, items, fields, relations, files, flows, operations, and schema design.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (11)

- `api-reference` — Directus REST API endpoints, curl examples, authentication patterns, schema migration pipeline. This skill should be used when the user asks for "Directus API endpoints", "Directus REST API", "Directus curl examples", "Directus API documentation", "Directus HTTP requests", or needs specific endpoint details for scripting.
- `docker-local-dev` — Run Directus 12 locally with Docker Compose — PostgreSQL, Redis, upload and extension volumes, secrets from .env, /server/ping health check, pinned image tag, first admin, extensions on hardened images, upgrades. This skill should be used when the user asks to "run Directus locally", "Directus Docker Compose", "Directus local dev stack", "start a local Directus instance", "docker-compose.yml for Directus", or needs a throwaway Directus to develop a frontend, flows or schema against.
- `examples` — End-to-end workflow examples, tool call patterns, and scenario walkthroughs for Directus MCP. This skill should be used when the user needs complete working examples, reference implementations, step-by-step walkthroughs, or tool call patterns for Directus.
- `field-relations` — Field types, relationship configuration — M2O, O2M, M2M, M2A, translations, files. This skill should be used when the user asks to add fields, configure field types, set up relations, create relationships between Directus collections, or design M2O/O2M/M2M/M2A structures.
- `file-management` — File and asset management — upload via URL, organize folders, query file metadata, retrieve base64 assets. This skill should be used when the user asks to manage files, upload images, import files from URLs, organize folders, query file metadata, or retrieve assets in Directus.
- `flow-automation` — Build and run Directus flows, covering event hooks, schedules, webhook and manual triggers, operations such as condition, request, read and update data, and the data chain that passes values between operations. Use it for any Directus question about creating, wiring, scheduling or triggering an automation flow, in any language. For a flow that does not run or a condition that never matches use troubleshoot.
- `item-operations` — Read, query and write records (items) in a Directus collection with the items MCP tool - filters and sorting, deep queries across relations, many-to-any field selection, aggregation with groupBy, pagination, batch create, and update or delete by keys or by query. Use it for how-to questions about the data in a collection, in any language. For SDK code use sdk-patterns, for setting up relations and field types field-relations, for data model design schema-design.
- `mcp-tools` — All Directus MCP tools reference — action patterns, parameters, query system. This skill should be used when the user asks about "Directus MCP tools", "which Directus tools are available", "how to use Directus MCP", "Directus tool parameters", or needs to know which MCP operations are available for Directus and how to use them correctly.
- `schema-design` — Schema design best practices — data modeling, collection planning, system fields, display templates, singletons, folders, versioning. This skill should be used when the user asks to design a data model, plan collections, create a database schema, or build a CMS/e-commerce/project database structure in Directus.
- `sdk-patterns` — @directus/sdk patterns — composable client, TypeScript types, CRUD operations, authentication, real-time subscriptions, server-side use in Next.js (fetch options, per-request tokens, relations in queries). This skill should be used when the user asks about "Directus SDK", "@directus/sdk", "Directus client library", "Directus TypeScript", "Directus in Next.js", or needs code patterns for integrating Directus into a JavaScript/TypeScript project.
- `troubleshoot` — Diagnose Directus problems such as 401, 403, 404, 409, 422 and 500 responses on items, fields, relations or assets, MCP connection and tool-call errors, permission and policy issues, schema conflicts, slow queries, and flows that never fire or whose conditions never match. Use it for any Directus question about something failing or behaving unexpectedly. For Docker setup use docker-local-dev; for building flows use flow-automation.

## Not carried over

- 2 agent(s) — Devin plugins do not support agents
- 10 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/directus-dev
