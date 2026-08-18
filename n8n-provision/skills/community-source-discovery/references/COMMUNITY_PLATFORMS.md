# Community Platforms for n8n Workflows

Third-party websites and marketplaces hosting n8n workflow templates beyond the official library. Use these when the official library and GitHub repos lack a suitable match.

## Platform Catalog

| Platform | URL | Workflows | API? | Type |
|----------|-----|-----------|------|------|
| n8nworkflows.xyz | n8nworkflows.xyz | ~9,320 (8,173 free / 1,147 paid) | No public API | Aggregator |
| n8nfind.net | n8nfind.net | ~9,050 | Unknown | Mirror/aggregator |
| n8nflow.net | n8nflow.net | ~6,071 | Unknown | Community curated |
| n8nbazar.ai | n8nbazar.ai | Unknown | AI-powered search | AI-enhanced marketplace |
| FlowEngine.cloud | flowengine.cloud | ~296 | No | AI-focused niche |
| n8nbasket.com | n8nbasket.com | Paid marketplace | No | Buy/sell premium |

---

## n8nworkflows.xyz

The largest independent n8n workflow aggregator.

**Stats:** ~9,320 workflows (8,173 free, 1,147 paid)
**GitHub mirror:** `nusquama/n8nworkflows.xyz` (~2,257 stars)

**Access patterns:**
1. **Web search:** Use `~~search` with `site:n8nworkflows.xyz {keyword}` to find specific workflows
2. **Scrape workflow page:** Use `~~scrape` on individual workflow URLs to extract the JSON
3. **GitHub repo:** The backing GitHub repo may contain workflow data in a structured format — check for JSON files or a database dump

**Extracting workflow JSON:**
- Individual workflow pages typically include a "Copy JSON" button or display the workflow definition
- Scrape the page and look for the n8n workflow JSON in the page content
- The JSON is usually embedded in a `<code>` block or downloadable as a file

**Quality notes:**
- Mix of community-contributed and scraped workflows
- Free workflows are generally usable; paid ones require account
- Large collection means noise — filter results carefully
- Some workflows may be outdated or reference deprecated nodes

---

## n8nfind.net

Large mirror/aggregator of the official n8n template library.

**Stats:** ~9,050 workflows

**Access patterns:**
1. **Web search:** `~~search` with `site:n8nfind.net {keyword}`
2. **Scrape:** `~~scrape` on workflow detail pages
3. May provide direct links to the official n8n template ID — check if the workflow page references an n8n.io template number

**Quality notes:**
- Mirrors official library content, so quality matches the source
- May include additional community submissions
- Useful when the official API is rate-limited or down
- Check if the workflow maps back to an official template ID for easier deployment via `~~template_deploy`

---

## n8nflow.net

Community-curated workflow collection.

**Stats:** ~6,071 workflows

**Access patterns:**
1. **Web search:** `~~search` with `site:n8nflow.net {keyword}`
2. **Browse categories:** The site organizes workflows by integration and use case
3. **Scrape:** `~~scrape` on individual workflow pages for JSON extraction

**Quality notes:**
- Community curation adds a quality filter
- Smaller than the aggregators but potentially better signal-to-noise ratio
- Check for workflow descriptions and ratings when available

---

## n8nbazar.ai

AI-powered workflow search platform.

**Stats:** Unknown total, growing collection

**Access patterns:**
1. **Natural language search:** The platform supports AI-powered queries — describe what you want in plain language
2. **Web search:** `~~search` with `site:n8nbazar.ai {keyword}`
3. **Scrape:** `~~scrape` on result pages

**Best for:**
- Complex, multi-step workflow searches where keyword matching fails
- Finding workflows by describing the desired outcome rather than specific tools
- The AI search may surface relevant workflows that keyword search misses

**Quality notes:**
- AI-enhanced search can find semantically relevant matches
- Collection size is unknown — may not have niche workflows
- Worth trying when other platforms return poor results

---

## FlowEngine.cloud

Niche platform focused on AI and automation workflows.

**Stats:** ~296 workflows

**Access patterns:**
1. **Browse:** Small enough to browse manually by category
2. **Copy-paste JSON:** Workflows typically provide copy-paste JSON directly on the page
3. **Scrape:** `~~scrape` on workflow pages for JSON extraction

**Best for:**
- AI-specific workflows (OpenAI, Claude, vector databases, RAG pipelines)
- Workflows combining n8n with AI services
- Curated quality over quantity

**Quality notes:**
- Small but focused collection
- Higher quality per workflow due to manual curation
- AI-focused workflows tend to use current node versions
- Good for finding LLM integration patterns

---

## n8nbasket.com

Premium workflow marketplace — buy and sell n8n workflows.

**Stats:** Paid marketplace, variable inventory

**Access patterns:**
1. **Browse:** Check marketplace listings for professional-grade workflows
2. **No scraping:** Paid content is behind authentication
3. Premium workflows typically include documentation and support

**Best for:**
- Production-ready, professionally built workflows
- Complex automations that would take significant time to build from scratch
- Workflows with documentation, support, and maintenance

**Quality notes:**
- Paid content is generally higher quality
- Includes professional documentation
- May offer support and updates
- Not suitable for automated scraping

---

## Search Strategy Across Platforms

### Priority order for community search

1. **n8nworkflows.xyz** — largest free collection, best first stop
2. **n8nfind.net** — large mirror, may have different indexing
3. **n8nflow.net** — community curated, good quality filter
4. **n8nbazar.ai** — try AI search for complex queries
5. **FlowEngine.cloud** — check for AI-specific workflows
6. **n8nbasket.com** — last resort for premium content

### Constructing search queries

For each platform, use `~~search` with site-specific targeting:

```
# Search across all community platforms
~~search("n8n workflow {keyword} site:n8nworkflows.xyz OR site:n8nfind.net OR site:n8nflow.net")

# Target a specific platform
~~search("site:n8nworkflows.xyz {keyword} n8n workflow")

# AI-powered search
~~search("site:n8nbazar.ai {description of desired workflow}")
```

### Extracting workflow JSON

After finding a workflow on any platform:

1. **Scrape the page:** `~~scrape({workflow_url})`
2. **Look for JSON:** Search the scraped content for n8n workflow JSON (contains `"nodes"` and `"connections"`)
3. **Parse and validate:** Extract the JSON, parse it, validate with `~~workflow_validate`
4. **Check for official template ID:** If the workflow references an n8n.io template number, use `~~template_deploy` instead for cleaner import
5. **Import:** Use `~~workflow_create` to import the validated JSON

### Handling extraction failures

- Some platforms use JavaScript rendering — `~~scrape` may not capture dynamic content
- Try alternative scrape providers if the first fails (follow CONNECTORS.md fallback pattern)
- Check if the platform has a GitHub repo with the raw workflow files
- As a last resort, manually construct the workflow based on the description and node list
