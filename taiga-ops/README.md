# taiga-ops (Devin plugin)

Taiga project-management ops plugin. Drive the full Taiga REST API by curl — projects, memberships, roles, milestones (sprints), epics, user stories, tasks, issues (with statuses, types, priorities, severities, points, custom attributes), wiki, history, attachments, comments, webhooks, notify policies, search, resolver, stats, and import/export. Authenticates with TAIGA_ADMIN_USERNAME + TAIGA_ADMIN_PASSWORD to obtain TAIGA_AUTH_TOKEN against TAIGA_API_URL.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (5)

- `api-reference` — This skill should be used when the user asks for "Taiga API endpoints", "Taiga REST API", "Taiga curl examples", "Taiga API documentation", the exact path/method for any Taiga resource, or needs HTTP details for projects, epics, user stories, tasks, issues, milestones, wiki, webhooks, custom attributes, search, or import/export. Index into the full per-domain endpoint catalog.
- `common-operations` — This skill should be used when the user wants to do project-management work in Taiga — "create a user story / task / issue / epic in Taiga", "start a new sprint", "move a story to In Progress", "assign a task", "comment on an issue", "add members to a Taiga project", "build a sprint report", or any everyday Taiga operation. Provides plain-language workflows that drive the REST API and route to the exact endpoints.
- `examples` — This skill should be used when the user wants a worked end-to-end Taiga example or walkthrough — "show me a full Taiga workflow", "example of setting up a project in Taiga", "how do I run sprint planning via the API", "end-to-end bug triage example", or wants to see several Taiga API calls chained together for a real scenario.
- `setup` — This skill should be used when the user wants to "connect to Taiga", "log into Taiga", "authenticate with Taiga", "get a Taiga auth token", "set up Taiga access", or before running any Taiga REST API call. Establishes the auth token and the global request conventions (headers, pagination, version locking, the resolver).
- `troubleshoot` — This skill should be used when a Taiga REST API call fails or behaves unexpectedly — "Taiga returns 401 / 403", "version conflict", "Taiga login fails", "can't find the object", "pagination missing results", "PATCH rejected", or any Taiga error response. Maps symptoms to causes and fixes.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/taiga-ops
