# Competitor research recipes

Exact calls to find competitors, read the ads they run, read their landing pages and collect customer voice. Raw output goes to `ads/research/raw/`, conclusions to `ads/research/competitors.md`.

## Contents

- Find the competitors
- Read the ads they run
- Read their landing pages
- Voice of customer
- Describe a competitor creative
- Question to cheapest call to cost
- Save the result

Run every command from the project root. Write each JSON body to a file first, then pass it as `@FILE`. Check cost before a paid call: `python3 ads/tools/ads.py apify actor ACTOR` prints the Actor's pricing and input fields.

## Find the competitors

### DataForSEO Labs: who bids on the same keywords

Live only. Price: 0.012 USD per call plus 0.00012 USD per returned item. Location and language are required (`2840` = United States, `en`).

```bash
mkdir -p ads/research/raw
cat > ads/research/raw/req-comp.json <<'EOF'
[{"target": "example.com", "location_code": 2840, "language_code": "en",
  "item_types": ["paid"], "exclude_top_domains": true, "limit": 20,
  "order_by": ["metrics.paid.etv,desc"]}]
EOF
python3 ads/tools/ads.py dataforseo post dataforseo_labs/google/competitors_domain/live \
  --data @ads/research/raw/req-comp.json --out ads/research/raw/comp-paid.json
jq '.tasks[0].result[0].items[] | {domain, common: .intersections, paid_etv: .metrics.paid.etv, paid_kw: .metrics.paid.count, paid_cost: .metrics.paid.estimated_paid_traffic_cost}' ads/research/raw/comp-paid.json
```

- `intersections`: keywords both domains rank for. `metrics.paid.etv`: estimated monthly paid traffic. `metrics.paid.estimated_paid_traffic_cost`: what that traffic would cost through ads, USD.
- No keywords yet, only a topic: `dataforseo_labs/google/serp_competitors/live` with `keywords: [...]` instead of `target`. Size one rival: `dataforseo_labs/google/domain_rank_overview/live` with `target`.
- Check the top-level `status_code` and every `tasks[].status_code`: 20000 is OK, `40102` means no results. Labs allows 30 parallel requests. Leave `include_clickstream_data` off: it doubles the price.

### Firecrawl search: who the market says the alternatives are

2 credits for up to 10 results.

```bash
python3 ads/tools/ads.py firecrawl search "alternatives to ExampleProduct" --limit 10 \
  --out ads/research/raw/search-alt.json
```

Query patterns: `<product> alternatives`, `best <category> software`, `<product> vs`. Keep the competitor's own domain, drop review and listicle domains from the shortlist.

## Read the ads they run

| Library | What it holds | Limit that bites |
|---|---|---|
| Meta Ad Library API | any ad delivered to the UK or EU in the past year; political and issue ads worldwide for 7 years | commercial ads outside the UK and EU are not returned; no spend or reach for commercial ads outside the EU |
| TikTok Ad Library (EU) | commercial content in EU/EEA/UK | 3,600 results per search term and country pair |
| TikTok Creative Center | top ads by country and period | no official API; use an Actor |
| Google Ads Transparency Center | last 12 months, per advertiser | text ads are stored as images |

### Meta Ad Library through the toolkit

Needs identity confirmation of the Facebook account and a developer app on that account. Without it the call returns an error: use the Apify route below.

```bash
python3 ads/tools/ads.py meta ad-library --terms "running shoes" --countries DE,GB --limit 25 \
  --out ads/research/raw/meta-lib.json
```

The command asks for the page name, the creative texts, link titles and descriptions, delivery start and stop time, `ad_snapshot_url`, platforms and languages, and follows pages up to `--limit` (page size at most 100). For EU reach and the targeting fields, call the endpoint directly:

```bash
python3 ads/tools/ads.py meta get ads_archive \
  -p search_terms="running shoes" -p ad_type=ALL -p ad_active_status=ALL \
  -p 'ad_reached_countries=["DE","GB"]' -p limit=25 \
  -p fields=id,page_id,page_name,ad_creative_bodies,ad_creative_link_titles,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,publisher_platforms,languages,eu_total_reach
```

- `ad_reached_countries` is required; `search_terms` at most 100 characters. `ad_active_status`: `ACTIVE` (default), `ALL`, `INACTIVE`; use `ALL` to measure how long an ad ran.
- `eu_total_reach`, `target_ages`, `target_gender`, `target_locations` exist for UK and EU delivery only. Page with `paging.cursors.after`; an empty `data` is the end. Maximum `limit` is unverified: stay at 25. `ad_snapshot_url` renders the ad; media cannot be bulk-downloaded.
- Docs: https://www.facebook.com/ads/library/api/

### Apify Actors for the ad libraries

Run through the toolkit. Always pass a cap: `--max-usd` stops the run at that cost, `--max-items` limits charged items.

```bash
python3 ads/tools/ads.py apify run ACTOR --input @ads/research/raw/in-ads.json \
  --max-usd 1 --max-items 100 --timeout 600 --out ads/research/raw/ads-out.json
```

Prices are the Free-plan list price per event on 2026-11-14; paid plans are cheaper. Re-check with `apify actor ACTOR` before a large run.

| Library | Actor | Price | Cost for 100 ads |
|---|---|---|---|
| Meta, by keyword and country | `igolaizola/facebook-ad-library-scraper` | 0.00075 per result plus 0.0075 per start | about 0.08 USD |
| Meta, by page URL (first party) | `apify/facebook-ads-scraper` | 0.0058 per ad | 0.58 USD |
| TikTok EU library | `lexis-solutions/tiktok-ads-scraper` | 0.00049 per ad plus 0.00001 per start | about 0.05 USD |
| TikTok Creative Center | `azzouzana/tiktok-creative-center-top-ads-scraper` | 0.001 per result, 0.002 per ad detail, 0.005 per start | about 0.11 USD |
| Google Transparency Center | `scrapesage/google-ads-transparency-scraper` | 0.002 per ad | 0.20 USD |

Minimal input of each Actor, one JSON file per run (the value under its id):

```json
{"igolaizola/facebook-ad-library-scraper": {"query": "running shoes", "country": "DE", "activeStatus": "active", "maxItems": 100},
 "apify/facebook-ads-scraper": {"startUrls": [{"url": "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DE&search_type=page&view_all_page_id=1234567890"}], "resultsLimit": 50, "activeStatus": "active"},
 "lexis-solutions/tiktok-ads-scraper": {"query": "running shoes", "country": "DE", "maxPages": 2},
 "azzouzana/tiktok-creative-center-top-ads-scraper": {"maxItems": 100, "countryCode": "US", "period": 30},
 "scrapesage/google-ads-transparency-scraper": {"queries": ["example.com"], "region": "US", "maxAdsPerSearch": 50, "adFormat": "ALL"}}
```

- `igolaizola`: output `ad_archive_id`, `snapshot.body.text`, `snapshot.title`, `snapshot.cta_text`, `snapshot.link_url`, `start_date`, `end_date`; spend and reach are not available for every ad.
- `apify/facebook-ads-scraper`: the `{"url": ...}` item shape is unverified; if rejected, pass the bare page slug. `isDetailsPerAd: true` adds reach and spend at extra cost per ad.
- `lexis-solutions`: output `adId`, `advertiserName`, `adTitle`, `adImpressions`, `adLandingUrl`, `adVideoUrl`; `startDate` and `endDate` format is unverified (try `YYYY-MM-DD`).
- `azzouzana`: `period` is `7`, `30` or `180`, up to 3,000 items per run; the only route to US top ads. Output field names are unverified: inspect the first item.
- `scrapesage`: `adFormat` is `ALL`, `TEXT`, `IMAGE`, `VIDEO`; output `creativeId`, `advertiserName`, `format`, `firstShown`, `lastShown`, `shownForDays`, `imageUrl`, `adUrl`.

- Third-party ad-library Actors have small user bases and change often: on a failure run `apify actor ACTOR` and try the next Actor for the same library. The TikTok Commercial Content API (EU ads) needs its own developer approval and host; the toolkit cannot call it.

### DataForSEO: Google Ads Transparency without an Actor

Live price 0.002 USD per call. Two steps: find the advertiser id, then list its ads.

```bash
cat > ads/research/raw/req-adv.json <<'EOF'
[{"keyword": "rival.example.com", "location_code": 2840}]
EOF
python3 ads/tools/ads.py dataforseo post serp/google/ads_advertisers/live/advanced \
  --data @ads/research/raw/req-adv.json --out ads/research/raw/adv.json
jq '.tasks[0].result[0].items[] | {type, advertiser_id, title, verified, approx_ads_count}' ads/research/raw/adv.json

cat > ads/research/raw/req-adsearch.json <<'EOF'
[{"target": "rival.example.com", "location_code": 2840, "platform": "google_search",
  "format": "all", "date_from": "2026-08-01", "date_to": "2026-11-14", "depth": 40}]
EOF
python3 ads/tools/ads.py dataforseo post serp/google/ads_search/live/advanced \
  --data @ads/research/raw/req-adsearch.json --out ads/research/raw/adsearch.json
jq '.tasks[0].result[0].items[] | {advertiser_id, creative_id, title, format, url, preview_url, first_shown, last_shown}' ads/research/raw/adsearch.json
```

- Replace `target` with `advertiser_ids: ["<ID>"]` (at most 25) when the domain matches several advertisers.
- `platform`: `all`, `google_play`, `google_maps`, `google_search`, `google_shopping`, `youtube`. `format`: `all`, `text`, `image`, `video`. `date_from` is 2018-05-31 at the earliest.
- Billing is per page of up to 40 ads; each further 40 costs one more base price. Keep `depth` at 40, a safe maximum is 120.
- `last_shown` minus `first_shown` is how long the ad survived: long-running creatives are the winners.
- Live ad copy for one keyword: `serp/google/organic/live/advanced` returns ads as items with `type: "paid"` (0.002 USD per 10 results; body `keyword`, `location_code`, `language_code`, `device`, `depth`). A rival's bought keywords: see `ranked_keywords` in the keyword recipes.

## Read their landing pages

One scrape returns the page text, a structured offer and a screenshot. Cost: 1 credit for the page, 4 more for the structured extraction, screenshot free.

```bash
cat > ads/research/raw/offer-schema.json <<'EOF'
{"type": "object", "required": ["headline"], "properties": {
  "headline": {"type": "string"}, "subheadline": {"type": "string"},
  "primary_cta": {"type": "string"}, "offer": {"type": "string"},
  "guarantees": {"type": "array", "items": {"type": "string"}},
  "social_proof": {"type": "array", "items": {"type": "string"}},
  "pricing_plans": {"type": "array", "items": {"type": "object", "properties": {
    "name": {"type": "string"}, "price": {"type": "string"}, "billing_period": {"type": "string"}}}},
  "testimonials": {"type": "array", "items": {"type": "object", "properties": {
    "quote": {"type": "string"}, "role_or_company": {"type": "string"}}}}}}
EOF
python3 ads/tools/ads.py firecrawl scrape https://rival.example.com/pricing \
  --formats markdown,screenshot --schema @ads/research/raw/offer-schema.json \
  --out ads/research/raw/lp-competitor.json
jq '.data.json' ads/research/raw/lp-competitor.json
```

- The structured result is `data.json`; the screenshot link is `data.screenshot`. The link expires after 24 hours: download it at once with `curl -sSL "$(jq -r .data.screenshot ads/research/raw/lp-competitor.json)" -o ads/research/raw/lp-competitor.png`.
- No personal names: leave the author out of `testimonials` unless the page shows a company only.
- List the pages worth scraping first: `firecrawl map https://rival.example.com --search pricing --limit 50` (1 credit; try `features`, `customers`, `compare` as the search word).

## Voice of customer

Reviews and comments give the customer's own words for pain, desire and objection. Use them for ad copy hooks.

Data-minimisation rule (Apify's legal notes): reviews and comments are personal data under GDPR whatever their source. Collect as few personal fields as possible, keep them only temporarily, and store text and rating, not names or handles. Aggregate or anonymise before the text reaches ad copy. Do not use an Actor that asks for a login cookie of a real account.

| Source | Actor | Price per review or item | Minimal input |
|---|---|---|---|
| Google Maps | `compass/Google-Maps-Reviews-Scraper` | 0.0006 plus 0.00005 start | `{"placeIds": ["<PLACE_ID>"], "maxReviews": 100, "reviewsSort": "newest", "language": "en"}` |
| Trustpilot | `automation-lab/trustpilot` | 0.000575 plus 0.005 start | `{"companyUrls": ["rival.example.com"], "maxReviewsPerCompany": 100}` |
| App Store | `thewolves/appstore-reviews-scraper` | 0.0001 | `{"appIds": ["<APP_ID>"], "country": "us", "maxItems": 100}` |
| Google Play | `neatrat/google-play-store-reviews-scraper` | 0.00015 | `{"appIdOrUrl": "<APP_ID>", "sortBy": "newest", "maxReviews": 100}` |
| Reddit threads | `apify/reddit-scraper` | 0.004 per post, 0.0032 per comment | `{"scrapeMode": "posts", "communityNames": ["running"], "communityQueries": ["shoes"], "maxPostsPerCommunity": 50}` |
| TikTok comments | `clockworks/tiktok-comments-scraper` | 0.00125 per comment | `{"postURLs": ["<VIDEO_URL>"], "commentsPerPost": 100}` |

- `maxReviews` of the Google Maps Actor defaults to 10,000,000: always set it. `trudax/reddit-scraper-lite` needs a login cookie: do not use it.
- Output fields differ per Actor. Keep only text, rating and date:

```bash
python3 ads/tools/ads.py apify run compass/Google-Maps-Reviews-Scraper \
  --input @ads/research/raw/in-reviews.json --max-usd 1 --max-items 100 --out ads/research/raw/reviews-raw.json
jq '[.[] | {stars, text}]' ads/research/raw/reviews-raw.json > ads/research/raw/reviews-min.json
rm ads/research/raw/reviews-raw.json
```

The raw review file is the one raw output that is deleted on purpose: it holds names and handles, and the data-minimisation rule above says to keep text and rating only.

Cluster `reviews-min.json` by theme (pain, desire, objection, phrase used) and write the clusters, with counts, into the "Customer voice" section of `ads/research/competitors.md`, under the competitor table.

## Describe a competitor creative

`analyze` describes an image or a video from a file or a link. Put the question in the prompt.

```bash
python3 ads/tools/ads.py analyze --provider gemini --url "<IMAGE_OR_VIDEO_URL>" \
  --prompt "Describe the hook in the first 3 seconds, the offer, the call to action, the on-screen text, the format and the emotional angle. Answer in 6 bullet points." \
  > ads/research/raw/analysis-001.txt
```

- Use `--file FILE` for a downloaded asset. Take the link from the Actor output (`imageUrl`, `adVideoUrl`, `videoUrls`). Use the same prompt for every ad, on the longest-running ads only.

## Question to cheapest call to cost

| Question | Cheapest call | Cost |
|---|---|---|
| Who buys the same keywords? | `dataforseo post dataforseo_labs/google/competitors_domain/live` | about 0.014 USD for 20 rivals |
| Who else is in this category? | `firecrawl search "<product> alternatives"` | 2 credits |
| Does this rival run Google ads? | `dataforseo post serp/google/ads_advertisers/live/advanced` | 0.002 USD |
| Which Google ads, how long? | `dataforseo post serp/google/ads_search/live/advanced` | 0.002 USD per 40 ads |
| Meta ads, UK or EU market | `meta ad-library --terms ... --countries DE,GB` | no price stated by Meta |
| Meta ads, other markets | `apify run igolaizola/facebook-ad-library-scraper` | about 0.08 USD per 100 ads |
| TikTok ads, EU market | `apify run lexis-solutions/tiktok-ads-scraper` | about 0.05 USD per 100 ads |
| TikTok ads, US market | `apify run azzouzana/tiktok-creative-center-top-ads-scraper` | about 0.11 USD per 100 ads |
| What is their offer and price? | `firecrawl scrape URL --schema @FILE` | 5 credits per page |
| What do customers say? | `apify run compass/Google-Maps-Reviews-Scraper` | about 0.06 USD per 100 reviews |

## Save the result

The skill (`SKILL.md`, track 1) defines the file `ads/research/competitors.md`: one table row per competitor, a "Customer voice" section and the closing "What this means for us". Fill the columns from these findings: positioning from the landing page headline; offer and price from the scraped pricing page; channels seen from the ad libraries; angles from the ad texts, with the longest-running ad and its age in days as the strongest evidence; landing page pattern (headline, proof, call to action, form); the gap from what none of them says. Add the count of paid keywords and their traffic value where DataForSEO gave them, and list the raw file names at the end of the file.

Docs: [Labs competitors](https://docs.dataforseo.com/v3/dataforseo_labs/google/competitors_domain/live.md), [Ads Transparency](https://docs.dataforseo.com/v3/serp/google/ads_search/live/advanced.md), [Firecrawl scrape](https://docs.firecrawl.dev/features/scrape.md), [Apify API](https://docs.apify.com/api/v2).
