# Budgets, tracking and compliance: pre-launch checks

What a media plan must verify before anything is launched on Google Ads, Meta or TikTok: budget floors, learning-phase arithmetic, objective and goal pairing, tracking, regional compliance and review times. Facts checked 2026-11-14; anything marked unverified is a gap to resolve at run time, not a number to assume.

## Contents

- Minimum budgets
- Learning phase and budget arithmetic
- Objectives and optimisation goals
- Tracking prerequisites
- Regional compliance gate
- Review times
- Pre-launch gate

## Minimum budgets

Currency caveat: every floor below is quoted in USD. Official pages publish no per-currency table for EUR, GBP or other currencies on Meta and TikTok, so read the account's real minimum at run time and compare the planned budget with it before launch.

| Platform | Level | Minimum (USD) | Notes |
|---|---|---|---|
| Google, Demand Gen | campaign, daily | 5 (local equivalent) | since 2026-04-01; below it the API returns `BUDGET_BELOW_PER_DAY_MINIMUM`; existing campaigns are unaffected until budget or duration is edited |
| Google, Search, Performance Max | campaign, daily | unverified | no published floor in the notes; the API validates at creation |
| Meta | ad set, daily, impressions billing | 0.50 | doubled to 1.00 for ad accounts in the countries listed below |
| Meta | ad set, daily, clicks, likes, video views | 2.50 | doubled to 5.00 in those countries |
| Meta | ad set, daily, low-frequency actions (app installs, offer claims) | 40 | same in every country; not doubled |
| Meta | campaign spend cap | about 100 equivalent | an error 2446307 means the cap is below the minimum |
| Meta | bid cap | impressions: at least the bid amount; clicks and actions: 5 times the bid amount | |
| TikTok | campaign, daily and total | above 50 (sources disagree: the guide text says 20, the per-currency table says 50; use 50) | 10 for TikTok Shop store campaigns |
| TikTok | ad group, daily | above 20 | 10 for store and showcase; lifetime budget = 20 x scheduled days |

Meta doubled-minimum countries: Australia, Austria, Belgium, Canada, Denmark, Finland, France, Germany, Greece, Hong Kong, Israel, Italy, Japan, Netherlands, New Zealand, Norway, Singapore, South Korea, Spain, Sweden, Switzerland, Taiwan, United Kingdom, United States.

Meta marketing guidance quotes higher figures (USD 5 - 10 for messaging goals, 3 - 5 for app installs, 7 or more days of schedule); treat them as guidance, not as the validation rule (sources disagree).

TikTok budget rules: the campaign budget is not lower than the ad group budget; the budget type cannot change after publishing; currency is fixed per ad account; the allowed range is the base range multiplied by a per-currency ratio (1 for USD, EUR, GBP, CAD, AUD, SGD, CHF, BRL, ILS, MYR, SAR; 10 for HKD, CNY, MXN, TRY, THB, CZK, EGP, UAH; 100 for JPY, RUB, INR; 4 for PLN; 50 for PHP; 10,000 for IDR and VND).

Read the real minimum at run time:

```bash
python3 ads/tools/ads.py google search --query "SELECT customer.currency_code FROM customer"
python3 ads/tools/ads.py google search --query "SELECT currency_constant.code, currency_constant.demand_gen_info.minimum_budget_per_day_micros FROM currency_constant WHERE currency_constant.code = 'EUR'"
python3 ads/tools/ads.py meta get "{account}/minimum_budgets"
python3 ads/tools/ads.py tiktok get advertiser/info/
```

The Meta response field names are unverified; read the answer rather than assuming them. A dry run (`launch plan`) asks the platform to validate budgets before any spend.

## Learning phase and budget arithmetic

| Platform | Rule | Source of the number |
|---|---|---|
| Meta | an ad set leaves learning after about 50 optimisation events in the week after its last significant edit; "Learning limited" appears when about 50 events are unlikely; Shops ads need 17 website purchases plus 5 on Meta | https://business.facebook.com/business/help/112167992830700/ |
| Meta | a significant edit resets learning: targeting, creative, optimisation goal, billing event, large budget change | same |
| Meta | a daily budget can overspend by up to 75 percent on one day; the weekly cap is 7 times the daily budget | https://business.facebook.com/business/help/190490051321426/ |
| Meta | ad set budget changes: 4 per hour per ad set | API rate rule |
| TikTok | 50 conversions is the key indicator, about 7 days; another page says volatility declines after about 25 results or 7 days (sources disagree: plan for 50) | https://ads.tiktok.com/resources/help/article/learning-phase |
| TikTok | avoid pausing and big edits during learning; reset triggers unverified | same |
| Google, Demand Gen | about 50 conversions, allow about 1 month; budget increases at most 15 percent per change; bid adjustments plus or minus 15 percent | https://support.google.com/google-ads/answer/16797388 |
| Google, Target CPA | evaluate over 30 days with 30 or more conversions; be ready to spend up to 2 times the daily budget on a day | https://support.google.com/google-ads/answer/6268632 |
| Google, Target ROAS | Search and Shopping: 15 conversions in 30 days; Demand Gen: 50 conversions in 35 days (10 in the last 7) or 100 account-wide | https://support.google.com/google-ads/answer/6268637 |
| Google, Performance Max | run at least 6 weeks; after a major change allow 1 - 2 weeks or one conversion cycle | https://support.google.com/google-ads/answer/11385582 |

Budget formulas (the Meta one is a rule of thumb derived from the 50-event rule, not an official formula):

| Platform | Minimum sensible budget | Example at target CPA 20 |
|---|---|---|
| Meta, per ad set | daily budget = target CPA x 50 / 7 | about 143 per day |
| TikTok, per ad group | daily budget = target CPA x 10 | 200 per day |
| TikTok, Smart+ campaign | daily campaign budget 30 x historical CPA, never below 10 x | 600 per day, floor 200 |
| Google, Demand Gen | daily budget = 10 x target CPA at minimum (15 x recommended in the API guide) | 200 per day, 300 recommended |
| Google, YouTube | daily budget 10 x target CPA (weak source, unverified on the full page) | 200 per day |

Planning rules:

1. If the formula result is above the budget, change the goal to a higher-volume event (click, landing page view, add to cart), or cut the number of ad sets and ad groups, or lengthen the test; do not launch a split that cannot reach the event count.
2. Multiply ad sets (or ad groups) by the per-unit budget; the sum must fit the total plan.
3. Schedule at least 7 days for Meta and TikTok, about 30 days for Google Demand Gen and Target CPA, 6 weeks for Performance Max.
4. Raise a running budget in steps of at most 15 percent (Google Demand Gen rule; apply as a safe default elsewhere).
5. Count a Meta budget edit as a learning risk when it is large; count targeting, creative and goal edits as resets.

## Objectives and optimisation goals

Pair the objective with a goal that matches the tracked event. The pairings below follow the API enums; Meta's official objective-to-goal matrix did not render on the fetched pages (unverified), so confirm a combination with a `validate_only` dry run.

| Platform | Objective | Typical optimisation goal or bidding | Needs |
|---|---|---|---|
| Meta | `OUTCOME_TRAFFIC` | `LINK_CLICKS`, `LANDING_PAGE_VIEWS` | landing URL |
| Meta | `OUTCOME_SALES` | `OFFSITE_CONVERSIONS`, `VALUE` | pixel or dataset, `custom_event_type` such as `PURCHASE`, `conversion_domain` |
| Meta | `OUTCOME_LEADS` | `LEAD_GENERATION`, `QUALITY_LEAD` | lead form or conversion event |
| Meta | `OUTCOME_ENGAGEMENT` | `POST_ENGAGEMENT`, `THRUPLAY`, `CONVERSATIONS` | page or message destination |
| Meta | `OUTCOME_AWARENESS` | `REACH`, `IMPRESSIONS`, `AD_RECALL_LIFT` | - |
| Meta | `OUTCOME_APP_PROMOTION` | `APP_INSTALLS` | app store link; low-frequency minimum 40 |
| TikTok | `TRAFFIC` | `CLICK`, `PAGE_VISIT` (billing CPC); `TRAFFIC_LANDING_PAGE_VIEW` (OCPM) | landing URL |
| TikTok | `WEB_CONVERSIONS` (Sales, website destination) | `CONVERT`, `VALUE` (OCPM) | pixel plus optimisation event |
| TikTok | `LEAD_GENERATION` | `LEAD_GENERATION` (OCPM) | form or destination; not for under-18 audiences |
| TikTok | `REACH` | `REACH`, `SHOW` (CPM) | - |
| TikTok | `VIDEO_VIEWS` | `ENGAGED_VIEW`, `ENGAGED_VIEW_FIFTEEN` (CPV) | - |
| TikTok | `APP_PROMOTION` | `INSTALL`, `IN_APP_EVENT` (OCPM) | app tracking |
| Google, Search | - | maximise conversions (optional target CPA), maximise conversion value (optional target ROAS), maximise clicks, target impression share, manual CPC | conversion tracking for value or CPA goals |
| Google, Performance Max | - | maximise conversions or maximise conversion value only | conversion tracking on the account |
| Google, Demand Gen | - | maximise clicks, target CPA, maximise conversions, target ROAS | conversion goals set up |

Meta objectives are six: Sales, Leads, Engagement, Traffic, Awareness, App promotion. TikTok objective menu: Reach, Consideration (Traffic, Video views, Community interaction), App promotion, Lead generation, Sales (website, TikTok Shop), Smart+ campaigns. `BRAND_CONSIDERATION` cannot be created through the API.

## Tracking prerequisites

### Google Ads

| Check | Value |
|---|---|
| Google tag | on every page; auto-tagging on; status can take up to 48 hours to show |
| Tag manager | enable the conversion linker; never run the Google tag and the tag manager together |
| Enhanced conversions | optional; SHA-256 hashed first-party email, phone, name, address |
| Conversion goals | required for Performance Max and Demand Gen; value and CPA goals need conversion history (see thresholds above) |
| Consent mode v2 (EEA, UK, Switzerland) | pass `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization` through a Google-certified consent management platform; blocking tags before interaction means Google cannot verify consent; advanced mode sends cookieless pings that enable modelling |
| Customer Match in the EEA | upload only with `ad_user_data` and `ad_personalization` granted; eligibility needs a good account history, 90 days, over USD 50,000 lifetime spend, no sensitive categories, no under-13s |
| TCF requirement | unverified |

### Meta

| Check | Value |
|---|---|
| Pixel or dataset | a dataset exists on the ad account and has recent events (`last_fired_time`); sales ad sets carry `promoted_object` with the pixel id and the event type |
| Conversions API | server events link to the dataset; Meta advises the pixel alongside the Conversions API for website events (a recommendation, not a mandate; wording only partly verified) |
| Event quality | check Event Match Quality, key coverage and freshness of the dataset before spending |
| Aggregated Event Measurement | no event configuration or per-domain event prioritisation needed; domain verification is no longer required for event configuration, but may still be needed for other reasons (unverified) |
| Insights | need tracking through the pixel or the Conversions API |

```bash
python3 ads/tools/ads.py meta get "{account}/adspixels" -p fields=id,name,last_fired_time,is_unavailable
```

### TikTok

| Check | Value |
|---|---|
| Pixel | exists on the advertiser (`pixel/list/`) and contains the optimisation event; the ad group carries `pixel_id` and `optimization_event`; the ad-level pixel id must equal the ad group's |
| Events API | advised together with the pixel; web events need the pixel code as source id, the event name, a Unix time, the page; send an `event_id` so a pixel event and a server event deduplicate; app source is allow-list only |
| Consent signals | no TikTok consent requirement found in the notes (unverified) |
| Business Center prerequisites, dedup details | unverified |

```bash
python3 ads/tools/ads.py tiktok get pixel/list/
```

## Regional compliance gate

Branch on the target geography. Each row is a blocking check.

| Topic | Rule | Platforms |
|---|---|---|
| EU advertiser and payer | ads targeting the EU, associated territories or worldwide need the advertiser (renamed from "beneficiary" in March 2026) and the payer legal names; the ad cannot be published without them; kept in the Ad Library 1 year after the last impression | Meta |
| EU political and social-issue ads | not allowed; Meta stopped delivering political, electoral and social-issue ads in the EU from 2025-10-06 (boosted posts included); Google bars political advertising as defined by Regulation (EU) 2024/900 and asks the advertiser to confirm the EU-political-ads question (answer "yes" means the campaigns cannot run in the EU); set the Google campaign field `contains_eu_political_advertising` explicitly; TikTok bans paid political advertising | all three |
| Consent | EEA, UK and Switzerland traffic needs valid consent and consent mode v2 signals for Google; keep records, allow withdrawal | Google |
| Meta special ad categories | financial products and services (required for US advertisers and audiences since 2025-01-21), employment, housing, social issues, elections, politics: age, gender, ZIP, exclusions and lookalikes are limited or removed in the US, Canada and some European countries | Meta |
| Google restricted targeting | no age, gender or ZIP targeting for housing, employment, consumer finance ads in the US and Canada; no personalised ads for under-18s; sensitive interest categories are not targetable | Google |
| Finance | Google: personal loans repayable in 61 or more days with APR disclosure, US personal loans at 36 percent APR and above banned, financial-services verification in the EEA; TikTok: 18+, licence and fee disclosure, payday loans, binary options, get-rich-quick, MLM and ICOs not allowed per market | Google, TikTok |
| Health, weight loss | Meta: 18+, no cure claims, no inferiority statements; TikTok: 18+, no "treat, cure, heal, prevent"; Google: certification for prescription-drug services | all three |
| Alcohol, gambling | allowed only in listed countries with certification or licence, no minors; TikTok bans all online-gambling ads in Brazil (2026-10) | all three |
| Minors on TikTok | no personalised ads to ages 13 - 17 in the EEA, UK, Switzerland and Brazil; audiences under 18 get no Lead Generation, no TikTok Shop sales and no detailed targeting | TikTok |
| Music | businesses must use the Commercial Music Library for video ads, branded content and carousels (or an uploaded MP3 up to 10 MB for carousels); a missing authorisation shows as the status `AD_STATUS_MUSIC_AUTHORIZATION_MISSING`; Meta Reels ads exclude licensed music | TikTok, Meta |
| AI-generated content | TikTok: set the AI-generated toggle on non-Spark ads (locked after submit), undisclosed AI content is rejected or restricted; Google: labels where EU, India or New York rules apply (from July 2026); Meta: "AI info" label on images heavily edited with Meta generative AI | all three |
| Advertiser identity | Google may require advertiser verification (ID or D-U-N-S, payments profile name must match; up to 5 business days per task); Meta may ask for advertiser verification | Google, Meta |
| Business name | Google business name must match the domain or the verified legal name | Google |

Unverified, ask the client: US state privacy laws (Google restricted data processing, Meta limited data use), UK rules beyond consent and minors, TikTok EU ad-repository duties.

## Review times

| Platform | Time | Re-review and notes |
|---|---|---|
| Google | most ads within 1 business day; check the status if still pending after 2 business days | an edit triggers 24 - 48 hours; a warning is sent at least 7 days before an editorial suspension |
| Meta | most ads within 24 hours, sometimes longer | edits to targeting, creative, optimisation goal or billing event trigger review; bid, budget and schedule changes do not |
| TikTok | most ads within 24 hours | edits trigger review again; TopView assets are pre-approved within 2 days; ad groups can be appealed |

Plan to submit at least 2 business days before the start date; 3 or more for TopView or a restricted category. After enabling, poll the review state (`launch status --file PLAN`) before telling the client the campaign is live.

## Pre-launch gate

Walk through these with the user in order; stop at the first failure.

1. Geography and category: list the target countries and the product category; apply the regional compliance table; block EU geos for any political or social-issue brief.
2. Age-restricted or special category: confirm the age target is 18 or older for health, weight loss, finance, alcohol and gambling; set the Meta special ad category when it applies.
3. Budget floors: compare every daily budget with the floor of its platform and level in the account currency, read at run time; reject any value at or below the TikTok USD floor (50 campaign, 20 ad group) or below the Google Demand Gen minimum.
4. Learning arithmetic: per ad set or ad group, check that budget reaches the event count within the schedule (Meta target CPA x 50 / 7, TikTok target CPA x 10, Google Demand Gen 10 - 15 x target CPA); otherwise change the goal, the structure or the length.
5. Objective and goal: confirm the optimisation goal matches the tracked event and the bidding strategy is allowed for the campaign type.
6. Tracking: confirm the tag, dataset or pixel exists and fired recently; confirm the optimisation event is present; confirm server events and deduplication where used.
7. Consent: for EEA, UK and Switzerland traffic confirm consent mode v2 signals (Google) and a consent banner on the landing page.
8. EU fields: for any EU target confirm the Meta advertiser and payer names, the Google EU-political-ads answer and the `contains_eu_political_advertising` value.
9. Identity: confirm advertiser verification status, business name match and a verified payment method.
10. Copy and creative: confirm the copy pack and files against the limits and specs references; confirm AI-content disclosures and TikTok music source.
11. Landing page: confirm it loads without errors for the ad platform's crawler, matches the display domain, and carries the privacy policy for lead forms.
12. Dry run: run `launch plan`, read the eight blocks, and get explicit approval before `launch apply`; everything is created paused.
13. After approval: apply, check the review state, activate only after the user confirms the schedule and the spend ceiling in `ads/config.json`.
