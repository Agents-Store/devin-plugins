---
name: examples
description: >
  End-to-end scenario walkthroughs for updating self-hosted Dify. Use when the user asks for
  "dify update example", "how to update dify", "show me an update walkthrough", "dify upgrade
  guide", "step-by-step dify update", or needs a complete example of the update process.
---

## Available Scenarios

| Scenario | Description | Reference |
|----------|-------------|-----------|
| Routine update | Pull latest main, no conflicts, add new env vars, rebuild | `references/scenarios/routine-update.md` |
| Tagged release update | Update to specific version, resolve conflict, custom project name | `references/scenarios/tagged-release-update.md` |

## Quick Reference: Happy Path

```bash
# From dify/ root directory
git fetch origin --tags
git checkout dev
git merge origin/main

# Move to docker directory
cd docker/

# Sync environment
grep -E '^[A-Z_][A-Z0-9_]*=' .env.example | cut -d= -f1 | sort > /tmp/example-keys
grep -E '^[A-Z_][A-Z0-9_]*=' .env | cut -d= -f1 | sort > /tmp/env-keys
NEW=$(comm -23 /tmp/example-keys /tmp/env-keys)
# Append new vars to .env

# Rebuild
docker compose up -d --build

# Verify
docker compose ps
```

## Quick Reference: Specific Version

```bash
git fetch origin --tags
git checkout dev
git merge v0.15.0
# Resolve any conflicts
cd docker/
# Sync .env
docker compose -p myproject up -d --build
docker compose ps
```
