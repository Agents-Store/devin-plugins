---
name: examples
description: This skill should be used when the user asks for "DataForSEO examples", "DataForSEO workflows", "SEO analysis example", "show me how to use DataForSEO", or needs complete end-to-end scenario walkthroughs for SEO data analysis with DataForSEO.
---

# DataForSEO Workflow Examples

Complete end-to-end scenarios demonstrating how to chain DataForSEO MCP tools for real SEO work.

## Available Scenarios

| Scenario | Description | Tools Used |
|----------|-------------|-----------|
| [Keyword Strategy](references/scenarios/keyword-strategy.md) | Build a keyword strategy for a new product launch | keyword_ideas, keyword_overview, search_intent, bulk_keyword_difficulty |
| [Competitor Gap Analysis](references/scenarios/competitor-gap-analysis.md) | Full competitive analysis with keyword and backlink gaps | competitors_domain, domain_intersection, ranked_keywords, backlinks_competitors |
| [Backlink Prospecting](references/scenarios/backlink-prospecting.md) | Find link building opportunities via competitor analysis | backlinks_summary, backlinks_referring_domains, backlinks_competitors, bulk_spam_score |
| [Content Opportunity Finder](references/scenarios/content-opportunity-finder.md) | Discover content topics with traffic potential | content_analysis_search, phrase_trends, keyword_ideas, serp_organic_live_advanced |

## Quick Start Pattern

Every DataForSEO workflow follows the same pattern:

1. **Discover** — Use broad tools (keyword_ideas, competitors_domain, content_analysis_search) to find opportunities
2. **Evaluate** — Use metrics tools (keyword_overview, bulk_keyword_difficulty, backlinks_summary) to assess potential
3. **Prioritize** — Filter by difficulty, volume, and relevance to select targets
4. **Deep Dive** — Use detailed tools (ranked_keywords, backlinks_backlinks, serp_organic_live_advanced) on top targets
5. **Report** — Compile findings into actionable recommendations

## Common Parameters Across All Scenarios

- `location_name`: Full country name — "United States", "United Kingdom", "Germany"
- `language_code`: ISO code — "en", "de", "fr", "es"
- `limit`: Results count (default 10, max 1000)
- `filters`: Array syntax for narrowing results
- `order_by`: Array of "field,direction" strings

## Cost Tips

- Start broad with bulk endpoints (cheaper per result)
- Use keyword_overview for up to 700 keywords in 1 call
- Use bulk_* endpoints for up to 1000 targets per call
- Filter at the API level, not after fetching all data
