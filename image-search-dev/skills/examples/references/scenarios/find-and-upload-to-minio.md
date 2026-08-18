# Scenario: Find and Upload to MinIO

Search for an image, then upload it to MinIO storage for persistent hosting in your application.

## Goal

Find a product photo for an e-commerce listing, upload it to MinIO, and get a hosted URL.

## Step 1: Search for the Image

Search Pexels for product-style photos:

```
Tool: searchPhotos
Input: {
  "query": "wireless headphones product white background",
  "orientation": "square",
  "size": "medium",
  "per_page": 10
}
```

Or search Unsplash:

```
Tool: get_search_photos
Input: {
  "query": "headphones product photography",
  "orientation": "squarish",
  "per_page": 10
}
```

## Step 2: Select the Best Match

Review the results and pick the best photo. Note the image URL at the appropriate size:

- For product thumbnails: use `src.small` (Pexels) or `urls.small` (Unsplash)
- For product detail page: use `src.medium` (Pexels) or `urls.regular` (Unsplash)
- For zoom/full-screen: use `src.large` (Pexels) or `urls.full` (Unsplash)

## Step 3: Track Download (Unsplash Only)

If you selected an Unsplash photo, track the download first:

```
Tool: get_photos_download
Input: { "id": "<unsplash_photo_id>" }
```

## Step 4: Upload to MinIO

Upload the selected image to MinIO for persistent storage:

```
Tool: a-minio-uploadImageToMinio
Input: {
  "body": {
    "file_url": "https://images.pexels.com/photos/12345/pexels-photo-12345.jpeg?auto=compress&cs=tinysrgb&w=940"
  }
}
```

The tool accepts any publicly accessible image URL and uploads it to the configured MinIO bucket.

## Step 5: Use the Hosted URL

The upload returns a MinIO-hosted URL. Use this URL in your application instead of linking directly to Pexels/Unsplash:

```typescript
const product = {
  name: "Wireless Headphones",
  image: "<returned_minio_url>",  // Persistent, self-hosted
  thumbnail: "<returned_minio_url_thumbnail>"
};
```

## Why Upload to MinIO?

- **Reliability** — Stock photo URLs may change or expire
- **Performance** — Serve from your own CDN/storage
- **Independence** — No runtime dependency on third-party services
- **Compliance** — Some licenses require hosting your own copy

## Full Workflow Summary

```
1. searchPhotos / get_search_photos  →  Find the right image
2. get_photos_download               →  Track download (Unsplash only)
3. a-minio-uploadImageToMinio        →  Upload to persistent storage
4. Use MinIO URL in your app         →  Reference the self-hosted copy
```

## Tips

- Upload the size you need — `src.medium` (940px) is usually sufficient for web apps
- Do not upload `src.original` unless you need print-quality resolution — larger files waste storage
- The MinIO upload tool requires a publicly accessible URL — all Pexels and Unsplash image URLs work
- For batch uploads, process one image at a time to avoid rate limits
