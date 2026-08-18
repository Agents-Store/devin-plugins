---
name: examples
description: Scenario walkthroughs for media hosting operations. Use when learning how to upload images or seeing practical usage patterns.
disable-model-invocation: true
---

# Media Hosting Examples

## Scenario 1: Upload a Single Image

**User**: "Upload this image to hosting: https://www.training.com.au/wp-content/uploads/Full-Stack-Developer-1.jpeg"

**Action**: Call the MCP tool with the provided URL.

```json
mcp__mcpware-dev-tools__a-minio-uploadImageToMinio({
  "body": {
    "file_url": "https://www.training.com.au/wp-content/uploads/Full-Stack-Developer-1.jpeg"
  }
})
```

**Result**: The tool returns the hosted URL from MinIO. Share this URL with the user.

---

## Scenario 2: Upload an Image Found During Research

**User**: "Find a good hero image for a developer portfolio and upload it to our hosting"

**Steps**:
1. Search for an appropriate image using web search or image search tools (Pexels, Unsplash)
2. Get the direct image URL from the search result
3. Upload using the tool:

```json
mcp__mcpware-dev-tools__a-minio-uploadImageToMinio({
  "body": {
    "file_url": "https://images.pexels.com/photos/example/developer-workspace.jpeg"
  }
})
```

4. Return the hosted URL to the user

---

## Scenario 3: Batch Upload Multiple Images

**User**: "Upload these three product images to hosting"

**Steps**: Call the tool once per image, sequentially:

```json
// Image 1
mcp__mcpware-dev-tools__a-minio-uploadImageToMinio({
  "body": { "file_url": "https://example.com/product-front.jpg" }
})

// Image 2
mcp__mcpware-dev-tools__a-minio-uploadImageToMinio({
  "body": { "file_url": "https://example.com/product-side.jpg" }
})

// Image 3
mcp__mcpware-dev-tools__a-minio-uploadImageToMinio({
  "body": { "file_url": "https://example.com/product-back.jpg" }
})
```

Collect all returned hosted URLs and present them together to the user.
