# Keyword research recipes

Exact calls for search volume, CPC, bid ranges, keyword ideas, competitors' paid keywords, Google Keyword Planner and Search Console mining. Raw output goes to `ads/research/raw/`, the keyword table to `ads/research/keywords.md`.

## Contents

- Volumes, CPC and bid ranges for a seed list
- Expand the seeds
- Competitors' paid keywords
- Forecast caveats
- Google Keyword Planner
- Mine Search Console
- Save the keyword table

Run every command from the project root. Write each JSON body to a file first and pass it as `@FILE`. DataForSEO bodies are a JSON array with one task object. After each call check the top-level `status_code` and every `tasks[].status_code` (20000 is OK) and read `cost` for the price paid.

## Volumes, CPC and bid ranges for a seed list

Source: Google Keyword Planner data through DataForSEO. Refreshed about mid-month.

Live: `keywords_data/google_ads/search_volume/live`, 0.09 USD per call, seconds. Standard: `.../task_post`, 0.06 USD per call, 1 to 3 hours.

Price is per call, not per keyword: fill each call with up to 1000 keywords (each at most 80 characters and 10 words, lower-case). Live limit: 12 calls per minute per account; wait 5 seconds between calls. Google merges near-duplicate variants, so send "car" and "cars" in separate calls if you need both.

Check which month is the latest published (`actual_data: true` means last month is out, so `date_to` may be last month):

```bash
python3 ads/tools/ads.py dataforseo get keywords_data/google_ads/status
```

```bash
cat > ads/research/raw/req-sv.json <<'EOF'
[{"location_code": 2840, "language_code": "en",
  "keywords": ["buy running shoes", "trail running shoes", "running shoes for flat feet"],
  "sort_by": "search_volume"}]
EOF
python3 ads/tools/ads.py dataforseo post keywords_data/google_ads/search_volume/live \
  --data @ads/research/raw/req-sv.json --out ads/research/raw/sv.json
jq -r '.tasks[0].result[] | [.keyword, .search_volume, .cpc, .competition, .competition_index, .low_top_of_page_bid, .high_top_of_page_bid] | @csv' ads/research/raw/sv.json
```

Fields: `search_volume` (average monthly searches), `cpc` (USD), `competition` (`LOW`, `MEDIUM`, `HIGH`), `competition_index` (0 to 100), `low_top_of_page_bid` and `high_top_of_page_bid` (top-of-page bid range), `monthly_searches` (history, up to 4 years with `date_from` and `date_to`).

- Omit `location_code` and you get worldwide data. Find codes: `dataforseo get keywords_data/google_ads/locations`, `dataforseo get serp/google/locations/US` (free). Russia and Belarus are not supported.
- Standard flow for big batches: `task_post` (up to 100 tasks per call), then `dataforseo get keywords_data/google_ads/search_volume/tasks_ready` (at most 20 calls per minute), then `dataforseo get keywords_data/google_ads/search_volume/task_get/<ID>`. Results stay available 30 days.
- Errors: `40209` too many parallel calls, `50301` Google busy (retry later, prefer the Standard flow), `40501` an invalid field named in the message.
- Docs: https://docs.dataforseo.com/v3/keywords_data/google_ads/search_volume/live.md

## Expand the seeds

Labs endpoints are Live only. Price: 0.012 USD per call plus 0.00012 USD per returned item (700 ideas cost about 0.10 USD). At most 30 parallel requests. `location_code` and `language_code` are required.

| Endpoint (after `v3/`) | Input | Returns |
|---|---|---|
| `dataforseo_labs/google/keyword_ideas/live` | `keywords` (at most 200 seeds), `limit` (default 700, at most 1000) | ideas with volume, CPC, bids, `keyword_properties.keyword_difficulty`, `search_intent_info.main_intent` |
| `dataforseo_labs/google/related_keywords/live` | `keyword`, `depth` 0 to 4 (up to 4680 ideas) | related queries with `depth` |
| `dataforseo_labs/google/keyword_suggestions/live` | `keyword` | long-tail phrases containing the seed |
| `dataforseo_labs/google/search_intent/live` | `keywords` (at most 1000), no location | `keyword_intent.label`: `informational`, `navigational`, `commercial`, `transactional` |
| `dataforseo_labs/google/bulk_keyword_difficulty/live` | `keywords` (at most 1000) | `keyword_difficulty` 0 to 100 |
| `keywords_data/google_ads/keywords_for_keywords/live` | `keywords` (at most 20) | ideas with the same fields as search volume; 0.09 USD per call |

```bash
cat > ads/research/raw/req-ideas.json <<'EOF'
[{"keywords": ["running shoes", "trail running"], "location_code": 2840, "language_code": "en",
  "limit": 300, "order_by": ["keyword_info.search_volume,desc"]}]
EOF
python3 ads/tools/ads.py dataforseo post dataforseo_labs/google/keyword_ideas/live \
  --data @ads/research/raw/req-ideas.json --out ads/research/raw/ideas.json
jq -r '.tasks[0].result[0].items[] | [.keyword, .keyword_info.search_volume, .keyword_info.cpc, .keyword_info.competition_level, .search_intent_info.main_intent] | @csv' ads/research/raw/ideas.json
```

- Do not set `include_clickstream_data`: it doubles the price.
- In two live calls (Ukraine, 2026-11-27) `keywords_for_keywords` returned only the seed keywords with their volumes and bids, and no new ideas. For ideas use Labs `keyword_ideas`.
- Add a `filters` condition on the product's core word, for example `["keyword", "like", "%running%"]`: sorted by volume, the 300 ideas of the same live run were generic shop queries with one relevant phrase.
- `filters` takes at most 8 conditions, for example `["keyword_info.search_volume", ">", 100]`.
- Labs data refreshes every 30 to 90 days; search volume from Google Ads data is fresher. Re-check the shortlist with the search volume call above.
- A domain's keywords: `dataforseo_labs/google/keywords_for_site/live` with `target`, `include_subdomains`, `limit`. Use it instead of the Google Ads variant of the same name: a help article calls that one deprecated.
- Docs: https://docs.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live.md

## Competitors' paid keywords

`ranked_keywords` with `item_types: ["paid"]` lists the keywords a domain buys, with the ad copy Google showed. Price 0.012 USD plus 0.00012 per row.

```bash
cat > ads/research/raw/req-paid.json <<'EOF'
[{"target": "competitor.example.com", "location_code": 2840, "language_code": "en",
  "item_types": ["paid"], "limit": 100,
  "order_by": ["keyword_data.keyword_info.search_volume,desc"]}]
EOF
python3 ads/tools/ads.py dataforseo post dataforseo_labs/google/ranked_keywords/live \
  --data @ads/research/raw/req-paid.json --out ads/research/raw/paid-kw.json
jq '.tasks[0].result[0].items[] | {kw: .keyword_data.keyword, sv: .keyword_data.keyword_info.search_volume, cpc: .keyword_data.keyword_info.cpc, pos: .ranked_serp_element.serp_item.rank_absolute, title: .ranked_serp_element.serp_item.title, description: .ranked_serp_element.serp_item.description, url: .ranked_serp_element.serp_item.url}' ads/research/raw/paid-kw.json
```

- `target` is a domain without `https://` and `www.`; a page needs the full URL.
- Per-item paid fields: `etv` (estimated monthly traffic), `estimated_paid_traffic_cost`, `rank_changes`, `is_new`, `is_up`, `is_down`.
- A keyword gap against a rival: `dataforseo_labs/google/domain_intersection/live` with `target1` (rival), `target2` (you), `item_types: ["paid"]`, `intersections: false` returns the keywords only `target1` has; `true` returns the shared ones. Error `40504` means more than 10 million intersections: pick other domains.
- Find which rivals to query first: see the competitor recipes (`competitors_domain`).
- Docs: https://docs.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live.md

## Forecast caveats

- Google no longer gives per-keyword forecasts. `keywords_data/google_ads/ad_traffic_by_keywords/live` returns one campaign-level dataset for all keywords in the task; `impressions` and `ctr` are always null. Use only `clicks`, `cost`, `average_cpc`, and as a rough cross-check. Required: `bid` (integer, high, for example 999), `match` (`exact`, `broad`, `phrase`); `date_interval`: `next_week`, `next_month`, `next_quarter`.
- Whether any Google impressions forecast still exists is unverified: do not promise impressions.
- Google's own forecast, through the generic call, is campaign-level too. `forecastPeriod.startDate` must be in the future, `endDate` within one year. Money is in micros (1 USD is 1000000). `clicks` and `averageCpcMicros` come back only for Manual CPC and Maximize Clicks.

```bash
cat > ads/research/raw/req-forecast.json <<'EOF'
{"forecastPeriod": {"startDate": "2026-12-01", "endDate": "2026-12-31"},
 "campaign": {
   "biddingStrategy": {"maximizeClicksBiddingStrategy": {"dailyTargetSpendMicros": "20000000", "maxCpcBidCeilingMicros": "2000000"}},
   "geoTargetConstants": ["geoTargetConstants/2840"],
   "languageConstants": ["languageConstants/1000"],
   "adGroups": [{"keywords": [{"text": "trail running shoes", "matchType": "EXACT"}]}]}}
EOF
python3 ads/tools/ads.py google call POST 'customers/{customer}:generateKeywordForecastMetrics' \
  --data @ads/research/raw/req-forecast.json
```

The call only reads, so it runs without `--yes`; `{customer}` is filled from `ads/.env`. Needs Basic access like the other Keyword Planner calls.

- Sizing rule (heuristic, label it as one in the report): clicks = volume x assumed click-through rate for the position x impression share; cost = clicks x CPC. State the assumed rates.
- Docs: https://developers.google.com/google-ads/api/docs/keyword-planning/generate-forecast-metrics

## Google Keyword Planner

Needs Basic access or higher: with Explorer access the planning calls are refused; then use the DataForSEO recipes above. Limit about 1 request per second. Metrics refresh monthly: cache the output.

Resolve ids first (free):

```bash
python3 ads/tools/ads.py google geo --query "Berlin" --country DE --locale en
```

| Id | Value |
|---|---|
| Geo target | numeric id from `google geo`, for example `2840` (United States); at most 10 per call |
| Language | numeric id, `1000` = English; others: `google search --query "SELECT language_constant.id, language_constant.code, language_constant.name FROM language_constant"` |

```bash
python3 ads/tools/ads.py google keyword-ideas --keywords "trail running shoes,running shoes" \
  --geo 2840 --language 1000 --limit 200 --out ads/research/raw/kp-ideas.json
python3 ads/tools/ads.py google keyword-ideas --url https://example.com/shoes \
  --geo 2840 --language 1000 --limit 200 --out ads/research/raw/kp-url.json
```

- One run takes 1 to 20 seed keywords or one URL. A URL seed uses that page only; a domain is used when the page has no hits.
- Result fields (from the API): `text`, `keywordIdeaMetrics.avgMonthlySearches`, `competition` (`LOW`, `MEDIUM`, `HIGH`), `competitionIndex` (0 to 100), `lowTopOfPageBidMicros` (20th percentile), `highTopOfPageBidMicros` (80th percentile). Divide micros by 1000000.
- `averageCpcMicros` comes back only when requested; if it is empty, take CPC from DataForSEO.
- Docs: https://developers.google.com/google-ads/api/docs/keyword-planning/generate-keyword-ideas

## Mine Search Console

Real queries that already bring impressions to the site. Skip when the site has no property or little traffic.

```bash
python3 ads/tools/ads.py gsc sites
python3 ads/tools/ads.py gsc query --site sc-domain:example.com --start 2026-08-10 --end 2026-11-08 \
  --dimensions query,page --row-limit 25000 --type web --format csv --out ads/research/raw/gsc-qp.csv
```

Request patterns:

| Question | Command change |
|---|---|
| Non-brand queries | `--dimensions query --filter "query:excludingRegex:(?i)(brandname)"` |
| Top landing pages | `--dimensions page --row-limit 1000` |
| Which countries | `--dimensions country,query --filter "query:includingRegex:(?i)running shoes|trail shoes"` (country codes are three letters) |
| Which devices on one page | `--dimensions device,query --filter "page:equals:https://example.com/shoes/"` |
| Recent trend | `--dimensions date --start 2026-11-01 --end 2026-11-14` (last days may be partial) |

- `ctr` is a fraction from 0 to 1; `position` is the average position. Rare and personal queries are omitted from the data.
- Brand exclusion by regex is an approximation.
- Use `--filter` more than once for more conditions. `OP` is `contains`, `equals`, `notContains`, `notEquals`, `includingRegex`, `excludingRegex`.

Scoring (heuristics, not Google guidance; tune the thresholds and say so in the report):

```text
paid candidate : impressions >= 500 and position 5 to 20 and ctr < 0.02   (visible, weak clicks)
defend organic : position <= 3 and ctr >= 0.10                            (lower bid or exclude)
landing page   : the page with most clicks per query cluster; flag pages whose mobile ctr is below desktop ctr
geo priority   : countries by impressions share, then by clicks per impression
```

Candidates still need CPC and competition from the sections above before they enter the table.
Docs: https://developers.google.com/webmaster-tools/v1/searchanalytics/query

## Save the keyword table

The skill (`SKILL.md`, track 2) defines the file `ads/research/keywords.md`: one row per keyword with its cluster, a negative list, and the date and source of the numbers. Fill its columns from these fields:

| Column | Filled from |
|---|---|
| keyword | any source |
| cluster | your own sorting into brand, competitor, solution, problem, irrelevant; the Labs `search_intent` label helps but is not the cluster |
| monthly volume | `search_volume` or `avgMonthlySearches` |
| CPC low and high | the top-of-page bid range (`low_top_of_page_bid` and `high_top_of_page_bid`, or the Keyword Planner micros divided by 1,000,000); `cpc` when only an average exists |
| competition | `competition` and `competition_index` |
| match type | heuristic: exact for transactional and brand-defence terms, phrase for commercial terms, broad only with conversion tracking and automated bidding |
| landing page | the page of the site that answers the keyword |
| source | `dataforseo-sv`, `labs-ideas`, `rival-paid:<domain>`, `kp`, `gsc` |

Irrelevant terms go into the "Negatives" list under the table. Keep the raw files in `ads/research/raw/` and write the research date at the top: volumes move monthly.
