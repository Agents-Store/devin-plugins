# nocodb-dev (Devin plugin)

NocoDB schema development plugin. Meta API v3 via curl and MCP (schema tools on Cloud/licensed through listTools/callTool) — tables, fields (35 types), views (9 types), filters, sorts, hooks (HookV3), comments, scripts, dashboards & widgets, workflows, documents, plus workspaces / members / teams / tokens. Bundles both Data API and Meta API OpenAPI specs.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (12)

- `api-reference` — NocoDB REST API reference for schema-development work — curl on Meta API v3. Loaded only on explicit cite. Use when:
- "NocoDB REST API"
- "API endpoints for tables/fields/views"
- "create a table via API"
- "what's in the OpenAPI spec"
- "Meta API endpoints"
- "field type schemas"
- "Hook v3 payload"
- "dashboard / widget API"

- `cli-reference` — Command-line access to NocoDB for schema work — curl recipes on Meta API v3 by resource, mapped to the commands of the official nocodb.sh script (installed with npx skills add nocodb/agent-skills). Loaded only on explicit cite. Use when:
- "NocoDB CLI"
- "NocoDB command line schema commands"
- "how do I create a table with curl"
- "nocodb.sh commands"
- "NocoDB agent-skills CLI"

- `dashboards` — Create and manage NocoDB Dashboards and Widgets via Meta API v3. Use when:
- "create a dashboard"
- "add a chart / metric / KPI widget"
- "list widgets on a dashboard"
- "fetch widget data"
- "update a dashboard"
- "delete a widget"

- `examples` — End-to-end NocoDB schema-development walkthroughs. Use when:
- "show me a schema example"
- "how do I build a CRM in NocoDB?"
- "e-commerce schema example"
- "schema design walkthrough"
- "NocoDB dev scenarios"

- `field-management` — Create, update, and delete NocoDB fields across all 35 supported types — text, numeric, date, select, attachment, JSON, geometry, links, lookup, rollup, formula, button, barcode/QR, system fields. Use when:
- "add a field"
- "create a column"
- "rename a field"
- "change field type"
- "delete a column"
- "add a formula"
- "set up lookup or rollup"
- "link two tables"
- "add a select option"

- `mcp-patterns` — NocoDB MCP for schema-development work — what the server lists directly, which schema tools hide behind listTools/callTool, and the Community vs Cloud/licensed contract. Use when:
- "what MCP tools can I use for schema?"
- "can MCP create tables / fields / views?"
- "listTools / callTool"
- "how do I discover NocoDB structure?"
- "MCP for nocodb-dev"

- `setup` — Verify NocoDB connection for schema-development work — MCP and REST (curl on Meta API v3). Use when:
- "check NocoDB dev setup"
- "verify NocoDB API access"
- "is my NocoDB token working?"
- "can I modify schema?"
- "test NocoDB MCP connection"

- `table-management` — Create, update, rename, duplicate, and delete NocoDB tables. Use when:
- "create a new NocoDB table"
- "rename a table"
- "delete a NocoDB table"
- "set the display field"
- "duplicate a table"
- "add a table with initial fields"

- `troubleshoot` — Diagnose schema-side NocoDB errors — read-only fields, type-change rejections, broken Lookups, formula errors, view config validation, version mismatches. Use when:
- "field type change rejected"
- "Lookup not working"
- "formula returns ERR"
- "cannot delete table"
- "Kanban not grouping"
- "schema cache stale"
- "NocoDB version too old"

- `view-management` — Create, configure, and delete NocoDB views — Grid, Form, Gallery, Kanban, Calendar, Map, Gantt, Timeline, List. Use when:
- "create a kanban view"
- "add a calendar / gantt / timeline view"
- "build a form for intake"
- "make a gallery of products"
- "set up filters on a view"
- "delete a view"
- "show / hide columns on a view"

- `webhooks` — Configure NocoDB webhooks (HookV3) — triggers, field scoping, and notification targets (URL, Email, Slack/Discord/Telegram/Whatsapp/Twilio messaging, Script). Use when:
- "add a webhook"
- "fire a Slack message on insert"
- "send email when a record changes"
- "trigger n8n on update"
- "list webhooks on a table"
- "delete a hook"

- `workflows` — List, execute, and inspect NocoDB Workflows (the platform's built-in automation engine) via Meta API v3; author drafts over MCP on Cloud/licensed. Use when:
- "list NocoDB workflows"
- "execute a workflow"
- "view workflow execution"
- "trigger workflow on demand"
- "fetch execution results"


## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 6 command(s) — Devin plugins do not support commands
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/nocodb-dev
