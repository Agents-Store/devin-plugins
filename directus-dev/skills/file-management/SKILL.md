---
name: file-management
description: File and asset management — upload via URL, organize folders, query file metadata, retrieve base64 assets. This skill should be used when the user asks to manage files, upload images, import files from URLs, organize folders, query file metadata, or retrieve assets in Directus.
---

# File Management

Reference for the `files`, `assets`, and `folders` MCP tools.

## Three Tools

| Tool | Purpose | Actions |
|------|---------|---------|
| `files` | File metadata CRUD + URL imports | read, update, delete, import |
| `assets` | Retrieve file content as base64 | read by ID |
| `folders` | Virtual file organization | create, read, update, delete |

**Note:** Files cannot be uploaded directly from local disk via MCP. Use the `import` action to import from URLs.

## Files Tool

### Import Files from URL

```json
Tool: files
Input: {
  "action": "import",
  "data": [{
    "url": "https://example.com/photo.jpg",
    "file": {
      "title": "Product Hero Image",
      "description": "Main product photo for landing page",
      "folder": "folder-uuid-here"
    }
  }]
}
```

### Batch Import

```json
Tool: files
Input: {
  "action": "import",
  "data": [
    {
      "url": "https://example.com/image1.jpg",
      "file": { "title": "Image 1", "folder": "folder-uuid" }
    },
    {
      "url": "https://example.com/image2.jpg",
      "file": { "title": "Image 2", "folder": "folder-uuid" }
    }
  ]
}
```

### List Files

```json
Tool: files
Input: {
  "action": "read",
  "query": {
    "fields": ["id", "title", "filename_download", "type", "filesize", "width", "height", "folder"],
    "filter": { "type": { "_starts_with": "image/" } },
    "sort": ["-uploaded_on"],
    "limit": 25
  }
}
```

### Filter by Folder

```json
Tool: files
Input: {
  "action": "read",
  "query": {
    "fields": ["id", "title", "type", "filesize"],
    "filter": { "folder": { "_eq": "folder-uuid" } },
    "limit": 50
  }
}
```

### Update File Metadata

```json
Tool: files
Input: {
  "action": "update",
  "keys": ["file-uuid"],
  "data": [{
    "title": "Updated Title",
    "description": "Better description for SEO",
    "focal_point_x": 0.5,
    "focal_point_y": 0.3
  }]
}
```

### Delete Files

```json
Tool: files
Input: {
  "action": "delete",
  "keys": ["file-uuid-1", "file-uuid-2"]
}
```

## File Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | uuid | File identifier |
| `title` | string | Display title |
| `filename_disk` | string | Storage filename |
| `filename_download` | string | Download filename |
| `type` | string | MIME type (e.g., `image/jpeg`) |
| `folder` | uuid | Parent folder ID |
| `filesize` | integer | Size in bytes |
| `width` | integer | Image width (px) |
| `height` | integer | Image height (px) |
| `duration` | integer | Audio/video duration (ms) |
| `description` | string | File description |
| `location` | string | Location metadata |
| `tags` | string \| null | Comma-separated tags string (not an array — the MCP tool schema expects `string \| null`, arrays will cause validation errors) |
| `uploaded_by` | uuid | Uploader user ID |
| `uploaded_on` | timestamp | Upload date |
| `modified_by` | uuid | Last modifier |
| `modified_on` | timestamp | Last modified date |
| `focal_point_x` | float | Focal point X (0-1) |
| `focal_point_y` | float | Focal point Y (0-1) |

## Assets Tool

Retrieve file content as base64 for AI analysis:

```json
Tool: assets
Input: { "id": "file-uuid" }
```

Returns:
```json
{ "data": "base64-encoded-content", "mimeType": "image/jpeg" }
```

Supports images and audio files. Use for:
- Image analysis with vision models
- Reading document content
- Audio file processing

## Folders Tool

### Create Folder

```json
Tool: folders
Input: {
  "action": "create",
  "data": [{
    "name": "Product Images",
    "parent": null
  }]
}
```

### Create Nested Folder

```json
Tool: folders
Input: {
  "action": "create",
  "data": [{
    "name": "Thumbnails",
    "parent": "parent-folder-uuid"
  }]
}
```

### List Folders

```json
Tool: folders
Input: {
  "action": "read",
  "query": {
    "fields": ["id", "name", "parent"],
    "sort": ["name"]
  }
}
```

### Update Folder

```json
Tool: folders
Input: {
  "action": "update",
  "keys": ["folder-uuid"],
  "data": [{ "name": "Renamed Folder" }]
}
```

### Delete Folder

```json
Tool: folders
Input: {
  "action": "delete",
  "keys": ["folder-uuid"]
}
```

**Note:** Folders are virtual (database only) — they don't correspond to filesystem directories in storage.

## Common Workflows

### Organize Files into Folders

1. Create folder structure:
```json
Tool: folders
Input: {
  "action": "create",
  "data": [
    { "name": "Blog" },
    { "name": "Products" },
    { "name": "Team" }
  ]
}
```

2. Move files to folders:
```json
Tool: files
Input: {
  "action": "update",
  "keys": ["file-uuid-1", "file-uuid-2"],
  "data": [{ "folder": "blog-folder-uuid" }]
}
```

### Import and Catalog Images

1. Create target folder
2. Import files from URLs with metadata:
```json
Tool: files
Input: {
  "action": "import",
  "data": [
    {
      "url": "https://cdn.example.com/hero.jpg",
      "file": {
        "title": "Homepage Hero",
        "folder": "folder-uuid"
      }
    }
  ]
}
```

### Rename and Tag Files in Bulk

1. List files to rename:
```json
Tool: files
Input: {
  "action": "read",
  "query": {
    "filter": { "title": { "_null": true } },
    "fields": ["id", "filename_download", "type"],
    "limit": 50
  }
}
```

2. Update each file with descriptive metadata

### Analyze an Image

1. Get file UUID from files list
2. Retrieve content:
```json
Tool: assets
Input: { "id": "file-uuid" }
```
3. The returned base64 data can be processed by vision models

## Best Practices

- Use folders to organize files — don't leave everything in the root
- Set descriptive titles on import — don't rely on original filenames
- Tags are `string | null` in the MCP tool schema — pass a comma-separated string like `"hero,product"`, never an array
- Filter by MIME type when listing: `{ "type": { "_starts_with": "image/" } }`
- Set focal points for images used in cropped contexts
- Import files with metadata in a single call rather than importing then updating
