---
name: backlink-audit
description: This skill should be used when the user asks about "backlink audit", "backlink analysis", "link profile", "toxic links", "referring domains", "link building", "backlink prospecting", "disavow list", "spam score", or needs to analyze backlink profiles using DataForSEO.
---

# Backlink Audit Workflows

Chained workflows for auditing, analyzing, and prospecting backlinks using DataForSEO MCP tools. All tool references use the `mcp__dataforseo__` prefix.

## Workflow 1: Full Profile Audit

Comprehensive audit of a domain's entire backlink profile.

### Step 1 — Get Summary Metrics

Call `backlinks_summary` to retrieve the high-level profile: total backlinks, referring domains, dofollow/nofollow ratio, domain rank, and broken backlinks count.

```
Tool: backlinks_summary
Params:
  target: "example.com"
```

### Step 2 — Pull Individual Backlinks

Call `backlinks_backlinks` with `mode: "one_per_domain"` to get one representative backlink per referring domain. Set `limit` to 100-200 for the initial review. This avoids thousands of links from a single domain flooding the results.

```
Tool: backlinks_backlinks
Params:
  target: "example.com"
  mode: "one_per_domain"
  limit: 100
  order_by: ["rank,desc"]
```

### Step 3 — Analyze Referring Domains

Call `backlinks_referring_domains` to get a domain-level view of who links to you, including each referring domain's rank, backlink count, and first/last seen dates.

```
Tool: backlinks_referring_domains
Params:
  target: "example.com"
  limit: 200
  order_by: ["rank,desc"]
```

### Step 4 — Review Anchor Text Distribution

Call `backlinks_anchors` to see the anchor text distribution. Look for over-optimized anchors (exact-match commercial terms exceeding 5-10% of total), suspicious patterns (foreign-language anchors you did not build), and branded vs. generic ratio.

```
Tool: backlinks_anchors
Params:
  target: "example.com"
  limit: 200
  order_by: ["backlinks,desc"]
```

Combine all four results into a profile summary: total links, domain diversity, dofollow ratio, anchor distribution health, and top linking domains.

## Workflow 2: Spam Detection

Identify toxic and spammy backlinks that could trigger penalties.

### Step 1 — Bulk Spam Score Check

Call `backlinks_bulk_spam_score` with your domain (and optionally competitor domains for comparison). This returns a spam score for each target.

```
Tool: backlinks_bulk_spam_score
Params:
  targets: ["example.com", "competitor1.com", "competitor2.com"]
```

### Step 2 — Review Suspicious Anchors

Call `backlinks_anchors` and flag anchors that match known spam patterns: gambling terms, pharma keywords, foreign-language text unrelated to your niche, or exact-match commercial phrases in high volume.

### Step 3 — Inspect Low-Rank Referring Domains

Call `backlinks_referring_domains` with `order_by: ["rank,asc"]` to surface the lowest-authority domains linking to you. Domains with rank 0-5 and high backlink counts are often spam networks.

```
Tool: backlinks_referring_domains
Params:
  target: "example.com"
  limit: 100
  order_by: ["rank,asc"]
```

### Step 4 — Build a Disavow List

From the results, compile domains that meet two or more spam indicators:
- Spam score above 50
- Rank below 10 with generic/spammy anchor text
- Anchor text in a language or topic unrelated to your site
- Hundreds of outbound links (link farm behavior)

Format the disavow list as `domain:spamsite.com` entries, one per line.

## Workflow 3: Link Building Prospecting

Find new link building opportunities by analyzing competitor backlink profiles.

### Step 1 — Find Backlink Competitors

Call `backlinks_competitors` with your domain to discover domains that have similar backlink profiles (they share many of the same referring domains).

```
Tool: backlinks_competitors
Params:
  target: "example.com"
```

### Step 2 — Compare Referring Domains

Call `backlinks_referring_domains` on your top 2-3 competitors. Cross-reference with your own referring domains list from Workflow 1.

### Step 3 — Identify Gap Domains

Use `backlinks_domain_intersection` to find referring domains that link to competitors but not to you. These are your prospecting targets.

```
Tool: backlinks_domain_intersection
Params:
  targets:
    1: "competitor1.com"
    2: "competitor2.com"
  exclude_targets: ["example.com"]
  limit: 200
```

### Step 4 — Qualify Prospects

Filter gap domains by rank > 30 (decent authority) and check their backlink counts. High-rank domains that link to multiple competitors in your niche are the highest-priority outreach targets.

## Workflow 4: Historical Trends and Link Velocity

Track how a backlink profile changes over time.

### Step 1 — Get Timeseries Summary

Call `backlinks_timeseries_summary` to see historical backlink and referring domain counts over time. Identify growth spikes, drops, or plateaus.

```
Tool: backlinks_timeseries_summary
Params:
  target: "example.com"
  date_from: "2025-01-01"
```

### Step 2 — Check New and Lost Timeseries

Call `backlinks_timeseries_new_lost_summary` to see the rate of new vs. lost backlinks over time. A healthy profile gains more links than it loses. Sudden spikes in new links may indicate a spam attack; sudden drops may indicate link removals or site issues.

### Step 3 — Get Recent Changes in Bulk

Call `backlinks_bulk_new_lost_backlinks` to see the most recent new and lost backlinks across one or multiple domains.

```
Tool: backlinks_bulk_new_lost_backlinks
Params:
  targets: ["example.com"]
```

### Step 4 — Monitor Referring Domain Changes

Call `backlinks_bulk_new_lost_referring_domains` to track which referring domains were recently gained or lost.

```
Tool: backlinks_bulk_new_lost_referring_domains
Params:
  targets: ["example.com"]
```

Compare link velocity against competitors to gauge whether your link building efforts are keeping pace.

## Interpreting Backlink Metrics

| Metric | Description | Healthy Range |
|--------|-------------|---------------|
| `rank` | Domain authority equivalent (0-1000) | >30 for meaningful authority |
| `backlinks` | Total backlink count | Context-dependent; quality > quantity |
| `referring_domains` | Unique domains linking to you | Higher diversity = healthier profile |
| `dofollow` | Count of dofollow links | 60-80% of total is typical |
| `nofollow` | Count of nofollow links | 20-40% is natural |
| `referring_domains_nofollow` | Domains with only nofollow links | Should not dominate |
| `broken_backlinks` | Links pointing to 404/error pages | Reclaim these via redirects |
| `anchor` | Anchor text used in the link | Branded anchors should dominate |
| `spam_score` | 0-100 likelihood of spam | <30 safe, 30-60 review, >60 toxic |

## Target Format

Pass domains without protocol or www prefix. Pass pages with full URL.

| Target Type | Format | Example |
|-------------|--------|---------|
| Domain | bare domain | `example.com` |
| Subdomain | include subdomain | `blog.example.com` |
| Page | full URL with protocol | `https://example.com/blog/guide` |
| Path | protocol + path | `https://example.com/blog/` |

## Bulk Operations

Use bulk endpoints for efficiency when analyzing multiple targets at once:

| Tool | Max Targets | Returns |
|------|-------------|---------|
| `backlinks_bulk_backlinks` | 1000 | Backlink counts per target |
| `backlinks_bulk_ranks` | 1000 | Domain rank per target |
| `backlinks_bulk_referring_domains` | 1000 | Referring domain counts per target |
| `backlinks_bulk_spam_score` | 1000 | Spam scores per target |
| `backlinks_bulk_new_lost_backlinks` | 1000 | Recent new/lost links per target |
| `backlinks_bulk_new_lost_referring_domains` | 1000 | Recent new/lost referring domains |
| `backlinks_bulk_pages_summary` | 1000 | Page-level backlink summary |

Always prefer bulk endpoints when analyzing 3+ targets. They return results for all targets in a single API call.

<example>
User: "Audit the backlink profile of example.com and find toxic links"

Workflow:
1. Call backlinks_summary for "example.com" — get total backlinks, referring domains, dofollow ratio, broken links
2. Call backlinks_bulk_spam_score with targets ["example.com"] — check overall spam score
3. Call backlinks_referring_domains for "example.com", order_by ["rank,asc"], limit 100 — surface lowest-authority linkers
4. Call backlinks_anchors for "example.com", limit 200 — review anchor text distribution
5. Flag domains with rank < 10 and spammy anchor text patterns
6. Present: profile summary (healthy metrics vs. concerns), anchor distribution chart, list of suspected toxic domains with evidence, draft disavow list
</example>

<example>
User: "Find link building opportunities by looking at competitor backlinks"

Workflow:
1. Call backlinks_summary for "yourdomain.com" — baseline metrics
2. Call backlinks_competitors for "yourdomain.com" — discover backlink competitors
3. Call backlinks_domain_intersection with targets {"1": "competitor1.com", "2": "competitor2.com"}, exclude_targets ["yourdomain.com"], limit 200
4. Filter gap domains: rank > 30, not in your existing referring domains
5. Call backlinks_bulk_ranks with the top 50 gap domains to confirm authority
6. Present: list of prospect domains sorted by rank, number of competitors they link to, suggested outreach priority, and estimated difficulty (higher rank = more valuable but harder to earn)
</example>
