# Scenario: Backlink Prospecting

Find high-quality link building opportunities by analyzing competitor backlink profiles.

## Step 1: Audit Your Current Backlink Profile

```
Tool: mcp__dataforseo__backlinks_summary
Input: {
  "target": "example.com",
  "include_subdomains": true,
  "exclude_internal_backlinks": true
}
```

Record baseline: total backlinks, referring_domains, rank, broken_backlinks.

## Step 2: Identify Competitor Backlink Profiles

```
Tool: mcp__dataforseo__backlinks_bulk_ranks
Input: {
  "targets": ["example.com", "competitor1.com", "competitor2.com", "competitor3.com"]
}
```

Compare rank scores. The gap between your rank and competitors' indicates link building potential.

## Step 3: Find Link Sources Unique to Competitors

Get competitor's referring domains:

```
Tool: mcp__dataforseo__backlinks_referring_domains
Input: {
  "target": "competitor1.com",
  "limit": 100,
  "order_by": ["rank,desc"],
  "filters": [["dofollow", "=", true]]
}
```

These are domains linking to your competitor but potentially not to you — outreach targets.

## Step 4: Check Spam Scores

Before pursuing outreach, verify domain quality:

```
Tool: mcp__dataforseo__backlinks_bulk_spam_score
Input: {
  "targets": ["potential-link-source1.com", "potential-link-source2.com", "...up to 1000"]
}
```

Filter out domains with spam_score > 30.

## Step 5: Analyze Anchor Text Distribution

Check your current anchor text profile for health:

```
Tool: mcp__dataforseo__backlinks_anchors
Input: {
  "target": "example.com",
  "limit": 50,
  "order_by": ["backlinks,desc"]
}
```

A healthy profile has diverse anchors: brand name (40-60%), naked URLs (20-30%), topic keywords (10-20%), generic ("click here") (5-10%). Over-optimized anchor text (>30% exact match keywords) is a red flag.

## Step 6: Track Link Velocity

```
Tool: mcp__dataforseo__backlinks_timeseries_summary
Input: {
  "target": "example.com",
  "date_from": "2024-01-01",
  "date_to": "2024-12-31"
}
```

Check new/lost backlink trends. Sudden drops indicate lost links that may need recovery.

## Step 7: Find Recently Lost Links

```
Tool: mcp__dataforseo__backlinks_bulk_new_lost_backlinks
Input: {
  "targets": ["example.com"],
  "date_from": "2024-10-01"
}
```

Recover recently lost high-value links by reaching out to the linking sites.

## Expected Output

A link building plan containing:
- Current backlink profile health assessment
- 20-50 vetted outreach targets (high rank, low spam score, dofollow)
- Anchor text recommendations for natural link profile
- Recently lost links to recover
- Link velocity benchmarks against competitors
