# n8n Template API Reference

Public REST API for the official n8n template library hosted at `api.n8n.io`. It covers the **whole** library (about 12,900 templates), unlike the template database inside n8n-mcp (about 2,350). Use it as the fallback when `search_templates` finds nothing or `get_template` answers `Template <id> not found`.

Shapes below were checked against the live API on 2026-10-02.

## Base URL

```
https://api.n8n.io/api
```

No authentication required for reading. All endpoints return JSON. An unknown template ID answers HTTP 404.

## Endpoints at a glance

| Need | Endpoint | Where the workflow JSON is |
|------|----------|----------------------------|
| Search | `GET /templates/search` | — (search items carry no workflow JSON) |
| Importable workflow, minimal wrapper | `GET /workflows/templates/<id>` | `.workflow` |
| Workflow plus full metadata | `GET /templates/workflows/<id>` | `.workflow.workflow` |
| Categories | `GET /templates/categories` | — |
| Collections | `GET /templates/collections` | — |

## Search Templates

```
GET /templates/search?search=<query>&rows=20&page=1&category=<name>
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Free-text query (URL-encode it) |
| `rows` | integer | 20 | Results per page — **max 100** (a larger value answers HTTP 400) |
| `page` | integer | 1 | Page number (1-indexed) |
| `category` | string | — | Category **name**, for example `AI` or `DevOps`. A parent category includes its children. A numeric category ID matches nothing (0 results), while the name `AI` returns thousands |

**Response:**

```json
{
  "totalWorkflows": 12918,
  "workflows": [
    {
      "id": 2947,
      "name": "National Weather Service 7-day forecast in Slack",
      "totalViews": 15420,
      "price": 0,
      "purchaseUrl": null,
      "description": "…",
      "createdAt": "2025-02-19T21:15:27.390Z",
      "user": { "id": 1, "name": "…", "username": "…", "bio": "…", "verified": true, "links": [], "avatar": "…" },
      "nodes": [
        {
          "id": 40,
          "name": "n8n-nodes-base.slack",
          "displayName": "Slack",
          "typeVersion": 2,
          "icon": "…", "codex": {}, "group": [], "defaults": {}, "iconData": {}, "nodeCategories": []
        }
      ]
    }
  ],
  "filters": [ { "counts": [ { "count": 9, "highlighted": "AI", "value": "AI" } ] } ]
}
```

Notes on the items:

- The top-level key is `workflows` (not `data`); `totalWorkflows` is the match count.
- A search item has the keys `id, name, totalViews, purchaseUrl, user, description, createdAt, nodes`, plus `price` on most items. `purchaseUrl` is always present; **`price` is absent on some free items** (18 of the first 100 results had no `price` key). It has **no** `recentViews` and **no** `categories` — those are in the detail endpoint.
- `nodes[].name` is the node type (`n8n-nodes-base.slack`). There is no `type` key. `displayName` is the human label.
- **Paid or free:** a template is paid when `purchaseUrl` is non-null **or** `price` > 0. A missing `price` means free, and `price: 0` means free — do not filter on `price == 0`, it drops the free items that carry no `price` key. A sample of 500 results held about 14% paid templates. Tell the user before importing a paid template.
- `filters[].counts` lists category names with hit counts for the current query — handy for narrowing.

## Paid-template check for a bare template ID

`price` and `purchaseUrl` exist **only on search items**. Neither by-ID endpoint carries them — the wrapper returns just `{id, name, workflow}` and the detail endpoint has no price fields — and n8n-mcp's `get_template` has none either (nor does `search_templates` offer a price field). So when you start from a bare ID (`/n8n-provision:deploy-template <id>`, `analyze-workflow <id>`, an ID from an n8n.io URL), look the template up in the search first, whichever provider will later supply the workflow JSON:

```bash
# 1. Title of the template (wrapper endpoint)
curl -s https://api.n8n.io/api/workflows/templates/<id> -o /tmp/template-<id>.json
# 2. Search for that title and match the item on id
curl -s "https://api.n8n.io/api/templates/search?rows=20&search=$(python3 -c 'import sys,json,urllib.parse;print(urllib.parse.quote(json.load(sys.stdin)["name"]))' < /tmp/template-<id>.json)" \
  | python3 -c 'import sys,json;ws=json.load(sys.stdin)["workflows"];hit=[w for w in ws if w["id"]==<id>];print(json.dumps({"price":hit[0].get("price"),"purchaseUrl":hit[0].get("purchaseUrl")}) if hit else "NO MATCH")'
```

Reading the result: `purchaseUrl` non-null or `price` > 0 means **paid**; `price` null (key missing) with `purchaseUrl` null means **free**. Checked live: template 10132 returns `price` 5 and a `purchaseUrl`, while its wrapper has no price at all; template 6270 returns no `price` key and `purchaseUrl` null (free).

If the output is `NO MATCH` (the title is ambiguous or too generic to rank the template into the first 20 hits, or the wrapper returned 404), you cannot tell whether it is paid: say so and **ask the user before importing**. Do not treat "no data" as "free".

## Get a Template

Two endpoints return template details. They differ in nesting:

### Wrapper `GET /workflows/templates/<id>` — use this for import

```
GET /workflows/templates/<id>
```

**Response:**

```json
{
  "id": 2947,
  "name": "National Weather Service 7-day forecast in Slack",
  "workflow": {
    "id": "…", "name": "…", "active": true, "meta": {}, "tags": [], "versionId": "…",
    "nodes": [ ... ],
    "connections": { ... },
    "settings": { "executionOrder": "v1" },
    "pinData": {}
  }
}
```

The workflow JSON is `.workflow`. It still carries source-instance fields (`id`, `active`, `meta`, `tags`, `versionId`) that must not go to the target instance.

```bash
curl -s https://api.n8n.io/api/workflows/templates/<id> -o /tmp/template-<id>.json
python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["id"], d["name"], list(d["workflow"]))' < /tmp/template-<id>.json
```

### Detail `GET /templates/workflows/<id>` — use this for metadata

```
GET /templates/workflows/<id>
```

**Response** (single top-level key):

```json
{
  "workflow": {
    "id": 2947,
    "name": "…",
    "views": 0, "recentViews": 0, "totalViews": 0,
    "createdAt": "…",
    "description": "…",
    "lastUpdatedBy": 0, "workflowInfo": {}, "status": "…", "reviewStatus": "…", "readyToDemo": false,
    "user": { ... },
    "nodes": [ ... ],
    "categories": [ ... ],
    "image": [ ... ],
    "workflow": {
      "nodes": [ ... ],
      "connections": { ... },
      "settings": { ... },
      "meta": { ... }, "tags": [], "pinData": {}, "versionId": "…"
    }
  }
}
```

The outer object is the template record (views, categories, author, images). The importable JSON is nested one level deeper, at **`.workflow.workflow`**. Use this endpoint when you need `recentViews`, `categories` or the author profile.

### What to send to n8n

Both endpoints give you a workflow object. `POST /api/v1/workflows` (and `n8n_create_workflow`) accept only:

`name`, `nodes`, `connections`, `settings` — plus optionally `staticData`, `pinData`, `projectId`, `parentFolderId`, `nodeGroups`, `description`.

The request schema rejects unknown properties, and `id`, `meta`, `tags`, `active` and `versionId` are read-only. So build the payload from those four keys only — do not post the fetched object as it is:

```bash
python3 - <<'PY'
import json
with open("/tmp/template-<id>.json") as f:
    tpl = json.load(f)
wf = tpl["workflow"]                      # for /templates/workflows/<id> use tpl["workflow"]["workflow"]
payload = {k: wf[k] for k in ("name", "nodes", "connections", "settings") if k in wf}   # settings can be absent on some templates
payload["name"] = tpl.get("name") or payload.get("name")   # the template's own title; --name overrides it
creds = sorted({c for n in payload["nodes"] for c in (n.get("credentials") or {})})
for n in payload["nodes"]:
    n.pop("credentials", None)            # source-instance credential IDs never work on the target
print(json.dumps({"requiredCredentials": creds, "nodeCount": len(payload["nodes"])}))
with open("/tmp/payload-<id>.json", "w") as f:
    json.dump(payload, f)
PY
```

Then pass `payload` to `~~workflow_validate` (`validate_workflow`) and `~~workflow_create`. Keep the printed `requiredCredentials` for credential planning. The tags the template carries are the author's, not yours — add your own batch tag after creation.

## List Categories

```
GET /templates/categories
```

**Response:**

```json
{
  "categories": [
    { "id": 25, "name": "AI", "displayName": null, "icon": "…", "parent": null },
    { "id": 47, "name": "AI Chatbot", "displayName": "AI Chatbot, Assistant, Agent",
      "icon": "…", "parent": { "id": 25, "name": "AI", "icon": "…" } }
  ]
}
```

A hierarchy: 7 top-level categories (`parent: null`) and their children — 31 entries in total. Filter searches with the category `name`. Do not hardcode IDs or the category list: it was rebuilt once and every ID changed. Fetch this endpoint when you need the current list.

## List Collections

```
GET /templates/collections
```

**Response:**

```json
{
  "collections": [
    {
      "id": 1,
      "rank": 1,
      "name": "…",
      "totalViews": 0,
      "createdAt": "…",
      "workflows": [ { "id": 100 }, { "id": 101 } ],
      "nodes": []
    }
  ]
}
```

The key is `collections`. There is no `description`, and `workflows` carries only IDs — fetch each ID for names. About 8 collections exist at the time of writing.

## Usage Notes

- **Rate limits**: None documented for read-only access; batch requests responsibly (1-2 requests per second).
- **Search behaviour**: `search` matches template name, description and node types.
- **Pagination**: `total_pages = ceil(totalWorkflows / rows)`; `rows` max is 100.
- **Node type format**: n8n's internal type identifier (`n8n-nodes-base.slack`, `@n8n/n8n-nodes-langchain.agent`), found in `nodes[].name`.
- **Credentials**: Template JSON carries credential references from the author's instance; they never work on yours. Strip them (the snippet above does) and plan credentials separately.
- **Node age**: Templates from the library often contain nodes that n8n 2.0 turned off or n8n 3.0 removes (Function, Item Lists, Cron, `executeCommand`, AI Agent v1, legacy OpenAI nodes). Run `workflow-analysis` before importing and `~~workflow_autofix` in preview mode afterwards.
