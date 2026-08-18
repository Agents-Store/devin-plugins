# n8n Template API Reference

Public REST API for the official n8n template library hosted at `api.n8n.io`.

## Base URL

```
https://api.n8n.io
```

No authentication required for reading. All endpoints return JSON.

## Endpoints

### Search Templates

```
GET /templates/search?search=<query>&rows=20&page=1&category=<id>
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Free-text search query |
| `rows` | integer | 20 | Results per page (max 100) |
| `page` | integer | 1 | Page number (1-indexed) |
| `category` | integer | — | Filter by category ID |

**Response:**

```json
{
  "totalWorkflows": 342,
  "data": [
    {
      "id": 1234,
      "name": "Send Slack notification on new GitHub issue",
      "totalViews": 15420,
      "recentViews": 890,
      "description": "Monitors GitHub for new issues and posts to Slack",
      "nodes": [
        { "type": "n8n-nodes-base.githubTrigger" },
        { "type": "n8n-nodes-base.slack" }
      ],
      "user": {
        "username": "n8n-team"
      },
      "createdAt": "2024-03-15T10:30:00.000Z",
      "categories": [
        { "id": 4, "name": "DevOps" }
      ]
    }
  ]
}
```

### Get Full Template

Two endpoints return template details with different response formats.

#### Flat format (ready for import)

```
GET /templates/workflows/<id>
```

Returns the full workflow JSON at the top level. This format is directly importable into n8n via the REST API or UI.

**Response:**

```json
{
  "id": 1234,
  "name": "Send Slack notification on new GitHub issue",
  "description": "...",
  "nodes": [ ... ],
  "connections": { ... },
  "settings": { ... }
}
```

#### Wrapped format

```
GET /workflows/templates/<id>
```

Returns the workflow nested inside a `workflow` key with additional metadata.

**Response:**

```json
{
  "id": 1234,
  "name": "Send Slack notification on new GitHub issue",
  "description": "...",
  "workflow": {
    "nodes": [ ... ],
    "connections": { ... },
    "settings": { ... }
  },
  "user": { "username": "n8n-team" },
  "totalViews": 15420
}
```

**Use `/templates/workflows/<id>` when you need JSON for direct import. Use `/workflows/templates/<id>` when you need metadata alongside the workflow.**

### List Categories

```
GET /templates/categories
```

Returns all template categories with their IDs and names.

**Response:**

```json
[
  { "id": 1, "name": "Marketing" },
  { "id": 2, "name": "Sales" },
  { "id": 25, "name": "AI" }
]
```

Currently 31 categories. Fetch this endpoint to get up-to-date IDs before filtering searches.

### List Collections

```
GET /templates/collections
```

Returns curated groups of templates organized by theme or use case.

**Response:**

```json
{
  "data": [
    {
      "id": 1,
      "name": "Getting Started with n8n",
      "description": "Essential workflows for new n8n users",
      "workflows": [
        { "id": 100, "name": "Hello World Workflow" },
        { "id": 101, "name": "Basic HTTP Request" }
      ]
    }
  ]
}
```

## Usage Notes

- **Rate limits**: No documented rate limits for read-only access, but batch requests responsibly (1-2 requests per second).
- **Search behavior**: The `search` parameter performs full-text matching against template name, description, and node types.
- **Pagination**: Always check `totalWorkflows` to determine if additional pages exist. `total_pages = ceil(totalWorkflows / rows)`.
- **Category IDs**: May change over time. Always fetch `/templates/categories` to confirm IDs before using them in filters.
- **Node type format**: Nodes in results use the internal n8n type identifier (e.g., `n8n-nodes-base.slack`, `@n8n/n8n-nodes-langchain.agent`).
- **Workflow JSON**: The JSON from `/templates/workflows/<id>` can be posted directly to the n8n instance API at `POST /api/v1/workflows` for import. Strip credential values before importing.
