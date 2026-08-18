---
name: connector-bootstrap
description: MUST be consulted at the start of ANY Plane-related request before answering the user or declaring tools unavailable. Discovers Plane tools across any MCP server, connector, or instance naming convention (cowork mode, remote MCP, local MCP, self-hosted, cloud). Use when the user mentions sprint, backlog, work item, cycle, epic, module, milestone, initiative, project, issue, ticket, task, standup, retro, estimate, roadmap, board, Plane, or any work-management operation — even if Plane tools are not visible yet. Also use before saying "I don't have access to Plane tools" or "tool not available".
---

# Plane Connector Bootstrap

This skill ensures Plane tools are reliably discovered in any environment: cowork mode, remote MCP, local MCP, Claude connectors, custom proxies, or self-hosted instances. Tool names vary by environment — **never assume tools are missing without probing first**.

## Why This Skill Exists

In cowork mode and certain remote setups, MCP/connector tools are **deferred**: Claude only sees their names in a system reminder until `ToolSearch` loads their schemas. A user request mentioning "sprint" or "work item" may arrive before the Plane tools are materialized into the tool set. **You must probe before refusing.**

Symptoms this skill prevents:
- Responding "I don't have access to Plane tools" when they are in fact available as deferred tools.
- Missing tools because the naming convention is different (`mcp__<any>__plane-i-*`, `mcp__plane__*`, `plane_*`, `connector-plane-*`, or fully custom).
- Only finding tools for one instance when multiple Plane workspaces are connected.

## Mandatory Bootstrap Protocol

Execute these steps **before** answering any Plane-related user request:

### Step 1 — Probe with ToolSearch

Call `ToolSearch` with multiple query variants. Do not stop at the first empty result:

```
ToolSearch(query="plane", max_results=20)
ToolSearch(query="work_item cycle project", max_results=20)
ToolSearch(query="list_projects create_work_item", max_results=20)
ToolSearch(query="sprint backlog issue", max_results=20)
```

If the user mentioned a specific concept (e.g. "module", "epic", "milestone", "initiative"), add a targeted query:

```
ToolSearch(query="+module list", max_results=10)
ToolSearch(query="+epic create", max_results=10)
ToolSearch(query="+milestone", max_results=10)
ToolSearch(query="+intake", max_results=10)
```

Use the `select:` form when you already know an action name from a skill:

```
ToolSearch(query="select:create_cycle,add_work_items_to_cycle,list_archived_cycles", max_results=10)
```

### Step 2 — Match by Action Suffix, Not by Prefix

Plane MCP tools may appear under **any** of these shapes (non-exhaustive):

- `mcp__<provider>__<prefix>-<action>`
- `mcp__<instance-slug>__<action>`
- `mcp__plane__<action>`
- `plane_<action>`
- `connector_plane_<action>`
- `<workspace>-plane-<action>`
- A fully custom name chosen by the connector author

**Match tools by the action suffix** (e.g., `create_cycle`, `list_work_items`, `add_work_items_to_cycle`). The prefix is environment-dependent and MUST NOT be hardcoded in this plugin or in your responses.

### Step 3 — Handle Multiple Instances

If the user has multiple Plane workspaces/instances connected, `ToolSearch` will return multiple tools with the same action suffix but different prefixes. In that case:

1. List the discovered instances to the user by their prefix/slug.
2. Ask which instance to operate on (use `AskUserQuestion` if available).
3. Remember the chosen instance for the rest of the conversation.
4. If only one instance matches, proceed without asking.

### Step 4 — Cache Discovered Names for the Session

Once you have resolved the actual tool names, keep them in working memory for the remainder of the conversation. Do **not** re-probe for every call in the same session unless the user switches instances or a call fails with "tool not found".

### Step 5 — Only Then Decide Whether Tools Are Missing

You may conclude "Plane tools are not connected" **only after** Steps 1–3 return no matches across all query variants. When reporting this to the user, say what you probed and suggest how to connect Plane (MCP, connector, or cowork).

## Discovery Cheat Sheet — Action Names to Probe

Group queries by Plane domain. Use these as ToolSearch inputs:

| Domain | Representative actions to search for |
|--------|--------------------------------------|
| Workspace | `get_me`, `get_workspace_members`, `get_workspace_features` |
| Projects | `list_projects`, `create_project`, `get_project_members`, `retrieve_project` |
| Work items | `list_work_items`, `create_work_item`, `update_work_item`, `search_work_items`, `retrieve_work_item_by_identifier` |
| Cycles / sprints | `list_cycles`, `create_cycle`, `add_work_items_to_cycle`, `list_archived_cycles`, `transfer_cycle_work_items` |
| Modules | `list_modules`, `create_module`, `add_work_items_to_module` |
| Epics | `list_epics`, `create_epic`, `update_epic` |
| Initiatives | `list_initiatives`, `create_initiative` |
| Milestones | `list_milestones`, `create_milestone`, `add_work_items_to_milestone` |
| States | `list_states`, `create_state` |
| Labels | `list_labels`, `create_label` |
| Relations | `list_work_item_relations`, `create_work_item_relation` |
| Comments / links | `list_work_item_comments`, `create_work_item_link` |
| Work logs | `list_work_logs`, `create_work_log` |
| Intake | `list_intake_work_items`, `create_intake_work_item` |
| Work item types / properties | `list_work_item_types`, `list_work_item_properties` |
| Pages | `create_workspace_page`, `create_project_page`, `retrieve_project_page` |

## Refusal Policy (Hard Rule)

Before you output any message that says or implies "I don't have Plane tools", "I can't access Plane", "tool not available", or "Plane is not connected":

1. You MUST have run at least **four** distinct `ToolSearch` queries covering the domains relevant to the user's request.
2. You MUST have attempted `select:` form for at least one action name taken from the relevant skill.
3. If the user's request involves multiple domains (e.g., sprint + backlog + work items), you MUST probe each.

Only then is a refusal justified — and it should include the list of probes you ran.

## Integration with Other Skills

All other plane-ops skills reference action names (e.g., `create_cycle`). Resolve those through this bootstrap protocol once per session. Every skill assumes that, by the time its logic runs, the actual tool names for the current instance have been discovered.
