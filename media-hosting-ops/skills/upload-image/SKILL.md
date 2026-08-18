---
name: upload-image
description: Use when the user asks to "upload image", "host image", "upload to minio", "image url to hosting", "store image", "upload picture", "get hosted url for image", "save image to hosting", "re-host image", "get a permanent url for image", "I need a stable link for this picture", "minio upload", or needs to upload an image from a public URL to media hosting. Also trigger when the user wants to store an image somewhere reliable, get a permanent/stable URL for a picture, or move an image to their own hosting — even if they don't explicitly say "upload".
---

# Upload Image to Media Hosting

Upload any publicly accessible image to MinIO-based media hosting and get back a permanent hosted URL.

## Tool

Use the MCP tool `mcp__mcpware-dev-tools__a-minio-uploadImageToMinio`.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `body.file_url` | string (URI) | Yes | Public URL of the image to upload |

## How to Call

```json
{
  "body": {
    "file_url": "https://example.com/photo.jpg"
  }
}
```

The tool downloads the image from the provided URL and uploads it to the MinIO bucket.

## Response Format

**Success** — the tool returns the permanent hosted URL in `data.uploaded_file_url`:

```json
{
  "success": true,
  "error": null,
  "data": {
    "uploaded_file_url": "https://w.autohoster.website/web/a2b0ce3cb0813f3b5f9d885054c734d0893972df3b3b.jpg"
  }
}
```

Share the `uploaded_file_url` value with the user — this is the permanent hosted link.

**Error** — when the source URL is unreachable or invalid:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "FILE_DOWNLOAD_FAILED",
    "message": "Unable to download file from source URL."
  }
}
```

When `success` is `false`, report the `error.message` to the user and ask them to verify the source URL.

## Requirements

- The `mcpware-dev-tools` MCP server must be connected
- The source URL must be publicly accessible (no auth-protected URLs)
- The URL must point directly to an image file

## Supported Image Formats

Common web image formats are supported: JPEG, PNG, GIF, WebP, SVG, BMP, TIFF, ICO.

## When to Use

1. **Hosting an image for use in other tools** - upload an image so its hosted URL can be used in documents, bots, or APIs
2. **Migrating images** - re-host images from external sources to your own media hosting
3. **Storing screenshots or generated images** - upload output from screenshot tools or image generators

## Batch Upload

To upload multiple images, call the tool once per image. Process them sequentially to avoid overwhelming the server.

## Error Handling

- If the source URL is unreachable, the tool returns an error - verify the URL is publicly accessible first
- If the URL does not point to a valid image, the upload will fail
- Large images may take longer to process
