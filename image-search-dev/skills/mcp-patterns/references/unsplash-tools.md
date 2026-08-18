# Unsplash MCP Tools (4 tools)

Complete parameter reference for all Unsplash tools from the `mcpware-dev-tools` MCP server.

**License:** Free for commercial use under the Unsplash License. Attribution not required but appreciated.

**CRITICAL REQUIREMENT:** Always call `get_photos_download` when using an Unsplash photo in your application. This is required by the Unsplash API guidelines for download tracking. Failure to track downloads may result in API access revocation.

## get_search_photos

Search for photos on Unsplash.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | — | Search terms |
| `orientation` | string | No | — | `landscape`, `portrait`, `squarish` |
| `page` | integer | No | 1 | Page number |
| `per_page` | integer | No | 10 | Results per page (max: 30) |

```
Tool: get_search_photos
Input: {
  "query": "mountain landscape sunset",
  "orientation": "landscape",
  "per_page": 10
}
```

**Note:** Unsplash uses `squarish` (not `square` like Pexels).

**Response fields:** `id`, `width`, `height`, `description`, `alt_description`, `urls` (object with `raw`, `full`, `regular`, `small`, `thumb`), `user` (photographer info), `links`.

## get_photos

Get a single photo by its ID. Use for retrieving full details of a photo found via search.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Photo ID |

```
Tool: get_photos
Input: { "id": "abc123XYZ" }
```

## get_photos_random

Get random photos, optionally filtered by query. Good for dynamic hero images, placeholders, or content variety.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | No | — | Topic filter (e.g., "technology", "nature") |
| `count` | integer | No | 1 | Number of random photos (max: 30) |

```
Tool: get_photos_random
Input: {
  "query": "technology",
  "count": 5
}
```

When no `query` is provided, returns completely random photos from the Unsplash library.

## get_photos_download

Track a photo download. **MUST be called every time an Unsplash photo is used.** This triggers Unsplash's download counter and is required by the API Terms of Service.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Photo ID to track |

```
Tool: get_photos_download
Input: { "id": "abc123XYZ" }
```

**When to call:** After selecting a photo from search results or random photos, before or after downloading/using the image URL in your application.

## Unsplash vs Pexels Comparison

| Feature | Unsplash | Pexels |
|---------|----------|--------|
| Photos | Yes | Yes |
| Videos | No | Yes |
| Collections | No | Yes |
| Orientation options | `landscape`, `portrait`, `squarish` | `landscape`, `portrait`, `square` |
| Max per_page | 30 | 80 |
| Color filter | No (via MCP) | Yes |
| Locale filter | No | Yes |
| Download tracking | Required | Not needed |
| Rate limit | 50 req/hr | 200 req/hr |
