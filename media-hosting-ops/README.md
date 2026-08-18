# media-hosting-ops (Devin plugin)

Media hosting operations plugin. Upload images by public URL to MinIO-based media hosting via the uploadImageToMinio MCP tool.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (2)

- `examples` — Scenario walkthroughs for media hosting operations. Use when learning how to upload images or seeing practical usage patterns.
- `upload-image` — Use when the user asks to "upload image", "host image", "upload to minio", "image url to hosting", "store image", "upload picture", "get hosted url for image", "save image to hosting", "re-host image", "get a permanent url for image", "I need a stable link for this picture", "minio upload", or needs to upload an image from a public URL to media hosting. Also trigger when the user wants to store an image somewhere reliable, get a permanent/stable URL for a picture, or move an image to their own hosting — even if they don't explicitly say "upload".

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/media-hosting-ops
