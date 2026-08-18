---
name: examples
description: >
  End-to-end scenario walkthroughs for n8n workflow provisioning. This skill should be used when
  the user asks for "n8n provisioning example", "how to import workflows", "n8n provision
  walkthrough", "batch import tutorial", "template deploy guide", "n8n setup example",
  "find and import n8n workflow", "deploy automation suite", or needs a complete example of
  discovering, analyzing, and deploying n8n workflows.
---

# Provisioning Examples

Scenario walkthroughs demonstrating the full provisioning lifecycle: discovery, analysis, import, credential setup, and activation. All tool references use `~~placeholder` syntax — see CONNECTORS.md for provider fallback.

## Available Scenarios

| Scenario | Description | Reference |
|----------|-------------|-----------|
| Provision a new instance | Set up a fresh n8n instance with 10 foundational workflows | `references/scenarios/provision-new-instance.md` |
| Find and import community workflow | Search official + community sources, fetch JSON, import | `references/scenarios/find-and-import-community-workflow.md` |
| Automation suite deployment | Deploy a coordinated "Slack + GitHub DevOps" suite of 5 workflows | `references/scenarios/automation-suite-deployment.md` |

## Quick Start: Simplest Provisioning Flow

The minimum viable path from search to deployed workflow:

### Step 1: Search for a template

```
~~template_search("slack notification new github issue")
```

Review results. Pick the best match by quality signals:
- `totalViews > 10,000` — well-established
- Short node list (< 15 nodes) — simpler to configure
- Recent activity — compatible with current n8n

### Step 2: Analyze the template

```
~~template_get(id={template_id})
```

Check:
- **Node types** — are all nodes available on the instance?
- **Credentials needed** — what API keys / OAuth tokens are required?
- **Complexity** — how many nodes, how many connections?

### Step 3: Deploy

```
~~template_deploy(id={template_id})
```

The deploy tool handles:
- Auto-fix for minor schema issues
- Credential stripping (credentials are not imported — must be configured manually)
- Workflow is created in **inactive** state

### Step 4: Verify

```
~~workflow_list
```

Confirm the workflow appears in the list. Check its status (should be inactive).

### Step 5: Configure and activate

1. Open the workflow in n8n UI
2. Set up required credentials for each node
3. Test with a manual execution
4. Activate the workflow

---

## Common Patterns Across Scenarios

### Pre-flight checks

Every provisioning session should start with:

```
1. ~~instance_audit → is the instance healthy?
2. ~~workflow_list → what's already deployed?
3. ~~credential_manage → what credentials exist?
```

This prevents conflicts and identifies reusable credentials.

### Search escalation

When the official library doesn't have what you need:

```
1. ~~template_search → official library (9,166+ templates)
2. Community GitHub repos → Zie619, enescingoz, etc. (see community-source-discovery skill)
3. Community platforms → n8nworkflows.xyz, n8nfind.net, etc.
4. Build from scratch → use n8n-native-mcp SDK tools
```

### Credential planning

Before deploying multiple workflows:

1. List all credential types needed across all workflows
2. Group by provider (e.g., all Slack workflows share one OAuth token)
3. Set up credentials once
4. Map to all workflows that need them

### Post-deployment verification

After every deployment:

1. Confirm workflow exists in `~~workflow_list`
2. Check workflow is inactive (not auto-activated)
3. Configure credentials
4. Run a manual test execution
5. Check execution output for errors
6. Activate only after successful test

## Convention Notes

- All examples use the CONNECTORS pattern — `~~placeholder` for tool-agnostic instructions
- Workflows are always imported in inactive state — never auto-activate
- Credentials are always stripped during import — must be configured manually
- Batch deployments use tags for grouping: `suite-{name}-{date}`
- Community JSON is always validated before import
