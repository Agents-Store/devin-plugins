# Scenario: Backlink Prospecting

Find high-quality link building opportunities by analyzing competitor backlink profiles. Each step is one `api_request` call with the method, path and `data` shown. Read each path's page with `docs_search` and agree a budget first.

## Step 1: Audit Your Current Backlink Profile

```
POST /v3/backlinks/summary/live
data: [{"target": "example.com", "include_subdomains": true, "exclude_internal_backlinks": true}]
```

Record the baseline: total backlinks, referring domains, rank, broken backlinks.

## Step 2: Identify Competitor Backlink Profiles

```
POST /v3/backlinks/bulk_ranks/live
data: [{"targets": ["example.com", "competitor1.com", "competitor2.com", "competitor3.com"]}]
```

Compare the rank scores. The gap between your rank and the competitors' indicates link building potential.

## Step 3: Find Link Sources Unique to Competitors

Get the competitor's referring domains:

```
POST /v3/backlinks/referring_domains/live
data: [{"target": "competitor1.com", "limit": 100, "order_by": ["rank,desc"],
        "filters": [["dofollow", "=", true]]}]
```

These domains link to your competitor and possibly not to you: outreach targets. To get only the ones that do not link to you, use the link-gap endpoint instead:

```
POST /v3/backlinks/domain_intersection/live
data: [{"targets": {"1": "competitor1.com", "2": "competitor2.com"},
        "exclude_targets": ["example.com"], "limit": 100}]
```

## Step 4: Check Spam Scores

Before pursuing outreach, verify domain quality (up to 1000 targets per call):

```
POST /v3/backlinks/bulk_spam_score/live
data: [{"targets": ["potential-link-source1.com", "potential-link-source2.com"]}]
```

Filter out domains with a spam score above 30.

## Step 5: Analyze Anchor Text Distribution

Check your current anchor text profile:

```
POST /v3/backlinks/anchors/live
data: [{"target": "example.com", "limit": 50, "order_by": ["backlinks,desc"]}]
```

A healthy profile has diverse anchors: brand name (40-60%), naked URLs (20-30%), topic keywords (10-20%), generic ("click here") (5-10%). Over-optimized anchor text (more than 30% exact-match keywords) is a red flag.

## Step 6: Track Link Velocity

```
POST /v3/backlinks/timeseries_summary/live
data: [{"target": "example.com", "date_from": "2025-01-01", "date_to": "2025-12-31"}]
```

Check new and lost backlink trends. Sudden drops indicate lost links that may need recovery.

## Step 7: Find Recently Lost Links

```
POST /v3/backlinks/bulk_new_lost_backlinks/live
data: [{"targets": ["example.com"], "date_from": "2026-09-01"}]
```

Recover recently lost high-value links by contacting the linking sites.

## Expected Output

A link building plan containing:
- Current backlink profile health assessment
- 20-50 vetted outreach targets (high rank, low spam score, dofollow)
- Anchor text recommendations for a natural link profile
- Recently lost links to recover
- Link velocity benchmarks against competitors
