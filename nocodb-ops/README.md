# nocodb-ops (Devin plugin)

NocoDB ops plugin for Agents Store. Record management, filtering (structured filters, exactDate date filters), sorting, reports, search, webhooks (events, payload, conditions), and data import/export for business users via the NocoDB MCP server (writes in batches of up to 100 records; extra tools on Cloud/licensed through listTools/callTool) and curl on the v3 API.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (10)

- `cli-reference` — Command-line access to NocoDB data -- curl recipes on the Data API v3 (records, links, attachments) and Meta API v3, mapped to the commands of the official nocodb.sh script (installed with npx skills add nocodb/agent-skills). Loaded only on explicit cite. Use when:
- "NocoDB CLI commands"
- "NocoDB curl recipes"
- "NocoDB agent-skills"
- "what CLI commands are available"
- "nocodb.sh commands"

- `examples` — NocoDB workflow examples, scenario walkthroughs, and practical patterns. Use when:
- "show me a NocoDB example"
- "workflow examples"
- "scenario walkthroughs"
- "how do I use NocoDB for..."
- "NocoDB use case"

- `import-export` — Import data into NocoDB tables and export records out. Use when:
- "import CSV into NocoDB"
- "load data into this table"
- "bulk create records"
- "export records to CSV"
- "migrate data between tables"
- "import JSON data"
- "extract all records"
- "download table data"

- `mcp-patterns` — NocoDB MCP tools reference for data work -- which tools the server lists, which sit behind listTools/callTool, the Community vs Cloud/licensed contract, and the exact parameter shapes (100-record batches, sort objects, filter vs where, date sub-operators). Use when:
- "what NocoDB tools are available?"
- "how do I query records?"
- "show me NocoDB MCP parameters"
- "which tool do I use for..."
- "NocoDB tool reference"
- "listTools / callTool"

- `record-management` — Create, read, update, and delete NocoDB records. Use when:
- "add a new record"
- "create entries in NocoDB"
- "update a record"
- "delete records"
- "bulk import data"
- "search and edit records"
- "how many records match..."
- "restore deleted records"

- `search-filter` — NocoDB filter syntax reference for searching, filtering, and sorting records. Use when:
- "filter records"
- "search for records where"
- "NocoDB where clause"
- "how to filter by date"
- "sort results"
- "query syntax"
- "find records matching"
- "filter by status"
- "records created this week"
- "combine multiple filters"

- `setup` — Verify NocoDB connection and MCP setup. Use when:
- "check my NocoDB connection"
- "verify MCP is working"
- "test NocoDB setup"
- "is NocoDB connected?"
- "troubleshoot NocoDB access"

- `troubleshoot` — Diagnose and fix NocoDB errors, connection issues, and MCP problems. Use when:
- "NocoDB not working"
- "connection error"
- "getting 401 error"
- "MCP tool not responding"
- "debug NocoDB"
- "filter not working"
- "timeout error"

- `views-and-reports` — Build reports, summaries, and dashboards from NocoDB data. Use when:
- "create a report"
- "summarize this table"
- "show sales by region"
- "build a dashboard"
- "aggregate data"
- "what views exist on this table?"
- "kanban board"
- "monthly summary"
- "count by category"
- "average order value"

- `webhooks` — Use NocoDB webhooks from the business side — which events exist, how to set one up in the UI, what the receiving system gets (payload), conditions, the Button trigger, and testing. Use when:
- "trigger something when a record changes"
- "send NocoDB data to n8n / another system"
- "set up a webhook in NocoDB"
- "what does the NocoDB webhook payload look like"
- "fire a webhook from a button"
- "webhook only when status becomes ..."
- "list the webhooks on a table"


## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 6 command(s) — Devin plugins do not support commands
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/nocodb-ops
