---
name: workflow-analysis
description: Analyze an n8n workflow JSON before importing — node inventory, connection topology, credential requirements, security flags, complexity scoring, and compatibility checks. Use when asked to "analyze n8n workflow", "check workflow before import", "workflow compatibility check", "review n8n template", "assess workflow complexity", or before importing any template or community workflow.
---

# Workflow Analysis

Analyze an n8n workflow JSON to assess compatibility, security, complexity, and credential requirements before importing to the target instance. Run this analysis on every workflow — whether from the official template library or community sources.

Library templates are often years old. Expect nodes that n8n 2.0 switched off or removed, and nodes that n8n 3.0 (planned for October 2026) removes — Step 6 lists them.

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

Extract credentials from nodes with a `credentials` field. Map each credential type to the service it connects. List unique types and check if they exist on the target instance using `~~credential_manage`. Also note any Data Table nodes: the table they reference must exist on the target before the workflow runs (create it with `~~datatable_manage`).

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

- **Switched off by default since n8n 2.0:** `n8n-nodes-base.executeCommand` and `n8n-nodes-base.localFileTrigger` are disabled (`NODES_EXCLUDE`). Importing a workflow that holds them fails unless the instance owner sets `NODES_EXCLUDE="[]"` — a security decision. Flag them as a **blocker** and suggest an alternative.
- **Removed in n8n 2.0:** Start (replaced by the Manual Trigger), Spontit, crowd.dev, Kitemaker, Automizy, and the Pyodide-based Python Code node (`_input` syntax; the native Python runner replaces it). Flag as a **blocker** on a 2.x target.
- **Removed in n8n 3.0 (October 2026):** Function (`n8n-nodes-base.function`) and Function Item (`functionItem`) — use Code; Item Lists (`itemLists`) — use Aggregate, Limit, Remove Duplicates, Sort, Split Out and Summarize; Cron (`cron`) and Interval (`interval`) — use Schedule Trigger; HTML Extract (`htmlExtract`) — use HTML; iCalendar (`iCal`); Convert binary (Move Binary Data); Read/Write Binary File(s); Read PDF; Workflow Trigger; Orbit; the legacy OpenAI, OpenAI Assistant and OpenAI Model nodes; the legacy HTTP Request Tool; SerpApi; Manual Chat Trigger; Chat Messages Retriever; Motorhead and Zep memory; the Insert and Load vector-store nodes. In Execute Sub-workflow, the Local File and URL sources are removed. Flag as a **warning**: the workflow imports and runs today but will break on upgrade.
- **AI Agent v1:** `@n8n/n8n-nodes-langchain.agent` with `typeVersion` < 2 is removed in 3.0 — flag it and suggest `typeVersion` 2 or later.
- **typeVersion:** Missing = very old export; unusually high = cutting-edge. Flag either. `n8n_autofix_workflow` (preview) and `autoUpgradeVersions` raise outdated versions.
- **Target check:** On a 2.x instance, Settings > Migration Report shows the affected nodes of the workflows already on it. Ask the owner to look there before a large batch.

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
