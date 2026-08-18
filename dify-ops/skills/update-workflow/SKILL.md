---
name: update-workflow
description: >
  Git workflow for updating self-hosted Dify — fetch upstream, merge main into dev, handle
  conflicts, checkout specific tags. Use when updating Dify, merging upstream changes, handling
  merge conflicts in Dify, or switching to a specific Dify version/tag. Triggers on "update dify",
  "pull dify changes", "merge main into dev", "upgrade dify", "dify version".
---

## Branch Model

User maintains two branches:
- **`main`** — tracks upstream `origin/main` (official Dify releases)
- **`dev`** — local customizations (custom ports, volumes, env overrides in docker-compose)

Updates flow: `origin/main` → local `main` → merge into `dev`

## Pre-flight Checks

Run from DIFY_ROOT (git repo root) before any update:

```bash
# 1. Verify we're in a git repo
git rev-parse --git-dir 2>/dev/null || echo "ERROR: Not a git repo"

# 2. Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# 3. Check for uncommitted changes
DIRTY=$(git status --porcelain)
if [ -n "$DIRTY" ]; then
  echo "WARNING: Uncommitted changes detected"
  git status --short
fi

# 4. Record current commit for rollback
PRE_UPDATE_COMMIT=$(git rev-parse HEAD)
echo "Pre-update commit: $PRE_UPDATE_COMMIT"
```

**If working tree is dirty:**
- Show `git status` to the user
- Ask: "You have uncommitted changes. Options: (1) commit them, (2) stash them, (3) abort"
- If stash: `git stash` — remember to `git stash pop` after update completes
- Record `STASHED=true` for later

## Update to Latest Main

```bash
cd $DIFY_ROOT

# Fetch all branches and tags
git fetch origin --tags

# Switch to dev if not already there
CURRENT=$(git branch --show-current)
if [ "$CURRENT" != "dev" ]; then
  git checkout dev
fi

# Merge upstream main into dev
git merge origin/main
```

If merge succeeds cleanly → proceed to env sync.

## Update to Specific Tag/Version

```bash
cd $DIFY_ROOT

# Fetch all tags
git fetch origin --tags

# Verify tag exists
TAG="$USER_TAG"
if ! git tag -l "$TAG" | grep -q "$TAG"; then
  # Try with 'v' prefix
  if git tag -l "v$TAG" | grep -q "v$TAG"; then
    TAG="v$TAG"
    echo "Found tag: $TAG (added v prefix)"
  else
    echo "ERROR: Tag '$TAG' not found"
    echo "Available recent tags:"
    git tag --sort=-creatordate | head -10
    # STOP — ask user to pick a valid tag
  fi
fi

# Switch to dev and merge the tag
git checkout dev
git merge "$TAG"
```

## Merge Conflict Handling

When `git merge` reports conflicts:

```bash
# List all conflicted files
CONFLICTS=$(git diff --name-only --diff-filter=U)
echo "Conflicted files:"
echo "$CONFLICTS"
```

### Resolution Strategy by File

| File | Strategy | Reason |
|------|----------|--------|
| `docker/.env.example` | Accept theirs | We sync .env separately; .env.example should match upstream |
| `docker/docker-compose.yaml` | Manual merge | User's custom ports/volumes must be preserved |
| Other files | Show diff, let user decide | Context-dependent |

### For `.env.example` conflicts:
```bash
git checkout --theirs docker/.env.example
git add docker/.env.example
```

### For `docker-compose.yaml` conflicts:
1. Read the file and show conflict markers to the user
2. Common conflict areas: port mappings, volume paths, image tags
3. User's customizations (usually port numbers like `8080:80`) should be kept
4. Upstream changes (new services, new env vars in service definitions) should be accepted
5. Help user merge manually, then `git add docker/docker-compose.yaml`

### For other files:
```bash
# Show the diff for each conflicted file
for f in $CONFLICTS; do
  echo "=== $f ==="
  git diff "$f"
done
```

### After resolving all conflicts:
```bash
git add .
git commit -m "Merge upstream into dev"
```

## Post-merge: Volume Backup

After successful merge (clean or resolved), **always backup Docker volumes before rebuilding containers** — volumes hold persistent data (postgres, redis, weaviate, file storage) that cannot be recovered if a container rebuild or migration corrupts them.

```bash
cd $DOCKER_DIR

# Create timestamped archive of all volumes
tar -cvf volumes-$(date +%s).tgz volumes
echo "Volume backup created"
```

Keep at least the last backup until the update is verified healthy. If disk space is a concern, remove older backups after confirming the new version works.

## Post-merge: Status

```bash
NEW_COMMIT=$(git rev-parse HEAD)
echo "Updated from $PRE_UPDATE_COMMIT to $NEW_COMMIT"
echo "Rollback command: git reset --hard $PRE_UPDATE_COMMIT"
echo "WARNING: Rollback will NOT undo database migrations — restore volumes from backup"
```

If stashed earlier:
```bash
git stash pop
```

## Checking Available Updates

To check if updates are available without applying them:

```bash
cd $DIFY_ROOT
git fetch origin --tags

# Commits behind main
BEHIND=$(git rev-list --count HEAD..origin/main)
echo "Commits behind origin/main: $BEHIND"

# Latest remote tag
LATEST_TAG=$(git tag --sort=-creatordate | head -1)
echo "Latest tag: $LATEST_TAG"

# Current local tag (if any)
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
echo "Current tag: $CURRENT_TAG"
```
