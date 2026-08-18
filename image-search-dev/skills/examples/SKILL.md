---
name: examples
description: This skill should be used when the user asks for "image search examples", "stock photo workflow", "show me how to find images", "media search walkthrough", "pexels usage example", "unsplash usage example", or wants to see end-to-end scenarios for finding and using stock images and videos.
---

# Image Search Examples

End-to-end scenario walkthroughs for common image and video search tasks.

## Scenarios

| Scenario | Services Used | Use Case |
|----------|---------------|----------|
| [Hero Images for Website](references/scenarios/hero-images-for-website.md) | Pexels + Unsplash | Find high-quality hero/banner images |
| [Media Gallery Builder](references/scenarios/media-gallery-builder.md) | Pexels | Browse collections, build photo + video galleries |
| [Video for Landing Page](references/scenarios/video-for-landing-page.md) | Pexels | Find background videos for web pages |
| [Find and Upload to MinIO](references/scenarios/find-and-upload-to-minio.md) | Pexels/Unsplash + MinIO | Search, select, and upload to persistent storage |

## Quick Reference Workflows

### Workflow 1: Search, Select, Use

```
1. searchPhotos → { "query": "...", "orientation": "landscape", "per_page": 10 }
2. Review results → pick the best match by id
3. Use the appropriate size URL in your app:
   - Thumbnail: src.tiny (130px)
   - Card: src.small (350px)
   - Content: src.medium (940px)
   - Hero: src.large (1880px)
```

### Workflow 2: Search, Compare, Select

```
1. searchPhotos → Pexels results (up to 80 per page)
2. get_search_photos → Unsplash results (up to 30 per page)
3. Compare quality and relevance
4. Select the best match
5. If Unsplash → call get_photos_download to track download
```

### Workflow 3: Search, Upload, Reference

```
1. searchPhotos → find the right image
2. a-minio-uploadImageToMinio → { "body": { "file_url": "<src.large URL>" } }
3. Use the returned MinIO URL in your application
```
