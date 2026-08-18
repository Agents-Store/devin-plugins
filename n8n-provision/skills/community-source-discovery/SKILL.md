---
name: community-source-discovery
description: Find n8n workflows from GitHub repositories and third-party platforms when the official template library is insufficient. Use when asked to "find n8n workflow on github", "community n8n workflows", "search github for n8n", "n8n workflow sources", "n8n automation repository", or when official template search returns no good matches.
---

# Community Source Discovery

Find n8n workflow JSON from GitHub repositories, community forums, and third-party platforms. Use this skill when the official template library (template-discovery) returns no suitable results or when the user specifically requests community/GitHub sources.

All web searches use `~~search` and page reads use `~~scrape` — see CONNECTORS.md for provider fallback chains.

See [references/GITHUB_SOURCES.md](references/GITHUB_SOURCES.md) for curated repository list and [references/COMMUNITY_PLATFORMS.md](references/COMMUNITY_PLATFORMS.md) for third-party platform details.

## Tiered Search Strategy

Always follow this order. Do NOT skip to GitHub without checking the official library first.

```
Tier 1: OFFICIAL LIBRARY (template-discovery skill)
  → ~~template_search with user's query
  → If good match found → stop, use it

Tier 2: GITHUB REPOSITORIES
  → ~~search with targeted GitHub queries
  → ~~scrape to fetch raw workflow JSON from repos

Tier 3: COMMUNITY PLATFORMS
  → ~~search on n8n community forum, blogs, tutorials
  → ~~scrape to extract workflow JSON or download links
```

### When to escalate from Tier 1 to Tier 2

- Official search returns 0 results.
- Results exist but none match the required node combination.
- User needs a workflow for a niche integration not in the template library.
- User explicitly asks for GitHub/community sources.
- Template library versions are outdated for the user's n8n version.

## Tier 2: GitHub Search

### Targeted search queries

Construct queries that combine the workflow purpose with GitHub-specific filters:

```
~~search("n8n workflow JSON site:github.com <use-case>")
~~search("n8n-nodes-base.<nodeName> workflow.json site:github.com")
~~search("repo:n8nio/n8n-templates <keyword>")
~~search("filename:workflow.json n8n <integration-name> site:github.com")
```

### High-value repositories

Search these repositories first — they contain curated, tested workflows:

| Repository | What It Contains |
|------------|-----------------|
| `n8nio/n8n-templates` | Official template source (may have more than API exposes) |
| `n8nio/n8n` | Core repo — example workflows in docs and tests |
| `n8nio/n8n-docs` | Documentation examples with workflow JSON |
| Community repos | User-shared workflows (search by topic) |

### Fetching raw JSON from GitHub

Once a workflow file is located, fetch the raw content:

```
1. ~~search("site:github.com n8n workflow <query>") → find repo URL
2. Convert GitHub URL to raw URL:
   github.com/user/repo/blob/main/file.json
   → raw.githubusercontent.com/user/repo/main/file.json
3. ~~scrape(raw_url) → workflow JSON
```

Always convert to `raw.githubusercontent.com` before scraping — the regular GitHub page wraps JSON in HTML.

### GitHub search operators

| Operator | Example | Purpose |
|----------|---------|---------|
| `site:github.com` | `n8n webhook site:github.com` | Limit to GitHub |
| `repo:<owner>/<name>` | `repo:n8nio/n8n-templates slack` | Search specific repo |
| `filename:` | `filename:workflow.json n8n` | Find workflow files by name |
| `path:` | `path:workflows/ n8n` | Search in specific directories |
| `extension:json` | `n8n nodes extension:json` | JSON files only |

## Tier 3: Community Platforms

When GitHub search is insufficient, search broader community sources:

```
Forum:     ~~search("site:community.n8n.io <query>")
Tutorials: ~~search("n8n workflow tutorial <query>")
YouTube:   ~~search("n8n tutorial <query> site:youtube.com")
```

- Forum posts often contain workflow JSON in code blocks — `~~scrape(post_url)` to extract.
- Blog tutorials frequently include downloadable workflow JSON.
- YouTube descriptions sometimes link to workflow JSON files.

## Quality Assessment

Not all community workflows are safe or functional. Assess every candidate before recommending.

### Heuristics

| Signal | Good | Caution |
|--------|------|---------|
| **GitHub stars** | > 50 on the repo | < 5 or no stars |
| **Last updated** | Within 6 months | Over 1 year ago |
| **Creator** | n8n team, known contributor | Anonymous, single-repo account |
| **Node versions** | Uses `typeVersion` matching user's n8n | Missing typeVersion or very old |
| **Hardcoded values** | Parameterized with expressions | Hardcoded API keys, URLs, IDs |
| **Error handling** | Has error-trigger or try/catch | No error handling at all |
| **Documentation** | README explains what the workflow does | No description |

### Red flags

- Workflow JSON contains actual API keys or tokens (security risk).
- Uses deprecated nodes (`n8n-nodes-base.function` instead of `n8n-nodes-base.code`).
- References community nodes not available in the user's installation.
- Over 50 nodes with no sub-workflow organization.
- No `connections` object or empty node list (broken export).

## After Discovery

Once a suitable community workflow is found:

```
1. ~~scrape(raw_json_url) → fetch the workflow JSON
2. Run workflow-analysis skill → assess compatibility and security
3. ~~workflow_validate(json) → validate before import
4. ~~workflow_create(json) → import to n8n instance (not ~~template_deploy)
5. ~~workflow_list → verify import succeeded
```

Use `~~workflow_create` (not `~~template_deploy`) for community JSON — template deploy is only for official library templates.
