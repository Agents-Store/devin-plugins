---
name: template-discovery
description: Search the official n8n template library (9,166+ templates). Use when asked to "search n8n templates", "find n8n workflow", "browse n8n template library", "n8n workflow catalog", "discover n8n automation", or need to find a template by keyword, node type, task, category, or architectural pattern.
---

# Template Discovery

Search the official n8n template library at api.n8n.io. The library contains 9,166+ community-contributed workflow templates across 31 categories. All searches use `~~template_search` — see CONNECTORS.md for provider fallback.

See [references/TEMPLATE_API.md](references/TEMPLATE_API.md) for full API endpoint documentation.

## 5 Search Modes

Choose the search mode that best matches the user's intent.

| Mode | When to Use | Example Query |
|------|-------------|---------------|
| **keyword** | Free-text search by name/description | `"slack notification"`, `"backup database"` |
| **by_nodes** | Find templates using specific node types | `"n8n-nodes-base.slack"`, `"n8n-nodes-base.googleSheets"` |
| **by_task** | Describe what the workflow should accomplish | `"send email when form submitted"` |
| **by_metadata** | Filter by category, complexity, popularity | `category=AI`, `category=DevOps` |
| **patterns** | Find architectural patterns (fan-out, polling, etc.) | `"error handling"`, `"retry pattern"`, `"sub-workflow"` |

### keyword (default)

Use for general discovery. Pass free-text to `~~template_search`.

```
~~template_search("slack notification when new github issue")
```

Combine terms for precision: `"slack AND github AND notification"` narrows better than single words.

### by_nodes

Find templates that use specific n8n node types. Useful when the user already knows which services to connect.

```
~~template_search(nodes=["n8n-nodes-base.slack", "n8n-nodes-base.googleSheets"])
```

Node type format: `n8n-nodes-base.<nodeName>` for built-in, `@n8n/n8n-nodes-langchain.<nodeName>` for AI nodes.

### by_task

Describe the desired outcome in plain language. The API performs semantic matching.

```
~~template_search(task="automatically post new blog articles to social media")
```

Best for users who describe what they want without knowing n8n terminology.

### by_metadata

Filter by category ID and/or other metadata fields.

```
~~template_search(category=25)  # AI category
~~template_search(category=2)   # Sales category
```

### patterns

Search for architectural patterns used across workflows.

```
~~template_search("webhook error handler retry")
~~template_search("fan-out merge pattern")
~~template_search("sub-workflow orchestration")
```

## Categories (31 total)

Key categories: Marketing (1), Sales (2), DevOps (4), Engineering (5), Support (6), AI (25), Databases (13), Security (26), Building Blocks (30), Utilities (31).

Fetch the full live list from `GET /templates/categories` — IDs may shift over time.

## Collections

Collections are curated groups of related templates (e.g., "Getting Started", "AI Agents", "Marketing Automation").

```
Fetch collections → browse collection → pick template
```

Use collections when the user wants to explore a topic rather than search for a specific workflow.

## Interpreting Results

Each result contains quality signals. Rank candidates using:

| Field | What It Tells You |
|-------|-------------------|
| `totalViews` | All-time popularity — higher = more trusted |
| `recentViews` | Trending now — high recent + low total = rising star |
| `user.username` | Creator identity — verified/prolific creators are more reliable |
| `nodes[].type` | Node types used — check for deprecated or community nodes |
| `description` | Workflow summary — read for fit before fetching full template |

### Quality heuristics

- **totalViews > 10,000**: Well-established, likely maintained
- **recentViews > 500**: Actively used, probably compatible with current n8n
- **Verified creator**: n8n team or recognized community member

## Pagination

Results default to 20 per page. Check `totalWorkflows` to know total pages. Fetch page 2+ only when page 1 lacks a good match. For broad queries, filter by category first to reduce noise.

## Search Strategy Sequence

1. Start with **keyword** search using the user's natural language.
2. If too many results, narrow with **by_metadata** (add category filter).
3. If too few results, broaden to **by_task** (semantic matching).
4. If the user names specific services, try **by_nodes** for exact matches.
5. For architecture questions, use **patterns** mode.
6. Review top 3-5 results by quality signals before fetching full template.

## After Discovery

Once a template is identified:

```
1. ~~template_get(id) → fetch full template with importable JSON
2. Review node list, credential requirements, complexity
3. ~~template_deploy(id) → import to the n8n instance (handles auto-fix)
```

If the official library has no match, escalate to the **community-source-discovery** skill.
