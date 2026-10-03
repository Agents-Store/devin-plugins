---
name: backlink-audit
description: This skill should be used when the user asks about "backlink audit", "backlink analysis", "link profile", "toxic links", "referring domains", "link building", "backlink prospecting", "disavow list", "spam score", or needs to analyze backlink profiles using DataForSEO.
---

# Backlink Audit Workflows

Chained workflows for auditing, analyzing and prospecting backlinks with DataForSEO. Every block below is one `api_request` call: the first line is the `method` and `path`, the second is `data`. Before the first call to a path, read its page with `docs_search` and agree a budget (`cost-awareness` skill). Paths and minimal bodies for the whole API are in `../mcp-patterns/references/endpoint-paths.md`.

## Workflow 1: Full Profile Audit

Comprehensive audit of a domain's entire backlink profile.

### Step 1 — Get Summary Metrics

The summary gives the high-level profile: total backlinks, referring domains, dofollow and nofollow counts, rank, and broken backlinks.

```
POST /v3/backlinks/summary/live
data: [{"target": "example.com"}]
```

### Step 2 — Pull Individual Backlinks

Use `mode: "one_per_domain"` to get one representative backlink per referring domain, so thousands of links from one domain do not flood the result. Start with a `limit` of 100 to 200.

```
POST /v3/backlinks/backlinks/live
data: [{"target": "example.com", "mode": "one_per_domain", "limit": 100, "order_by": ["rank,desc"]}]
```

### Step 3 — Analyze Referring Domains

A domain-level view of who links to you, with each referring domain's rank, backlink count and first and last seen dates.

```
POST /v3/backlinks/referring_domains/live
data: [{"target": "example.com", "limit": 200, "order_by": ["rank,desc"]}]
```

### Step 4 — Review Anchor Text Distribution

Look for over-optimized anchors (exact-match commercial terms above 5 to 10 percent of the total), suspicious patterns (foreign-language anchors you did not build), and the ratio of branded to generic anchors.

```
POST /v3/backlinks/anchors/live
data: [{"target": "example.com", "limit": 200, "order_by": ["backlinks,desc"]}]
```

Combine the four results into a profile summary: total links, domain diversity, dofollow ratio, anchor health and the top linking domains.

## Workflow 2: Spam Detection

Identify toxic and spammy backlinks that could trigger penalties.

### Step 1 — Bulk Spam Score Check

Send your domain, and optionally competitors for comparison. One call takes up to 1000 targets.

```
POST /v3/backlinks/bulk_spam_score/live
data: [{"targets": ["example.com", "competitor1.com", "competitor2.com"]}]
```

### Step 2 — Review Suspicious Anchors

Run the anchors call from Workflow 1 and flag anchors that match known spam patterns: gambling terms, pharma keywords, foreign-language text unrelated to your niche, or exact-match commercial phrases in high volume.

### Step 3 — Inspect Low-Rank Referring Domains

Sort referring domains by ascending rank to surface the lowest-authority linkers. Domains with rank 0 to 5 and high backlink counts are often spam networks.

```
POST /v3/backlinks/referring_domains/live
data: [{"target": "example.com", "limit": 100, "order_by": ["rank,asc"]}]
```

### Step 4 — Build a Disavow List

Compile the domains that meet two or more spam indicators:
- Spam score above 50
- Rank below 10 with generic or spammy anchor text
- Anchor text in a language or topic unrelated to your site
- Hundreds of outbound links (link farm behavior)

Format the disavow list as `domain:spamsite.com` entries, one per line.

## Workflow 3: Link Building Prospecting

Find new link opportunities by analyzing competitor backlink profiles.

### Step 1 — Find Backlink Competitors

Domains with a similar backlink profile (they share many of your referring domains).

```
POST /v3/backlinks/competitors/live
data: [{"target": "example.com", "limit": 20}]
```

### Step 2 — Compare Referring Domains

Run the referring domains call on your top 2 or 3 competitors and cross-reference with your own list from Workflow 1.

### Step 3 — Identify Gap Domains

Domain intersection finds referring domains that link to the competitors and not to you. `targets` is an object keyed "1", "2", and so on; `exclude_targets` removes domains that already link to you.

```
POST /v3/backlinks/domain_intersection/live
data: [{"targets": {"1": "competitor1.com", "2": "competitor2.com"},
        "exclude_targets": ["example.com"], "limit": 200}]
```

### Step 4 — Qualify Prospects

Keep gap domains with rank above 30 and check their backlink counts. High-rank domains that link to several competitors in your niche are the highest-priority outreach targets.

## Workflow 4: Historical Trends and Link Velocity

Track how a backlink profile changes over time.

### Step 1 — Get Timeseries Summary

Historical backlink and referring domain counts. Identify growth spikes, drops and plateaus.

```
POST /v3/backlinks/timeseries_summary/live
data: [{"target": "example.com", "date_from": "2025-01-01"}]
```

### Step 2 — Check New and Lost Timeseries

The rate of new against lost backlinks. A healthy profile gains more than it loses. A sudden spike of new links may be a spam attack; a sudden drop may mean link removals or site issues.

```
POST /v3/backlinks/timeseries_new_lost_summary/live
data: [{"target": "example.com", "date_from": "2025-01-01"}]
```

### Step 3 — Get Recent Changes in Bulk

The most recent new and lost backlinks across one or many domains. `date_from` is the threshold: links first seen after it are new, links seen before it and not since are lost.

```
POST /v3/backlinks/bulk_new_lost_backlinks/live
data: [{"targets": ["example.com"], "date_from": "2026-09-01"}]
```

### Step 4 — Monitor Referring Domain Changes

Which referring domains were gained or lost.

```
POST /v3/backlinks/bulk_new_lost_referring_domains/live
data: [{"targets": ["example.com"], "date_from": "2026-09-01"}]
```

Compare link velocity with competitors to judge whether your link building keeps pace.

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

Pass domains without protocol or `www.`. Pass pages as absolute URLs.

| Target Type | Format | Example |
|-------------|--------|---------|
| Domain | bare domain | `example.com` |
| Subdomain | include subdomain | `blog.example.com` |
| Page | full URL with protocol | `https://example.com/blog/guide` |
| Path | protocol + path | `https://example.com/blog/` |

## Bulk Operations

Bulk endpoints answer for many targets in one call. Prefer them when analyzing 3 or more targets.

| Path under `/v3/backlinks/` | Max targets | Returns |
|-------------|-------------|---------|
| `bulk_backlinks/live` | 1000 | Backlink counts per target |
| `bulk_ranks/live` | 1000 | Rank per target |
| `bulk_referring_domains/live` | 1000 | Referring domain counts per target |
| `bulk_spam_score/live` | 1000 | Spam scores per target |
| `bulk_new_lost_backlinks/live` | 1000 | Recent new and lost links per target |
| `bulk_new_lost_referring_domains/live` | 1000 | Recent new and lost referring domains |
| `bulk_pages_summary/live` | 1000 | Page-level backlink summary |

<example>
User: "Audit the backlink profile of example.com and find toxic links"

Workflow:
1. docs_search for the four paths below; show the plan (4 calls, limits 100 to 200); get the user's budget
2. api_request POST /v3/backlinks/summary/live for "example.com" — totals, referring domains, dofollow ratio, broken links
3. POST /v3/backlinks/bulk_spam_score/live with targets ["example.com"] — overall spam score
4. POST /v3/backlinks/referring_domains/live with order_by ["rank,asc"], limit 100 — the lowest-authority linkers
5. POST /v3/backlinks/anchors/live with limit 200 — anchor text distribution
6. Flag domains with rank < 10 and spammy anchor patterns
7. Present: profile summary (healthy metrics against concerns), anchor distribution, suspected toxic domains with evidence, draft disavow list
</example>

<example>
User: "Find link building opportunities by looking at competitor backlinks"

Workflow:
1. docs_search for the paths below; get the user's budget
2. api_request POST /v3/backlinks/summary/live for "yourdomain.com" — baseline
3. POST /v3/backlinks/competitors/live for "yourdomain.com" — backlink competitors
4. POST /v3/backlinks/domain_intersection/live with targets {"1": "competitor1.com", "2": "competitor2.com"}, exclude_targets ["yourdomain.com"], limit 200
5. Keep gap domains with rank > 30
6. POST /v3/backlinks/bulk_ranks/live with the top 50 gap domains to confirm authority
7. Present: prospect domains sorted by rank, how many competitors each links to, suggested outreach priority and estimated difficulty (higher rank is more valuable and harder to earn)
</example>
