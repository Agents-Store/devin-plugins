---
name: n8n-native-mcp
description: Guide for using n8n native MCP server tools. Use when creating workflows from SDK code, executing workflows, publishing/unpublishing, getting node type definitions, using get_sdk_reference, or working with the official n8n MCP server. Also use when asking about "native MCP", "n8n SDK", "workflow from code", "execute workflow".
---

# n8n Native MCP Server

Official n8n MCP server. 16 tools. SDK-based approach — write TypeScript workflow code instead of raw JSON.

---

## SDK Workflow (Recommended Flow)

Follow this sequence when building workflows with the native MCP server:

```
get_sdk_reference → search_nodes → get_node_types → write code → validate_workflow → create_workflow_from_code
```

**Never skip steps.** Each step provides information required by the next.

1. **get_sdk_reference** — Learn SDK patterns, expressions, syntax rules
2. **search_nodes** — Find node IDs and discriminators for the services you need
3. **get_node_types** — Get exact TypeScript type definitions for discovered nodes
4. **Write code** — Build the workflow using SDK patterns and correct parameter names
5. **validate_workflow** — Verify the code compiles and produces valid workflow JSON
6. **create_workflow_from_code** — Deploy the validated workflow to n8n

---

## Tool Reference

### SDK & Discovery Tools

#### `get_sdk_reference`

Get SDK patterns, expressions, functions, and rules. **Call this FIRST** before building any workflow.

**Parameters:**
- `section` (optional) — Which section to retrieve. One of:
  - `"patterns"` — SDK coding patterns and workflow structure
  - `"expressions"` — n8n expression syntax (`{{ }}` usage)
  - `"functions"` — Built-in helper functions
  - `"rules"` — Validation rules and constraints
  - `"import"` — Import statements and module setup
  - `"guidelines"` — Coding guidelines and best practices
  - `"design"` — Workflow design guidance
  - `"all"` — Everything (large response)

**Usage:**
```
mcp__n8n-native-mcp__get_sdk_reference(section: "patterns")
```

Start with `"patterns"` for basic workflow structure. Add `"guidelines"` and `"design"` for complex workflows.

---

#### `search_nodes`

Search for nodes by service name, trigger type, or utility. Returns node IDs and discriminators.

**Parameters:**
- `queries` (required, array of strings) — Search terms

**Usage:**
```
mcp__n8n-native-mcp__search_nodes(queries: ["webhook", "slack", "if", "set"])
```

**Returns:** Node IDs (e.g., `n8n-nodes-base.webhook`) with discriminators (resource, operation, mode). Record the discriminators — you need them for `get_node_types`.

**Tips:**
- Search for both service nodes AND utility nodes (set, if, merge, code, switch)
- Search for triggers separately (e.g., `"schedule trigger"`, `"webhook"`)
- Use specific terms: `"gmail"` not `"email"`, `"slack"` not `"chat"`

---

#### `get_node_types`

Get TypeScript type definitions for nodes. **MUST call before writing code** — never guess parameter names.

**Parameters:**
- `nodeIds` (required, array of objects) — Node IDs with discriminators

**Usage:**
```
mcp__n8n-native-mcp__get_node_types(nodeIds: [
  { "id": "n8n-nodes-base.webhook" },
  { "id": "n8n-nodes-base.slack", "resource": "message", "operation": "send" },
  { "id": "n8n-nodes-base.if" }
])
```

**Important:** Include discriminators from `search_nodes` results. Without discriminators, you get the base type which may lack operation-specific parameters.

**Returns:** TypeScript parameter definitions with exact field names, types, and descriptions.

---

#### `get_suggested_nodes`

Get curated node recommendations organized by workflow category.

**Parameters:**
- `category` (optional) — Filter by category. Examples:
  - `"chatbot"` — Conversational AI nodes
  - `"notification"` — Alert and messaging nodes
  - `"scheduling"` — Cron and timer triggers
  - `"data-transformation"` — Parsing, mapping, filtering
  - `"integration"` — Third-party service connectors

**Usage:**
```
mcp__n8n-native-mcp__get_suggested_nodes(category: "notification")
```

Use this for inspiration when you know what kind of workflow you want but not which specific nodes to use.

---

### Workflow Creation & Management Tools

#### `create_workflow_from_code`

Create a new workflow from validated SDK code.

**Parameters:**
- `code` (required, string) — Validated TypeScript SDK code
- `name` (optional, string) — Workflow name
- `description` (optional, string) — Short description (1-2 sentences)
- `projectId` (optional, string) — Target project ID
- `folderId` (optional, string) — Target folder ID

**Usage:**
```
mcp__n8n-native-mcp__create_workflow_from_code(
  code: "<validated SDK code>",
  name: "Slack Notification on Webhook",
  description: "Receives webhook events and sends formatted notifications to a Slack channel."
)
```

**Always validate code first** with `validate_workflow` before creating.

**Always include a description** — it helps users find and understand workflows later.

---

#### `update_workflow`

Update an existing workflow with new SDK code. Replaces the entire workflow definition.

**Parameters:**
- `workflowId` (required, string) — ID of the workflow to update
- `code` (required, string) — New validated SDK code

**Usage:**
```
mcp__n8n-native-mcp__update_workflow(
  workflowId: "abc123",
  code: "<validated SDK code>"
)
```

Follow the same build sequence (search_nodes → get_node_types → write → validate) before calling update.

---

#### `validate_workflow`

Validate SDK code before creating or updating a workflow. Returns workflow JSON on success or detailed error messages on failure.

**Parameters:**
- `code` (required, string) — TypeScript SDK code to validate

**Usage:**
```
mcp__n8n-native-mcp__validate_workflow(code: "<SDK code>")
```

**On success:** Returns the compiled workflow JSON. The code is safe to use with `create_workflow_from_code` or `update_workflow`.

**On failure:** Returns error details including line numbers and descriptions. Fix errors and re-validate until clean.

**Always validate before creating.** This catches:
- Missing imports
- Invalid parameter names
- Type mismatches
- Incorrect node configurations
- Missing required fields

---

#### `get_workflow_details`

Get details for a specific workflow, including nodes, connections, and trigger information.

**Parameters:**
- `workflowId` (required, string) — Workflow ID

**Usage:**
```
mcp__n8n-native-mcp__get_workflow_details(workflowId: "abc123")
```

---

#### `search_workflows`

Search workflows by name or description.

**Parameters:**
- `query` (optional, string) — Search term
- `projectId` (optional, string) — Filter by project
- `limit` (optional, number) — Maximum results

**Usage:**
```
mcp__n8n-native-mcp__search_workflows(query: "slack notification", limit: 10)
```

Returns workflow IDs, names, descriptions, and active status.

---

#### `search_projects`

Find project IDs for organizing workflows.

**Parameters:**
- `query` (optional, string) — Search term
- `type` (optional, string) — `"personal"` or `"team"`

**Usage:**
```
mcp__n8n-native-mcp__search_projects(type: "team")
```

---

#### `search_folders`

Find folder IDs within a project.

**Parameters:**
- `projectId` (required, string) — Project to search within
- `query` (optional, string) — Search term

**Usage:**
```
mcp__n8n-native-mcp__search_folders(projectId: "proj123", query: "production")
```

---

### Lifecycle Tools

#### `publish_workflow`

Activate a workflow for production execution. Triggers become live.

**Parameters:**
- `workflowId` (required, string) — Workflow to publish
- `versionId` (optional, string) — Specific version to publish

**Usage:**
```
mcp__n8n-native-mcp__publish_workflow(workflowId: "abc123")
```

**Warning:** Publishing activates all triggers. Webhooks start accepting requests, schedules start firing, and event listeners start consuming events. Verify the workflow is correct before publishing.

---

#### `unpublish_workflow`

Deactivate a workflow. Stops all triggers and execution.

**Parameters:**
- `workflowId` (required, string) — Workflow to deactivate

**Usage:**
```
mcp__n8n-native-mcp__unpublish_workflow(workflowId: "abc123")
```

---

#### `archive_workflow`

Archive a workflow. Removes it from the active list without deleting.

**Parameters:**
- `workflowId` (required, string) — Workflow to archive

**Usage:**
```
mcp__n8n-native-mcp__archive_workflow(workflowId: "abc123")
```

---

### Execution Tools

#### `execute_workflow`

Execute a workflow by ID. Supports multiple input types and execution modes.

**Parameters:**
- `workflowId` (required, string) — Workflow to execute
- `mode` (optional, string) — `"manual"` (test) or `"production"`
- `inputData` (optional, object) — Input data, varies by trigger type:
  - **Chat input:** `{ "chatInput": "Hello, how can I help?" }`
  - **Form input:** `{ "formData": { "field1": "value1" } }`
  - **Webhook input:** `{ "body": { ... }, "headers": { ... } }`

**Usage (manual test):**
```
mcp__n8n-native-mcp__execute_workflow(
  workflowId: "abc123",
  mode: "manual"
)
```

**Usage (with chat input):**
```
mcp__n8n-native-mcp__execute_workflow(
  workflowId: "abc123",
  inputData: { "chatInput": "Summarize today's tasks" }
)
```

Use `"manual"` mode for testing. Use `"production"` only for verified workflows.

---

#### `get_execution`

Get details of a specific execution run.

**Parameters:**
- `executionId` (required, string) — Execution ID (returned by `execute_workflow`)
- `includeData` (optional, boolean) — Include full execution data
- `nodeNames` (optional, array of strings) — Filter to specific node outputs
- `truncateData` (optional, boolean) — Truncate large data fields

**Usage:**
```
mcp__n8n-native-mcp__get_execution(
  executionId: "exec456",
  includeData: true,
  nodeNames: ["Slack"],
  truncateData: true
)
```

---

## Native vs External MCP

### Key Architectural Difference

| Aspect | Native MCP | External MCP |
|--------|-----------|--------------|
| **Workflow input** | TypeScript SDK code (string) | JSON objects (nodes[], connections{}) |
| **Creation flow** | Write code → validate → create | Build JSON → create directly |
| **Type safety** | Full TypeScript definitions | Schema-based validation |
| **Node discovery** | IDs + discriminators | Keyword search + docs |
| **Editing** | Full workflow replacement | Incremental partial updates |
| **Templates** | Not available | 2,700+ community templates |
| **Credentials** | Not available | Full CRUD + schema discovery |
| **Audit** | Not available | Security audit + deep scan |

### When Native is Better

- **Complex workflows** — TypeScript code is easier to reason about than large JSON structures
- **Version control** — SDK code diffs are readable; JSON diffs are not
- **Reproducibility** — Same code always produces the same workflow
- **Type safety** — get_node_types provides exact parameter definitions
- **Lifecycle management** — Publish, unpublish, archive in one place

### When External is Better

- **Quick edits** — Partial updates modify specific nodes without touching others
- **Template deployment** — Access to 2,700+ ready-made workflows
- **Credential management** — Full CRUD operations on credentials
- **Security auditing** — Instance-level security scanning
- **Incremental building** — Add nodes one at a time, test as you go
- **Data tables** — Manage n8n internal data tables

---

## Example: Full Workflow Creation

Build a workflow that receives a webhook, processes the data, and sends a Slack message.

### Step 1: Get SDK Reference

```
mcp__n8n-native-mcp__get_sdk_reference(section: "patterns")
```

Learn the basic workflow structure, how to define nodes, and how to connect them.

### Step 2: Search for Nodes

```
mcp__n8n-native-mcp__search_nodes(queries: ["webhook", "slack", "set", "if"])
```

Returns node IDs and discriminators:
- `n8n-nodes-base.webhook`
- `n8n-nodes-base.slack` (resource: "message", operation: "send")
- `n8n-nodes-base.set`
- `n8n-nodes-base.if`

### Step 3: Get Type Definitions

```
mcp__n8n-native-mcp__get_node_types(nodeIds: [
  { "id": "n8n-nodes-base.webhook" },
  { "id": "n8n-nodes-base.slack", "resource": "message", "operation": "send" },
  { "id": "n8n-nodes-base.set" },
  { "id": "n8n-nodes-base.if" }
])
```

Returns exact TypeScript parameter names and types for each node. Use these — never guess.

### Step 4: Write the Code

Using the SDK patterns from step 1 and the exact parameter names from step 3, write the TypeScript workflow code.

**Follow `@builderHint` annotations from type definitions** — they indicate recommended defaults. For example, if `get_node_types` returns `@builderHint Always default to latest mini model gpt-5-mini` for an OpenAI node, use that model, not an older one. Hints reflect the current best practice from n8n and the service provider.

### Step 5: Validate

```
mcp__n8n-native-mcp__validate_workflow(code: "<your SDK code>")
```

If errors are returned, fix them and re-validate. Repeat until clean.

### Step 6: Create

```
mcp__n8n-native-mcp__create_workflow_from_code(
  code: "<validated SDK code>",
  name: "Webhook to Slack Notification",
  description: "Receives webhook events and sends formatted Slack messages based on event type."
)
```

### Step 7: Test

```
mcp__n8n-native-mcp__execute_workflow(
  workflowId: "<returned workflow ID>",
  mode: "manual",
  inputData: { "body": { "event": "deploy", "status": "success" } }
)
```

### Step 8: Publish (when ready)

```
mcp__n8n-native-mcp__publish_workflow(workflowId: "<workflow ID>")
```

---

## Best Practices

### Always Follow the Sequence

1. **Always call `get_sdk_reference` first** — The SDK has specific patterns and syntax rules. Skipping this leads to invalid code.

2. **Always call `get_node_types` before writing code** — Never guess parameter names. The type definitions contain the exact field names, types, and required/optional status. Wrong parameter names are the #1 cause of validation failures.

3. **Always validate before creating** — `validate_workflow` catches errors that would cause silent failures at runtime. A workflow that validates successfully will deploy correctly.

### Workflow Naming

- Use descriptive names: "Webhook to Slack Alert" not "My Workflow"
- Always include a `description` parameter when creating — it appears in the n8n UI and helps with search

### Execution Safety

- Use `mode: "manual"` for all testing
- Only switch to `mode: "production"` after verifying manual execution succeeds
- Check execution results with `get_execution` after running

### Organizing Workflows

- Use `search_projects` and `search_folders` to find the right location before creating
- Pass `projectId` and `folderId` to `create_workflow_from_code` to place workflows correctly
- Use consistent naming conventions across workflows

### Updating Workflows

- Always re-validate new code before calling `update_workflow`
- `update_workflow` replaces the entire workflow — make sure the new code includes all nodes
- If you only need to change one node, consider using the external MCP's `n8n_update_partial_workflow` instead

### IF / Switch Node Metadata

Filter-based nodes (IF v2.2+, Switch v3.2+) require a `conditions.options` metadata object — without it, the workflow saves via native MCP but fails when edited via external MCP or n8n UI. Always include it:

```javascript
const checkCondition = ifElse({
  version: 2.3,
  config: {
    name: 'Is Active?',
    parameters: {
      conditions: {
        options: { version: 2, leftValue: '', caseSensitive: true, typeValidation: 'strict' },
        conditions: [
          {
            leftValue: expr('={{ $json.status }}'),
            operator: { type: 'string', operation: 'equals' },
            rightValue: 'active'
          }
        ]
      }
    }
  }
});
```

For unary operators (`empty`, `notEmpty`, `true`, `false`), add `singleValue: true` to the operator object and omit `rightValue`.

### Error Handling

- If `validate_workflow` returns errors, read the error messages carefully — they include line numbers
- Common errors: wrong import path, missing discriminator in node config, incorrect parameter name
- If stuck, call `get_sdk_reference(section: "rules")` to review constraints
- Re-run `get_node_types` if parameter names seem wrong — you may need different discriminators
