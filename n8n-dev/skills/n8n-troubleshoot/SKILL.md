---
name: n8n-troubleshoot
description: Troubleshoot n8n workflow development issues. Use when encountering MCP connection errors, API authentication failures, workflow execution problems, expression errors, node configuration issues, or any n8n-related error. Also use when asking about "n8n error", "n8n not working", "debug n8n", "fix n8n".
---

# n8n Troubleshooting Guide

Every `curl` below builds its path from `N8N_BASE`, the instance root. `N8N_API_URL` may hold
the root or already end in `/api/v1`, so derive it first:

```bash
N8N_BASE="${N8N_API_URL%/}"; N8N_BASE="${N8N_BASE%/api/v1}"
```

## MCP Connection Issues

### External MCP Server (n8n-mcp-external)

**"Connection refused" or "ECONNREFUSED"**
- Cause: n8n instance is not reachable at the configured URL
- Fix:
  1. Verify `N8N_API_URL` is correct and includes the protocol (e.g., `https://n8n.example.com`)
  2. Confirm n8n is running: `curl -s $N8N_BASE/healthz`
  3. Check firewall rules — the MCP server must be able to reach n8n's port
  4. If using Docker, ensure the container is on the correct network

**"401 Unauthorized"**
- Cause: Invalid or expired API key
- Fix:
  1. Verify `N8N_API_KEY` is set correctly
  2. Regenerate the API key in n8n: Settings → n8n API → Create an API key
  3. Check that the key has not been revoked
  4. Test directly: `curl -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE/api/v1/workflows?limit=1"`

**"Timeout" or hanging requests**
- Cause: Network latency or n8n overloaded
- Fix:
  1. Check n8n instance health and resource usage
  2. Verify there is no proxy or load balancer dropping connections
  3. Try a simple health check: `curl -m 5 $N8N_BASE/healthz`

### Native MCP Server (n8n-native-mcp)

**"Failed to connect" or "Connection error"**
- Cause: Wrong URL format for the native MCP endpoint, or MCP is not enabled
- Fix:
  1. URL must end with `/mcp-server/http` (e.g., `https://n8n.example.com/mcp-server/http`) — copy it from Settings → Instance-level MCP → Connect → Server URL
  2. Do NOT include `/api/v1` in the native MCP URL
  3. Verify MCP is enabled: Settings → Instance-level MCP → Enable MCP access (instance owner or admin). `N8N_DISABLED_MODULES=mcp` removes the feature entirely.

**"Invalid token" or "Authentication failed"**
- Cause: Wrong or missing MCP token
- Fix:
  1. Check `N8N_MCP_TOKEN` environment variable
  2. Regenerate the token: Settings → Instance-level MCP → Connect → **API key** tab (generating a new one revokes the old one; update every client)
  3. Ensure the token is passed in the Authorization header as `Bearer <token>`
  4. Or switch to OAuth: `claude mcp add --transport http n8n-native-mcp https://<n8n-host>/mcp-server/http`, then `/mcp`

**A tool answers for some workflows but refuses others**
- Cause: instance-level MCP is per workflow — a workflow must be **Available in MCP**, and only published workflows with a webhook, form, schedule or chat trigger are eligible. `search_workflows` is the exception: it shows previews of every workflow the user can see.
- Fix: enable the workflow (workflow menu → Settings → Available in MCP, or Settings → Instance-level MCP → Workflows exposed). Agents are exposed the same way (**Agents exposed**).

**`NOT_CONFIGURED` from `n8n_test_workflow`, `n8n_manage_agents`, `n8n_explore_node_resources` or `n8n_workflow_versions` (`source: "native"`)**
- Cause: these external tools go through the instance-level MCP and need `N8N_MCP_ACCESS_TOKEN` in the `n8n-mcp-external` server's `env` (n8n 2.34+)
- Fix: set it (Settings → Instance-level MCP → Connect → API key); it is a separate secret from `N8N_API_KEY`

### Diagnostic Steps

Run the health check tool to diagnose MCP connectivity:

```
mcp__n8n-mcp-external__n8n_health_check({mode: "diagnostic"})
```

This will test:
- API connectivity
- Authentication
- Available features and tool status
- `mcpVersion` and `versionCheck` (is `n8n-mcp` itself up to date)

`n8nVersion` is usually absent from the answer — n8n stopped exposing its version to API clients in 1.119.0, and `n8nVersionNote` says so. That is not an error.

---

## API Authentication Errors

### Error Code Reference

| Status | Meaning | Solution |
|--------|---------|----------|
| 401 | Invalid or missing API key | Check `X-N8N-API-KEY` header. Regenerate key if needed. |
| 403 | Insufficient permissions | User role lacks permission for this operation. Check role in Settings → Users. |
| 404 | Wrong URL or missing resource | Verify `N8N_API_URL` and endpoint path. Resource may have been deleted. |
| 429 | Rate limited | Add delays between requests. Reduce batch sizes. |

### Quick Authentication Test

```bash
# Test API key validity
curl -s -o /dev/null -w "%{http_code}" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE/api/v1/workflows?limit=1"
```

Expected output: `200`. Any other code indicates a problem.

### Common Authentication Mistakes

1. **Missing protocol in URL:** Use `https://n8n.example.com`, not `n8n.example.com`
2. **Doubled path:** `$N8N_API_URL/api/v1/workflows` returns 404 when `N8N_API_URL` already ends in `/api/v1` (or `/`) — use `$N8N_BASE`, derived above
3. **Wrong header name:** Must be `X-N8N-API-KEY`, not `Authorization` or `X-Api-Key`
4. **Key from wrong instance:** Ensure the key was generated on the instance you are targeting

---

## Workflow Validation Issues

### Stuck in Validation Loop

If a workflow keeps failing validation after multiple fix attempts:
1. Use `n8n_autofix_workflow` to auto-fix common structural issues:
   ```
   mcp__n8n-mcp-external__n8n_autofix_workflow({id: "workflow-id"})
   ```
2. If autofix does not resolve it, export the workflow JSON and manually inspect the structure
3. Check for circular connections — n8n does not support them

### Expression Format Errors

- Expressions must be wrapped in `{{ }}` double curly braces
- Inside `{{ }}`, use standard JavaScript
- Outside Code nodes, always use `{{ }}` for dynamic values
- Common mistake: `$json.field` without braces — must be `{{ $json.field }}`

See the `n8n-expression-syntax` skill for detailed expression guidance.

### Node Type Version Mismatch

When a workflow references a node version that does not exist:
- Use `n8n_autofix_workflow` with typeversion correction
- Manually update the `typeVersion` field in the workflow JSON
- Check available versions: `mcp__n8n-mcp-external__get_node({nodeType: "nodes-base.httpRequest", mode: "versions"})`

### Connection Errors in Workflow Definition

- Node names in connections must match **exactly** (case-sensitive)
- A connection references a node by its `name` field, not its `type`
- Verify all connection targets exist in the workflow's `nodes` array
- Orphaned connections (pointing to deleted nodes) cause validation failures

---

## Expression Errors

### "Cannot read property 'X' of undefined"

- **Cause:** The data path does not exist in the incoming data
- **Fix:** Check the actual data structure from the previous node
- **Debug:** Add a Set node before the failing node to inspect `{{ JSON.stringify($json) }}`
- **Common issue:** Accessing nested properties without null checks — use `{{ $json.parent?.child?.value }}`

### Webhook Data Not Accessible

- Webhook body data is at `{{ $json.body.field }}` in the node immediately after the Webhook
- Headers are at `{{ $json.headers['header-name'] }}`
- Query parameters are at `{{ $json.query.param }}`
- If the Webhook is not the immediate predecessor, use `{{ $('Webhook').item.json.body.field }}`

### Expression Shows as Literal Text

- Missing `{{ }}` — the value is being treated as a static string
- Check for invisible characters or copy-paste issues
- Ensure the field accepts expressions (not all fields do)

### Expression in Code Node

- Code nodes use **direct JavaScript**, not `{{ }}` expression syntax
- Access input data with `$input.all()`, `$input.first()`, `$input.item`
- Access specific node output with `$('NodeName').all()`
- Use `return` to output data (Run Once mode) or work with `$input.item` (Run Once for Each Item)

---

## Node Configuration Errors

### "Missing required field"

- Different operations require different fields
- Check the node documentation or use `get_node` to see required parameters:
  ```
  mcp__n8n-mcp-external__get_node({nodeType: "nodes-base.httpRequest", detail: "full"})
  ```
- Required fields change based on the selected operation/resource

### Wrong nodeType Format

Two naming conventions are used in different contexts:

| Context | Format | Example |
|---------|--------|---------|
| Searching/validating nodes | `nodes-base.*` | `nodes-base.httpRequest` |
| Workflow JSON definitions | `n8n-nodes-base.*` | `n8n-nodes-base.httpRequest` |

Using the wrong prefix is a frequent source of "node not found" errors.

### AI Node Connection Type Errors

n8n has 8 AI connection types. Using the wrong one causes silent failures:

1. `ai_agent` — Main AI agent connection
2. `ai_chain` — Chain connection
3. `ai_document` — Document loader
4. `ai_embedding` — Embedding model
5. `ai_languageModel` — LLM connection (most common)
6. `ai_memory` — Memory/context
7. `ai_outputParser` — Output parser
8. `ai_tool` — Tool for AI agent
9. `ai_vectorStore` — Vector store

Check the `n8n-node-configuration` skill for detailed AI node wiring guidance.

---

## Execution Failures

### Timeout

- **Symptom:** Execution stops with a timeout error
- **Fix:** Increase `executionTimeout` in workflow settings
- **Global setting:** Set `EXECUTIONS_TIMEOUT` and `EXECUTIONS_TIMEOUT_MAX` environment variables
- **Per-workflow:** Workflow Settings → Timeout After (seconds)

### Memory Issues / Out of Memory

- **Symptom:** n8n crashes or execution killed by OS
- **Fix:**
  1. Use **Split In Batches** node for large datasets — process 50-100 items at a time
  2. Avoid storing large binary data in workflow items
  3. Increase Node.js memory: set `NODE_OPTIONS=--max-old-space-size=4096`
  4. Enable `EXECUTIONS_DATA_SAVE_ON_ERROR=none` to reduce memory pressure

### Rate Limiting from External Services

- **Symptom:** 429 errors from APIs called by workflow nodes
- **Fix:**
  1. Add **Wait** nodes between API calls (1-2 seconds)
  2. Use **Split In Batches** with smaller batch sizes
  3. Enable retry on the HTTP Request node (Settings → Retry On Fail)
  4. Set retry count and wait between retries

### Check Execution Logs

```
# List recent failed executions
mcp__n8n-mcp-external__n8n_executions({action: "list", status: "error", limit: 5})

# Get details of a specific execution
mcp__n8n-mcp-external__n8n_executions({action: "get", id: "exec-id", mode: "error"})
```

---

## Common Error Messages

| Error Message | Cause | Fix |
|---------------|-------|-----|
| "Node not found" | Wrong nodeType prefix in tool calls | Use `nodes-base.*` for search/validate tools, `n8n-nodes-base.*` in workflow JSON |
| "Workflow could not be activated" (n8n 2.x calls it publishing) | No trigger node in workflow, or the publish permission is missing (`PUBLISH_FORBIDDEN`, n8n 2.39+) | Add a trigger node (Webhook, Schedule Trigger, etc.) as the entry point; for the permission, the API key needs the `workflow:activate` scope and the user `workflow:publish` |
| "Invalid expression" | Syntax error inside `{{ }}` | Check brackets, quotes, variable names. Validate with expression tester. |
| "Credential not found" | Missing or wrong credential ID | List credentials first with API or MCP tool. Use the correct ID. |
| "Connection refused" | n8n instance not reachable | Check `N8N_API_URL`, firewall, container status, DNS |
| "Duplicate node name" | Two nodes have the same name | Rename one of the duplicate nodes — names must be unique |
| "Unknown node type" | Community node not installed | Install the package via n8n Settings → Community Nodes |
| "Workflow data too large" | Workflow JSON exceeds size limit | Remove unnecessary data, simplify large expressions, reduce node count |
| "SQLITE_BUSY" | SQLite database locked | Switch to PostgreSQL for production, or reduce concurrent executions |
| "No encryption key found" | Missing `N8N_ENCRYPTION_KEY` | Set the environment variable. Required for credential encryption. |

---

## Diagnostic Commands

### MCP Tool Diagnostics

```
# Full health check
mcp__n8n-mcp-external__n8n_health_check({mode: "diagnostic"})

# Native MCP: is the server reachable and the token valid?
mcp__n8n-native-mcp__search_workflows({limit: 1})

# Quick connectivity test — list a few workflows
mcp__n8n-mcp-external__n8n_list_workflows({limit: 5})

# Check for recent errors
mcp__n8n-mcp-external__n8n_executions({action: "list", status: "error", limit: 5})

# Validate a specific workflow
mcp__n8n-mcp-external__n8n_validate_workflow({id: "workflow-id"})

# Validate workflow JSON directly
mcp__n8n-mcp-external__validate_workflow({workflow: {...}})
```

### CLI Diagnostics

```bash
# Check n8n version
n8n --version

# Run security audit
n8n audit

# Check license
n8n license:info
```

### curl Diagnostics

```bash
# Health check
curl -s "$N8N_BASE/healthz"

# API access test
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE/api/v1/workflows?limit=1" | jq '.data | length'

# Check execution queue
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE/api/v1/executions?status=running&limit=10" | jq '.data | length'
```

---

## Related Skills

For deeper investigation of specific issue categories:

- **n8n-validation-expert** — Deep dive into validation errors, profiles, and fix strategies
- **n8n-expression-syntax** — Expression debugging, data path resolution, common patterns
- **n8n-node-configuration** — Node-specific configuration issues, AI connection types, operation dependencies
- **n8n-setup** (setup skill) — MCP connection configuration, initial setup troubleshooting
- **n8n-api-reference** — Full API endpoint reference for direct curl-based debugging
- **n8n-cli-recipes** — CLI commands for server-side diagnostics and management
- **n8n-native-mcp** — Native MCP gating ("Available in MCP"), tool behaviour and Agents
- **n8n-error-handling** — Wiring error outputs, error workflows and retries in the workflow itself
- **n8n-self-hosting** — Docker Compose, queue mode, task runners, upgrades and backups
