---
name: examples
description: This skill should be used when the user asks for "DataForSEO examples", "DataForSEO workflows", "SEO analysis example", "show me how to use DataForSEO", or needs complete end-to-end scenario walkthroughs for SEO data analysis with DataForSEO.
---

# DataForSEO Workflow Examples

Complete end-to-end scenarios showing how to chain DataForSEO `api_request` calls for real SEO work. Each call is shown as its REST path and `data` body; the scenarios assume the docs-first cycle and an agreed budget from the `mcp-patterns` and `cost-awareness` skills.

## Available Scenarios

| Scenario | Description | Endpoints Used |
|----------|-------------|----------------|
| [Keyword Strategy](references/scenarios/keyword-strategy.md) | Build a keyword strategy for a new product launch | keyword_ideas, keyword_suggestions, keyword_overview, search_intent, bulk_keyword_difficulty |
| [Competitor Gap Analysis](references/scenarios/competitor-gap-analysis.md) | Full competitive analysis with keyword and backlink gaps | competitors_domain, domain_rank_overview, domain_intersection, backlinks competitors, bulk_ranks |
| [Backlink Prospecting](references/scenarios/backlink-prospecting.md) | Find link building opportunities via competitor analysis | backlinks summary, bulk_ranks, referring_domains, bulk_spam_score, anchors |
| [Content Opportunity Finder](references/scenarios/content-opportunity-finder.md) | Discover content topics with traffic potential | content_analysis summary and phrase_trends, keyword_ideas, SERP organic, llm_mentions |

## Quick Start Pattern

Every DataForSEO workflow follows the same pattern:

1. **Plan**: read the endpoint pages with `docs_search`, list the calls, agree a budget
2. **Discover**: broad endpoints (keyword_ideas, competitors_domain, content_analysis search) find opportunities
3. **Evaluate**: metrics endpoints (keyword_overview, bulk_keyword_difficulty, backlinks summary) assess potential
4. **Prioritize**: filter by difficulty, volume and relevance to select targets
5. **Deep Dive**: detailed endpoints (ranked_keywords, backlinks, SERP organic) on the top targets
6. **Report**: compile findings into actionable recommendations

## Common Parameters Across All Scenarios

- `location_code`: 2840 is United States; `location_name` with the full country name also works
- `language_code`: ISO code, "en", "de", "fr", "es"
- `limit`: result rows; 10 unless set in the default `.ai` mode, 1000 at most
- `filters`: array syntax for narrowing results
- `order_by`: array of "field,direction" strings

## Cost Tips

- Start broad with bulk endpoints (cheaper per result)
- Use keyword_overview for up to 700 keywords in one call
- Use the bulk endpoints for up to 1000 targets per call
- Filter in the request, not after fetching all the data
- Show the plan and get the user's go-ahead before the first `api_request`
