---
name: mcp-patterns
description: This skill should be used when the user asks about "image search MCP tools", "pexels tools", "unsplash tools", "which image search tools are available", "how to find stock photos", "search photos MCP", "stock image tools", "pexels parameters", "unsplash parameters", or needs to know which MCP operations are available for searching stock images and videos.
---

# Image Search MCP Tool Patterns

Reference for all Pexels and Unsplash MCP tools available via the `mcpware-dev-tools` server.

## Service Overview

| Service | Tools | Photos | Videos | Collections | License |
|---------|-------|--------|--------|-------------|---------|
| **Pexels** | 9 | Yes | **Yes** | Yes | Free commercial, attribution appreciated |
| **Unsplash** | 4 | Yes | **No** | No | Unsplash License (free commercial) |
| **MinIO** | 1 | Upload only | — | — | N/A |

**Unsplash has NO video support.** For videos, use Pexels exclusively (`searchVideos`, `getPopularVideos`).

## Task Routing

Pick the right tool for the job:

| Task | Best Tool | Fallback | Service |
|------|-----------|----------|---------|
| Search photos | `searchPhotos` | `get_search_photos` | Pexels / Unsplash |
| Search videos | `searchVideos` | `getPopularVideos` | Pexels |
| Curated photos | `getCuratedPhotos` | `get_photos_random` | Pexels / Unsplash |
| Trending videos | `getPopularVideos` | — | Pexels |
| Photo by ID | `getPhoto` | `get_photos` | Pexels / Unsplash |
| Video by ID | `getVideo` | — | Pexels |
| Browse collections | `getFeaturedCollections` → `getCollectionMedia` | — | Pexels |
| Random photos | `get_photos_random` | `getCuratedPhotos` | Unsplash / Pexels |
| Upload to storage | `a-minio-uploadImageToMinio` | — | MinIO |

## Quick Usage Examples

### Search Photos (Pexels)

```
Tool: searchPhotos
Input: {
  "query": "modern office workspace",
  "orientation": "landscape",
  "size": "large",
  "per_page": 10
}
```

**`size` parameter mapping (photos):** `large` = 24MP+, `medium` = 12MP, `small` = 4MP. This filters by source photo resolution, not output size.

Returns URLs in multiple sizes: `src.original`, `src.large2x` (1880px), `src.large` (940px), `src.medium` (350px), `src.small` (130px), `src.tiny`.

### Search Photos (Unsplash)

```
Tool: get_search_photos
Input: {
  "query": "mountain landscape sunset",
  "orientation": "landscape",
  "per_page": 10
}
```

Returns URLs: `urls.raw`, `urls.full`, `urls.regular` (1080px), `urls.small` (400px), `urls.thumb` (200px).

**CRITICAL:** Always call `get_photos_download` after using an Unsplash photo — required by Unsplash API guidelines for download tracking.

```
Tool: get_photos_download
Input: { "id": "<photo_id>" }
```

### Search Videos (Pexels only — Unsplash has no video)

```
Tool: searchVideos
Input: {
  "query": "tech startup",
  "orientation": "landscape",
  "size": "medium",
  "per_page": 5
}
```

**`size` parameter mapping (videos):** `large` = 4K, `medium` = Full HD (1080p), `small` = HD (720p). Use `medium` for web backgrounds, `large` only for 4K displays.

Returns video files with multiple quality options in `video_files` array (each with `link`, `quality`, `width`, `height`).

### Filter Videos by Duration and Resolution

Use `getPopularVideos` for precise duration/resolution filtering:

```
Tool: getPopularVideos
Input: {
  "min_width": 1920,
  "min_height": 1080,
  "max_duration": 15,
  "per_page": 10
}
```

Key parameters unavailable in `searchVideos`:
- `min_width` / `min_height` — enforce exact minimum resolution (e.g., 1920x1080 for Full HD)
- `min_duration` / `max_duration` — filter by length in seconds (e.g., `max_duration: 15` for short loops)

## Responsive Image Sizes

Both services return multiple image sizes. Pick the right one for your use case:

| Use Case | Pexels Field | Unsplash Field | Typical Width |
|----------|-------------|----------------|---------------|
| Thumbnail | `src.tiny` | `urls.thumb` | 130-200px |
| List/card | `src.small` | `urls.small` | 350-400px |
| Content area | `src.medium` | `urls.regular` | 940-1080px |
| Hero/banner | `src.large2x` | `urls.full` | 1880-2000px+ |
| Print/full | `src.original` | `urls.raw` | Full resolution |

## Complementary Tool: MinIO Upload

After finding an image, upload it to MinIO for persistent storage:

```
Tool: a-minio-uploadImageToMinio
Input: {
  "body": {
    "file_url": "https://images.pexels.com/photos/12345/pexels-photo-12345.jpeg"
  }
}
```

Returns a hosted URL to use in your application.

## Best Practices

- **Search broadly first**, then refine with `orientation`, `size`, `color` filters
- **Use Pexels for videos** — Unsplash only has photos
- **Combine both services** for wider selection — search Pexels and Unsplash in parallel
- **Always track Unsplash downloads** — call `get_photos_download` for every photo used
- **Use pagination** (`page`, `per_page`) for large result sets — do not fetch everything at once
- **Pick the right image size** — use thumbnails for previews, regular for content, full for hero sections

## Detailed Tool Reference

For complete parameter tables for all tools, see:
- `references/pexels-tools.md` — All 9 Pexels tools
- `references/unsplash-tools.md` — All 4 Unsplash tools
