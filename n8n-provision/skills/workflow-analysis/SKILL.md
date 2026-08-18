---
name: workflow-analysis
description: Analyze an n8n workflow JSON before importing — node inventory, connection topology, credential requirements, security flags, complexity scoring, and compatibility checks. Use when asked to "analyze n8n workflow", "check workflow before import", "workflow compatibility check", "review n8n template", "assess workflow complexity", or before importing any template or community workflow.
---

# Workflow Analysis

Analyze an n8n workflow JSON to assess compatibility, security, complexity, and credential requirements before importing to the target instance. Run this analysis on every workflow — whether from the official template library or community sources.

## Analysis Pipeline

Execute these steps in order on the workflow JSON:

```
1. NODE INVENTORY     → catalog all node types
2. CONNECTION TOPOLOGY → map the flow structure
3. CREDENTIAL AUDIT   → list required credentials
4. SECURITY SCAN      → flag risks
5. COMPLEXITY SCORE   → rate difficulty
6. COMPATIBILITY CHECK → verify version support
7. REPORT             → structured output
```

## Step 1: Node Inventory

List every node in the `nodes[]` array. Classify each by origin:

| Prefix | Classification | Example |
|--------|---------------|---------|
| `n8n-nodes-base.*` | Built-in (core) | `n8n-nodes-base.slack` |
| `@n8n/n8n-nodes-langchain.*` | AI nodes (official) | `@n8n/n8n-nodes-langchain.agent` |
| `n8n-nodes-*` (other) | Community node | `n8n-nodes-puppeteer` |
| `@<scope>/n8n-nodes-*` | Community (scoped) | `@custom/n8n-nodes-myservice` |

### What to extract per node

- `type` — full node type identifier
- `typeVersion` — version of the node implementation
- `name` — display name in the workflow
- `parameters` — configuration (analyzed in security scan)
- `position` — layout coordinates (ignore for analysis)

### Summary format

```
Built-in nodes: 8 (Webhook, IF, Set, Code, Slack, HTTP Request, Merge, NoOp)
AI nodes: 2 (Agent, OpenAI Chat Model)
Community nodes: 1 (n8n-nodes-puppeteer)
Total: 11
```

Flag any community nodes — these require separate installation on the target instance.

## Step 2: Connection Topology

Analyze the `connections` object to determine the workflow's flow structure.

| Topology | Characteristics | Indicators |
|----------|----------------|------------|
| **Linear** | A → B → C → D | Each node has exactly 1 output connection |
| **Branched** | A → B, A → C | A node has 2+ output connections (IF, Switch) |
| **Looped** | A → B → C → A | A connection path returns to an earlier node |
| **Error-handled** | Main + Error paths | Nodes have `onError` settings or Error Trigger node present |
| **Sub-workflow** | Calls external workflow | Contains `n8n-nodes-base.executeWorkflow` node |
| **Parallel** | Fan-out → Merge | Multiple branches converge at a Merge node |

Detect topology by: IF/Switch nodes (branching), connection cycles (loops), `errorTrigger` or `onError` settings (error handling), `executeWorkflow` nodes (sub-workflows), branch + Merge combinations (parallelism).

## Step 3: Credential Requirements

Extract credentials from nodes with a `credentials` field. Map each credential type to the service it connects. List unique types and check if they exist on the target instance using `~~credential_manage`.

## Step 4: Security Scan

Inspect node parameters for security risks.

| Flag | What to Look For | Severity |
|------|-----------------|----------|
| **Hardcoded API key** | String matching `sk-`, `xoxb-`, `Bearer`, API key patterns in parameters | Critical |
| **Hardcoded URL** | External URLs in HTTP Request nodes (may point to attacker-controlled servers) | High |
| **Hardcoded secrets** | Passwords, tokens, or keys in any node parameter value | Critical |
| **Open webhook** | Webhook node with no authentication (`authentication: "none"`) | High |
| **Code execution** | Code node with external HTTP calls or file system access | Medium |
| **Unfiltered input** | Set/Function nodes that pass user input without sanitization | Medium |
| **External sub-workflow** | ExecuteWorkflow calling a workflow ID that may not exist locally | Low |

Scan procedure: iterate all node `parameters` recursively, check strings against API key patterns (`sk-`, `xoxb-`, `Bearer`), check Webhook `authentication` setting, check Code nodes for `require()`, `fetch()`, `fs.` usage.

## Step 5: Complexity Scoring

| Level | Criteria |
|-------|----------|
| **Simple** | < 5 nodes, linear topology, 0-1 credentials |
| **Medium** | 5-15 nodes, some branching, 2-3 credentials |
| **Complex** | 15+ nodes, error handling, sub-workflows, 4+ credentials |

Scoring weights: node count (30%), branching (20%), credentials (20%), error handling (15%), community nodes (15%).

## Step 6: Compatibility Check

Verify the workflow will work on the target n8n instance.

### Check for

- **Deprecated nodes**: `n8n-nodes-base.function` → `code` (since v0.198), `functionItem` → `code` (v0.198), `executeCommand` → `code` (v1.0)
- **typeVersion**: Missing = very old export; unusually high = cutting-edge. Flag either.
- **AI nodes**: `@n8n/n8n-nodes-langchain.*` requires n8n v1.19+ with AI enabled.

## Step 7: Structured Report

Output the analysis as a structured report.

```
## Workflow Analysis: <workflow name>

### Summary
- **Nodes**: <count> (<built-in>, <AI>, <community>)
- **Topology**: <Linear | Branched | Looped | Parallel>
- **Complexity**: <Simple | Medium | Complex>
- **Credentials needed**: <count>
- **Security flags**: <count> (<critical>, <high>, <medium>, <low>)
- **Compatibility**: <OK | Warnings | Blockers>

### Node Inventory
<table of all nodes with type, version, classification>

### Credential Requirements
<list of credential types with associated nodes>

### Security Findings
<list of flags with severity, node name, description>

### Compatibility Notes
<deprecated nodes, version requirements, community node dependencies>

### Recommendation
<Import as-is | Import with modifications | Do not import>
<specific actions needed before import>
```

## Quick Analysis (Abbreviated)

For official templates with high view counts, run a shortened version: count nodes, check for community nodes, scan for hardcoded secrets, list credentials, give complexity rating. Use the full 7-step pipeline for complex workflows or community-sourced JSON.
