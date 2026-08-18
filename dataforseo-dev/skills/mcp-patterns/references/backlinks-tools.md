# Backlinks Tools

19 tools for link profile analysis, competitor backlink research, and spam detection. All prefixed with `mcp__dataforseo__backlinks_`.

## Tool Reference

### Core Analysis

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `summary` | Get backlink profile overview for a domain | `target` (required), `include_subdomains`, `exclude_internal_backlinks` |
| `backlinks` | List individual backlinks pointing to a target | `target`, `limit`, `offset`, `filters`, `order_by`, `mode` (as_is/one_per_domain/one_per_anchor) |
| `anchors` | Get anchor text distribution | `target`, `limit`, `offset`, `filters`, `order_by` |
| `referring_domains` | List domains linking to target | `target`, `limit`, `offset`, `filters`, `order_by` |
| `referring_networks` | List referring IP networks | `target`, `limit`, `offset`, `filters`, `order_by` |
| `domain_pages` | List pages on target domain with backlink data | `target`, `limit`, `offset`, `filters`, `order_by` |
| `domain_pages_summary` | Summary of pages with backlink metrics | `target`, `limit`, `offset`, `filters` |

### Competitor Analysis

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `competitors` | Find domains competing for similar backlinks | `target`, `limit`, `offset`, `filters`, `order_by` |
| `domain_intersection` | Find referring domains shared between targets | `targets` (array of domains), `limit`, `offset`, `filters` |
| `page_intersection` | Find referring domains shared between pages | `pages` (array of URLs), `limit`, `offset`, `filters` |

### Bulk Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `bulk_backlinks` | Get backlink counts for up to 1000 targets | `targets` (array, up to 1000) |
| `bulk_ranks` | Get domain/page rank for multiple targets | `targets` (array) |
| `bulk_referring_domains` | Get referring domain counts in bulk | `targets` (array) |
| `bulk_new_lost_backlinks` | Get new/lost backlink counts | `targets` (array), `date_from` |
| `bulk_new_lost_referring_domains` | Get new/lost referring domain counts | `targets` (array), `date_from` |
| `bulk_pages_summary` | Get page-level metrics in bulk | `targets` (array) |
| `bulk_spam_score` | Get spam scores for multiple targets | `targets` (array) |

### Timeseries

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `timeseries_summary` | Historical backlink count over time | `target`, `date_from`, `date_to` |
| `timeseries_new_lost_summary` | Historical new/lost backlinks over time | `target`, `date_from`, `date_to` |

## Parameter Details

- `target` -- domain or URL to analyze. Example: `"example.com"` or `"example.com/page"`.
- `targets` -- array of domains/URLs for bulk or intersection tools.
- `mode` -- controls deduplication for `backlinks` tool:
  - `"as_is"` -- return all backlinks
  - `"one_per_domain"` -- one backlink per referring domain
  - `"one_per_anchor"` -- one backlink per unique anchor text
- `include_subdomains` -- boolean. Include links to subdomains of the target.
- `exclude_internal_backlinks` -- boolean. Exclude links from the target domain itself.
- `date_from`, `date_to` -- ISO date strings (e.g., `"2025-01-01"`). Used for timeseries and new/lost tools.
- `filters` -- array syntax: `[["rank", ">", 50]]`. Combine with `"and"` / `"or"`.
- `order_by` -- array: `["rank,desc"]`.

## Usage Examples

### Full backlink audit for a domain

```
Step 1 -- Tool: mcp__dataforseo__backlinks_summary
Params:
  target: "example.com"
  include_subdomains: true

Step 2 -- Tool: mcp__dataforseo__backlinks_referring_domains
Params:
  target: "example.com"
  limit: 100
  order_by: ["rank,desc"]
```

### Find shared link sources between competitors

```
Tool: mcp__dataforseo__backlinks_domain_intersection
Params:
  targets: ["mysite.com", "competitor1.com", "competitor2.com"]
  limit: 50
  filters: [["rank", ">", 30]]
```

Returns referring domains that link to multiple targets -- ideal for link building outreach.

## Tips

- Start with `summary` to get the big picture before diving into individual backlinks.
- Use `bulk_spam_score` to quickly identify potentially toxic link sources.
- `one_per_domain` mode in `backlinks` gives a cleaner view of unique referring sites.
- Bulk tools are the most cost-effective way to compare multiple domains at once.
- Use `timeseries_summary` to detect sudden link gains or drops (possible negative SEO or penalties).
