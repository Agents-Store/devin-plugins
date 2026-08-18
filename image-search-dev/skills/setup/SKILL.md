---
name: setup
description: This skill should be used when the user asks to "verify image search setup", "check pexels connection", "check unsplash MCP", "test image search tools", "is pexels working", "is unsplash working", or needs to confirm that the Pexels and Unsplash MCP tools are operational.
---

# Image Search Setup Verification

Verify that Pexels and Unsplash MCP tools are accessible via the `mcpware-dev-tools` server.

## Prerequisites

- The `mcpware-dev-tools` MCP server must be configured in your Claude Code settings or project `.mcp.json`
- Valid API keys for Pexels and/or Unsplash must be configured in the MCP server

## Verification Steps

### 1. Check Pexels Connection

Run a minimal search to verify the Pexels tools are accessible:

```
Tool: searchPhotos
Input: { "query": "test", "per_page": 1 }
```

**Expected:** Returns a result with at least one photo object containing `id`, `src`, `photographer`.

### 2. Check Unsplash Connection

Run a minimal search to verify the Unsplash tools are accessible:

```
Tool: get_search_photos
Input: { "query": "test", "per_page": 1 }
```

**Expected:** Returns a result with at least one photo object containing `id`, `urls`, `user`.

### 3. Check MinIO Upload (Optional)

If you plan to upload found images to MinIO storage, verify the upload tool is available by checking that `a-minio-uploadImageToMinio` appears in the available tools list.

### Service Status Summary

After running the checks, report status:

| Service | Tool Tested | Status |
|---------|-------------|--------|
| Pexels | `searchPhotos` | Working / Not Available |
| Unsplash | `get_search_photos` | Working / Not Available |
| MinIO Upload | `a-minio-uploadImageToMinio` | Available / Not Available |

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Tool not found | `mcpware-dev-tools` MCP server not configured | Add the MCP server to your Claude Code settings |
| 401 Unauthorized | Invalid API key in MCP server config | Check API key configuration in the MCP server |
| Empty results | API key valid but no permissions | Verify API key has search permissions |
| Timeout | Network issue | Check internet connectivity |

## What This Skill Does NOT Cover

- Installing or configuring the `mcpware-dev-tools` MCP server — that is managed outside this plugin
- Creating Pexels or Unsplash API keys — visit https://www.pexels.com/api/ or https://unsplash.com/developers
- Configuring MinIO buckets — see your MinIO admin panel
