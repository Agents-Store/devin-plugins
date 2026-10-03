---
name: media-search
description: This skill should be used when the user asks to "find images", "search photos", "find stock photos", "search videos", "find media for app", "get stock images", "find pictures for website", "Pexels API", "Unsplash API", or needs to find images, videos, or other media content for their application or website.
---

# Media Search for Development

Find images, videos and visual content for applications with the **Pexels REST API**, the **Unsplash REST API** and Jina web image search. Pexels and Unsplash are called with `curl` (or any HTTP client) — there is no bundled MCP server for them. Full parameter tables: `mcp-patterns/references/media-tools.md`.

## Service Comparison

| Service | Content | Licence | Access | Best For |
|---------|---------|---------|--------|----------|
| **Pexels** | Photos + videos | Free commercial use; link to Pexels and photographer credit required for API use | REST, `PEXELS_API_KEY` | Stock photos and videos, locale-aware search |
| **Unsplash** | Photos only | Unsplash License; API guidelines apply (hotlink, download tracking, attribution) | REST, `UNSPLASH_ACCESS_KEY` | High-quality editorial photos |
| **Jina** | Web images | Varies by source | Bundled MCP `search_images` | Images from any website, inspiration |

**Without API keys**, use Jina `search_images` with `"return_url": true` — it needs no extra setup. For stock-quality results without keys you can also use `web_search_advanced_exa` (opt-in Exa tool) with `includeDomains: ["pexels.com", "unsplash.com"]`.

## Keys

```bash
export PEXELS_API_KEY=...        # https://www.pexels.com/api/
export UNSPLASH_ACCESS_KEY=...   # https://unsplash.com/developers
```

Set them in the environment that launches Claude Code (for example the `env` block of your local settings). Never write key values into files that are committed.

## Pattern 0: Jina Web Image Search (Always Available)

```
Tool: search_images
Input: {
  "query": "modern office workspace interior design",
  "num": 15,
  "return_url": true
}
```

**Always pass `return_url: true`.** By default the tool returns base64 JPEGs, and every call fills the context with image data. Use it for design inspiration, reference images, and when stock photos are not specific enough.

## Pattern 1: Search Stock Photos

### Pexels

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/search?query=modern+office+workspace&orientation=landscape&size=large&per_page=15&locale=en-US"
```

Use `src.large` (940 px wide), `src.medium` (350 px high) or `src.small` (130 px high) by need. Pass `locale` (for example `ru-RU`, `de-DE`, `ja-JP`) with a query written in that language. Other filters: `color` (name or hex), `page`.

### Unsplash

```bash
curl -s -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}" \
  "https://api.unsplash.com/search/photos?query=mountain+landscape+sunset&orientation=landscape&per_page=10"
```

Returns `urls.regular` (1080 px), `urls.small` (400 px), `urls.thumb` (200 px), plus the photographer in `user` and the download event URL in `links.download_location`.

### Unsplash checklist (required for every API use)

1. **Hotlink** the image from `photo.urls.*` — do not download and re-upload it to your own storage or CDN (the download-and-store workflow below is for Pexels only).
2. **Call `photo.links.download_location`** (with the same `Authorization` header and all query parameters) when the photo is actually used — inserted into a post, set as a header, chosen by a user.
3. **Attribute** Unsplash and the photographer with links that carry `?utm_source=<app_name>&utm_medium=referral`:
   `Photo by <a href="https://unsplash.com/@<username>?utm_source=<app_name>&utm_medium=referral"><name></a> on <a href="https://unsplash.com/?utm_source=<app_name>&utm_medium=referral">Unsplash</a>`
4. Keep the Access Key (and Secret Key) on the server — proxy requests instead of calling the API from client-side code.
5. Do not name your app after Unsplash, sell unaltered photos, or replicate the Unsplash experience.

```bash
# after the user picks a photo — tracking call, send asynchronously
curl -s -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}" "<photo.links.download_location>"
```

## Pattern 2: Search Videos (Pexels only)

Video endpoints live under `/v1/videos/` (the old `/videos/` prefix is being retired).

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/videos/search?query=tech+startup+office&orientation=landscape&size=medium&per_page=5"
```

Each video returns `video_files[]` — pick the file that fits (`quality`, `width`, `file_type`, `link`). To filter by resolution or length use the popular endpoint, which is the only one with those parameters:

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/videos/popular?min_width=1920&max_duration=20&per_page=10"
```

### Background video for a landing page

1. Search with `orientation=landscape&size=medium` (Full HD is enough for the web; `large` is 4K and much heavier), or use `popular` with `min_width=1920&max_duration=15..20` for short loops.
2. Pick a file from `video_files`:

```typescript
const file = video.video_files.find(f => f.width >= 1920 && f.file_type === 'video/mp4')
          ?? video.video_files.find(f => f.file_type === 'video/mp4');
```

3. Embed with a poster image (`video.video_pictures[0].picture`) and add a "Videos provided by Pexels" link:

```html
<video autoplay muted loop playsinline poster="<video_picture_url>">
  <source src="<video_file_link>" type="video/mp4">
</video>
```

Try other search terms if results are generic: "abstract particles motion", "digital network connection", "circuit board closeup", "gradient blur background". Check that the loop point is seamless.

## Pattern 3: Curated and Collections (Pexels)

```bash
# Editorially curated photos — placeholder or featured content
curl -s -H "Authorization: ${PEXELS_API_KEY}" "https://api.pexels.com/v1/curated?per_page=20"

# Browse featured collections, then fetch the media of one
curl -s -H "Authorization: ${PEXELS_API_KEY}" "https://api.pexels.com/v1/collections/featured?per_page=10"
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/collections/<collection_id>?type=photos&sort=desc&per_page=20"
```

Collections hold photos and videos; `type` filters to one of them. Good for building a gallery from a theme (travel, nature, abstract).

## Pattern 4: Random Unsplash Photos

```bash
curl -s -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}" \
  "https://api.unsplash.com/photos/random?query=technology&orientation=landscape&count=5"
```

Good for dynamic hero images. Every returned photo still needs the checklist above (hotlink, download event, attribution).

## Pattern 5: Specific Media by ID

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" "https://api.pexels.com/v1/photos/2014422"
curl -s -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}" "https://api.unsplash.com/photos/<photo_id>"
```

## Pattern 6: Persist a Pexels Image in Your Own Storage

Pexels licence permits keeping your own copy (Unsplash does not — see the checklist). Download the size you need, then upload it with your storage tool; keep photographer and source URL next to the file for attribution.

```bash
# 1. pick a size from the search response: src.medium, src.large, src.large2x ...
curl -sL -o hero.jpg "<photo.src.large>"
# 2. upload with your own tooling (S3-compatible example)
aws s3 cp hero.jpg "s3://<bucket>/media/hero.jpg" --endpoint-url "${S3_ENDPOINT_URL}"
```

Store the `photographer`, `photographer_url` and `url` fields with the record — the "Photo by <photographer> on Pexels" credit and the link to Pexels are still required on display. Upload `medium` or `large` for web use; avoid `original` unless you need print resolution.

## Workflow: Find Media for Your App

1. **Search broadly** with a general term; add `orientation`, `size`, `color` and `locale` to refine.
2. **Compare** Pexels and Unsplash results (each has different content and aesthetics).
3. **Select** a photo and note the URL at the right size.
4. **Unsplash:** hotlink `urls.*`, call `download_location`, render the attribution. **Pexels:** hotlink or store a copy, and render the Pexels link plus photographer credit.
5. **Cache** search responses — rate limits are low (Pexels 200/hour and 20 000/month, Unsplash 50/hour in demo mode and 1 000/hour in production).

## Integration Tips

### Responsive images

| Size | Pexels `src.*` | Unsplash `urls.*` | Typical width |
|------|----------------|-------------------|---------------|
| Thumbnail | `tiny` | `thumb` | 130-200 px |
| Small | `small` | `small` | 350-400 px |
| Medium | `medium` | `regular` | 940-1080 px |
| Large | `large` / `large2x` | `full` | 1880-2000 px+ |
| Original | `original` | `raw` | Full resolution |

Unsplash `urls.*` accept resize parameters (`w`, `h`, `fit`, `q`) — change them on the returned URL instead of re-hosting the image.

### Content pipelines

Combine media search with web scraping: scrape the source text, derive keywords, search stock media for each article, build a package of text plus images (with attribution data).

## Notes

- Always check image licences before commercial use; web images from Jina vary by source.
- Never commit API keys; both keys are read from the environment.
- Troubleshooting (401, 403, 429): see the `troubleshoot` skill.
