# Scenario: Find Stock Media for a Blog App

You're building a blog application and need high-quality images for hero sections and article thumbnails.

## Step 1: Search for Hero Images

### Pexels (photos + videos)

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/search?query=technology+abstract+gradient&orientation=landscape&size=large&per_page=20"
```

### Unsplash (high-quality photos)

```bash
curl -s -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}" \
  "https://api.unsplash.com/search/photos?query=minimal+workspace+technology&orientation=landscape&per_page=15"
```

## Step 2: Search for Category-Specific Images

For different blog categories (one request per query; each call counts against the 200 requests/hour limit — cache the results):

```bash
for q in "artificial+intelligence+robot" "web+development+coding" "startup+business+meeting"; do
  curl -s -H "Authorization: ${PEXELS_API_KEY}" \
    "https://api.pexels.com/v1/search?query=${q}&orientation=landscape&per_page=10"
done
```

## Step 3: Find Background Videos

```bash
curl -s -H "Authorization: ${PEXELS_API_KEY}" \
  "https://api.pexels.com/v1/videos/search?query=abstract+technology+particles&orientation=landscape&size=medium&per_page=5"
```

## Step 4: Search Web for Design Inspiration

```
Tool: search_images
Input: {
  "query": "tech blog hero image design inspiration dribbble",
  "num": 10,
  "return_url": true
}
```

`return_url: true` returns URLs and metadata instead of base64 images, which would otherwise fill the context.

## Step 5: Remove Near-Duplicates

If you collected images from several sources, compare their `alt`/description text and drop near-duplicates by hand, or pass those descriptions to Jina `deduplicate_strings` and keep the images behind the distinct ones. (There is no image de-duplication tool.)

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

## Step 7: Unsplash Requirements (hotlink, download event, attribution)

For each Unsplash photo you actually use:

```bash
# download event — fire asynchronously, keep the query parameters in the URL
curl -s -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}" "<photo.links.download_location>"
```

- Keep hotlinking `photo.urls.*` — do not copy the file to your own storage.
- Render "Photo by <name> on Unsplash" with links to the photographer and to Unsplash, both with `?utm_source=<app_name>&utm_medium=referral`.

For Pexels photos show a link to Pexels and credit the photographer.

## Tips

- Use landscape orientation for hero images, portrait for sidebars
- Store multiple sizes for responsive design (thumbnail, medium, large)
- Consider Unsplash `GET /photos/random?query=...` for dynamic hero images (each photo still needs the download event and attribution)
- Cache image URLs — no need to re-search every page load
- Check licensing: Pexels and Unsplash are free for commercial use
