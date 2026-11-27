# Performance queries: Google Ads, Meta, TikTok, Search Console

Copy-ready pulls of performance numbers through `ads/tools/ads.py`, and the traps that make numbers from different platforms incomparable. Use it before every report.

## Contents

- Metric map and unit traps
- Rules that apply to every pull
- Google Ads (GAQL)
- Meta insights
- TikTok report
- Search Console baseline
- Comparing platforms fairly
- Diagnosis pulls
- Diagnostic heuristics

Docs, one per platform: [GAQL grammar](https://developers.google.com/google-ads/api/docs/query/grammar), [Meta Insights](https://developers.facebook.com/documentation/ads-commerce/marketing-api/insights.md), [TikTok sync report](https://business-api.tiktok.com/portal/docs/run-a-synchronous-report/v1.3), [Search Analytics query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query).

## Metric map and unit traps

| Metric | Google Ads | Meta insights | TikTok report |
|---|---|---|---|
| Spend | `metrics.cost_micros` | `spend` | `spend` |
| Impressions | `metrics.impressions` | `impressions` | `impressions` |
| Clicks | `metrics.clicks` | `clicks` | `clicks` |
| CTR | `metrics.ctr` (ratio 0-1) | `ctr` | `ctr` |
| CPC | `metrics.average_cpc` | `cpc` | `cpc` |
| CPM | compute | compute | `cpm` |
| Conversions | `metrics.conversions` | `actions` (array) | `conversion` |
| Cost per conversion | compute | `cost_per_action_type` (array) | `cost_per_conversion` |
| Conversion value | `metrics.conversions_value` | `action_values` (array) | web: `total_complete_payment_rate`; app: `total_purchase_value` |
| ROAS | compute | compute | web: `complete_payment_roas`; else compute |
| Video views | look the field up with the fields query below | look it up in the Insights field list | `video_play_actions`, `video_watched_6s` |

Unit traps:

| Platform | Trap | Safe choice |
|---|---|---|
| Google | Money fields end in `_micros`: divide by 1,000,000. | `spend = cost_micros / 1e6` |
| Google | Do not rely on the unit of `average_cpc`. | `cpc = cost_micros / 1e6 / clicks` |
| Google | `conversions` counts only conversion actions with `include_in_conversions_metric=true`; `all_conversions` counts every action. | Report `conversions`; name `all_conversions` separately if shown. |
| Meta | Budgets are in minor units (cents); the unit of insights `spend` was not confirmed on the pages read. | Compare `spend` with Ads Manager once per account before trusting it. |
| Meta | `actions` and `action_values` are arrays split by `action_type`; do not rely on the units of `ctr` and `cpc`. | Pick one `action_type` for every report; `ctr = clicks / impressions`, `cpc = spend / clicks`. |
| TikTok | Metric values come back as strings; do not rely on the units of `ctr` and `cpc`. | Cast, then compute from `clicks`, `impressions`, `spend`. |
| TikTok | Purchase value sits in `total_complete_payment_rate` despite the name (web); `total_purchase_value` is the app metric. | Cross-check one day against Ads Manager. |

Compute: CPM = spend / impressions x 1000; cost per conversion = spend / conversions; ROAS = conversion value / spend. Zero denominator: print `n/a`, never 0.

## Rules that apply to every pull

- Run from the project root; save raw output with `--out ads/reports/raw/<name>.json` and keep it untouched.
- One explicit date window for all platforms: `--start`/`--since`/`BETWEEN`, never presets. Presets disagree on whether today is included (Google `LAST_7_DAYS` excludes today).
- End the window at yesterday: today is partial on every platform. Search Console lags 2 to 3 days more, so its pull, when the user wants an organic baseline at all, ends at today minus 3 days and is labelled as a separate window.
- Never run mutating commands for reporting. `--yes` appears below only where a read is sent as a POST (asynchronous reports); it changes nothing in the ad account.

## Google Ads (GAQL)

Command: `google search --query GAQL [--customer ID] [--format json|csv] [--out FILE]`; it reads all pages. Put GAQL in a shell variable.

```bash
python3 ads/tools/ads.py google customers
Q='SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, metrics.impressions, metrics.clicks, metrics.ctr, metrics.cost_micros, metrics.conversions, metrics.conversions_value FROM campaign WHERE segments.date BETWEEN "2026-11-01" AND "2026-11-13" AND campaign.status != "REMOVED" ORDER BY metrics.cost_micros DESC'
python3 ads/tools/ads.py google search --query "$Q" --format json --out ads/reports/raw/google-campaigns.json
```

Each block below is a value for `--query` (double quotes inside GAQL, single quotes around the shell variable); the `FROM` resource sets the row grain.

```sql
-- keywords
SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, campaign.name, ad_group.name, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM keyword_view WHERE segments.date BETWEEN "2026-11-01" AND "2026-11-13" AND ad_group_criterion.status != "REMOVED" ORDER BY metrics.cost_micros DESC

-- search terms (not Performance Max; for Performance Max use FROM campaign_search_term_view)
SELECT search_term_view.search_term, segments.keyword.info.match_type, search_term_view.status, campaign.name, ad_group.name, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM search_term_view WHERE segments.date BETWEEN "2026-11-01" AND "2026-11-13" ORDER BY metrics.cost_micros DESC

-- ads (Search; Demand Gen: add AND ad_group_ad.ad.type = DEMAND_GEN_MULTI_ASSET_AD)
SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.ad.final_urls, ad_group_ad.status, campaign.name, ad_group.name, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM ad_group_ad WHERE segments.date BETWEEN "2026-11-01" AND "2026-11-13" AND ad_group_ad.status != "REMOVED" ORDER BY metrics.cost_micros DESC

-- Performance Max asset groups
SELECT asset_group.id, asset_group.name, asset_group.primary_status, asset_group.ad_strength, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.conversions_value FROM asset_group WHERE segments.date BETWEEN "2026-11-01" AND "2026-11-13"
```

Date syntax:

| Form | Example | Trap |
|---|---|---|
| Explicit | `segments.date BETWEEN "2026-11-01" AND "2026-11-13"` | `YYYY-MM-DD` or `YYYYMMDD`; evaluated in the account time zone |
| Predefined | `segments.date DURING LAST_30_DAYS` | Only: `TODAY`, `YESTERDAY`, `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `LAST_BUSINESS_WEEK`, `LAST_MONTH`, `LAST_WEEK_MON_SUN`, `LAST_WEEK_SUN_SAT`, `THIS_MONTH`, `THIS_WEEK_MON_TODAY`, `THIS_WEEK_SUN_TODAY` |
| Period start | `segments.month = "2026-11-01"` | `segments.week/month/quarter` filter with `=` and the first day of the period |

Two facts from live reads on 2026-11-26 and 2026-11-27:

- `DURING LAST_7_DAYS` excludes today. A same-day check needs `DURING TODAY` or explicit dates: a morning check with the preset reported 0 impressions while the day already had 7,879.
- On Demand Gen, Gmail `clicks` are ad opens. Clicks to the site are `metrics.gmail_secondary_clicks` (live: 68 Gmail clicks, 0 secondary clicks).

GAQL rules:

- Only `AND` between conditions, no `OR`: run two queries or use `IN (...)`.
- A `segments.*` field multiplies rows (`date`, `week`, `month`, `quarter`, `keyword.info.match_type`, `ad_network_type`, `ad_sub_network_type`). Add one at a time. Not every segment and metric can be selected together: on a rejected query drop segments first, then check compatibility (below).
- `search_term_view` excludes Performance Max and aggregates per ad group: use `campaign_search_term_view` for Performance Max and never merge the two.
- Since 2026-06-01 day, hour and week segments reach back only 37 months from today: for longer history use `segments.month` or `segments.quarter`.

Check which fields combine (read-only: a path that ends in `:search` runs without `--yes`):

```bash
echo '{"query": "SELECT name, selectable, filterable, selectable_with WHERE name LIKE \"metrics.video%\""}' > ads/reports/raw/fields-query.json
python3 ads/tools/ads.py google call POST googleAdsFields:search --data @ads/reports/raw/fields-query.json
```

Wasted spend: search terms with cost and no conversions. Rank by cost; review before adding negatives, because `conversions` counts only conversion actions marked for the conversions column.

```bash
Q='SELECT search_term_view.search_term, campaign.name, ad_group.name, metrics.clicks, metrics.cost_micros, metrics.conversions FROM search_term_view WHERE segments.date BETWEEN "2026-10-15" AND "2026-11-13" AND metrics.cost_micros > 0 AND metrics.conversions = 0 ORDER BY metrics.cost_micros DESC LIMIT 100'
python3 ads/tools/ads.py google search --query "$Q" --format csv --out ads/reports/raw/google-terms.csv
```


## Meta insights

Command: `meta insights [--object ID] [--level account|campaign|adset|ad] [--preset P | --since DATE --until DATE] [--fields LIST] [--breakdowns LIST] [-p KEY=VALUE] [--format json|csv] [--out FILE]`. It follows every page and returns a flat list of rows; `-p` repeats and adds any other Insights parameter.

```bash
python3 ads/tools/ads.py meta insights --level campaign --since 2026-11-01 --until 2026-11-13 --fields campaign_id,campaign_name,spend,impressions,clicks,reach,frequency,actions,action_values,cost_per_action_type --out ads/reports/raw/meta-campaigns.json
python3 ads/tools/ads.py meta insights --level adset --since 2026-11-01 --until 2026-11-13 --fields adset_id,adset_name,spend,impressions,clicks,actions,action_values --out ads/reports/raw/meta-adsets.json
# account level: --level account; ad level: --level ad --fields ad_id,ad_name,spend,impressions,clicks,actions,action_values
```

Breakdowns (`--breakdowns LIST`, comma separated):

```bash
python3 ads/tools/ads.py meta insights --level campaign --since 2026-11-01 --until 2026-11-13 --fields campaign_name,spend,impressions,clicks,actions --breakdowns age,gender --out ads/reports/raw/meta-age-gender.json
# placement: --level adset --breakdowns publisher_platform,platform_position ; country: --breakdowns country
```

Breakdown rules (Meta breakdowns page lists the valid combinations):

- Use one breakdown group per pull: `age,gender` and `publisher_platform,platform_position` are valid pairs.
- `dma` is unsupported since 2026-06-22: use `country` or `region`. Hourly breakdowns cannot request `video_*`, unique metrics, `reach` or `frequency`. `relevance_score` and `newsfeed_*` fail with any breakdown.
- Keep `actions` in `--fields` when you use breakdowns (`action_breakdowns` defaults to `action_type`).

`--preset` takes `last_7d`, `last_30d`, `this_month`, `last_month` and others; without a preset or dates the toolkit asks for `last_7d`. For cross-platform reports use `--since`/`--until`.

Attribution windows and daily rows go in through `-p`. Quote JSON values in single quotes.

```bash
python3 ads/tools/ads.py meta insights --level campaign --since 2026-11-01 --until 2026-11-13 --fields campaign_name,spend,actions -p 'action_attribution_windows=["7d_click","1d_view"]' --out ads/reports/raw/meta-windows.json
python3 ads/tools/ads.py meta insights --level campaign --preset last_7d --fields campaign_name,spend,actions -p time_increment=1 -p 'action_attribution_windows=["1d_click"]' --out ads/reports/raw/meta-daily.json
```

Windows that return data: `1d_click`, `7d_click`, `28d_click`, `1d_view`, `1d_ev` (engaged view), `default`. `7d_view` and `28d_view` return no data since 2026-01-12: an empty result is not zero conversions. The default window is not stated consistently by Meta's pages: always pass the windows and print them in the report.

`action_report_time` (`impression`, `conversion`, `mixed`, `lifetime`) sets whether a conversion is dated by the ad impression or by the conversion; keep one value across reports. `time_increment` accepts 1-90, `monthly` or `all_days`. `meta insights` reads every page; a bare `meta get` on an edge returns one page, so look for `paging.next` in its output.

Reading the arrays (inspect the first row; expect objects with `action_type` and a string `value`):

```bash
python3 -c 'import json; d=json.load(open("ads/reports/raw/meta-campaigns.json")); r=d.get("data", d) if isinstance(d, dict) else d; print(sorted({a.get("action_type") for x in r for a in x.get("actions", [])}))'
```

Pick one type from that list per goal, then take `value` from `actions` (count), `action_values` (value) and `cost_per_action_type` (cost) for that same type. Cast `value` to a number. Never sum all types.

Freshness: refreshes about every 15 minutes (today is partial); numbers stop changing 28 days after the reported date, so re-pull before judging a campaign that ended less than 28 days ago. Totals reach 37 months back. Error 100 subcode 1487534 means too much data: narrow the window or the level.

Asynchronous report for large pulls (can take up to 1 h). `meta post` prints a dry run unless `--yes`; this POST only starts a report job:

```bash
python3 ads/tools/ads.py meta post '{account}/insights' -p level=ad -p fields=ad_id,ad_name,impressions,spend,actions -p date_preset=last_30d --yes
python3 ads/tools/ads.py meta get "<REPORT_RUN_ID>" -p fields=async_status,async_percent_completion
python3 ads/tools/ads.py meta insights --object "<REPORT_RUN_ID>" --out ads/reports/raw/meta-async.json
```

`<REPORT_RUN_ID>` is the `report_run_id` of the first call. Wait until `async_status` is `Job Completed` and `async_percent_completion` is 100. `Job Failed` or `Job Skipped`: resubmit. The id expires after 30 days.

## TikTok report

Command: `tiktok report --level LEVEL --start DATE --end DATE [--metrics LIST] [--dimensions LIST] [--format json|csv] [--out FILE]`. Levels: `AUCTION_ADVERTISER`, `AUCTION_CAMPAIGN`, `AUCTION_ADGROUP`, `AUCTION_AD`. Without `--metrics` the toolkit asks for `spend`, `impressions`, `clicks`, `ctr`, `cpc`, `cpm`, `conversion`, `cost_per_conversion` and `conversion_rate`. Names such as `campaign_name` come back only when you list them in `--metrics`.

```bash
python3 ads/tools/ads.py tiktok report --level AUCTION_ADVERTISER --start 2026-11-01 --end 2026-11-13 --metrics spend,impressions,clicks,ctr,cpc,cpm,conversion,cost_per_conversion --out ads/reports/raw/tiktok-account.json
# campaign: --level AUCTION_CAMPAIGN --dimensions campaign_id ; ad group: --level AUCTION_ADGROUP --dimensions adgroup_id ; daily: --dimensions campaign_id,stat_time_day (window up to 30 days)
python3 ads/tools/ads.py tiktok report --level AUCTION_AD --start 2026-11-01 --end 2026-11-13 --dimensions ad_id --metrics ad_name,spend,impressions,clicks,conversion,video_play_actions,video_watched_6s --out ads/reports/raw/tiktok-ads.json
```

Metrics: `campaign_name`, `adgroup_name`, `ad_name`, `currency`, `spend`, `impressions`, `clicks`, `ctr`, `cpc`, `cpm`, `reach`, `frequency`, `conversion`, `cost_per_conversion`, `vta_conversion`, `cta_conversion`, `video_play_actions`, `video_watched_6s`, `complete_payment_roas`, `total_complete_payment_rate`, `total_purchase_value`. Not every metric is valid with every dimension or level: when a request fails, remove metrics one by one. Data is offline for some metrics (about 16 h): yesterday is not final.

Dimensions: `campaign_id`, `adgroup_id`, `ad_id` (Smart+: `ad_id_v2`), `stat_time_day`, `stat_time_hour`, `country_code`. One ID dimension and/or one time dimension per request. Reports cover up to 20,000 ads; ID filters take up to 100 IDs; dates follow the ad-account time zone.

Limits: window with `stat_time_day` up to 30 days; with `stat_time_hour` up to 1 day; with no time dimension up to 365 days; `page_size` 1-1,000 (default 10).

`tiktok report` reads every page (1,000 rows each) and returns one flat row per dimension value. For a parameter it has no flag for, such as `filtering`, call the endpoint directly; arrays and objects go in as JSON text, and this raw call returns one page:

```bash
python3 ads/tools/ads.py tiktok get report/integrated/get/ -p report_type=BASIC -p service_type=AUCTION -p data_level=AUCTION_CAMPAIGN -p 'dimensions=["campaign_id"]' -p 'metrics=["campaign_name","spend","conversion"]' -p start_date=2026-11-01 -p end_date=2026-11-13 -p 'filtering=[{"field_name":"campaign_ids","filter_type":"IN","filter_value":"[\"<CAMPAIGN_ID>\"]"}]' -p page_size=1000
```

Asynchronous report: use it when the window with `stat_time_day` exceeds 30 days, with `stat_time_hour` exceeds 1 day, or the report would exceed 20,000 ads. It has no date-range limit and no paging; it filters only by `campaign_ids`, `adgroup_ids`, `ad_ids`, `country_code`; it reports `country_code` as a country name. Limits: 500 task creations per ad account per hour. Tasks stay valid 30 days.

```bash
cat > ads/reports/raw/tiktok-task.json <<'EOF'
{"report_type": "BASIC", "service_type": "AUCTION", "data_level": "AUCTION_CAMPAIGN", "dimensions": ["campaign_id", "stat_time_day"], "metrics": ["campaign_name", "spend", "conversion"], "start_date": "2026-06-01", "end_date": "2026-11-13"}
EOF
python3 ads/tools/ads.py tiktok post report/task/create/ --data @ads/reports/raw/tiktok-task.json --yes
python3 ads/tools/ads.py tiktok get report/task/check/ -p task_id="<TASK_ID>"
python3 ads/tools/ads.py tiktok get report/task/download/ -p task_id="<TASK_ID>"
```

`task_id` comes from the first response. Poll the second command until `status` is `SUCCESS` (other values: `QUEUING`, `PROCESSING`, `FAILED`, `CANCELED`). The download format is not documented on the pages read: save the output to a file and inspect it before parsing.


## Search Console baseline

Organic clicks on the same landing pages show what paid traffic adds: match `ad_group_ad.ad.final_urls` to `page` by path, and never add organic and paid clicks. Command: `gsc query --site SITE --start DATE --end DATE [--dimensions query,page] [--row-limit N] [--type web] [--data-state final|all] [--filter DIM:OP:VALUE]`. `--site` defaults to `GSC_SITE_URL`; the toolkit pages through up to `--row-limit` rows.

```bash
python3 ads/tools/ads.py gsc sites
python3 ads/tools/ads.py gsc query --site sc-domain:example.com --start 2026-10-15 --end 2026-11-10 --dimensions page --type web --row-limit 1000 --out ads/reports/raw/gsc-pages.json
python3 ads/tools/ads.py gsc query --site sc-domain:example.com --start 2026-10-15 --end 2026-11-10 --dimensions page,query --type web --filter page:contains:/shoes/ --row-limit 5000 --format csv --out ads/reports/raw/gsc-shoes.csv
```

| Fact | Consequence |
|---|---|
| Data arrives 2-3 days late, and days are Pacific Time (California) | End the window at today minus 3 days and use windows of 7 days or more, which also absorbs the one-day offset against other time zones. `--data-state all` adds the fresh, not yet final days: label them as preliminary. |
| Rows are sorted by clicks; the API exposes at most 50,000 rows per day per search type; 25,000 rows per call | Add `--filter` or shorten the window for large sites. |
| `--filter` operators: `contains`, `equals`, `notContains`, `notEquals`, `includingRegex`, `excludingRegex`; filters combine with AND only | A brand exclusion is `query:excludingRegex:(?i)(brandname)`; it only approximates the brand filter of the web interface. |

## Comparing platforms fairly

Read account currency and time zone once per account:

```bash
Q='SELECT customer.id, customer.currency_code, customer.time_zone, customer.status FROM customer'
python3 ads/tools/ads.py google search --query "$Q"
python3 ads/tools/ads.py meta get '{account}' -p fields=currency,timezone_name,account_status
python3 ads/tools/ads.py tiktok get advertiser/info/ -p 'advertiser_ids=["{advertiser}"]'
```

| Trap | Google Ads | Meta | TikTok | Rule |
|---|---|---|---|---|
| Time zone and currency | `customer.time_zone`, `customer.currency_code` | `timezone_name`, `currency` | ad-account time zone; `currency` fixed per account | Same explicit dates everywhere, windows of 7 days or more; never add spend across currencies without a stated rate. |
| Conversion definition | Only actions with `include_in_conversions_metric=true` | One `action_type` out of `actions` | `conversion` counts the optimization event of the ad group (confirm it in Ads Manager) | List what each platform counts; compare like events (purchase to purchase). |
| Attribution window | not documented on the pages read: take it from the account settings and state it in the report | Set per request; `7d_view` and `28d_view` return nothing since 2026-01-12 | not documented on the pages read: take it from the account settings and state it in the report | Meta: pass the window explicitly. Never compare Meta `1d_click` with a platform of unknown window; label the gap. |
| Conversion dated by click or by conversion | not documented on the pages read: take it from the account settings and state it in the report | `action_report_time`: `impression`, `conversion`, `mixed`, `lifetime` | not documented on the pages read: take it from the account settings and state it in the report | A short window shifts numbers between platforms; compare totals over 28 or more days when possible. |
| View-through | not documented on the pages read: take it from the account settings and state it in the report | `1d_view` counts views; `1d_ev` counts engaged views | `vta_conversion` (view) and `cta_conversion` (click) exist | Report click-only numbers beside the total. |
| Minimum data before a judgement (learning phase) | the learning volumes of the media-plan reference apply | the same; a move to Advantage+ resets learning | the same | Do not rank campaigns or ads edited inside the window; state the data volume next to every verdict. |

## Diagnosis pulls

Read-only pulls for the questions the report raises. Review states of single ads are read with the calls in the launch references of the `launch-campaign` skill (`../../launch-campaign/references/google-ads.md`, `meta-ads.md`, `tiktok-ads.md`).

Is a Google Search campaign limited by its budget, or by its rank?

```bash
Q='SELECT campaign.name, campaign_budget.amount_micros, metrics.cost_micros, metrics.search_impression_share, metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share FROM campaign WHERE segments.date BETWEEN "2026-12-01" AND "2026-12-07" AND campaign.advertising_channel_type = "SEARCH" AND campaign.status = "ENABLED"'
python3 ads/tools/ads.py google search --query "$Q" --out ads/reports/raw/google-impression-share.json
```

A large share lost to budget with a cost per result under target means the budget caps a campaign that works; a large share lost to rank points at bids, ads or landing pages instead. Daily spend against the cap is `cost_micros` per `segments.date` beside `campaign_budget.amount_micros`.

Is a Meta or TikTok creative wearing out? Pull four weeks in weekly rows and watch frequency rise while the click rate falls:

```bash
python3 ads/tools/ads.py meta insights --level ad --preset last_28d --fields ad_name,impressions,reach,frequency,clicks,ctr,spend -p time_increment=7 --out ads/reports/raw/meta-fatigue.json
python3 ads/tools/ads.py tiktok report --level AUCTION_AD --start 2026-11-10 --end 2026-12-07 --dimensions ad_id,stat_time_day --metrics ad_name,impressions,reach,frequency,clicks,ctr,spend --out ads/reports/raw/tiktok-fatigue.json
```

## Diagnostic heuristics

Heuristics, not platform guidance. There is no trustworthy general benchmark for ad CTR, CPC, CPA or ROAS: do not invent one; compare with the account's own earlier period. Quota: Google Basic access allows 15,000 operations a day (Explorer 2,880); each `search` request is one.

| Signal | Rule | Source of the rule |
|---|---|---|
| Wasted spend | Search term with `cost_micros > 0` and `conversions = 0` over the window | Structural, from the query above |
| Organic page worth paid support | `impressions >= 500`, `position` 5 to 20, `ctr < 0.02` | planning heuristic, not platform guidance |
| Defend organic, bid lower; weak mobile page | `position <= 3` and `ctr >= 0.10`; mobile `ctr` below desktop `ctr` on one page | Same |

Every verdict states the window, the attribution window, the conversion event and the currency next to the number.
