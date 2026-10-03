# stack-composable-stack-v1 (Devin plugin)

Composable Stack v1 architecture plugin. How PostgreSQL (direct MCP + PostgREST API), NocoDB, n8n, Trigger.dev, and NocoBase (prod + dev sandbox) fit together for data-driven applications with low-code interfaces: layer roles, data-access selection, integration patterns between services, and project bootstrap. Tool knowledge comes from its dependencies.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (7)

- `background-job` — This skill should be used when the user wants to "create a background job", "run async task", "process data in background", "schedule recurring task", "set up a queue", "choose between n8n and Trigger.dev", or needs to decide how background processing is split between Trigger.dev and n8n in the Composable Stack.
- `data-access-selection` — This skill should be used when the user needs to choose how to read or write data in the Composable Stack — "NocoDB MCP or PostgreSQL MCP", "PostgREST or MCP", "which data access should I use", "how should n8n read the database", "how should a Trigger.dev task call PostgreSQL", "complex SQL or simple CRUD", "batch data operation", or is picking between the stack's data-access paths.
- `full-feature` — This skill should be used when the user wants to "build a complete feature", "create end-to-end functionality", "implement a full feature across all layers", "build feature with data model and automation", or needs a step-by-step recipe for building features that span the Data, Logic, and Interface layers of the Composable Stack.
- `init-project` — This skill should be used when the user asks to "set up composable stack", "initialize project", "configure environment", "connect MCP services", or needs to set up all MCP connections and environment variables for the Composable Stack v1.
- `nocobase-to-n8n` — This skill should be used when the user wants to "trigger n8n from NocoBase", "connect NocoBase UI to n8n", "automate NocoBase actions with n8n", "create NocoBase workflow that calls n8n", or needs to integrate NocoBase interface events with n8n workflow automation.
- `nocodb-to-n8n` — This skill should be used when the user wants to "trigger n8n workflow from NocoDB", "connect NocoDB data to n8n", "create webhook from NocoDB to n8n", "automate NocoDB with n8n", or needs to integrate NocoDB data events with n8n workflow automation.
- `nocodb-to-trigger` — This skill should be used when the user wants to "trigger background task from NocoDB", "connect NocoDB to Trigger.dev", "process NocoDB data with Trigger.dev", "run background job on NocoDB change", or needs to integrate NocoDB data events with Trigger.dev background tasks.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/stack-composable-stack-v1
