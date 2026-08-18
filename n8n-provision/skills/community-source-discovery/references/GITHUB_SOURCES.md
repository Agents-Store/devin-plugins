# GitHub Sources for n8n Workflows

Catalog of GitHub repositories hosting importable n8n workflow JSON files. Use these as fallback when the official n8n template library (api.n8n.io) lacks a suitable match.

## Repository Catalog

| Repo | Stars | Workflows | License | Last Active |
|------|-------|-----------|---------|-------------|
| Zie619/n8n-workflows | ~53,500 | 4,300+ | Unspecified | Monthly scrape from n8n.io |
| enescingoz/awesome-n8n-templates | ~20,900 | 280+ | MIT | Active maintenance |
| Danitilahun/n8n-workflow-templates | ~606 | 2,053 | MIT | Periodic updates |
| ritik-prog/n8n-automation-templates-5000 | ~335 | 5,000+ | MIT | Bulk upload |
| zengfr/n8n-workflow-all-templates | ~100 | 8,615+ | Unspecified | Monthly auto-sync |
| EtienneLescot/n8n-as-code | ~636 | 7,700+ | MIT | Active development |

---

## Zie619/n8n-workflows

The largest community collection. Scraped from n8n.io and community submissions.

**Web UI:** `https://zie619.github.io/n8n-workflows`
- Browse by category, search by keyword
- Each workflow has a detail page with description, node list, and raw JSON link

**Raw JSON access pattern:**
```
https://raw.githubusercontent.com/Zie619/n8n-workflows/main/workflows/{id}.json
```

**Search strategy:**
1. Use `~~search` with query: `site:github.com/Zie619/n8n-workflows {keyword}`
2. Or scrape `https://zie619.github.io/n8n-workflows` and search the index page
3. Workflow IDs map to n8n.io template IDs when sourced from the official library

**Quality notes:**
- Mixed quality — includes raw scrapes and curated submissions
- Always validate JSON schema before import
- Some workflows reference deprecated node types (pre-n8n 1.0)
- Check `nodes[].typeVersion` to detect outdated node versions

---

## enescingoz/awesome-n8n-templates

Curated, high-quality collection organized by integration category.

**Directory structure:**
```
Telegram/
Discord/
OpenAI/
Slack/
WhatsApp/
DevOps/
Google/
Notion/
Airtable/
...
```

**Raw JSON access pattern:**
```
https://raw.githubusercontent.com/enescingoz/awesome-n8n-templates/main/{Category}/{filename}.json
```

**Search strategy:**
1. Browse category directories matching the user's target integration
2. File names are descriptive (e.g., `Slack-GitHub-PR-Notification.json`)
3. Use `~~search` with query: `site:github.com/enescingoz/awesome-n8n-templates {keyword}`

**Quality notes:**
- Higher quality than bulk collections — each template is manually reviewed
- Fewer workflows but better documentation per workflow
- Good starting point before checking larger repos
- Regularly updated with new integrations

---

## Danitilahun/n8n-workflow-templates

Well-organized collection with a searchable backend.

**Directory structure:**
```
workflows/
  {id}.json
  {id}.json
  ...
```

**FastAPI search backend:** The repo includes a Python FastAPI backend for searching workflows. Not always running publicly, but the JSON files are directly accessible.

**Raw JSON access pattern:**
```
https://raw.githubusercontent.com/Danitilahun/n8n-workflow-templates/main/workflows/{id}.json
```

**Search strategy:**
1. Use `~~search` targeting the repo for keyword matches
2. Workflow file names are numeric IDs — use the repo's README or search to map IDs to descriptions
3. The `workflows/` directory can be listed via GitHub API for bulk access

**Quality notes:**
- Clean JSON format, ready for import
- Numeric IDs make browsing harder — search is essential
- Good coverage of common automation patterns

---

## ritik-prog/n8n-automation-templates-5000

Large bulk collection organized by category.

**Directory structure:**
```
{category}/
  {workflow-name}.json
```

**Raw JSON access pattern:**
```
https://raw.githubusercontent.com/ritik-prog/n8n-automation-templates-5000/main/{category}/{filename}.json
```

**Search strategy:**
1. Browse category directories for the target integration
2. File names are descriptive
3. Use `~~search` for specific keywords within the repo

**Quality notes:**
- MIT licensed — safe for production use
- Large volume but variable quality
- Some workflows may use older n8n node versions
- Always validate before importing

---

## zengfr/n8n-workflow-all-templates

Most comprehensive mirror — auto-synced monthly from n8n.io official library.

**Raw JSON access pattern:**
```
https://raw.githubusercontent.com/zengfr/n8n-workflow-all-templates/main/{filename}.json
```

**Search strategy:**
1. This repo mirrors the official library — use it when `~~template_search` is unavailable or rate-limited
2. Files are named by template ID or title
3. Monthly sync means it may lag 1-4 weeks behind the live library

**Quality notes:**
- Mirrors official library quality — generally high
- Auto-generated, so no curation beyond what n8n.io provides
- Useful as a backup data source when the API is down

---

## EtienneLescot/n8n-as-code

Workflows in TypeScript SDK format rather than raw JSON.

**Format:** TypeScript files using the n8n SDK
```typescript
// Example: not directly importable as JSON
import { Workflow } from 'n8n-workflow';
// ...
```

**Conversion required:** These are NOT raw JSON workflow files. To import:
1. Extract the workflow definition from the TypeScript code
2. Convert to n8n JSON format
3. Or use them as reference for building workflows via `n8n-native-mcp`

**Search strategy:**
1. Best for understanding patterns and architecture
2. Use as reference when building complex workflows programmatically
3. TypeScript provides better documentation of parameter types

**Quality notes:**
- High quality code with type safety
- Not directly importable — needs conversion
- Excellent for learning n8n workflow patterns
- Active development with regular additions

---

## General Access Patterns

### Fetching raw JSON from GitHub

```
# Direct raw file URL
https://raw.githubusercontent.com/{owner}/{repo}/main/{path}/{file}.json

# GitHub API (respects rate limits, returns metadata)
https://api.github.com/repos/{owner}/{repo}/contents/{path}
```

### Rate limiting

- Unauthenticated GitHub API: 60 requests/hour
- Authenticated: 5,000 requests/hour
- Raw file access (raw.githubusercontent.com): No strict rate limit, but may be throttled

### Scraping with ~~scrape

When fetching workflow JSON from GitHub:
1. Use the `raw.githubusercontent.com` URL for direct JSON content
2. Use `~~scrape` on the main repo page only if you need to discover file paths
3. Parse the JSON response — it should be a valid n8n workflow object with `nodes[]` and `connections{}`

### Validation after fetch

Always validate fetched community JSON before importing:
```
1. Parse JSON — must be valid
2. Check for required fields: nodes, connections
3. Check node types — look for deprecated types
4. Check typeVersion — flag outdated versions
5. Use ~~workflow_validate if available
6. Then import via ~~workflow_create
```
