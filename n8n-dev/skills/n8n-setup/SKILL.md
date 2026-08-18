---
name: n8n-setup
description: Verify n8n MCP connection and configure n8n MCP servers. Use when the user asks to "verify n8n connection", "check n8n MCP", "test n8n setup", "configure n8n", "set up n8n MCP", or needs to confirm that n8n MCP integration is operational.
---

# n8n MCP Setup & Verification

Configure and verify n8n MCP server connections for workflow development.

---

## Two MCP Server Types

n8n provides two complementary MCP servers. Each serves a different purpose.

### External MCP (`n8n-mcp-external`)

Third-party MCP server by czlonkowski. Optimized for workflow **development**.

- **22+ tools** for node search, validation, workflow CRUD, templates, credentials, audit, data tables
- Installed via `npx n8n-mcp`
- Communicates over **stdio** transport
- Best for: building, editing, validating, and debugging workflows
- Repository: https://github.com/czlonkowski/n8n-mcp

**Key capabilities:**
- Search and inspect 400+ built-in nodes
- Validate node configurations against schemas
- Create, read, update, delete workflows (JSON-based)
- Deploy from 2,700+ community templates
- Manage credentials (create, update, delete, list schemas)
- Audit instance security
- Manage data tables and rows
- Auto-fix validation errors

### Native MCP (`n8n-native-mcp`)

Official MCP server by the n8n team. Optimized for workflow **execution**.

- **16 tools** for SDK-based workflow creation, execution, publishing
- Built into n8n (no separate install)
- Communicates over **HTTP** transport
- Best for: creating workflows from TypeScript SDK code, executing, publishing
- Requires n8n version with MCP support enabled

**Key capabilities:**
- Get SDK reference and type definitions
- Search and discover nodes with discriminators
- Create workflows from TypeScript SDK code
- Validate SDK code before deployment
- Execute workflows (manual or production mode)
- Publish/unpublish/archive workflows
- Search projects and folders

---

## Environment Variables

Set these at the **project level** (not plugin level). The plugin references them via `${VAR}` placeholders.

### For External MCP

| Variable | Description | How to Generate |
|----------|-------------|-----------------|
| `N8N_API_URL` | n8n instance URL (e.g., `https://your-n8n.example.com`) | Your n8n deployment URL |
| `N8N_API_KEY` | API authentication key | n8n UI: Settings → API → Create API Key |

### For Native MCP

| Variable | Description | How to Generate |
|----------|-------------|-----------------|
| `N8N_API_URL` | n8n instance URL (same as above) | Your n8n deployment URL |
| `N8N_MCP_TOKEN` | MCP server authentication token | n8n UI: Settings → API → Create MCP Token |

### Setting Environment Variables

Store these in your shell profile or project-level `.env`:

```bash
export N8N_API_URL="https://your-n8n.example.com"
export N8N_API_KEY="your-api-key-here"
export N8N_MCP_TOKEN="your-mcp-token-here"
```

**Security note:** Never commit API keys or tokens to version control. Use environment variables or a secrets manager.

---

## Project `.mcp.json` Configuration

Create or update `.mcp.json` in your project root.

### External MCP Only (stdio)

Use when you need workflow development tools — node search, validation, workflow CRUD, templates, credentials, audit.

```json
{
  "mcpServers": {
    "n8n-mcp-external": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "${N8N_API_URL}",
        "N8N_API_KEY": "${N8N_API_KEY}"
      }
    }
  }
}
```

### Native MCP Only (HTTP)

Use when you need SDK-based workflow creation, execution, and publishing.

```json
{
  "mcpServers": {
    "n8n-native-mcp": {
      "type": "http",
      "url": "${N8N_API_URL}/mcp-server/http",
      "headers": {
        "Authorization": "Bearer ${N8N_MCP_TOKEN}"
      }
    }
  }
}
```

### Combined Configuration (Both Servers)

Use when you need the full capability set — development tools from external plus SDK-based creation and execution from native.

```json
{
  "mcpServers": {
    "n8n-mcp-external": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "${N8N_API_URL}",
        "N8N_API_KEY": "${N8N_API_KEY}"
      }
    },
    "n8n-native-mcp": {
      "type": "http",
      "url": "${N8N_API_URL}/mcp-server/http",
      "headers": {
        "Authorization": "Bearer ${N8N_MCP_TOKEN}"
      }
    }
  }
}
```

---

## Verification Steps

After configuring `.mcp.json`, verify each server is operational.

### Verify External MCP

**Step 1: Health check**

Call `mcp__n8n-mcp-external__n8n_health_check`.

Expected response:
```json
{
  "status": "OK",
  "version": "1.x.x",
  "connectedToN8n": true
}
```

If `connectedToN8n` is `false`, the N8N_API_URL or N8N_API_KEY is incorrect.

**Step 2: Test node search**

Call `mcp__n8n-mcp-external__search_nodes` with `query: "webhook"`.

Expected: a list of matching nodes including `n8n-nodes-base.webhook`.

**Step 3: Test workflow listing**

Call `mcp__n8n-mcp-external__n8n_list_workflows`.

Expected: a list of existing workflows (may be empty on fresh instances).

### Verify Native MCP

**Step 1: Search workflows**

Call `mcp__n8n-native-mcp__search_workflows`.

Expected: a list of workflows (may be empty on fresh instances). If this returns results or an empty list without errors, the connection is working.

**Step 2: Get SDK reference**

Call `mcp__n8n-native-mcp__get_sdk_reference` with `section: "patterns"`.

Expected: SDK patterns documentation. This confirms the native MCP server is fully operational.

**Step 3: Search nodes**

Call `mcp__n8n-native-mcp__search_nodes` with `queries: ["webhook"]`.

Expected: node search results with IDs and discriminators.

### Quick Verification Checklist

| Check | Tool | Pass Condition |
|-------|------|----------------|
| External health | `n8n_health_check` | `status: "OK"`, `connectedToN8n: true` |
| External nodes | `search_nodes` | Returns node results |
| External workflows | `n8n_list_workflows` | Returns list (no auth error) |
| Native workflows | `search_workflows` | Returns list (no auth error) |
| Native SDK | `get_sdk_reference` | Returns documentation |
| Native nodes | `search_nodes` | Returns results with discriminators |

---

## Available Tools by Server

### External MCP Tools (22+)

| Tool | Purpose |
|------|---------|
| `n8n_health_check` | Verify connection to n8n instance |
| `search_nodes` | Find nodes by keyword |
| `get_node` | Get node details and documentation |
| `validate_node` | Validate node configuration |
| `search_templates` | Search community templates |
| `get_template` | Get template details |
| `n8n_deploy_template` | Deploy template to instance |
| `n8n_create_workflow` | Create workflow from JSON |
| `n8n_get_workflow` | Get workflow by ID |
| `n8n_list_workflows` | List all workflows |
| `n8n_update_full_workflow` | Replace entire workflow |
| `n8n_update_partial_workflow` | Update specific nodes/connections |
| `n8n_delete_workflow` | Delete workflow |
| `n8n_generate_workflow` | AI-generate workflow from description |
| `n8n_autofix_workflow` | Auto-fix validation errors |
| `n8n_test_workflow` | Test workflow execution |
| `n8n_executions` | Get execution history |
| `n8n_workflow_versions` | Get workflow version history |
| `validate_workflow` | Validate complete workflow |
| `n8n_validate_workflow` | Server-side workflow validation |
| `n8n_manage_credentials` | CRUD operations on credentials |
| `n8n_manage_datatable` | Manage data tables and rows |
| `n8n_audit_instance` | Security audit |
| `tools_documentation` | Get tool docs, AI agent guide, Code node guides |

### Native MCP Tools (16)

| Tool | Purpose |
|------|---------|
| `get_sdk_reference` | SDK patterns, expressions, rules |
| `search_nodes` | Search nodes with discriminators |
| `get_node_types` | TypeScript type definitions |
| `get_suggested_nodes` | Curated node recommendations |
| `create_workflow_from_code` | Create from SDK code |
| `update_workflow` | Update from SDK code |
| `validate_workflow` | Validate SDK code |
| `get_workflow_details` | Get workflow details |
| `search_workflows` | Search workflows |
| `search_projects` | Find project IDs |
| `search_folders` | Find folder IDs |
| `publish_workflow` | Activate for production |
| `unpublish_workflow` | Deactivate workflow |
| `archive_workflow` | Archive workflow |
| `execute_workflow` | Execute workflow |
| `get_execution` | Get execution details |

---

## When to Use Which MCP

Choose the right server based on the task.

| Task | Recommended MCP | Reason |
|------|-----------------|--------|
| Search/discover nodes | External | Richer search with docs mode |
| Validate node config | External | Schema-aware validation profiles |
| Create workflow (JSON) | External | Direct JSON structure |
| Create workflow (SDK code) | Native | TypeScript SDK with type safety |
| Edit workflow incrementally | External | Partial update support |
| Deploy templates | External | 2,700+ template library |
| Execute/test workflow | Both | External has test, Native has execute |
| Manage credentials | External | Full CRUD + schema discovery |
| Security audit | External | Built-in + custom deep scan |
| Publish/unpublish | Native | Lifecycle management |
| Version management | External | Version history access |
| Get node type definitions | Native | TypeScript-level detail with discriminators |
| Search projects/folders | Native | Organization structure |
| Archive workflow | Native | Soft-delete management |

### Decision Flowchart

```
Need to BUILD a workflow?
├── From scratch with type safety → Native (SDK code)
├── From JSON structure → External (create_workflow)
└── From community template → External (deploy_template)

Need to EDIT a workflow?
├── Change specific nodes → External (update_partial)
├── Replace entire workflow → External (update_full)
└── Rewrite from SDK code → Native (update_workflow)

Need to RUN a workflow?
├── Quick test → External (test_workflow)
└── Manual or production execution → Native (execute_workflow)

Need to MANAGE the instance?
├── Credentials → External
├── Security audit → External
├── Data tables → External
└── Projects/folders → Native
```

---

## Troubleshooting

For common connection issues:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "Connection refused" | n8n not running or wrong URL | Verify N8N_API_URL is correct and n8n is running |
| "401 Unauthorized" | Invalid API key or token | Regenerate key in n8n Settings → API |
| "npx n8n-mcp not found" | Package not available | Run `npx n8n-mcp` manually to verify install |
| External tools timeout | n8n instance unreachable | Check network, firewall, VPN |
| Native MCP 404 | MCP not enabled in n8n | Enable MCP server in n8n settings |
| "ECONNREFUSED" on localhost | Wrong port | Default n8n port is 5678; verify with `N8N_API_URL=http://localhost:5678` |
| Partial tool failures | API key lacks permissions | Create a new API key with full permissions |

For detailed troubleshooting procedures, refer to the **troubleshoot** skill.

---

## Setup Checklist

Use this checklist when setting up n8n MCP for a new project:

1. [ ] n8n instance is running and accessible
2. [ ] API key generated (for external MCP)
3. [ ] MCP token generated (for native MCP)
4. [ ] Environment variables set (`N8N_API_URL`, `N8N_API_KEY`, `N8N_MCP_TOKEN`)
5. [ ] `.mcp.json` created in project root with desired server(s)
6. [ ] External MCP health check passes
7. [ ] Native MCP search_workflows succeeds
8. [ ] Both servers return tool results without auth errors
