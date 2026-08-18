# Scenario: Find Stock Media for a Blog App

You're building a blog application and need high-quality images for hero sections and article thumbnails.

## Step 1: Search for Hero Images

### Pexels (photos + videos)

```
Tool: searchPhotos
Input: {
  "query": "technology abstract gradient",
  "orientation": "landscape",
  "size": "large",
  "per_page": 20
}
```

### Unsplash (high-quality photos)

```
Tool: get_search_photos
Input: {
  "query": "minimal workspace technology",
  "orientation": "landscape",
  "per_page": 15
}
```

## Step 2: Search for Category-Specific Images

For different blog categories:

```
Tool: searchPhotos
Input: { "query": "artificial intelligence robot", "orientation": "landscape", "per_page": 10 }

Tool: searchPhotos
Input: { "query": "web development coding", "orientation": "landscape", "per_page": 10 }

Tool: searchPhotos
Input: { "query": "startup business meeting", "orientation": "landscape", "per_page": 10 }
```

## Step 3: Find Background Videos

```
Tool: searchVideos
Input: {
  "query": "abstract technology particles",
  "orientation": "landscape",
  "size": "medium",
  "per_page": 5
}
```

## Step 4: Search Web for Design Inspiration

```
Tool: search_images
Input: {
  "query": "tech blog hero image design inspiration dribbble",
  "num": 10
}
```

## Step 5: Deduplicate Results

If you collected images from multiple sources:

```
Tool: deduplicate_images
Input: {
  "images": ["<url1>", "<url2>", "<url3>", "..."]
}
```

## Step 6: Use in Your App

```typescript
// Pexels image sizes
const heroImage = photo.src.large2x;  // 1880px for hero
const thumbnail = photo.src.medium;    // 350px for cards
const preview = photo.src.small;       // 130px for lists

// Unsplash image sizes
const heroImage = photo.urls.full;     // Full resolution
const thumbnail = photo.urls.regular;  // 1080px
const preview = photo.urls.thumb;      // 200px
```

## Step 7: Track Downloads (Unsplash requirement)

```
Tool: get_photos_download
Input: { "id": "<photo_id>" }
```

Call this for each Unsplash photo you use — required by their API guidelines.

## Tips

- Use landscape orientation for hero images, portrait for sidebars
- Store multiple sizes for responsive design (thumbnail, medium, large)
- Consider using `get_photos_random` for dynamic hero images that change on each visit
- Cache image URLs — no need to re-search every page load
- Check licensing: Pexels and Unsplash are free for commercial use
