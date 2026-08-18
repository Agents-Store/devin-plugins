---
name: n8n-examples
description: End-to-end n8n workflow development scenarios with step-by-step walkthroughs. Use when starting a new workflow, looking for real-world examples, wanting to see complete workflow creation from start to finish, or asking about "n8n example", "workflow example", "show me how to build", "sample workflow".
---

# n8n Workflow Examples

Step-by-step scenario walkthroughs showing complete workflow development from planning to deployment.

---

## Available Scenarios

### 1. [Webhook to Slack Notification](references/scenarios/webhook-to-slack.md)

**Pattern**: Webhook Processing
**Complexity**: Simple (4 nodes)
**What you learn**:
- Create a webhook-triggered workflow
- Access webhook body data correctly (`$json.body.*`)
- Configure Slack node for message posting
- Add response to webhook caller

### 2. [Scheduled Report Generator](references/scenarios/scheduled-report.md)

**Pattern**: Scheduled Task + HTTP API Integration
**Complexity**: Medium (6 nodes)
**What you learn**:
- Set up cron-based scheduling
- Fetch data from external APIs
- Transform data with Code node (JavaScript)
- Send formatted email reports
- Add error handling with Error Trigger

### 3. [AI Agent Chatbot](references/scenarios/ai-agent-chatbot.md)

**Pattern**: AI Agent Workflow
**Complexity**: Complex (7+ nodes)
**What you learn**:
- Configure AI Agent with language model
- Add tools (HTTP Request, database)
- Set up memory for conversation context
- Handle chat input/output via webhook
- AI connection types (ai_languageModel, ai_tool, ai_memory)

---

## Workflow Development Process

Every scenario follows the same process:

### 1. Plan
- Identify the workflow pattern (see n8n-workflow-patterns skill)
- List required nodes
- Map the data flow

### 2. Discover Nodes
```
search_nodes({query: "node-name"})
get_node({nodeType: "nodes-base.nodeName", detail: "standard"})
```

### 3. Create Workflow
Use external MCP for JSON-based creation:
```
n8n_create_workflow({name, nodes, connections})
```
Or native MCP for SDK-based creation:
```
get_sdk_reference() → get_node_types([...]) → validate_workflow(code) → create_workflow_from_code(code)
```

### 4. Validate
```
n8n_validate_workflow({id: "workflow-id"})
```

### 5. Iterate
```
n8n_update_partial_workflow({id, operations: [...]})
```

### 6. Activate
```
n8n_update_partial_workflow({id, operations: [{type: "activateWorkflow"}]})
```

---

## Quick Reference: Node Types

Common nodes used across scenarios:

| Node | Type (search/validate) | Type (workflow) | Purpose |
|------|----------------------|-----------------|---------|
| Webhook | `nodes-base.webhook` | `n8n-nodes-base.webhook` | HTTP trigger |
| Schedule | `nodes-base.scheduleTrigger` | `n8n-nodes-base.scheduleTrigger` | Cron trigger |
| HTTP Request | `nodes-base.httpRequest` | `n8n-nodes-base.httpRequest` | API calls |
| Code | `nodes-base.code` | `n8n-nodes-base.code` | Custom JS/Python |
| Set | `nodes-base.set` | `n8n-nodes-base.set` | Transform fields |
| IF | `nodes-base.if` | `n8n-nodes-base.if` | Conditional routing |
| Slack | `nodes-base.slack` | `n8n-nodes-base.slack` | Slack messages |
| AI Agent | `nodes-langchain.agent` | `@n8n/n8n-nodes-langchain.agent` | AI agent |

**Remember**: Two different nodeType formats — `nodes-base.*` for search/validate tools, `n8n-nodes-base.*` for workflow creation tools.

---

## Related Skills

- **n8n-workflow-patterns** — Architectural patterns for all workflow types
- **n8n-mcp-tools-expert** — External MCP tool usage details
- **n8n-native-mcp** — Native MCP (SDK-based) workflow creation
- **n8n-expression-syntax** — Expression patterns for data mapping
- **n8n-node-configuration** — Node-specific configuration guidance
