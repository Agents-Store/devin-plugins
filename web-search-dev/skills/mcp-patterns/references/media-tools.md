# Media Search MCP Tools (13 tools)

Stock photo and video tools from Pexels (9 tools) and Unsplash (4 tools). These require separate MCP server configuration — they are not bundled in this plugin's `.mcp.json`.

## Pexels (9 tools)

### searchPhotos
Search for stock photos.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search terms |
| `orientation` | string | No | `landscape`, `portrait`, `square` |
| `size` | string | No | `small`, `medium`, `large` |
| `color` | string | No | Filter by color |
| `per_page` | integer | No | Results per page (default: 15, max: 80) |
| `page` | integer | No | Page number |

```
Tool: searchPhotos
Input: {
  "query": "modern office workspace",
  "orientation": "landscape",
  "per_page": 10
}
```

### searchVideos
Search for stock videos.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search terms |
| `orientation` | string | No | `landscape`, `portrait`, `square` |
| `size` | string | No | `small`, `medium`, `large` |
| `per_page` | integer | No | Results per page |
| `page` | integer | No | Page number |

```
Tool: searchVideos
Input: { "query": "tech startup office", "orientation": "landscape", "per_page": 5 }
```

### getCuratedPhotos
Get editorially curated photos (no search query needed).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `per_page` | integer | No | Results per page |
| `page` | integer | No | Page number |

### getPopularVideos
Get trending/popular videos.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `per_page` | integer | No | Results per page |

### getPhoto
Get a single photo by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Photo ID |

### getVideo
Get a single video by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Video ID |

### getFeaturedCollections
Get featured photo/video collections.

### getMyCollections
Get the authenticated user's collections.

### getCollectionMedia
Get media from a specific collection.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Collection ID |
| `type` | string | No | `photos`, `videos` |
| `per_page` | integer | No | Results per page |

## Unsplash (4 tools)

### get_search_photos
Search for photos on Unsplash.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search terms |
| `page` | integer | No | Page number |
| `per_page` | integer | No | Results per page (max: 30) |
| `orientation` | string | No | `landscape`, `portrait`, `squarish` |
| `color` | string | No | Filter by color |

```
Tool: get_search_photos
Input: {
  "query": "nature landscape mountain",
  "orientation": "landscape",
  "per_page": 10
}
```

### get_photos
Get a single photo by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Photo ID |

### get_photos_random
Get a random photo, optionally filtered.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | No | Topic filter |
| `orientation` | string | No | Orientation filter |
| `count` | integer | No | Number of random photos (max: 30) |

### get_photos_download
Track a photo download (required by Unsplash API guidelines).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Photo ID |

## Usage Notes

- **Pexels**: Free for commercial use. Attribution appreciated but not required. API key from https://www.pexels.com/api/
- **Unsplash**: Free for commercial use under Unsplash License. Must trigger download tracking. API key from https://unsplash.com/developers
- Both return image URLs in multiple sizes — use the appropriate size for your app (thumbnail, regular, full)
- For finding images, also consider `search_images` from Jina which searches the open web (not just stock sites)
