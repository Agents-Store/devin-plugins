---
name: template-discovery
description: Search the official n8n template library (12,900+ templates). Use when asked to "search n8n templates", "find n8n workflow", "browse n8n template library", "n8n workflow catalog", "discover n8n automation", or need to find a template by keyword, node type, task, category, or architectural pattern.
---

# Template Discovery

Search the official n8n template library. It holds about 12,900 community-contributed workflow templates in 7 top-level categories (31 including subcategories), served by the public API at `api.n8n.io`. Searches use `~~template_search` — see CONNECTORS.md for provider fallback.

See [references/TEMPLATE_API.md](references/TEMPLATE_API.md) for the full API endpoint documentation.

## Two providers, two sizes

| Provider | Covers | Use for |
|----------|--------|---------|
| **n8n-mcp** (`search_templates`, `get_template`) | about 2,350 templates in a local database (roughly 18% of the library), with AI-generated metadata (complexity, setup time, required services) | Fast first pass; metadata filters; node-type search |
| **`api.n8n.io`** (Bash `curl`) | the full library, about 12,900 templates | Anything the local database misses; template IDs found on n8n.io; paid-template detection |

Always try the MCP provider first. **Fall through to `api.n8n.io` when it returns zero results, no relevant match, or `Template <id> not found`** — a template ID taken from an n8n.io URL (for example 2947) is often not in the local database. Keyword mode there is loose (it can return hundreds of weak hits for a specific title), so judge relevance, not just the count.

```bash
# Search the full library (rows max 100, page starts at 1)
curl -s 'https://api.n8n.io/api/templates/search?rows=20&page=1&search=<url-encoded-query>'

# Add a category by NAME (not by number)
curl -s 'https://api.n8n.io/api/templates/search?rows=20&search=<query>&category=AI'
```

The response is `{"totalWorkflows", "workflows": [...], "filters"}`; each item has `id, name, totalViews, purchaseUrl, user, description, createdAt, nodes` and, on most items, `price` (absent on some free ones). Field details are in TEMPLATE_API.md.

## 5 Search Modes (n8n-mcp)

Choose the search mode that best matches the user's intent. Parameter names are those of `search_templates`.

| Mode | Parameters | When to Use |
|------|-----------|-------------|
| **keyword** (default) | `query` | Free-text search over names and descriptions |
| **by_nodes** | `nodeTypes: [...]` (full type with prefix) | Find templates that use specific node types |
| **by_task** | `task` — one of the enum below | Curated templates for a common automation task |
| **by_metadata** | `category` (string), `complexity`, `minSetupMinutes` / `maxSetupMinutes`, `requiredService`, `targetAudience` | Filter by complexity, setup time, service or audience |
| **patterns** | optional `task` | Architecture overview: node frequencies and connection chains — **not** a list of templates |

`task` values: `ai_automation`, `data_sync`, `webhook_processing`, `email_automation`, `slack_integration`, `data_transformation`, `file_processing`, `scheduling`, `api_integration`, `database_operations`.

### keyword (default)

Use for general discovery.

```
search_templates({query: "slack notification github issue"})
```

Keyword mode searches names and descriptions, not node types. Use specific nouns; for node types use `by_nodes`.

### by_nodes

Find templates that use specific node types. Useful when the user already knows which services to connect.

```
search_templates({searchMode: "by_nodes", nodeTypes: ["n8n-nodes-base.slack", "n8n-nodes-base.googleSheets"]})
```

Node type format: `n8n-nodes-base.<nodeName>` for built-in, `@n8n/n8n-nodes-langchain.<nodeName>` for AI nodes. The prefix is required.

### by_task

Pick the closest task from the enum — free text is not accepted in this mode. For free-text intent use keyword mode.

```
search_templates({searchMode: "by_task", task: "email_automation"})
```

### by_metadata

Filter by metadata mined from each template. `category` is a string (for example `"devops"`), not a number.

```
search_templates({searchMode: "by_metadata", category: "devops", complexity: "simple"})
search_templates({searchMode: "by_metadata", requiredService: "openai", maxSetupMinutes: 30})
```

### patterns

Summaries of common workflow shapes, mined from the local database.

```
search_templates({searchMode: "patterns", task: "webhook_processing"})
```

Returns node frequencies and connection chains, not templates. Without `task` this server may answer `Workflow patterns not generated yet` — fall back to a keyword search such as `query: "error handler retry"` or `query: "sub-workflow"`.

## Categories (api.n8n.io)

Categories are a hierarchy: 7 top-level categories with child categories (31 in total). The `category` parameter of the public API takes the category **name**, and a parent includes its children.

Never hardcode category IDs — they changed when the library was reorganised. Read the live list:

```bash
curl -s https://api.n8n.io/api/templates/categories
```

The response is `{"categories": [{id, name, displayName, icon, parent}]}`; `parent` is `null` for top-level entries. Use `name` as the `category` value (`category=AI`, `category=DevOps`).

## Collections

Collections are curated groups of related templates.

```bash
curl -s https://api.n8n.io/api/templates/collections
```

The response is `{"collections": [{id, rank, name, totalViews, createdAt, workflows: [{id}], nodes: []}]}`. A collection lists only template IDs; fetch each one for details. Use collections when the user wants to explore a topic rather than search for a specific workflow.

## Interpreting Results

Each result carries quality signals. Rank candidates using:

| Field (api.n8n.io) | Field (n8n-mcp) | What It Tells You |
|--------------------|-----------------|-------------------|
| `totalViews` | `views` | All-time popularity — higher = more trusted |
| `user.username`, `user.verified` | `author.username`, `author.verified` | Creator identity — verified creators are more reliable |
| `nodes[].name` (for example `n8n-nodes-base.slack`) | `nodes[]` (strings) | Node types used — check for deprecated or community nodes |
| `purchaseUrl`, `price` (search items only) | — | Paid template (see below) |
| `description` | `description` | Workflow summary — read for fit before fetching the full template |
| `createdAt` | `created` | Age — old templates may use outdated nodes |

On `api.n8n.io` the node type is in `nodes[].name`; the `type` key does not exist. `recentViews` and `categories` appear only in the detail endpoint, not in search results.

### Quality heuristics

- **totalViews > 10,000**: Well-established, likely maintained
- **Verified creator**: n8n team or recognized community member
- **Recent `createdAt`**: more likely built on current node versions; older templates often carry nodes that n8n removed or will remove

### Paid templates

The library now has paid templates. In a sample of 500 results about 14% were paid. Their JSON is also served by the public API, but a paid template belongs to its author. **Paid = `purchaseUrl` non-null or `price` > 0; a missing `price` means free** (some free items have no `price` key at all, so do not filter on `price == 0`). When a paid template is the best match, tell the user instead of importing it silently.

Price lives only on **search items** of `api.n8n.io`. The by-ID endpoints and n8n-mcp `get_template` do not carry it. For a bare template ID, first look the item up in `/templates/search` and match it on `id` (recipe: TEMPLATE_API.md, "Paid-template check for a bare template ID"). If no search item matches, say so and ask the user before importing.

## Pagination

n8n-mcp: `limit` (default 20, max 100) and `offset`; read `hasMore` and `total` from the response. `api.n8n.io`: `rows` (max 100) and `page` (1-indexed); `totalWorkflows` is the total count, so `pages = ceil(totalWorkflows / rows)`. Fetch the next page only when the first lacks a good match; narrow with a category or node filter instead of paging through broad queries.

## Search Strategy Sequence

1. Start with a **keyword** search using the user's wording (MCP first).
2. If too many results, narrow with **by_metadata** (MCP) or a `category` name (api.n8n.io).
3. If the user names specific services, use **by_nodes** for exact matches.
4. If the user describes a common task, try **by_task**.
5. If the MCP provider returns nothing relevant, repeat the search against `api.n8n.io`.
6. For architecture questions, use **patterns** (or a keyword search when patterns are unavailable).
7. Review the top 3-5 results by quality signals before fetching the full template.

## After Discovery

Once a template is identified:

```
1. ~~template_get(templateId) → full template with importable JSON
   (n8n-mcp get_template first; on "not found" → curl https://api.n8n.io/api/workflows/templates/<id>)
2. Review node list, credential requirements, complexity, and the price (from the search item; for a bare ID run the paid-template check first)
3. Import: ~~template_deploy for templates in the local database,
   ~~workflow_create for templates fetched from api.n8n.io (see single-workflow-import)
```

If the official library has no match, escalate to the **community-source-discovery** skill.
