# Scenario: Media Gallery Builder

Build a media gallery combining photos and videos from Pexels collections and search results.

## Goal

Create a gallery page for a travel blog with photos and videos from Pexels.

## Step 1: Browse Featured Collections

Find curated collections that match the travel theme:

```
Tool: getFeaturedCollections
Input: { "per_page": 15 }
```

Review the returned collections. Each has `id`, `title`, `description`, `photos_count`, `videos_count`. Look for travel, nature, or adventure-themed collections.

## Step 2: Get Collection Media

Fetch photos from a promising collection:

```
Tool: getCollectionMedia
Input: {
  "id": "<collection_id>",
  "type": "photos",
  "per_page": 20,
  "sort": "desc"
}
```

Then fetch videos from the same collection:

```
Tool: getCollectionMedia
Input: {
  "id": "<collection_id>",
  "type": "videos",
  "per_page": 10
}
```

## Step 3: Supplement with Search

Fill gaps with targeted searches:

```
Tool: searchPhotos
Input: {
  "query": "beach sunset tropical",
  "orientation": "landscape",
  "per_page": 15
}
```

```
Tool: searchVideos
Input: {
  "query": "ocean waves aerial drone",
  "orientation": "landscape",
  "size": "medium",
  "per_page": 5
}
```

## Step 4: Add Curated Content

Include some editorially selected photos for visual variety:

```
Tool: getCuratedPhotos
Input: { "per_page": 10, "page": 3 }
```

Use different `page` values to get diverse curated sets.

## Step 5: Build the Gallery Data

Organize the collected media into a gallery structure:

```typescript
interface GalleryItem {
  type: 'photo' | 'video';
  id: string;
  thumbnail: string;  // src.small or video_pictures[0]
  medium: string;     // src.medium
  full: string;       // src.large or video_files[0].link
  photographer: string;
  alt: string;
}
```

Map Pexels response fields:
- Photos: `src.small` → thumbnail, `src.medium` → grid view, `src.large` → lightbox
- Videos: `video_pictures[0].picture` → thumbnail, `video_files` → playback (pick by quality)

## Step 6: Implement Pagination

For galleries with many items, paginate through results:

```
Tool: searchPhotos
Input: { "query": "travel adventure", "per_page": 20, "page": 1 }
// ... display first page ...
Tool: searchPhotos
Input: { "query": "travel adventure", "per_page": 20, "page": 2 }
// ... display second page ...
```

## Tips

- Collections provide thematically consistent media — better visual coherence than search
- Mix collection media with search results for variety
- Use `sort: "desc"` in `getCollectionMedia` for newest content first
- Pexels `per_page` goes up to 80 — use larger pages for batch loading
- Check `photos_count` and `videos_count` in collection metadata before fetching
