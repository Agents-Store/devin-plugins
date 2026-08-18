# Pexels MCP Tools (9 tools)

Complete parameter reference for all Pexels tools from the `mcpware-dev-tools` MCP server.

**License:** Free for commercial use. Attribution appreciated but not required.

## searchPhotos

Search for stock photos by keyword.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | — | Search terms (e.g., "modern office") |
| `orientation` | string | No | — | `landscape`, `portrait`, `square` |
| `size` | string | No | — | `large` (24MP), `medium` (12MP), `small` (4MP) |
| `color` | string | No | — | Filter by color (e.g., "red", "blue", "#FF0000") |
| `locale` | string | No | — | Locale for search (e.g., `en-US`, `uk-UA`, `de-DE`, `fr-FR`, `ja-JP`, `zh-CN`, `ko-KR`, `ru-RU`) |
| `per_page` | integer | No | 15 | Results per page (1-80) |
| `page` | integer | No | 1 | Page number |

```
Tool: searchPhotos
Input: {
  "query": "nature landscape",
  "orientation": "landscape",
  "size": "large",
  "color": "green",
  "per_page": 20
}
```

**Response fields:** `id`, `width`, `height`, `url` (Pexels page), `photographer`, `photographer_url`, `src` (object with `original`, `large2x`, `large`, `medium`, `small`, `portrait`, `landscape`, `tiny`), `alt`.

## searchVideos

Search for stock videos by keyword.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | — | Search terms |
| `orientation` | string | No | — | `landscape`, `portrait`, `square` |
| `size` | string | No | — | `large` (4K), `medium` (Full HD), `small` (HD) |
| `locale` | string | No | — | Locale for search |
| `per_page` | integer | No | 15 | Results per page (1-80) |
| `page` | integer | No | 1 | Page number |

```
Tool: searchVideos
Input: {
  "query": "drone aerial city",
  "orientation": "landscape",
  "size": "medium",
  "per_page": 5
}
```

**Response fields:** `id`, `width`, `height`, `url`, `duration`, `user`, `video_files` (array with `id`, `quality`, `file_type`, `width`, `height`, `link`), `video_pictures`.

## getCuratedPhotos

Get editorially curated photos. No search query needed — returns hand-picked editorial content.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `per_page` | integer | No | 15 | Results per page (1-80) |
| `page` | integer | No | 1 | Page number |

```
Tool: getCuratedPhotos
Input: { "per_page": 20 }
```

Good for placeholder content, featured images, or design inspiration.

## getPopularVideos

Get trending/popular videos.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `per_page` | integer | No | 15 | Results per page (1-80) |
| `page` | integer | No | 1 | Page number |
| `min_width` | integer | No | — | Minimum video width in pixels |
| `min_height` | integer | No | — | Minimum video height in pixels |
| `min_duration` | integer | No | — | Minimum duration in seconds |
| `max_duration` | integer | No | — | Maximum duration in seconds |

```
Tool: getPopularVideos
Input: {
  "per_page": 10,
  "min_width": 1920,
  "max_duration": 30
}
```

Use `min_width`/`min_height` to filter by resolution. Use `min_duration`/`max_duration` for length constraints (e.g., short clips for backgrounds).

## getPhoto

Get a single photo by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Photo ID |

```
Tool: getPhoto
Input: { "id": "12345" }
```

## getVideo

Get a single video by its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Video ID |

```
Tool: getVideo
Input: { "id": "67890" }
```

## getFeaturedCollections

Get featured photo/video collections curated by Pexels editors.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `per_page` | integer | No | 15 | Results per page (1-80) |
| `page` | integer | No | 1 | Page number |

```
Tool: getFeaturedCollections
Input: { "per_page": 10 }
```

Returns collection `id`, `title`, `description`, `media_count`, `photos_count`, `videos_count`.

## getMyCollections

Get the authenticated user's own collections.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `per_page` | integer | No | 15 | Results per page (1-80) |
| `page` | integer | No | 1 | Page number |

```
Tool: getMyCollections
Input: { "per_page": 10 }
```

## getCollectionMedia

Get photos and/or videos from a specific collection.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `id` | string | Yes | — | Collection ID |
| `type` | string | No | — | `photos` or `videos` (omit for both) |
| `per_page` | integer | No | 15 | Results per page (1-80) |
| `page` | integer | No | 1 | Page number |
| `sort` | string | No | `asc` | `asc` or `desc` |

```
Tool: getCollectionMedia
Input: {
  "id": "abc123",
  "type": "photos",
  "per_page": 20,
  "sort": "desc"
}
```

Two-step workflow: first browse collections with `getFeaturedCollections` or `getMyCollections`, then fetch media from a collection with `getCollectionMedia`.
