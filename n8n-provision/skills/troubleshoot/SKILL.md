---
name: troubleshoot
description: >
  Diagnose and fix n8n provisioning and import issues. This skill should be used when the user
  encounters "n8n import error", "template deploy failed", "workflow validation error",
  "provisioning troubleshoot", "n8n provision problem", "community node missing",
  "credential not found", "workflow won't activate", "batch deploy failed", or needs help
  debugging n8n workflow import and deployment issues.
---

# Troubleshoot n8n Provisioning

Diagnostic reference for issues encountered during template discovery, workflow import, batch provisioning, and credential setup. All tool references use `~~placeholder` syntax — see CONNECTORS.md for provider fallback.

## Quick Diagnostics

Run these checks first to establish instance state:

```
1. ~~instance_audit → check instance health, version, node inventory
2. ~~workflow_list → list existing workflows, detect conflicts
3. ~~credential_manage → list existing credentials, check types available
```

If the instance is unreachable, check:
- Instance URL is correct and accessible
- API key / authentication is valid
- n8n is running and healthy (check `/healthz` endpoint)

## Deployment Failures

| Error | Cause | Fix |
|-------|-------|-----|
| Template not found (404) | Template ID does not exist in the official library | Verify template ID; it may have been removed or renumbered. Search by keyword instead |
| Deploy timeout | n8n instance is slow or overloaded | Retry with a longer timeout. Check instance resources (CPU/memory) |
| Instance unreachable | Wrong URL, instance down, or network issue | Verify instance URL. Check if n8n is running. Test with `~~instance_audit` |
| API key invalid (401) | Expired or incorrect API key | Regenerate API key in n8n Settings > API. Update MCP server config |
| API key insufficient (403) | API key lacks required permissions | Use an Owner-level API key. Check n8n RBAC settings |
| Rate limit exceeded (429) | Too many API calls in short period | Wait and retry. Space out batch deployments. Check n8n rate limit config |
| Workflow already exists | Name collision with existing workflow | Rename the workflow before import, or append a suffix |
| Import payload too large | Workflow JSON exceeds request size limit | Check n8n's `N8N_PAYLOAD_SIZE_MAX` env var. Increase if needed |

## Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Missing node type | Workflow uses a node not installed on the instance | Install the missing node package. Check `nodes[].type` in the JSON |
| Invalid connections | Connection references a node that doesn't exist | Fix connection `source`/`target` node names to match actual node names |
| Deprecated node | Workflow uses a node type removed in current n8n version | Replace with the successor node. Check n8n migration docs |
| Schema version mismatch | Workflow JSON format doesn't match instance version | Update the workflow JSON format. Older workflows may need `meta.instanceId` |
| Invalid parameter value | Node parameter has wrong type or invalid option | Check node documentation for valid parameter values |
| Expression syntax error | `{{ }}` expression contains invalid JavaScript | Fix the expression. Common: missing `.` accessor, wrong variable name |
| Duplicate node names | Two nodes have the same `name` field | Rename one node to be unique within the workflow |
| Missing required field | A required node parameter is not set | Add the missing parameter. Use `~~template_get` for the complete definition |

## Community Node Issues

| Error | Cause | Fix |
|-------|-------|-----|
| Node type not found | Community node package not installed | Install via n8n Settings > Community Nodes, or `n8n-node-dev install {package}` |
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
| Cannot create credential via API | n8n API doesn't support all credential types programmatically | Create credentials manually in the n8n UI, then reference by ID |
| Credential test fails | Credentials are correct but test endpoint is down | Try using the credential in an actual workflow execution instead |

## Batch Provisioning Issues

| Error | Cause | Fix |
|-------|-------|-----|
| Partial deployment (some workflows failed) | Individual workflow errors during batch | Check each failed workflow's error. Fix and retry individually |
| Naming conflicts | Multiple workflows in the batch have the same name | Add unique suffixes before batch import |
| Webhook path collisions | Two workflows claim the same webhook URL path | Modify webhook paths to be unique. Use prefixes like `/batch-1/...` |
| Credential mapping across batch | Shared credentials not applied to all workflows | After batch import, map credentials to each workflow systematically |
| Tag not applied | Batch tag failed to apply during import | Apply tags after import using workflow update API |
| Import order violation | Workflow depends on another that hasn't been imported yet | Follow dependency-aware import order from BATCH_STRATEGIES.md |

## Version Incompatibilities

| Error | Cause | Fix |
|-------|-------|-----|
| n8n version too old for template | Template uses features from a newer n8n version | Upgrade n8n instance, or find an older version of the template |
| `typeVersion` mismatch | Node `typeVersion` in workflow doesn't match installed node | Update n8n. Or manually downgrade `typeVersion` in the JSON (risky — test thoroughly) |
| API version mismatch | Template uses API v2 features on a v1 instance | Upgrade n8n or adapt the workflow to use v1 API format |
| Workflow format version | Old workflow format missing `meta` or `versionId` fields | Add missing fields: `"meta": {"instanceId": ""}`, `"versionId": ""` |
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
│   → Verify ID, search by keyword, check community sources
├── Import failed?
│   ├── Validation error?
│   │   → Check node types, connections, parameters
│   ├── Permission error?
│   │   → Check API key permissions
│   └── Size error?
│       → Check payload size limits
├── Workflow imported but won't activate?
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
