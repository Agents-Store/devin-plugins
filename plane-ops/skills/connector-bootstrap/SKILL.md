---
name: connector-bootstrap
description: MUST be consulted at the start of ANY Plane-related request before answering the user or declaring tools unavailable. Discovers Plane tools across any MCP server, connector, or instance naming convention - the resource tools of Plane MCP 0.3.0 and later (one tool per resource with an `action` parameter, which every other plane-ops skill and command is written for) - and carries the fallback translation for servers older than 0.3.0 that expose one tool per operation. Use when the user mentions sprint, backlog, work item, cycle, epic, module, milestone, initiative, project, issue, ticket, task, standup, retro, estimate, roadmap, board, Plane, or any work-management operation, even if Plane tools are not visible yet. Also use before saying "I don't have access to Plane tools" or "tool not available".
---

# Plane Connector Bootstrap

This skill ensures Plane tools are reliably discovered in any environment: cowork mode, remote MCP, local MCP, Claude connectors, custom proxies, or self-hosted instances. Tool names vary by environment and by server version - **never assume tools are missing without probing first**.

## Two Tool Surfaces

| Surface | Where you meet it | Tool shape |
|---------|-------------------|------------|
| **Resource tools** (what this plugin is written for) | Official Plane MCP server 0.3.0 and later (hosted or `uvx plane-mcp-server`) | One tool per resource - `workitem`, `cycle`, `module`, `page`, ... - and an `action` parameter selects the operation: `cycle(action="list", project_id=...)` |
| **Per-operation tools** (fallback) | Servers before 0.3.0 and other connectors | One tool per operation: `list_cycles`, `create_work_item`, ... See "Fallback: Servers Older Than 0.3.0" below |

The marker of the resource surface is a tool named `workitem` (or `cycle`) whose schema has an `action` enum. On the official server the old per-operation names are still callable as hidden aliases, but they are **not advertised**: a probe for `create_cycle` or `list_work_items` returns nothing there, and an agent that only probes legacy names wrongly concludes that Plane is not connected.

Every skill and command in this plugin writes calls as `resource(action=..., ...)`. On the resource surface call them exactly so; only on a per-operation server translate them with the fallback table.

## Why This Skill Exists

In cowork mode and certain remote setups, MCP/connector tools are **deferred**: Claude only sees their names in a system reminder until `ToolSearch` loads their schemas. A user request mentioning "sprint" or "work item" may arrive before the Plane tools are materialized into the tool set. **You must probe before refusing.**

Symptoms this skill prevents:
- Responding "I don't have access to Plane tools" when they are in fact available as deferred tools.
- Probing only per-operation names and missing the resource tools of Plane MCP 0.3+.
- Missing tools because the server name differs (`mcp__plane__*`, `mcp__<any>__plane-i-*`, `plane_*`, `connector-plane-*`, or fully custom).
- Only finding tools for one instance when multiple Plane workspaces are connected.

## Mandatory Bootstrap Protocol

Execute these steps **before** answering any Plane-related user request.

### Step 1 - Probe with ToolSearch

Start with the probes that find the resource surface, and do not stop at the first empty result:

```
ToolSearch(query="plane", max_results=20)
ToolSearch(query="workitem cycle module", max_results=20)
```

If either returns tools named `...__workitem`, `...__cycle`, `...__project`, you are on the resource surface: note the server segment of the name, then load the schemas you need with the `select:` form:

```
ToolSearch(query="select:mcp__<server>__workitem,mcp__<server>__cycle,mcp__<server>__project", max_results=10)
```

If the user mentioned a specific concept, add a targeted query:

```
ToolSearch(query="+module", max_results=10)
ToolSearch(query="+milestone", max_results=10)
ToolSearch(query="+initiative", max_results=10)
ToolSearch(query="+intake", max_results=10)
ToolSearch(query="+page", max_results=10)
ToolSearch(query="+release", max_results=10)
```

Fallback probes for older servers and other connectors (per-operation names):

```
ToolSearch(query="work_item cycle project", max_results=20)
ToolSearch(query="list_projects create_work_item", max_results=20)
ToolSearch(query="sprint backlog issue", max_results=20)
```

There is no epic tool on the official server: an epic is a `workitem` whose type is named "Epic" (`workitem_type(action=resolve, project_id, name="Epic")` returns the `type_id`, then `workitem(action=create, ..., type_id=<id>)`; list epics with `workitem(action=list, pql='type = "<type-id>"')`; children use the `parent` field; link an epic to an initiative with `initiative(action=manage_workitems, add_ids=[<epic work item id>])`).

### Step 2 - Match by Resource Name, Then by Action Suffix

**Resource surface.** The tool name is `mcp__<server>__<resource>`; the operation goes into the `action` parameter. The server segment is whatever the user named their connection (`plane`, `plane-cloud`, `mcp__plugin_...`): never hardcode it. Resource names:

`workitem`, `cycle`, `module`, `milestone`, `initiative`, `intake`, `state`, `label`, `member`, `page`, `project`, `workspace`, `work_log`, `workitem_type`, `workitem_property`, `workitem_relation`, `workitem_comment`, `workitem_link`, `workitem_activity`, `workitem_attachment`, `project_estimate`, `release`, `release_tag`, `release_label`, `customer`, `customer_property`, `customer_request`, `collection`, `template`, and `get_pql_reference` (no `action`: it returns the syntax of the `pql` filter).

Every tool's own description lists its actions with their required and optional parameters. That generated description is the authoritative reference at call time - read it before the first call on a resource.

**Per-operation surface.** Tools may appear under **any** of these shapes (non-exhaustive):

- `mcp__<provider>__<prefix>-<action>`
- `mcp__<instance-slug>__<action>`
- `plane_<action>`, `connector_plane_<action>`, `<workspace>-plane-<action>`
- A fully custom name chosen by the connector author

**Match per-operation tools by the action suffix** (e.g., `create_cycle`, `list_work_items`). The prefix is environment-dependent and MUST NOT be hardcoded in this plugin or in your responses.

### Step 3 - Handle Multiple Instances

If the user has multiple Plane workspaces/instances connected, `ToolSearch` will return several tools with the same resource or action name but different server segments. In that case:

1. List the discovered instances to the user by their server segment/slug.
2. Ask which instance to operate on (use `AskUserQuestion` if available).
3. Remember the chosen instance for the rest of the conversation.
4. If only one instance matches, proceed without asking.

### Step 4 - Cache Discovered Names for the Session

Once you have resolved the actual tool names, keep them in working memory for the remainder of the conversation. Do **not** re-probe for every call in the same session unless the user switches instances or a call fails with "tool not found".

### Step 5 - Only Then Decide Whether Tools Are Missing

You may conclude "Plane tools are not connected" **only after** Steps 1-3 return no matches across all query variants. When reporting this to the user, say what you probed and suggest how to connect Plane (see "How to Connect Plane" below).

## Calling Conventions of the Resource Surface

- **Scope.** Supply `project_id` for a project's own set; omit it to address the workspace (`workitem list`, `workitem count`, `page`, `state`, `workitem_type`). A wrong scope still succeeds against the other scope, so check which one you meant.
- **Declared parameters only.** Parameters are validated against the action's declared set; an extra or misspelled parameter is an error, not a silent drop. When a call is rejected, re-read the tool description rather than guessing. The id of a work item is `workitem_id` (not `work_item_id`).
- **Filters and counts.** `workitem` `list` / `list_archived` / `count` and `cycle` / `module` `list_workitems` take a `pql` filter (Plane Query Language, at most 5 conditions; call `get_pql_reference` for the syntax). `workitem(action=count, group_by=...)` returns aggregates without listing items. Prefer both to listing everything and filtering client-side.
- **Pagination.** List actions that take `cursor` / `per_page` return an envelope with `results` and `next_cursor`; pass `next_cursor` back as `cursor` to read the next page, and do not mistake a first page for the whole set. `project(action=list)` is paginated too. `initiative(action=list)` returns everything in one call.
- **Plural actions.** `manage_workitems` takes `add_ids` and/or `remove_ids`, returns nothing, and is read back with `list_workitems`.
- **Archive and delete.** `archive` is an action (not a flag); `delete` is permanent. The plugin's PreToolUse hook makes Claude Code show its permission dialog for delete-type actions (`delete`, `remove_*`, `detach*`, `delete_point`, `delete_option`, `delete_value`, `delete_definition`) and for `manage_workitems` calls that carry `remove_ids` (`unlink_ids` on `customer`), and adds a warning to the context on `archive`; name the target in your message before calling, and do not retry a delete the user declined.

## How to Connect Plane

The plugin ships no MCP server; the user connects Plane one of these ways:

| Way | Command or setting |
|---|---|
| Hosted, OAuth (recommended for interactive use) | `claude mcp add --transport http plane https://mcp.plane.so/http/mcp`, then run `/mcp` in a session and authenticate |
| Hosted, personal access token (CI, headless, shared setups) | URL `https://mcp.plane.so/http/api-key/mcp` with headers `Authorization: Bearer ${PLANE_PAT}` and `x-workspace-slug: <workspace-slug>`; the older `x-api-key` header no longer works |
| Self-hosted Plane or offline (stdio) | `uvx plane-mcp-server stdio` with `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, and `PLANE_BASE_URL` for the self-hosted URL |

The hosted server cannot reach private self-hosted instances, and its OAuth flow is not available on Plane Community Edition; use stdio there. The SSE endpoint and the npm package `@makeplane/plane-mcp-server` are deprecated. Name the connection with `plane` in it (for example `plane`, `plane-cloud`): the plugin's safety hook only watches servers whose name contains `plane`.

## Refusal Policy (Hard Rule)

Before you output any message that says or implies "I don't have Plane tools", "I can't access Plane", "tool not available", or "Plane is not connected":

1. You MUST have run at least **four** distinct `ToolSearch` queries, including `plane` and `workitem cycle module`, and covering the domains relevant to the user's request.
2. You MUST have attempted the `select:` form at least once - for the resource tools (`mcp__<server>__workitem`) if a server segment is known, otherwise for a per-operation name such as `select:list_projects`.
3. You MUST have tried at least one per-operation probe (`list_projects create_work_item`) in addition to the resource probes.
4. If the user's request involves multiple domains (e.g., sprint + backlog + work items), you MUST probe each.

Only then is a refusal justified - and it should include the list of probes you ran and the connection options above.

## Fallback: Servers Older Than 0.3.0 (Per-Operation Tools)

Use this section **only** when the probes find per-operation tools and no resource tools. Every other plane-ops skill and command is written as `resource(action=...)`; translate each call with the table. Names marked with an asterisk exist only on other connectors (never on the official server, not even as hidden aliases); the unmarked names are the official server's pre-0.3.0 tools. Upgrading the server to 0.3.0 or later is the better fix.

| Resource call (as written in this plugin) | Per-operation tool |
|---|---|
| `project(action=list\|retrieve\|create\|update\|delete)` | `list_projects` / `retrieve_project` / `create_project` / `update_project` / `delete_project` |
| `project(action=get_features\|update_features)` | `get_project_features`\* / `update_project_features` |
| `project(action=archive\|unarchive)`, `project(action=worklog_summary)` | `manage_project_archive` (`archive=true\|false`), `get_project_worklog_summary` |
| `workspace(action=get_features\|update_features)` | `get_features` or `get_workspace_features`\* / `update_workspace_features` |
| `member(action=me\|list_workspace\|list_project)` | `get_me` / `get_workspace_members` / `get_project_members` |
| `workitem(action=list\|list_archived\|search\|retrieve\|create\|update\|delete)` | `list_work_items` / `list_archived_work_items` / `search_work_items` / `retrieve_work_item` / `create_work_item` / `update_work_item` / `delete_work_item` |
| `workitem(action=retrieve_by_identifier, workitem_identifier="PROJ-42")` | `retrieve_work_item_by_identifier` with the identifier split: `project_identifier="PROJ"`, `issue_identifier=42` (integer) |
| `workitem(action=count\|archive\|manage_assignee\|manage_label)` | `count_work_items` / `manage_work_item_archive` / `manage_work_item_assignee` / `manage_work_item_label` (official pre-0.3.0 only); other connectors have no equivalent: count and edit client-side from the listed items |
| `cycle(action=list\|retrieve\|create\|update\|delete)` | `list_cycles` / `retrieve_cycle` / `create_cycle` / `update_cycle` / `delete_cycle` |
| `cycle(action=list_workitems\|transfer_workitems\|complete)` | `list_cycle_work_items` / `transfer_cycle_work_items` / `complete_cycle` (official), or `update_cycle` with `end_date` set to today where there is no `complete_cycle` |
| `cycle(action=manage_workitems, add_ids\|remove_ids)` | `manage_cycle_work_items` (official), or `add_work_items_to_cycle`\* (`issue_ids`, plural array) / `remove_work_item_from_cycle`\* |
| `cycle(action=list, archived=true)`, `cycle(action=archive\|unarchive)` | `list_archived_cycles`\*, `archive_cycle`\* / `unarchive_cycle`\*, or `manage_cycle_archive` (official, `archive=true\|false`) |
| `module(action=list\|retrieve\|create\|update\|delete)` | `list_modules` / `retrieve_module` / `create_module` / `update_module` / `delete_module` |
| `module(action=list_workitems\|manage_workitems)` | `list_module_work_items` / `manage_module_work_items` (official), or `add_work_items_to_module`\* (`issue_ids`) / `remove_work_item_from_module`\* |
| `module(action=list, archived=true)`, `module(action=archive\|unarchive)` | `list_archived_modules`\*, `archive_module`\* / `unarchive_module`\*, or `manage_module_archive` (official) |
| `milestone(action=list\|retrieve\|create\|update\|delete\|list_workitems)` | `list_milestones` / `retrieve_milestone` / `create_milestone` / `update_milestone` / `delete_milestone` / `list_milestone_work_items` |
| `milestone(action=manage_workitems)` | `manage_milestone_work_items` (official), or `add_work_items_to_milestone`\* / `remove_work_items_from_milestone`\* |
| `initiative(action=list\|retrieve\|create\|update\|delete\|list_projects)` | `list_initiatives` / `retrieve_initiative` / `create_initiative` / `update_initiative` / `delete_initiative` / `list_initiative_projects` |
| `initiative(action=add_projects\|remove_projects)`, `initiative(action=manage_workitems)` | `manage_initiative_projects` (`action=add\|remove`), `add_epic_to_initiative`\* |
| epics: `workitem_type(action=resolve, name="Epic")` + `workitem(...)` | `list_epics`\* / `create_epic`\* / `retrieve_epic`\* / `update_epic`\* / `delete_epic`\* where the connector has them: they are that connector's native epic tools, use them as they are |
| `intake(action=list\|retrieve\|create\|update\|delete)` | `list_intake_work_items` / `retrieve_intake_work_item` / `create_intake_work_item` / `update_intake_work_item` / `delete_intake_work_item` |
| `state(action=...)`, `label(action=...)` | `list_states` / `retrieve_state` / `create_state` / `update_state` / `delete_state`; `list_labels` / `retrieve_label` / `create_label` / `update_label` / `delete_label` |
| `workitem_relation(action=list\|create\|delete)`, `..._definition` actions | `list_work_item_relations` / `create_work_item_relation` / `remove_work_item_relation`; `list_work_item_relation_definitions` / `create_..._definition` / `update_..._definition` / `delete_..._definition` |
| `workitem_comment(action=...)`, `workitem_link(action=...)` | `list\|retrieve\|create\|update\|delete_work_item_comment`; `list\|retrieve\|create\|update\|delete_work_item_link` |
| `workitem_activity(action=list\|retrieve)`, `work_log(action=...)` | `list_work_item_activities` / `retrieve_work_item_activity`; `list_work_logs` / `create_work_log` / `update_work_log` / `delete_work_log` |
| `workitem_type(action=...)`, `workitem_property(action=...)` | `list\|retrieve\|resolve\|create\|update\|delete_work_item_type`, `import_work_item_types_to_project`; `list\|retrieve\|create\|update\|delete_work_item_property` plus the `..._property_option`, `..._property_value` and `manage_work_item_type_properties` tools |
| `page(action=create\|retrieve\|list)` | `create_page` / `retrieve_page` / `list_pages` (official), or `create_project_page`\* / `create_workspace_page`\* / `retrieve_project_page`\* / `retrieve_workspace_page`\* |
| `page(action=update\|archive\|delete\|set_collection\|attach_to_workitem)` | `attach_page_to_work_item` / `detach_page_from_work_item` exist on the official server; other page operations do not: tell the user to edit, archive or delete in the Plane web UI |
| `project_estimate(action=...)` | `get_project_estimate`, `create\|update\|delete_project_estimate`, `link_estimate_to_project`, `..._project_estimate_point(s)` (official) |

No per-operation equivalent exists for `release`, `release_tag`, `release_label`, `customer*`, `collection`, `template`, `workitem_attachment`, the `pql` filter and `workitem(action=count)` aggregates on other connectors: say so and filter, count or write release notes client-side (a page built from the listed work items).

### Parameter differences on per-operation servers

The resource surface fixes its parameter names; per-operation servers use their own. Before the first mutation on such a server, inspect the tool's JSON Schema and use the schema's names. Typical variants:

| Resource surface | Per-operation servers |
|---|---|
| `workitem_id` | `work_item_id` (the hidden aliases of the official server keep it too) |
| `state`, `labels`, `type_id`, `parent` | `state_id` or `state`, `label_ids` or `labels`, `type`, `parent_id` or `parent` |
| `add_ids` / `remove_ids` | `issue_ids` (plural array) |
| `workitem_ids` on `workitem_relation(action=create)` | `issues` (plural array), `work_item_id` for the id |
| `intake(action=create, name, ...)` flat fields | a single `data` object wrapping the work item fields |
| `workitem_link(action=create, url, title)` | some connectors accept `url` only; the title is then taken from the target page |
| `milestone` `title` | `title` on most deployments, `name` on a few |

Known quirks of older servers and bridges:
- **Archive of an active cycle or module** is rejected with HTTP 400 (it needs a completed state or a past `end_date`); on 0.3.0 and later `cycle(action=archive)` ends a running cycle first.
- **List-typed parameters.** Some MCP bridges fail to serialize arrays or objects (`Input should be a valid list`). Try the native list, then a JSON-encoded string, then an array of objects (`[{"id": "..."}]`); if all fail, do the operation in the Plane UI and tell the user.
- **`update_module`** may return a stub with null fields even when the update succeeded: read it back with `retrieve_module`.
- **No `pql` and no `count`.** List with the available filters (or the whole project) and filter client-side; count from the listed items.

## Integration with Other Skills

All other plane-ops skills and commands write resource calls (`cycle(action=create, ...)`). Resolve the tool names through this bootstrap protocol once per session; on a per-operation server translate each call with the fallback table above. Every skill assumes that, by the time its logic runs, the actual tool names for the current instance have been discovered.
