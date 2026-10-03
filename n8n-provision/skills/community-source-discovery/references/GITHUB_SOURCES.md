# GitHub Sources for n8n Workflows

Catalog of GitHub repositories hosting importable n8n workflow JSON files. Use these as fallback when the official n8n template library (api.n8n.io) lacks a suitable match.

Figures below were read from GitHub on 2026-10-02/03 and drift fast — re-check stars, license and last push (`gh api repos/<owner>/<name>`) before relying on them.

## Repository Catalog

| Repo | Stars | Workflows | License | Last push |
|------|-------|-----------|---------|-----------|
| Zie619/n8n-workflows | ~56,900 | 4,343 files | MIT | 2026-06 |
| enescingoz/awesome-n8n-templates | ~25,700 | 280+ | none stated (GitHub reports NOASSERTION) | 2026-09 |
| EtienneLescot/n8n-as-code | ~1,590 | 7,700+ | MIT | 2026-10 (active) |
| ritik-prog/n8n-automation-templates-5000 | ~510 | 5,000+ | MIT | 2026-07 |
| zengfr/n8n-workflow-all-templates | ~116 | 12,333 files | Apache-2.0 | 2026-09 |
| Danitilahun/n8n-workflow-templates | ~720 | 2,053 | none | **2025-07 — stale** (over a year without a push: Caution) |

A repo with no license gives you no stated right to reuse its workflows — say so when recommending one. The official n8n library itself is **not** in git; its only public source is `api.n8n.io`.

---

## Zie619/n8n-workflows

The largest community collection. Scraped from n8n.io and community submissions.

**Web UI:** `https://zie619.github.io/n8n-workflows`
- Browse by category, search by keyword
- Each workflow has a detail page with description, node list, and raw JSON link

**Directory structure** (one folder per integration, one file per workflow):
```
workflows/<Integration>/<NNNN_Name_Trigger>.json
```
Example: `workflows/Telegram/0001_Telegram_Schedule_Automation_Scheduled.json`.

**Raw JSON access pattern:**
```
https://raw.githubusercontent.com/Zie619/n8n-workflows/main/workflows/<Integration>/<file>.json
```
There is no flat `workflows/<id>.json` — that URL answers 404. Find the file name first: list the integration folder through the GitHub API (`https://api.github.com/repos/Zie619/n8n-workflows/contents/workflows/<Integration>`).

**Search strategy:**
1. Use `~~search` with query: `site:github.com/Zie619/n8n-workflows {keyword}`
2. Or scrape `https://zie619.github.io/n8n-workflows` and search the index page
3. The numeric file prefix is the repo's own counter. A match with an n8n.io template ID is **not** confirmed — do not assume one

**Quality notes:**
- Mixed quality — includes raw scrapes and curated submissions
- Always validate JSON schema before import
- Some workflows reference deprecated node types (pre-n8n 1.0) or nodes removed in n8n 2.0 and 3.0
- Check `nodes[].typeVersion` to detect outdated node versions

---

## enescingoz/awesome-n8n-templates

Curated collection organized by integration or use-case folders.

**Directory structure** (examples; the list of folders changes):
```
AI_Research_RAG_and_Data_Analysis/
Gmail_and_Email_Automation/
Google_Drive_and_Google_Sheets/
OpenAI_and_LLMs/
Database_and_Storage/
Forms_and_Surveys/
Notion/
Slack/
...
```

**Raw JSON access pattern** (file names contain spaces — URL-encode them):
```
https://raw.githubusercontent.com/enescingoz/awesome-n8n-templates/main/{Folder}/{filename}.json
```

**Search strategy:**
1. Browse folders matching the user's target integration
2. File names are descriptive
3. Use `~~search` with query: `site:github.com/enescingoz/awesome-n8n-templates {keyword}`

**Quality notes:**
- Fewer workflows than the bulk collections, with a README per folder
- Good starting point before checking larger repos
- No license is declared — mention it to the user

---

## ritik-prog/n8n-automation-templates-5000

Large bulk collection.

**Directory structure** (top level):
```
Templates based on paltforms/     (sic)
n8n_2000_workflows/
n8n advance/
workflows by Zie619/
```
Each folder holds `*.json` workflow files. Folder and file names contain spaces — URL-encode them.

**Raw JSON access pattern:**
```
https://raw.githubusercontent.com/ritik-prog/n8n-automation-templates-5000/main/{folder}/{filename}.json
```

**Search strategy:**
1. List the folder through the GitHub API, or browse it on github.com
2. File names are descriptive
3. Use `~~search` for specific keywords within the repo

**Quality notes:**
- MIT licensed
- Large volume but variable quality; `workflows by Zie619/` duplicates another repo in this list
- Some workflows may use older n8n node versions
- Always validate before importing

---

## zengfr/n8n-workflow-all-templates

Mirror of the official library, synchronized roughly monthly (12,333 files).

**Directory structure:**
```
n8n-workflow-all-templates/00/00/00/{id}_{Title}.json
index_files_1.md, index_files_2.md, ...   (searchable index of all files)
```

**Raw JSON access pattern:** take the path from an index file or from GitHub, then
```
https://raw.githubusercontent.com/zengfr/n8n-workflow-all-templates/main/{path}/{id}_{Title}.json
```
Files are not at the repo root — a root-level URL answers 404.

**Search strategy:**
1. Search the `index_files_N.md` pages for the keyword (they list ID and title), or use `~~search` with `site:github.com/zengfr/n8n-workflow-all-templates {keyword}`
2. The file name starts with the n8n.io template ID, so a hit can also be fetched from `api.n8n.io` — prefer that when the API is reachable
3. Monthly sync means it may lag 1-4 weeks behind the live library

**Quality notes:**
- Mirrors official library quality — generally high
- Auto-generated, so no curation beyond what n8n.io provides
- Useful as a backup data source when the API is down; Apache-2.0

---

## EtienneLescot/n8n-as-code

Workflows in TypeScript SDK format rather than raw JSON, plus tooling that gives an AI agent node schemas.

**Format:** TypeScript files using the n8n SDK
```typescript
// Example: not directly importable as JSON
import { Workflow } from 'n8n-workflow';
// ...
```

**Conversion required:** These are NOT raw JSON workflow files. To import:
1. Extract the workflow definition from the TypeScript code
2. Convert to n8n JSON format
3. Or use them as reference for building workflows via `n8n-native-mcp` (`create_workflow_from_code` takes TypeScript SDK code)

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

## Danitilahun/n8n-workflow-templates (stale)

A collection with a Python search backend. **The last push was in 2025-07**, which is past this plugin's "over 1 year" threshold: treat it as Caution, prefer the repos above, and use it only when nothing else has a match. It carries no license.

**Directory structure:** `workflows/<NNNN_Name>.json` (numeric prefix, like the Zie619 collection).

**Raw JSON access pattern:**
```
https://raw.githubusercontent.com/Danitilahun/n8n-workflow-templates/main/workflows/<file>.json
```
List `workflows/` through the GitHub API to find file names.

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
3. Check node types — look for deprecated types and nodes n8n removed (see workflow-analysis, Step 6)
4. Check typeVersion — flag outdated versions
5. Build the payload (name, nodes, connections, settings; strip node credentials)
6. Use ~~workflow_validate (validate_workflow) on the payload
7. Then import via ~~workflow_create
```
