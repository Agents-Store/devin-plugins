# outline-ops (Devin plugin)

Outline knowledge-base ops plugin. Drive the full Outline REST API by curl — documents (create, search, move, archive, trash, import/export, AI answers, memberships), collections (CRUD, archive, duplicate, import, user/group permissions, export), comments & reactions, pins, subscriptions, notifications, stars, views, shares & access requests, webhook subscriptions, users & groups, attachments & file operations, revisions, templates, events (audit log), API keys, OAuth clients, and data attributes (154 operations). Also points to Outline's built-in MCP server. Authenticates with a Bearer OUTLINE_API_KEY against OUTLINE_API_URL.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (5)

- `api-reference` — This skill should be used when the user asks for "Outline API endpoints", "Outline REST API", "Outline curl examples", "Outline API documentation", the exact method/parameters for any Outline resource, or needs HTTP details for documents, collections, comments, reactions, pins, subscriptions, notifications, stars, views, shares, webhook subscriptions, access requests, auth, API keys, users, groups, attachments, file operations, revisions, templates, events, OAuth clients, or data attributes. Index into the full per-domain endpoint catalog.
- `common-operations` — This skill should be used when the user wants to do knowledge-base work in Outline — "create a document", "search Outline", "update a doc", "move a document to a collection", "create a collection", "share a document", "invite users to Outline", "star a document", "comment on a doc", or any everyday Outline operation. Provides plain-language workflows that drive the REST API and route to the exact methods.
- `examples` — This skill should be used when the user wants a worked end-to-end Outline example or walkthrough — "show me a full Outline workflow", "example of building a knowledge base in Outline", "how do I publish and share a doc via the API", "document lifecycle example", "onboard users to Outline", or wants to see several Outline API calls chained together for a real scenario.
- `setup` — This skill should be used when the user wants to "connect to Outline", "authenticate with Outline", "set up Outline access", "use my Outline API key", or before running any Outline REST API call. Establishes the API key + base URL from the environment and the global request conventions (RPC POST style, Bearer header, response envelope, limit/offset pagination, sorting, rate limits, policies).
- `troubleshoot` — This skill should be used when an Outline REST API call fails or behaves unexpectedly — "Outline returns 401 / 403 / 404 / 429 / 400", "Outline API key not working", "can't find the document", "empty data / missing results", "self-hosted Outline URL not working", "SSL error", or any Outline error response. Maps symptoms to causes and fixes.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/outline-ops
