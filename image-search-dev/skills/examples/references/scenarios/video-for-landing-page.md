# Scenario: Video for Landing Page

Find background videos for website hero sections and landing pages using Pexels.

## Goal

Find a short, high-quality looping video for a tech startup landing page background.

## Step 1: Search for Relevant Videos

```
Tool: searchVideos
Input: {
  "query": "technology abstract motion",
  "orientation": "landscape",
  "size": "medium",
  "per_page": 10
}
```

The `size: "medium"` filter returns Full HD quality — ideal for web backgrounds.

## Step 2: Check Popular/Trending Videos

Browse trending videos for high-quality alternatives:

```
Tool: getPopularVideos
Input: {
  "per_page": 10,
  "min_width": 1920,
  "max_duration": 20
}
```

The `min_width: 1920` ensures at least Full HD resolution. The `max_duration: 20` limits to short clips suitable for looping backgrounds.

## Step 3: Evaluate Video Quality

Get full details on a promising video:

```
Tool: getVideo
Input: { "id": "<video_id>" }
```

Check the `video_files` array for available qualities:

| Quality | Typical Resolution | Use Case |
|---------|-------------------|----------|
| `hd` | 1280x720 | Mobile, low bandwidth |
| `sd` | 960x540 | Fallback |
| `hls` | Adaptive | Streaming |
| Full HD | 1920x1080 | Desktop background |
| 4K | 3840x2160 | High-DPI displays |

## Step 4: Refine Search Terms

If initial results don't match, try different approaches:

```
Tool: searchVideos
Input: {
  "query": "data visualization network",
  "orientation": "landscape",
  "per_page": 10
}
```

Alternative search terms for tech landing pages:
- "abstract particles motion"
- "digital network connection"
- "code programming screen"
- "circuit board closeup"
- "gradient blur background"

## Step 5: Select the Right Quality

From the `video_files` array, pick the file matching your needs:

```typescript
// Find Full HD MP4 file
const videoFile = video.video_files.find(
  f => f.width >= 1920 && f.file_type === 'video/mp4'
);
const videoUrl = videoFile.link;
```

## Step 6: Implement in HTML

```html
<div class="hero">
  <video autoplay muted loop playsinline>
    <source src="<video_url>" type="video/mp4">
  </video>
  <div class="hero-content">
    <h1>Your Product Name</h1>
  </div>
</div>
```

## Tips

- Use `max_duration: 15-20` for seamless looping background videos
- `orientation: "landscape"` is essential for full-width backgrounds
- Prefer `size: "medium"` (Full HD) over `size: "large"` (4K) for web — smaller file size
- Pexels is the only service with video support — Unsplash has photos only
- Consider `getPopularVideos` for trending, high-quality content that's already proven popular
- Test video loop points — some clips loop more seamlessly than others
