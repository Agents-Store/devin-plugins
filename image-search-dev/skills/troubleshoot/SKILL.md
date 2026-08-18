---
name: troubleshoot
description: This skill should be used when the user encounters "pexels error", "unsplash error", "image search not working", "rate limit on stock photos", "stock photo tool not found", "image search rate limited", or needs to diagnose and fix problems with Pexels, Unsplash, or MinIO upload tools.
---

# Image Search Troubleshooting

Diagnostic steps and fixes for common problems with Pexels, Unsplash, and MinIO upload tools.

## Quick Diagnostics

Run these checks in order:

1. **Tool availability** — try `searchPhotos` with `{ "query": "test", "per_page": 1 }`. If "tool not found", the `mcpware-dev-tools` MCP server is not configured.
2. **API key validity** — a successful search confirms the API key works. A 401 error means the key is invalid.
3. **Rate limits** — a 429 error means you hit the rate limit. Wait before retrying.

## Pexels Issues

| Error | Cause | Fix |
|-------|-------|-----|
| Tool not found | `mcpware-dev-tools` MCP not configured | Add the MCP server to Claude Code settings |
| 401 Unauthorized | Invalid Pexels API key | Regenerate key at https://www.pexels.com/api/ |
| 429 Too Many Requests | Rate limit exceeded (200 req/hr) | Wait 1-2 minutes, then retry with smaller `per_page` |
| Empty results | Query too specific or misspelled | Try broader search terms, remove filters |
| Timeout | Network or service issue | Check connectivity, retry |

### Pexels Rate Limits

- **200 requests per hour** per API key
- **200 monthly requests** on free tier (check your plan)
- Reduce usage: use smaller `per_page`, cache results, avoid redundant searches

## Unsplash Issues

| Error | Cause | Fix |
|-------|-------|-----|
| Tool not found | `mcpware-dev-tools` MCP not configured | Add the MCP server to Claude Code settings |
| 401 Unauthorized | Invalid Unsplash API key | Regenerate key at https://unsplash.com/developers |
| 429 Too Many Requests | Rate limit exceeded (50 req/hr) | Wait before retrying |
| 403 Forbidden | App not approved for production | Apply for production access on Unsplash developer dashboard |
| Empty results | Query too narrow | Use broader terms |

### Unsplash Rate Limits

- **50 requests per hour** for demo apps
- **5000 requests per hour** for approved production apps
- Apply for production access: Unsplash Developer dashboard → Your Apps → Apply for Production

### Unsplash Download Tracking

If you receive a warning about download tracking: always call `get_photos_download` with the photo `id` after using any Unsplash photo. This is mandatory per Unsplash API Terms of Service. Skipping it may lead to API access revocation.

## MinIO Upload Issues

| Error | Cause | Fix |
|-------|-------|-----|
| Tool not found | `mcpware-dev-tools` MCP not configured | Add the MCP server to Claude Code settings |
| Upload failed | Invalid or inaccessible image URL | Verify the URL is publicly accessible |
| Bucket error | MinIO bucket not configured | Check MinIO server configuration |
| File too large | Image exceeds upload limit | Use a smaller image size (e.g., `src.medium` instead of `src.original`) |

## Cross-Service Issues

### "Tool not found" for All Tools

All image search tools come from the `mcpware-dev-tools` MCP server. If no tools are found:
1. Check that `mcpware-dev-tools` is listed in your MCP server configuration
2. Verify the MCP server is running and accessible
3. Restart Claude Code to refresh MCP connections

### Slow Responses

| Symptom | Cause | Fix |
|---------|-------|-----|
| Searches take > 10s | Large `per_page` value | Reduce to 10-15 results |
| Multiple timeouts | MCP server overloaded | Space out requests |
| Inconsistent speed | Network variability | Retry failed requests |

### Choosing Between Services

If one service is unavailable or rate-limited, switch to the other:

| Need | If Pexels unavailable | If Unsplash unavailable |
|------|----------------------|------------------------|
| Photos | Use `get_search_photos` (Unsplash) | Use `searchPhotos` (Pexels) |
| Videos | No alternative — Unsplash has no video support | Use `searchVideos` (Pexels) |
| Curated | Use `get_photos_random` (Unsplash) | Use `getCuratedPhotos` (Pexels) |
