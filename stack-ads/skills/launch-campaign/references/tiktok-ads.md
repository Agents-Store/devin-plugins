# TikTok Ads: launch reference

How to create TikTok campaigns with real money: which route and flow to pick, the rules that make a request valid, copy-ready plan files and look-ups, and the errors to expect. Facts were read from the official TikTok API for Business documentation on 2026-11-14. No body here was run against a live ad account, and TikTok offers no validation mode, so `launch apply` into disabled objects is the test; all calls use `python3 ads/tools/ads.py` as described in the toolkit reference of the `init-project` skill (`../../init-project/references/toolkit.md`).

## Contents

- 1. Route and flow
- 2. Before you build the plan
- 3. Manual flow: traffic plan
- 4. Upgraded Smart+ flow: website sales
- 5. Look-ups
- 6. Dry run, apply, verify, activate
- 7. MCP route
- 8. Limits, errors, deprecations
- 9. Official documentation

## 1. Route and flow

Route:

| | Official `tiktok-ads` MCP server | Toolkit direct API (`tiktok ...`, `launch ...`) |
|---|---|---|
| Sign-in | OAuth in the client, no developer app | developer app, then a long-term token in `TIKTOK_ACCESS_TOKEN` (`tiktok oauth-exchange`) |
| Covers | Smart+, GMV Max, uploads, reporting (about 400 tools) | any endpoint through `tiktok get` and `tiktok post` |
| Safety net | none: no dry run, no ledger, no budget ceiling | guard rails, ledger, rollback |

Use the toolkit whenever its keys exist: it is the only route with a dry run on record, a ledger and budget ceilings. Use the MCP server only while there is no developer app, and then apply the money rules by hand (section 7).

Flow, by campaign objective:

| Objective | Flow | Create with | Note |
|---|---|---|---|
| Traffic, Reach, Video views, Engagement | manual | `campaign/create/`, `adgroup/create/`, `ad/create/` | documented, no sunset notice found |
| Sales (website), App promotion, Lead generation | Upgraded Smart+ | `smart_plus/campaign/create/`, `smart_plus/adgroup/create/`, `smart_plus/ad/create/` | manual creation of these objectives ends: the guide says after 2026-12-31, the site banner says from 2027-01-01. Treat 2026-12-31 as the last day and start on Smart+ now |
| TikTok Shop sales | GMV Max | `campaign/gmv_max/create/` | needs a connected shop, section 4 |

Never use `campaign/spc/create/` (legacy Smart+, closed since 2026-03-31) or `ad/aco/create/` (ACO, no longer supported).

## 2. Before you build the plan

| Check | Rule |
|---|---|
| API version | The toolkit calls the version stored in `ads/config.json` under `api.tiktok`; confirm it reads `v1.3`. Version 2.0 documents only OAuth tokens, reporting and Symphony, so a create call on 2.0 fails |
| Trailing slash | Every path ends with `/` (`campaign/create/`). A missing slash or a wrong HTTP method gives HTTP 404; the toolkit adds the slash when it is missing |
| Success | HTTP 200 can still carry `code` other than 0. The toolkit turns a non-zero `code` into an error (exit code 1) and prints `message`, which names the bad field, and `request_id` |
| Account | `TIKTOK_ADVERTISER_ID` is added to every call, so leave `advertiser_id` out of a body: a body that names another advertiser is refused. Write `{advertiser}` where an id is needed inside a value. Budgets are in the ad account currency, fixed per account: `tiktok get advertiser/info/ -p 'advertiser_ids=["{advertiser}"]'` returns `currency`, `timezone`, `status` |
| Budget minimums | USD terms: ad group daily above 20, campaign minimum 50 (the guide says 20, the currency table says 50: use 50). TikTok Shop store campaigns 10. Multiply by the currency ratio: JPY, RUB, INR 100; IDR, VND 10000; CNY, HKD, MXN, TRY, THB, CZK, EGP, UAH 10; PLN 4; PHP 50; others 1. Budgets must be whole multiples of the currency precision |
| Budget ceiling | The toolkit refuses a daily budget above `guardrails.max_daily_budget` in `ads/config.json`. Raise it in the file on purpose, never in the plan |
| Idempotency | `request_id` (64-bit integer string) on create calls makes a repeat within 10 seconds safe and allows duplicate names. Required on every Smart+ create. Names: up to 512 characters, no emoji; uploaded file names are unique per advertiser (error 40911) |

Identity (who the ad appears to be posted by):

| Identity type | Use |
|---|---|
| `TT_USER` | TikTok Business Account linked to your TikTok for Business account. Spark Ads. Check `can_push_video` before pushing a new video |
| `BC_AUTH_TT` | TikTok account added to your Business Center (needs `identity_authorized_bc_id`). Spark Ads |
| `AUTH_CODE` | created when you apply a Spark Ads authorization code; the ad then uses `tiktok_item_id` of an existing post |
| `CUSTOMIZED_USER` | virtual profile. Closed for TikTok placements: since 2026-01-15 no ad account can create non-Spark ads with a custom identity there. Only Pangle-only and Global-App-Bundle-only placements stay open (viability unverified, do not rely on it) |

A freshly generated video has no TikTok post, so it cannot be a Spark post. Choose in this order:

1. Push it from a linked account: `identity_type` `TT_USER` or `BC_AUTH_TT` with the uploaded `video_id`. The official pages confirm this push for Smart+ only; for the manual flow it is unverified, and the sample plan of section 3 uses it. If `ad/create/` returns code 40002, use option 2.
2. Publish the video on the TikTok account, have the account holder create an authorization code (post menu, Ad settings, Ad authorization, duration, copy), apply it, then create the ad with `AUTH_CODE` and `tiktok_item_id`.

No linked account yet (the identity list holds no `TT_USER` and no `BC_AUTH_TT` entry): link one before you plan an ad for TikTok placement. On the MCP route `tiktok_identity_connect_ui` (advertiser id and Business Center id) returns an authorization address in `bc_auth_qr_code`; the owner of the TikTok account opens it on the phone that runs the TikTok app, or scans it as a QR code, and approves. The account then shows among the Business Center assets (`bc_asset_admin_get`, `asset_type` `TT_ACCOUNT`) and is still missing from the identity list until it is linked to the ad account: `bc_asset_advertiser_assign` with `bc_id`, `advertiser_id`, `asset_id` and `asset_type` `TT_ACCOUNT`, a write, so show it to the user first. After that `identity_get` with `identity_type` `BC_AUTH_TT` and `identity_authorized_bc_id` returns the account with `can_push_video` and `can_pull_video`.

List identities with `tiktok get identity/get/ -p identity_type=TT_USER` (add `identity_authorized_bc_id` for `BC_AUTH_TT`). Apply a Spark Ads code (replace `+` with `%2B`) with `tiktok post tt_video/authorize/ --data @ads/launch/spark-code.json`, the file holding `{"auth_code": "<SPARK_AUTH_CODE>"}`. Without `--yes` the command only prints what it would send: show that to the user, and add `--yes` after they agree, because it binds the post to the ad account for the duration of the code.

Since 2026-01-27 `dark_post_status` defaults to ON (the post is shown through ads only). An identity with `ads_only_mode` true cannot switch it off. Accounts with `is_gpppa` true (government, politician) cannot be used for Spark Ads.

Pixel (required when the goal is `CONVERT` or `VALUE`, not allowed otherwise): `tiktok get pixel/list/` lists `pixel_id`, `pixel_code`, `pixel_name` and the pixel events. Take `pixel_id` for the ad group (`TIKTOK_PIXEL_ID` holds it) and confirm the `optimization_event` you want (for example `SHOPPING`, `COMPLETE_PAYMENT`) is among the events. An ad-level `tracking_pixel_id`, when set, must equal the ad group `pixel_id`. No pixel: stop and ask the user to create one in Ads Manager (Tools, Events, Data sources); never launch a conversion goal without one.

## 3. Manual flow: traffic plan

Save as `ads/launch/tiktok-traffic.json`. Replace every `<...>` value and the texts. The campaign and ad group bodies below were created disabled and deleted on a live ad account on 2026-11-22; the upload and ad steps were not. Campaign, ad group and ad carry `operation_status` `DISABLE`; the toolkit refuses anything else. `advertiser_id` is added automatically. Paths in `file` are relative to the project root.

```json
{
  "name": "tiktok-traffic-demo",
  "platform": "tiktok",
  "objective": "Traffic to the landing page",
  "budget": {"daily": 50, "currency": "USD"},
  "landing_url": "https://example.com/",
  "steps": [
    {"id": "video", "do": "tiktok.upload_video",
     "with": {"file": "ads/creatives/video-9x16.mp4", "name": "demo-video-001"}},
    {"id": "cover", "do": "tiktok.upload_image",
     "with": {"file": "ads/creatives/cover-9x16.jpg"}},
    {"id": "campaign", "do": "tiktok.post",
     "with": {"path": "campaign/create/", "body": {
       "objective_type": "TRAFFIC",
       "campaign_name": "Demo traffic",
       "budget_mode": "BUDGET_MODE_INFINITE",
       "operation_status": "DISABLE"}}},
    {"id": "adgroup", "do": "tiktok.post",
     "with": {"path": "adgroup/create/", "body": {
       "campaign_id": "{{campaign.campaign_id}}",
       "adgroup_name": "Demo ad group",
       "promotion_type": "WEBSITE",
       "placement_type": "PLACEMENT_TYPE_NORMAL",
       "placements": ["PLACEMENT_TIKTOK"],
       "location_ids": ["<LOCATION_ID>"],
       "gender": "GENDER_UNLIMITED",
       "budget_mode": "BUDGET_MODE_DAY",
       "budget": 50,
       "schedule_type": "SCHEDULE_START_END",
       "schedule_start_time": "2026-12-01 00:00:00",
       "schedule_end_time": "2026-12-08 00:00:00",
       "optimization_goal": "CLICK",
       "bid_type": "BID_TYPE_NO_BID",
       "billing_event": "CPC",
       "pacing": "PACING_MODE_SMOOTH",
       "operation_status": "DISABLE"}}},
    {"id": "ad", "do": "tiktok.post",
     "with": {"path": "ad/create/", "body": {
       "adgroup_id": "{{adgroup.adgroup_id}}",
       "creatives": [{
         "ad_name": "Demo ad 1",
         "identity_type": "TT_USER",
         "identity_id": "<IDENTITY_ID>",
         "ad_format": "SINGLE_VIDEO",
         "video_id": "{{video.video_id}}",
         "image_ids": ["{{cover.image_id}}"],
         "ad_text": "Your headline, up to 100 characters",
         "call_to_action": "LEARN_MORE",
         "landing_page_url": "https://example.com/",
         "operation_status": "DISABLE"}]}}}
  ]
}
```

The ad step pushes an uploaded video with a `TT_USER` identity, which is unverified for the manual flow (section 2, option 1): if the step fails with code 40002, switch that step to the authorization-code route.

Fields used:

| Field | Level | Required | Allowed values | Rule |
|---|---|---|---|---|
| `objective_type` | campaign | yes | `TRAFFIC`, `REACH`, `VIDEO_VIEWS`, `ENGAGEMENT` for this flow | `BRAND_CONSIDERATION` cannot be created; `APP_INSTALL`, `CONVERSIONS`, `CATALOG_SALES`, `SHOP_PURCHASES` are deprecated |
| `campaign_name` | campaign | yes | text | up to 512 characters, no emoji |
| `budget_mode` | campaign | yes | `BUDGET_MODE_DAY`, `BUDGET_MODE_TOTAL`, `BUDGET_MODE_INFINITE` | `budget` is required for DAY and TOTAL. Campaign DAY forces ad group DAY; TOTAL and INFINITE allow any ad group mode. `BUDGET_MODE_TOTAL` is a lifetime budget: the toolkit refuses it unless the user has set `guardrails.max_total_budget`. With `BUDGET_MODE_INFINITE` on the campaign, every ad group of the plan must carry a daily or total budget: a campaign that nothing limits is refused. An ad group hangs under a campaign of the same plan and an ad under an ad group of the same plan: adding one to a campaign that already exists is a single `tiktok post` command, shown to the user first |
| `budget_optimize_on` | campaign | no | true or false | true (CBO): ad group budget and pacing are ignored and `bid_type` becomes required. Leave unset here |
| `operation_status` | all three | yes (toolkit) | `DISABLE`, `ENABLE` | the toolkit accepts only `DISABLE` |
| `promotion_type` | ad group | yes, except Reach, Video views, Engagement | `WEBSITE`, `APP_ANDROID`, `APP_IOS`, `LEAD_GENERATION`, `TIKTOK_SHOP` | traffic to a site is `WEBSITE` |
| `placement_type`, `placements` | ad group | `placements` required for NORMAL | `PLACEMENT_TYPE_NORMAL` or `PLACEMENT_TYPE_AUTOMATIC`; `PLACEMENT_TIKTOK`, `PLACEMENT_PANGLE`, `PLACEMENT_GLOBAL_APP_BUNDLE` | immutable after creation |
| `location_ids` | ad group | yes (or `zipcode_ids`) | ids from section 5 | up to 3000, no overlapping places |
| `gender`, `age_groups`, `languages` | ad group | no | `GENDER_FEMALE`, `GENDER_MALE`, `GENDER_UNLIMITED`; `AGE_13_17` ... `AGE_55_100` | 13-17 is restricted in the US, LATAM, EEA, UK, CH, CA (error 40065) |
| `budget_mode`, `budget` | ad group | yes | `BUDGET_MODE_DAY` or `BUDGET_MODE_TOTAL` | DAY: above the minimum in section 2. Match plan `budget.daily`. A later raise must be at least 105% of the current spend |
| `schedule_type` | ad group | yes | `SCHEDULE_START_END`, `SCHEDULE_FROM_NOW` | TOTAL needs START_END. FROM_NOW needs a DAY budget |
| `schedule_start_time`, `schedule_end_time` | ad group | start yes; end for START_END or TOTAL | `YYYY-MM-DD HH:MM:SS`, UTC | start at most 12 hours in the past; end after start |
| `optimization_goal`, `billing_event` | ad group | yes | `CLICK` with `CPC`; `TRAFFIC_LANDING_PAGE_VIEW`, `CONVERT`, `LEAD_GENERATION` with `OCPM`; `REACH`, `SHOW` with `CPM`; `ENGAGED_VIEW` with `CPV` | the pair is fixed, a wrong pair is a 40002. `CONVERT` and `VALUE` need `pixel_id` and `optimization_event` (section 2); no other goal accepts them |
| `bid_type`, `pacing` | ad group | yes | `BID_TYPE_NO_BID` (maximum delivery) or `BID_TYPE_CUSTOM` (cost cap); `PACING_MODE_SMOOTH` or `PACING_MODE_FAST` | CUSTOM needs `bid_price` (CPC, CPM, CPV) or `conversion_bid_price` (OCPM) |
| `identity_type`, `identity_id` | creative | yes | section 2 | use `{{campaign.campaign_id}}` and `{{adgroup.adgroup_id}}` for the parent ids |
| `ad_format` | creative | yes | `SINGLE_VIDEO`, `SINGLE_IMAGE`, `CAROUSEL_ADS`, `LIVE_CONTENT`, `CATALOG_CAROUSEL` | up to 20 `creatives[]` per request, 50 ads per ad group; video needs `video_id` and `image_ids` with one cover of the same aspect ratio; carousel takes 1-35 `image_ids` and a `music_id` |
| `ad_text`, `landing_page_url` | creative | yes | text, URL | text up to 100 characters, no emoji |
| `call_to_action` | creative | yes | `LEARN_MORE`, `SHOP_NOW`, `SIGN_UP`, `ORDER_NOW`, `BOOK_NOW`, `CONTACT_US`, `DOWNLOAD_NOW`, `GET_QUOTE`, `APPLY_NOW`, `WATCH_NOW` and others | `call_to_action_id` (a recommended portfolio) wins when both are sent |
| `operation_status` | creative | yes (toolkit) | `DISABLE` | it sits inside each entry of `creatives[]` (API default `ENABLE`). `ad/create/` makes one ad per entry, so the toolkit refuses an entry without `DISABLE` |

Uploads (steps `video` and `cover`): video up to 500 MB, ratios 9:16, 16:9 or 1:1, `.mp4 .mov .mpeg .avi`; image JPG, JPEG or PNG, up to 50 MB and 3,686,400 pixels (1440 by 2560). Give each upload a name never used before. Right after upload a video may still be processing (40901): wait 30 seconds to 5 minutes and retry the ad step.

## 4. Upgraded Smart+ flow: website sales

Three calls, each answer feeds the next: `campaign_id`, then `adgroup_id`, then `smart_plus_ad_id`. Skeleton of the `steps` part of a plan with `"platform": "tiktok"`; the upload steps are the same as in section 3. Smart+ may still need an allowlisted account: error 40118 means ask the TikTok representative to enable it.

```jsonc
"steps": [
  // ...upload_video "video" and upload_image "cover" as in section 3
  {"id": "campaign", "do": "tiktok.post", "with": {"path": "smart_plus/campaign/create/", "body": {
    "request_id": "<64-BIT-INTEGER-STRING-1>",  // required
    "objective_type": "WEB_CONVERSIONS",        // only APP_PROMOTION, WEB_CONVERSIONS, LEAD_GENERATION
    "sales_destination": "WEBSITE",             // WEBSITE | APP | WEB_AND_APP, required for WEB_CONVERSIONS
    "campaign_name": "Smart+ web sales",
    "budget": 50,                               // CBO is the default: budget_mode defaults to BUDGET_MODE_DYNAMIC_DAILY_BUDGET
    "operation_status": "DISABLE"}}},
  {"id": "adgroup", "do": "tiktok.post", "with": {"path": "smart_plus/adgroup/create/", "body": {
    "request_id": "<64-BIT-INTEGER-STRING-2>",  // required
    "campaign_id": "{{campaign.campaign_id}}",
    "adgroup_name": "Smart+ ad group",
    "promotion_type": "WEBSITE",
    "optimization_goal": "CONVERT",
    "pixel_id": "{pixel}",                      // TIKTOK_PIXEL_ID; needed for CONVERT and VALUE
    "optimization_event": "<PIXEL_EVENT>",      // needed with a pixel; use an event the pixel reports
    "bid_type": "BID_TYPE_CUSTOM",              // or BID_TYPE_NO_BID, then drop conversion_bid_price
    "conversion_bid_price": 10,
    "billing_event": "OCPM",                    // only OCPM or CPC
    "schedule_type": "SCHEDULE_START_END",
    "schedule_start_time": "2026-12-01 00:00:00",
    "schedule_end_time": "2026-12-08 00:00:00",
    "targeting_spec": {"location_ids": ["<LOCATION_ID>"]},   // required; targeting_optimization_mode defaults to AUTOMATIC
    "operation_status": "DISABLE"}}},
  {"id": "ad", "do": "tiktok.post", "with": {"path": "smart_plus/ad/create/", "body": {
    "adgroup_id": "{{adgroup.adgroup_id}}",     // this call takes no request_id
    "ad_name": "",                              // empty = automatic name
    "creative_list": [{"creative_info": {
      "ad_format": "SINGLE_VIDEO",
      "video_info": {"video_id": "{{video.video_id}}"},
      "image_info": [{"web_uri": "{{cover.image_id}}"}],     // web_uri takes the image id of the upload, not a URL
      "identity_type": "TT_USER",                             // a Spark identity sits inside creative_info
      "identity_id": "<IDENTITY_ID>"}}],
    "ad_text_list": [{"ad_text": "Your headline"}],
    "landing_page_url_list": [{"landing_page_url": "https://example.com/lp"}],
    "call_to_action_list": [{"call_to_action": "LEARN_MORE"}],   // shape taken from the official response example
    "operation_status": "DISABLE"}}}                             // top level of the body
]
```

What the official pages confirm and what they leave open (read 2026-11-14):

- Required on the ad group: `request_id`, `promotion_type`, `optimization_goal`, `bid_type`, `billing_event`, `schedule_type`, `schedule_start_time`, `targeting_spec`. `budget` and `budget_mode` belong on the ad group only when the campaign has CBO off (`budget_optimize_on` false).
- `operation_status` (`ENABLE` default, `DISABLE`) is a parameter of all three create calls.
- `ad_text_list` and `landing_page_url_list` are top-level lists beside `creative_list`. A dynamic call to action goes in `ad_configuration.call_to_action_id` instead of `call_to_action_list` (section 5).
- A custom identity (`CUSTOMIZED_USER`) goes into `ad_configuration`, not `creative_info`, and is restricted for non-Spark ads (section 2).
- The official ad group examples cover app installs only. The website-with-pixel body above follows the parameter table and was not run against a live account: `launch apply` is its real test.

Smart+ rules:

| Rule | Value |
|---|---|
| Campaign budget | CBO (default): `BUDGET_MODE_DYNAMIC_DAILY_BUDGET` or `BUDGET_MODE_TOTAL`. Non-CBO (`budget_optimize_on` false): INFINITE (default), DAY or TOTAL. `budget_mode` is immutable. With CBO the ad group takes no budget; goal, event and bid settings must match across ad groups. Without CBO the ad group needs `budget` |
| Ad | 1-50 creatives, 1-5 `ad_text_list` entries. Valid identity and creative combinations: official page in section 9. Spark Pull takes 1-50 `tiktok_item_id` instead of uploaded videos |
| Status values | `operation_status` is `ENABLE`, `DISABLE` or `DELETE`. Status calls, up to 20 ids each: `smart_plus/campaign/status/update/` with `campaign_ids`, `smart_plus/adgroup/status/update/` with `adgroup_ids`, `smart_plus/ad/status/update/` with `smart_plus_ad_ids`. `launch activate` and `launch rollback` use them. Read back with `smart_plus/campaign/get/`, `smart_plus/adgroup/get/`, `smart_plus/ad/get/` |

GMV Max (TikTok Shop): `campaign/gmv_max/create/`. Required: `store_id` (from `gmv_max/store/list/`, must have `is_gmv_max_available`), `store_authorized_bc_id`, an advertiser holding exclusive GMV Max authorization for the shop (`gmv_max/exclusive_authorization/get/` and `.../create/`), `shopping_ads_type` (`PRODUCT` or `LIVE`), `optimization_goal` `VALUE`, `deep_bid_type` `VO_MIN_ROAS`, `roas_bid` (recommended by `gmv_max/bid/recommend/`), daily `budget`, `schedule_type`, `schedule_start_time`. PRODUCT adds `product_specific_type` (`ALL`, or `CUSTOMIZED_PRODUCTS` with up to 400 `item_group_ids`) and `product_video_specific_type` (`AUTO_SELECTION` with `identity_list`, or `CUSTOM_SELECTION` with `item_list`); LIVE requires `identity_list`. Report on it with `gmv_max/report/get/`, not the integrated report. Parameter shapes beyond this list were not read from the official pages: read the GMV Max page first.

GMV Max cannot be created paused: the create call has no `operation_status`, and the campaign is switched on and off afterwards with `campaign/status/update/` (`campaign_ids`). The toolkit therefore refuses this call inside a launch plan, and outside one unless it carries `--activate` as well as `--yes`; it leaves no ledger entry, so `launch rollback` cannot undo it. Prefer the Smart+ flow. Create a GMV Max campaign only when the user asks for exactly that and has agreed, with the daily budget stated in words, that delivery may start at once: run `tiktok post campaign/gmv_max/create/ --data @FILE` without `--yes` first and show what it prints, then add `--yes --activate`, and pause it with the status call if it should wait.

## 5. Look-ups

Read calls through `tiktok get`; `advertiser_id` is added automatically. Pass array parameters as JSON text in one quoted `-p`.

| Need | Call |
|---|---|
| Region ids | `tiktok get tool/region/ -p 'placements=["PLACEMENT_TIKTOK"]' -p objective_type=TRAFFIC` (add `-p level_range=TO_COUNTRY`; `app_promotion_type` for app promotion). The advertiser's own tree: `tiktok get search/region/` |
| Interests, behaviors, hashtags | `tiktok get targeting/search/ -p targeting_type=INTEREST_AND_BEHAVIOR -p search_keywords=<WORD>`; `sub_targeting_types` narrows (`GENERAL_INTEREST`, `PURCHASE_INTENTION`, `VIDEO_INTERACTION`, `CREATOR_INTERACTION`, `HASHTAG_INTERACTION`). It is a GET with query-string parameters; how arrays are encoded there is not documented: pass them as JSON text and read the `message` if it is refused |
| Category lists | `tiktok get tool/interest_category/`, `tiktok get tool/action_category/`, `tiktok get tool/language/` |
| Identities, pixels | `tiktok get identity/get/ -p identity_type=TT_USER`, `tiktok get pixel/list/` |
| Call to action | Safe choice: a fixed value from section 3 (`call_to_action`, or `call_to_action_list` on Smart+). Dynamic: `tiktok get creative/cta/recommend/ -p new_version=true -p objective_type=TRAFFIC -p promotion_type=WEBSITE` returns `recommend_assets` with `asset_ids` and `asset_content`; post them to `creative/portfolio/create/` with `creative_portfolio_type` `CTA` (a write: run `tiktok post` without `--yes`, show it, add `--yes` after the user's yes), and the returned `creative_portfolio_id` is the value for `call_to_action_id` |
| Audience size | `tiktok post ad/audience_size/estimate/ --data @ads/launch/audience-estimate.json`. A POST that only estimates, so it runs without `--yes`. The body mirrors the ad group targeting, for example `{"objective_type": "TRAFFIC", "optimization_goal": "CLICK", "placements": ["PLACEMENT_TIKTOK"], "location_ids": ["<LOCATION_ID>"]}`; the exact required set is unverified |

Result ids go into `location_ids`, `interest_category_ids`, `interest_keyword_ids`, `purchase_intention_keyword_ids`, `action_category_ids` (with `action_scene`: `VIDEO_RELATED`, `CREATOR_RELATED`, `HASHTAG_RELATED`) and `languages`. The `tool/interest_keyword/recommend/` route is gone: use `targeting/search/`.

## 6. Dry run, apply, verify, activate

```bash
python3 ads/tools/ads.py launch plan --file ads/launch/tiktok-traffic.json
python3 ads/tools/ads.py launch apply --file ads/launch/tiktok-traffic.json --yes
python3 ads/tools/ads.py launch status --file ads/launch/tiktok-traffic.json
python3 ads/tools/ads.py tiktok get ad/review_info/ -p 'ad_ids=["<AD_ID>"]'
python3 ads/tools/ads.py launch activate --file ads/launch/tiktok-traffic.json --yes
python3 ads/tools/ads.py launch rollback --file ads/launch/tiktok-traffic.json --remove --yes
```

`launch plan` checks the plan file, the `DISABLE` statuses, the budgets (the sum the steps carry against `budget.daily` and the ceiling) and the step references, and prints the eight blocks. TikTok has no validate-only mode and, after 2026-12-01, no sandbox, so the platform checks nothing at this stage: VALIDATE says `checked by the toolkit only` for a step and `wait` for a step that needs an id of an earlier one. Nothing is uploaded or created. It cannot catch a wrong enum pair, an invalid location, an unknown pixel, a bad file, a missing allowlist or a rejected creative. Close that gap with the look-ups of section 5 before the plan, and treat `launch apply` as the real validation: every object is created disabled and the first failing step stops the run with the platform `code` and `message`. After a failure fix that step in the plan file, run `launch plan` again and show the new output to the user, and after their yes run `launch apply`: the toolkit refuses a plan whose content changed since its last clean dry run, and it skips the steps already in the ledger (`ads/launch/ledger.jsonl`), so nothing is created twice. A failure without a clear answer (a timeout, an interrupted run, a TikTok code of 50000 or above) may have created the object anyway, and `launch apply` then refuses to run again: look for the object in Ads Manager by name (or with `tiktok get campaign/get/`, `adgroup/get/`, `ad/get/`), and tell the user what you found. An orphan is disabled; delete it only with their agreement: put its id and `"operation_status": "DELETE"` into a body file, run `tiktok post campaign/status/update/ --data @FILE` (or the `adgroup` or `ad` route) without `--yes`, show it, and add `--yes` after their yes. Found or not, `--resend` sends the create again, so ask first, then run `launch apply --file ... --yes --resend STEP`. A step that was applied may not be edited in the plan afterwards. To start over, `launch rollback --remove --yes` deletes what was created and clears the plan from the ledger: run it only when the user asks for removal.

Verify before activating:

| Check | How |
|---|---|
| Review | `launch status --file ...` reads objects back; detail with `tiktok get campaign/get/`, `adgroup/get/`, `ad/get/`. `ad/review_info/` returns `review_status`: `ALL_AVAILABLE` (can deliver), `PART_AVAILABLE` (some countries), `UNAVAILABLE`, plus `reject_info`. An ad must be approved before it delivers; the documentation does not say whether an ad created disabled is reviewed before it is enabled, nor how long review takes: poll after activation |
| Secondary statuses | `AD_STATUS_AUDIT`, `AD_STATUS_AUDIT_DENY`, `AD_STATUS_PARTIAL_AUDIT_NO_DELIVERY`, `AD_STATUS_TRANSCODING_FAIL`, `AD_STATUS_BUDGET_EXCEED`, `AD_STATUS_BALANCE_EXCEED`, `AD_STATUS_NOT_START` |
| Rejected | fix the creative. An appeal (`adgroup/appeal/` with `advertiser_id`, `adgroup_id`; Smart+ `smart_plus/ad/appeal/`) contests TikTok's decision in the advertiser's name: propose it to the user and send it only after their yes, without `--yes` first. Causes: language not accepted in the target place, unsupported action such as swipe up, low quality or no clear audio, creative inconsistent with the landing page, unauthorized brand or music. Optional pre-review: `creative/pre_review/task/create/` and `.../get/` (body unverified) |

`launch activate` without `--yes` changes nothing: it prints what would be enabled and the budget of the plan. Show that to the user. With `--yes` it starts spend: run it only after the user's explicit yes to the daily budget stated in words. It enables the campaign, then the ad groups, then the ads. Delivery begins once the ads pass review, so read `ad/review_info/` (Smart+: `smart_plus/ad/review_info/`) afterwards: `ALL_AVAILABLE` or an accepted `PART_AVAILABLE` means it runs; `UNAVAILABLE` means fix the creative, and nothing is spent meanwhile.

Serialisation: never run two writes at once on the same ad group or ad; a parallel create or update fails with an optimistic-locking error (40202, retry). Update one ad at a time (Smart+: one operation per 5 seconds per ad). A budget raise must be at least 105% of the current spend.

Single status changes outside a plan go through `tiktok post` with a small body file. Enabling needs `--activate` as well as `--yes`, and the same explicit approval as `launch activate`: run the command without `--yes` first, show what it prints, state the daily budget in words, and send it only after the user's yes:

| Flow | Path | Id field (1-20 ids) |
|---|---|---|
| manual | `campaign/status/update/`, `adgroup/status/update/`, `ad/status/update/` | `campaign_ids`, `adgroup_ids`, `ad_ids` |
| Smart+ | `smart_plus/campaign/status/update/`, `smart_plus/adgroup/status/update/`, `smart_plus/ad/status/update/` | `campaign_ids`, `adgroup_ids`, `smart_plus_ad_ids` |

`operation_status` is `ENABLE`, `DISABLE` or `DELETE`. An ad group or ad the platform refuses to change is named in `error_list` of a response that still carries `code` 0: read it. `launch activate` and `launch rollback` use these calls, in batches of 20. `launch activate` stops on a non-empty `error_list`; `launch rollback` goes on with the other objects, ends with an error that names the refused ones, and finishes when it is run again.

## 7. MCP route

Server `tiktok-ads` of this plugin. Authorize it from `/mcp` (OAuth with the TikTok for Business account, no developer app). The authorization lasts 30 days, then sign in again; the access token lives 24 hours, the refresh token 30 days. Tokens are scoped to one server path: the flat server (`https://business-api.tiktok.com/open_mcp/tt-ads-mcp-flat`, about 400 tools) and the layered one (`.../tt-ads-mcp-layer`, about 40 core tools, the rest on demand) need separate sign-ins. Prefer the layered one when context is tight. The server also accepts the long-term token of a developer app as `Authorization: Bearer` (no expiry, 10 requests per second on the Basic level); the plugin does not configure that, because a header with an unset variable would stop the server from loading for users who sign in through OAuth. To use it, add the server yourself with that header.

The layered server offers its tools in two ways. About 45 core tools are called by name: the account and identity reads, `report_integrated_get`, and every `smart_plus_*` tool. All the others, the whole manual flow included, run through a dispatcher of three core tools:

| Dispatcher tool | Does |
|---|---|
| `tool_list` | names every other tool by group, with a one-line summary |
| `tool_get` | returns the description and the input schema of the tools you name in `tool_name_list` |
| `tool_execute` | runs one of them: `tool_name` and `params` (put `advertiser_id` inside `params`) |

| Step | Tool of the `tiktok-ads` server | Called |
|---|---|---|
| Identities | `identity_get` | by name |
| Audience size, call to action | `ad_audience_size_estimate`, `creative_cta_recommend_get` | through `tool_execute` |
| Uploads | `file_name_check`, `file_video_ad_upload`, `file_image_ad_upload`, `file_video_suggestcover_get` | through `tool_execute` |
| Manual flow | `campaign_create`, `adgroup_create`, `ad_create` | through `tool_execute` |
| Smart+ | `smart_plus_campaign_create`, `smart_plus_adgroup_create`, `smart_plus_ad_create` | by name |
| GMV Max | `gmv_max_store_list_get`, `campaign_gmv_max_create`, `gmv_max_report_get` | through `tool_execute` |
| Review and status | `ad_review_info_get`, `campaign_status_update`, `adgroup_status_update`, `ad_status_update` | through `tool_execute` |

The bodies are the ones of sections 3 and 4 with `advertiser_id` added. The plugin's hook judges a `tool_execute` call by the tool it names: a read runs, a write asks first. Two tools are named like reads and still change something: `split_test_end_get` stops a split test and `creative_image_edit_get` stores an edited image in the asset library. The hook asks for both.

- Create everything disabled (`operation_status` `DISABLE`, on every entry of `creatives` for a manual ad), as in the plan. The toolkit guard rails do not apply: add up the daily budgets yourself, keep the sum under `guardrails.max_daily_budget`, and write every returned id to a note in `ads/launch/` so the objects can be paused later.
- Before each write, an upload included, show the user the full request (names, budgets, dates, targeting, files) and wait for their yes. One yes covers one call.
- Enable only after a second, explicit yes to the daily budget stated in words. A GMV Max campaign cannot be created disabled: it needs that yes before it is created.
- Limit: 6 requests per second per tool per user. `smart_plus_ad_create`, `smart_plus_ad_update`, `smart_plus_ad_status_update`: one operation per 5 seconds per ad, else a concurrency error.

## 8. Limits and errors

Rate limits per app, QPS / QPM / QPD: Basic (default) 10 / 600 / 864,000; Advanced 20 / 1,200 / 1,728,000; Premium 30 / 1,800 / 2,592,000; Ultimate 50 / 3,000 / 4,320,000. A QPM breach: wait 5 minutes; QPD resets at 00:00 UTC. `ad/create/` is tighter: Basic 5 QPS, 150 QPM, 86,400 QPD. Create objects one at a time; on 40100, 40016 or 40133 back off exponentially. Entity limits: 999 campaigns per ad account, 999 ad groups per campaign, 50 ads per ad group.

Codes (read `code` and `message`; the code overrides the HTTP status):

| Code | Meaning and fix |
|---|---|
| 20001 | partly successful: read `error_list` |
| 40000, 40002, 40065 | invalid or incompatible parameter: fix the field named in `message` (often a wrong goal and billing pair; 40065 is age 13-17 targeting, change `age_groups`) |
| 40001, 40125 | no permission or scope missing: add scopes (Ads Management, Creative Management, Audience Management, Pixel Management, Reporting) to the app, re-authorize |
| 40006, 40010 | wrong API version for the parameters, or wrong domain: version per section 2, base URL `https://business-api.tiktok.com/open_api` |
| 40007, 40300, 40301 | object or advertiser not found: check the ids and `TIKTOK_ADVERTISER_ID` |
| 40011, 40502 | too many ids (20 per status call, 100 per report filter), or maximum ads reached: batch, use another ad group |
| 40016, 40100, 40133 | throttled (app, app, advertiser): back off, lower the rate, raise the tier |
| 40101, 40102, 40104, 40105, 40106, 40113 | token or app problem: send the `Access-Token` header, re-authorize, check app id and secret |
| 40110 | `auth_code` used or expired (valid 1 hour, single use): open the advertiser authorization URL again |
| 40118 | not on the allowlist: ask the TikTok representative |
| 40202 | write conflict: retry, one write at a time. 50000, 50002, 51305 (HTTP 5xx): TikTok-side, wait about 5 minutes, retry, then raise a ticket |
| 40900-40914 | upload errors: signature, empty, too large, wrong type, expired, invalid: fix the file. 40911 duplicate name: rename. 40901 transcoding: wait, retry. 40902, 40903, 40913 URL not fetched: fix the URL |

Deprecations to code around:

| Item | Rule |
|---|---|
| Sandbox, creative optimisation API | Sandbox ends 2026-12-01 and never had Smart+: test on the real account, everything `DISABLE`, low budget, short schedule (codes 40008, 40009, 40013, 40014 are sandbox-only). `ad/aco/create/` (ACO) is closed: create ads with `ad/create/` or the Smart+ ad call |
| Manual flow, legacy Smart+, custom identity | sections 1 and 2; `campaign/spc/create/` closed since 2026-03-31 |
| Reporting | Stay on v1.3 (`tiktok report`, `tiktok get report/integrated/get/`). Version 2.0 renames fields (`ad_id_v2` to `ad_id`, `search_terms` to `search_term`, filters `campaign_ids` to `campaign_id`), merges Basic and Audience reports and drops GMV Max reports (use `gmv_max/report/get/`). Keep field names in one place. v1.3 limits: day dimension 30 days per call, hour dimension 1 day, otherwise 365 days, 100 ids per filter, 1000 rows per page |

## 9. Official documentation

Base `https://business-api.tiktok.com/portal/docs/<page>/v1.3`. Pages: campaign `create-a-campaign`; ad group `create-an-ad-group-reference`; ad `create-ads`; uploads `upload-a-video`, `upload-an-image-reference`; identities `identities`, `get-the-identity-list`, `create-spark-ads`, `apply-an-authorization-code`; Smart+ `upgraded-smart-campaign`, `create-an-upgraded-smart-campaign`, `create-an-upgraded-smart-ad-group`, `create-an-upgraded-smart-ad`, `create-a-regular-upgraded-smart-web-campaign`, `upgraded-smart-ad-creative-combinations-by-identity-and-ad-type`; GMV Max `create-a-gmv-max-campaign`; pixels `get-pixels`; status `update-the-operation-statuses-of-campaigns`, `update-the-statuses-of-ad-groups`, `update-the-statuses-of-ads`; review `get-review-info-of-ads`; budgets `budget`, `budget-verification-ratio-and-value-range-for-each-currency`; reference `enumerations-appendix`, `return-codes-appendix`, `rate-limits`, `whats-new`; MCP `tiktok-ads-mcp-server`, `available-tools-in-tiktok-for-business-mcp-server`.
