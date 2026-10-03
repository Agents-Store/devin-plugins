---
name: troubleshoot
description: >
  Diagnose and fix n8n provisioning and import issues. This skill should be used when the user
  encounters "n8n import error", "template deploy failed", "workflow validation error",
  "provisioning troubleshoot", "n8n provision problem", "community node missing",
  "credential not found", "workflow won't activate", "workflow won't publish", "template not found",
  "batch deploy failed", or needs help
  debugging n8n workflow import and deployment issues.
---

# Troubleshoot n8n Provisioning

Diagnostic reference for issues encountered during template discovery, workflow import, batch provisioning, and credential setup. All tool references use `~~placeholder` syntax — see CONNECTORS.md for provider fallback.

## Quick Diagnostics

Run these checks first to establish instance state:

```
1. ~~instance_health → is the instance reachable, is the API key accepted (status, responseTimeMs)
2. ~~workflow_list → list existing workflows, detect conflicts
3. ~~credential_manage → list existing credentials, check types available
```

`~~instance_health` has no version, uptime or node-inventory fields (n8n stopped reporting its version to API clients in 1.119.0). To see what the key can do, call `GET /api/v1/discover`. Installed community nodes: `GET /api/v1/community-packages`. `~~instance_audit` is a **security** audit — use it for security questions, not for "is it up".

If the instance is unreachable, check:
- Instance URL is correct and accessible
- API key / authentication is valid
- n8n is running and healthy (check `/healthz` endpoint)

## Deployment Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `Template <id> not found` from `get_template` / `n8n_deploy_template` | The template is not in the n8n-mcp local database (about 2,350 of 12,900) | Fetch it from `api.n8n.io`: `curl -s https://api.n8n.io/api/workflows/templates/<id>`, take `.workflow`, and import with `~~workflow_create` (`single-workflow-import`, Path 1b) |
| Template not found (HTTP 404 from `api.n8n.io`) | Template ID does not exist in the official library | Verify template ID; it may have been removed or renumbered. Search by keyword instead |
| Deploy timeout | n8n instance is slow or overloaded | Retry with a longer timeout. Check instance resources (CPU/memory) |
| Instance unreachable | Wrong URL, instance down, or network issue | Verify instance URL. Check if n8n is running. Test with `~~instance_health` |
| API key invalid (401) | Expired or incorrect API key. Every key has a Label and an Expiration; an expired key answers 401 | Create a new key in n8n Settings > n8n API (set a Label and an Expiration). Update the MCP server config |
| API key insufficient (403) | Key scope or user role too low. Scopes exist only on Enterprise — elsewhere a key has the rights of its user | Check the key's scopes and the user's project role. `GET /credentials` (credential list) works only for Owner and Admin; publishing needs the `workflow:activate` scope **and** the `workflow:publish` permission |
| `PUBLISH_FORBIDDEN` (403, n8n 2.39+) | The key or user may edit a workflow but not publish it | Add `workflow:activate` to the key and `workflow:publish` to the user's role, or publish in the editor. Retrying with the same credentials will not help |
| Publish refused (409) | An open workflow review blocks publishing, or the webhook path collides with another workflow | Resolve the review, or change the webhook path, then publish again |
| Rate limit exceeded (429) | Too many API calls in short period | Wait and retry. Space out batch deployments. Check n8n rate limit config |
| Workflow already exists | Name collision with existing workflow | Rename the workflow before import, or append a suffix |
| Import payload too large | Workflow JSON exceeds request size limit | Check n8n's `N8N_PAYLOAD_SIZE_MAX` env var. Increase if needed |

## Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Missing node type | Workflow uses a node not installed on the instance | Install the missing node package. Check `nodes[].type` in the JSON |
| Invalid connections | Connection references a node that doesn't exist | Fix connection `source`/`target` node names to match actual node names |
| Deprecated node | Workflow uses a node type removed in the current n8n version. n8n 2.0 removed Start, Spontit, crowd.dev, Kitemaker, Automizy and the Pyodide Python node; n8n 3.0 (October 2026) removes Function, Function Item, Item Lists, Cron, HTML Extract, legacy OpenAI nodes, AI Agent v1 and others | Replace with the successor node (see `workflow-analysis`, Step 6). On a 2.x instance Settings > Migration Report lists affected nodes |
| `executeCommand` or `localFileTrigger` fails to import or load | Both are switched off by default since n8n 2.0 (`NODES_EXCLUDE`) | Prefer a different node. The instance owner can re-enable them with `NODES_EXCLUDE="[]"` — a security decision, not an import fix |
| Create fails with an unknown or read-only property | The payload carried `id`, `meta`, `tags`, `active` or `versionId`; the create schema rejects unknown properties and those are read-only | Rebuild the payload from `name`, `nodes`, `connections` and `settings` only |
| Invalid parameter value | Node parameter has wrong type or invalid option | Check node documentation for valid parameter values |
| Expression syntax error | `{{ }}` expression contains invalid JavaScript | Fix the expression. Common: missing `.` accessor, wrong variable name |
| Duplicate node names | Two nodes have the same `name` field | Rename one node to be unique within the workflow |
| Missing required field | A required node parameter is not set | Add the missing parameter. Use `~~template_get` for the complete definition |

## Community Node Issues

| Error | Cause | Fix |
|-------|-------|-----|
| Node type not found | Community node package not installed | Install via n8n Settings > Community Nodes (Owner or Admin), `POST /api/v1/community-packages` with `{name, version}`, the `N8N_COMMUNITY_PACKAGES` environment variable (n8n 2.21+; removes packages not on the list), or `npm i` in the n8n nodes directory plus a restart (required for queue mode and private packages). `n8n-node-dev` is a node-development CLI and cannot install packages |
| Version mismatch | Installed node version doesn't match workflow expectations | Update the community node to the version the workflow expects |
| Community node deprecated | Package removed from npm or abandoned | Find an alternative node. Check npm for fork or replacement |
| Node crashes on execution | Bug in community node code | Check node's GitHub issues. Downgrade to a stable version. Report the bug |
| `typeVersion` too high | Workflow built with newer node version than installed | Update the community node package to latest |

## Credential Issues

| Error | Cause | Fix |
|-------|-------|-----|
| Credential type not found | Workflow references a credential type not available | The credential type may require a community node. Install the corresponding node package |
| OAuth token expired | OAuth2 credential needs re-authorization | Re-authorize in n8n UI: Credentials > Edit > Reconnect |
| Wrong credential schema | Credential fields don't match what the node expects | Delete and recreate the credential with the correct type |
| Credential not mapped | Workflow imported without credential assignments | Edit each node in the workflow, select the correct credential |
| Cannot create credential via API | OAuth2 credentials need a browser consent; other types failed validation | Token, key and basic-auth credentials: `~~credential_manage` — `getSchema` for the type, then `create`. OAuth2: create in the n8n UI and authorize there, then reference by ID |
| Credential test fails | Credentials are correct but test endpoint is down | Try using the credential in an actual workflow execution instead |

## Batch Provisioning Issues

| Error | Cause | Fix |
|-------|-------|-----|
| Partial deployment (some workflows failed) | Individual workflow errors during batch | Check each failed workflow's error. Fix and retry individually |
| Naming conflicts | Multiple workflows in the batch have the same name | Add unique suffixes before batch import |
| Webhook path collisions | Two workflows claim the same webhook URL path | Modify webhook paths to be unique. Use prefixes like `/batch-1/...` |
| Credential mapping across batch | Shared credentials not applied to all workflows | After batch import, map credentials to each workflow systematically |
| Tag not applied | The deploy tools take no tags | After the deploy call `~~workflow_update` with operation `addTag` (list tags with `n8n_list_catalog({kind: "tags"})`) |
| Import order violation | Workflow depends on another that hasn't been imported yet | Follow dependency-aware import order from BATCH_STRATEGIES.md |

## Version Incompatibilities

| Error | Cause | Fix |
|-------|-------|-----|
| n8n version too old for template | Template uses features from a newer n8n version | Upgrade n8n instance, or find an older version of the template |
| `typeVersion` mismatch | Node `typeVersion` in workflow doesn't match what the instance supports | Deploy with `autoUpgradeVersions` (default on in `n8n_deploy_template`), or run `~~workflow_autofix` (`typeversion-upgrade` / `typeversion-correction`) in preview mode and apply after review. Do not edit `typeVersion` by hand or add `meta` / `versionId` — those are read-only on create |
| Sub-workflow references | Workflow calls sub-workflows by ID that don't exist | Import sub-workflows first, then update the parent's sub-workflow references |

## Web Scraping Failures (Community Source Discovery)

| Error | Cause | Fix |
|-------|-------|-----|
| Scrape returns HTML, not JSON | Page uses JavaScript rendering | Try a different scrape provider (Firecrawl handles JS better). Or use raw.githubusercontent.com URLs |
| JSON parse error | Scraped content contains extra HTML/text around the JSON | Extract only the JSON portion. Look for `{"nodes":` as the start marker |
| Rate limited by GitHub | Too many raw.githubusercontent.com requests | Wait and retry. Or use GitHub API with authentication for higher limits |
| Workflow JSON incomplete | Page didn't fully load, or JSON was truncated | Retry the scrape. Try a different URL format (e.g., GitHub API instead of raw) |
| Community platform down | Third-party site is temporarily unavailable | Try the next platform in priority order (see COMMUNITY_PLATFORMS.md) |

## Diagnostic Decision Tree

```
Problem reported
├── Instance unreachable?
│   → Check URL, check if n8n is running, check API key
├── Template not found?
│   → get_template "not found": fetch from api.n8n.io; HTTP 404 there: verify ID, search by keyword, check community sources
├── Import failed?
│   ├── Validation error?
│   │   → Check node types, connections, parameters
│   ├── Permission error?
│   │   → Check API key permissions
│   └── Size error?
│       → Check payload size limits
├── Workflow imported but won't publish (or does nothing when published)?
│   ├── Publish refused?
│   │   → PUBLISH_FORBIDDEN: key scope / project permission; 409: review or webhook collision
│   ├── Missing credentials?
│   │   → Map credentials in n8n UI
│   ├── Node error?
│   │   → Check for deprecated/missing nodes
│   └── Expression error?
│       → Fix expression syntax
└── Batch deployment partial failure?
    → Check individual errors, fix and retry failed workflows
```

## When to Escalate

- **Instance crashes during import** — likely a memory issue. Check n8n container resources
- **Persistent API 500 errors** — n8n server-side issue. Check n8n logs
- **Credential type completely missing** — may require n8n source-level investigation
- **All providers fail for web scraping** — network or firewall issue on the user's side
