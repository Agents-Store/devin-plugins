---
name: media-search
description: This skill should be used when the user asks to "find images", "search photos", "find stock photos", "search videos", "find media for app", "get stock images", "find pictures for website", or needs to find images, videos, or other media content for their application or website.
---

# Media Search for Development

Find images, videos, and visual content for applications using Pexels, Unsplash, and Jina image search.

## Service Comparison

| Service | Content | License | MCP Tools | Best For |
|---------|---------|---------|-----------|----------|
| **Pexels** | Photos + Videos | Free commercial, attribution appreciated | 9 tools | Stock photos and videos |
| **Unsplash** | Photos only | Free commercial (Unsplash License) | 4 tools | High-quality editorial photos |
| **Jina** | Web images | Varies by source | `search_images` | Finding images from any website |

**If Pexels and Unsplash are not configured**, use Jina's `search_images` as the primary fallback — it searches the open web and requires no additional MCP setup beyond the plugin's bundled Jina server. For stock-quality images without dedicated MCP, also try `web_search_advanced_exa` (opt-in Exa tool) with `includeDomains: ["pexels.com", "unsplash.com"]`.

## Pattern 0: Jina Web Image Search (Always Available)

Use this when Pexels/Unsplash MCP tools are not configured, or when you need images from the open web (not just stock sites):

```
Tool: search_images
Input: {
  "query": "modern office workspace interior design",
  "num": 15
}
```

Returns image URLs from across the web — useful for design inspiration, reference images, and when stock photos aren't specific enough. Bundled with this plugin, no extra configuration needed.

## Pattern 1: Search Stock Photos

### Pexels

```
Tool: searchPhotos
Input: {
  "query": "modern office workspace",
  "orientation": "landscape",
  "size": "large",
  "per_page": 15
}
```

Returns URLs in multiple sizes — use `src.large` (940px), `src.medium` (350px), or `src.small` (130px) based on your needs.

### Unsplash

```
Tool: get_search_photos
Input: {
  "query": "mountain landscape sunset",
  "orientation": "landscape",
  "per_page": 10
}
```

Returns `urls.regular` (1080px), `urls.small` (400px), `urls.thumb` (200px).

**Important:** Call `get_photos_download` when using an Unsplash photo to track the download as required by their API guidelines.

### Jina Web Image Search

```
Tool: search_images
Input: {
  "query": "dashboard UI design inspiration",
  "num": 10
}
```

Searches the open web — returns images from any website, not just stock photo sites. Useful for design inspiration and reference.

## Pattern 2: Search Videos

```
Tool: searchVideos
Input: {
  "query": "tech startup office",
  "orientation": "landscape",
  "size": "medium",
  "per_page": 5
}
```

Returns video files with multiple quality options. Use for background videos, hero sections, or content.

### Trending Videos

```
Tool: getPopularVideos
Input: { "per_page": 10 }
```

## Pattern 3: Get Curated/Random Content

### Pexels Curated

```
Tool: getCuratedPhotos
Input: { "per_page": 20 }
```

Editorially selected — good for placeholder content or featured images.

### Unsplash Random

```
Tool: get_photos_random
Input: {
  "query": "technology",
  "orientation": "landscape",
  "count": 5
}
```

Returns random photos matching the query — good for dynamic hero images.

## Pattern 4: Browse Collections

```
Tool: getFeaturedCollections
Input: { "per_page": 10 }
```

Then get media from a collection:

```
Tool: getCollectionMedia
Input: {
  "id": "collection-id",
  "type": "photos",
  "per_page": 20
}
```

## Pattern 5: Get Specific Media by ID

When you found a photo/video you want to use:

```
Tool: getPhoto
Input: { "id": 12345 }
```

```
Tool: getVideo
Input: { "id": 67890 }
```

## Workflow: Find Media for Your App

1. **Search broadly** — use `searchPhotos` with general terms
2. **Refine** — add `orientation`, `size`, `color` filters
3. **Preview** — check returned URLs at different sizes
4. **Select and download** — use the appropriate size URL for your app
5. **Track download** (Unsplash only) — call `get_photos_download`

## Integration Tips

### For Web Apps

```typescript
// Use small/medium URLs for thumbnails, large for detail views
const imageUrl = photo.src.medium; // Pexels
const imageUrl = photo.urls.regular; // Unsplash
```

### For Content Pipelines

Combine media search with web scraping:
1. Scrape content from source site
2. Search for relevant stock images based on content
3. Build content package with text + images

### For Responsive Images

Both Pexels and Unsplash provide multiple sizes:

| Size | Pexels Field | Unsplash Field | Typical Width |
|------|-------------|----------------|---------------|
| Thumbnail | `src.tiny` | `urls.thumb` | 130-200px |
| Small | `src.small` | `urls.small` | 350-400px |
| Medium | `src.medium` | `urls.regular` | 940-1080px |
| Large | `src.large` | `urls.full` | 1880-2000px+ |
| Original | `src.original` | `urls.raw` | Full resolution |

## Notes

- Pexels and Unsplash require separate MCP configuration — they are not bundled in this plugin's `.mcp.json`
- If neither stock service is configured, use Jina's `search_images` which searches the open web
- Always check image licenses before using in commercial applications
- Consider using `deduplicate_images` (Jina) when collecting images from multiple sources
