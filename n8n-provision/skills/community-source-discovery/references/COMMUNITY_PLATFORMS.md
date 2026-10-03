# Community Platforms for n8n Workflows

Third-party websites and marketplaces hosting n8n workflow templates beyond the official library. Use these when the official library and GitHub repos lack a suitable match.

Counts and availability below were checked on 2026-09-30 and 2026-10-03 and change often — treat them as orientation, not as facts to quote.

## Platform Catalog

| Platform | URL | Workflows | API? | Type | Status |
|----------|-----|-----------|------|------|--------|
| n8nworkflows.xyz | n8nworkflows.xyz | ~11,660 | No public API | Aggregator | Live |
| n8nflow.net | n8nflow.net | ~7,020 | Unknown | Community curated | Live, redirects to `www.n8nflow.net` |
| n8nfind.net | n8nfind.net | Unknown (was ~9,050) | Unknown | Mirror/aggregator | Live, but behind a Cloudflare challenge (HTTP 403): `~~scrape` will not get through |
| n8nbasket.com | n8nbasket.com | Paid marketplace | No | Buy/sell premium | Live |

Removed from earlier versions of this list: **n8nbazar** (its `.ai` domain no longer resolves) and **FlowEngine.cloud** (now an n8n hosting platform, not a workflow library). Do not search either.

---

## n8nworkflows.xyz

The largest independent n8n workflow aggregator.

**Stats:** ~11,660 workflows (free and paid; the split is not published)
**GitHub mirror:** `nusquama/n8nworkflows.xyz` (~2,500 stars)

**Access patterns:**
1. **Web search:** Use `~~search` with `site:n8nworkflows.xyz {keyword}` to find specific workflows
2. **Scrape workflow page:** Use `~~scrape` on individual workflow URLs to extract the JSON (the site may answer a plain HTTP client with 403 — try the other scrape provider)
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

## n8nflow.net

Community-curated workflow collection.

**Stats:** ~7,020 workflows. The bare domain redirects to `www.n8nflow.net`.

**Access patterns:**
1. **Web search:** `~~search` with `site:n8nflow.net {keyword}`
2. **Browse categories:** The site organizes workflows by integration and use case
3. **Scrape:** `~~scrape` on individual workflow pages for JSON extraction (use the `www` address)

**Quality notes:**
- Community curation adds a quality filter
- Smaller than the aggregators but potentially better signal-to-noise ratio
- Check for workflow descriptions and ratings when available

---

## n8nfind.net

Large mirror/aggregator of the official n8n template library.

**Stats:** Unknown (about 9,050 when last counted)

**Access patterns:**
1. **Web search:** `~~search` with `site:n8nfind.net {keyword}` — search engines can still list it
2. **Scrape:** the site answers automated clients with a Cloudflare challenge (HTTP 403). Try a browser-capable scrape provider; if every provider fails, take the template number from the search result and fetch that template from `api.n8n.io`
3. May provide direct links to the official n8n template ID — check if the workflow page references an n8n.io template number

**Quality notes:**
- Mirrors official library content, so quality matches the source
- Not worth the effort now that `api.n8n.io` serves the whole library directly

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
- Not suitable for automated scraping; any purchase is the user's decision

---

## Search Strategy Across Platforms

### Priority order for community search

1. **n8nworkflows.xyz** — largest collection, best first stop
2. **n8nflow.net** — community curated, good quality filter
3. **n8nfind.net** — search only; scraping is blocked
4. **n8nbasket.com** — last resort for premium content

### Constructing search queries

For each platform, use `~~search` with site-specific targeting:

```
# Search across the community platforms
~~search("n8n workflow {keyword} site:n8nworkflows.xyz OR site:n8nflow.net OR site:n8nfind.net")

# Target a specific platform
~~search("site:n8nworkflows.xyz {keyword} n8n workflow")
```

### Extracting workflow JSON

After finding a workflow on any platform:

1. **Scrape the page:** `~~scrape({workflow_url})`
2. **Look for JSON:** Search the scraped content for n8n workflow JSON (contains `"nodes"` and `"connections"`)
3. **Parse and validate:** Extract the JSON, parse it, build the payload (name, nodes, connections, settings; strip node credentials), validate with `~~workflow_validate`
4. **Check for official template ID:** If the workflow references an n8n.io template number, fetch it through the `template-discovery` provider chain (n8n-mcp, then `api.n8n.io`) instead — the library copy is the original
5. **Import:** Use `~~workflow_create` to import the validated payload (the workflow arrives as an unpublished draft)

### Handling extraction failures

- Some platforms use JavaScript rendering — `~~scrape` may not capture dynamic content
- Try alternative scrape providers if the first fails (follow CONNECTORS.md fallback pattern)
- Check if the platform has a GitHub repo with the raw workflow files
- As a last resort, manually construct the workflow based on the description and node list
