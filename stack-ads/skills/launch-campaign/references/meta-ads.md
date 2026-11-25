# Meta ads: create a campaign through the toolkit

Exact, current parameters for creating Facebook and Instagram ads on a real ad account: a complete plan file for `launch plan` / `launch apply`, variations, the rules behind the fields, and the two other official routes (CLI, MCP). Facts were read from Meta's official pages on 2026-11-14. No body here was run against a live ad account: the first `launch plan`, and `launch apply` into paused objects, are the test.

## Contents

- 1. Before you build the plan
- 2. Image ad, traffic objective: complete plan
- 3. Variations
- 4. Objectives, optimisation goals, billing events
- 5. Dry run, apply, verify, activate, roll back
- 6. Other official routes: `meta ads` CLI and `meta-ads` MCP server
- 7. Limits and errors

Official reference per object (append `.md` for clean markdown). Base `https://developers.facebook.com/documentation/ads-commerce/marketing-api/`:

| Object | Page under the base |
|---|---|
| Campaign, ad set, creative, image, video, previews | `reference/ad-account/` + `campaigns`, `adsets`, `adcreatives`, `adimages`, `advideos`, `generatepreviews` |
| Ad | `reference/adgroup` |
| Flexible creative, Advantage+ | `ad-creative/asset-feed-spec`, `advantage-campaigns` |
| Rate limits, errors | `overview/rate-limiting`, `error-reference` |

## 1. Before you build the plan

**Credentials** (`META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID` numeric, `META_PAGE_ID`; optional `META_PIXEL_ID`, `META_INSTAGRAM_USER_ID`, `META_APP_ID`, `META_APP_SECRET`):

- A system-user token with scopes `ads_management`, `ads_read`, `business_management`, `pages_show_list`, `pages_read_engagement`, `pages_manage_ads`, `read_insights`. The system user must be assigned to the ad account, the Page and (for conversions) the pixel.
- Own ad account: Limited Access to the Marketing API is enough; its rate limits are strict (section 7).

```bash
python3 ads/tools/ads.py doctor --live --only meta
python3 ads/tools/ads.py meta get "{account}" -p fields=id,name,account_status,currency,funding_source,min_daily_budget,default_dsa_beneficiary,default_dsa_payor
python3 ads/tools/ads.py meta get "{account}/promote_pages"
```

| Check | Required result |
|---|---|
| `account_status` | `1` (ACTIVE). 2 DISABLED, 3 UNSETTLED, 7 PENDING_RISK_REVIEW, 9 IN_GRACE_PERIOD, 100/101 closing/closed: stop |
| `funding_source` | present. Without a payment method objects are created but never deliver |
| `currency` | budgets are integers in its minor unit (EUR/USD: cents) |
| `promote_pages` | contains `META_PAGE_ID` |
| `min_daily_budget` | your ad set `daily_budget` is not below it (`meta get "{account}/minimum_budgets"` also exists; its fields are unverified) |

**Conversion objectives** need a pixel (dataset) with recent events:

```bash
python3 ads/tools/ads.py meta get "{account}/adspixels" -p fields=id,name,last_fired_time,is_unavailable
```

Use the pixel with `is_unavailable` false and a recent `last_fired_time`. A pixel that never fired, or last fired weeks ago, will not optimise: fix tracking first. Its `id` goes into `promoted_object.pixel_id` (`META_PIXEL_ID`).

**Special ad categories**: `special_ad_categories` is required on every campaign. `[]` for none. Values: `EMPLOYMENT`, `HOUSING`, `FINANCIAL_PRODUCTS_SERVICES` (replaced `CREDIT` on 2025-01-14), `ISSUES_ELECTIONS_POLITICS`, `ONLINE_GAMBLING_AND_GAMING`. Add `special_ad_category_country` (ISO-2 array) when set. Social-issue, electoral and political ads are not allowed in the EU. A campaign in a regulated category with Advantage+ audience must set `advantage_audience` explicitly. The value is the advertiser's declaration, with legal weight: take it from the compliance answers of the approved media plan, and when the plan gives none, ask the user before the dry run. `[]` in the samples stands for the answer "none"; it is not a default to copy.

**EU delivery**: the ad set needs `dsa_beneficiary` and `dsa_payor` (legal names of who benefits and who pays). Account defaults `default_dsa_beneficiary` and `default_dsa_payor` (set together) cover a missing field; with neither the request fails. Read them with the account call above.

**API version**: plan paths carry no version. The toolkit calls the Marketing API version stored in `ads/config.json` under `api.meta_graph`: one value, change it there only. Unversioned calls fail; a deprecated version is auto-upgraded and the response carries the header `X-Ad-Api-Version-Warning`. The recipes below were read in the `v27.0` documentation (released 2026-11-04); `v26.0` and `v25.0` (expires 2027-02-23) are live; `v24.0` expired 2026-11-10. Do not hard-code a version anywhere else.

**What changed in 2025-2026 and breaks older recipes**

| Change | Do |
|---|---|
| Legacy Advantage+ Shopping and App campaigns can no longer be created or edited (all versions since 2026-05-19) | do not send `smart_promotion_type`; build a normal `OUTCOME_SALES` / `OUTCOME_APP_PROMOTION` campaign |
| Advantage+ state is derived from three levers: budget at campaign level, no placement targeting, `advantage_audience` 1. `advantage_state` is read-only | set the levers; read back `meta get <CAMPAIGN_ID> -p fields=name,objective,advantage_state_info` |
| `advantage_audience` must be explicit on new ad sets whose targeting is not default | always send `targeting_automation.advantage_audience` as 1 or 0 |
| `is_adset_budget_sharing_enabled` required on campaign create when the budget is on the ad set (v24+) | send `false` or `true` (true lets ad sets share up to 20% of budget) |
| v27.0: new Sales ad sets get `targeting_automation.individual_setting.device=1` by default | send `0` to opt out |
| Facebook video feeds placement removed (v24); Instagram Explore feed and Messenger story removed (v26) | do not list them in positions |
| `7d_view` and `28d_view` attribution windows return no data since 2026-01-12 | for insights use `1d_click`, `7d_click`, `28d_click`, `1d_view`; omit `attribution_spec` unless required (windows allowed in it: unverified) |
| Detailed-targeting interests were consolidated; removed ones error | re-find ids with `meta search --type adinterest --q TEXT` |

## 2. Image ad, traffic objective: complete plan

Save as `ads/launch/traffic-de.json`. Replace the texts, the image path, the legal names and the start date. Budget: `budget.daily` is in major units (guard rail check), `daily_budget` in params is in minor units: 20 EUR is `2000`. The ad set budget must stay under `guardrails.max_daily_budget` in `ads/config.json`.

```json
{
  "name": "traffic-de",
  "platform": "meta",
  "objective": "Website traffic, Germany, one image ad",
  "budget": {"daily": 20, "currency": "EUR"},
  "landing_url": "https://example.com/",
  "steps": [
    {"id": "img", "do": "meta.upload_image", "with": {"file": "ads/creatives/hero-1x1.png"}},
    {"id": "campaign", "do": "meta.post", "with": {"path": "{account}/campaigns", "params": {
      "name": "Traffic DE - spring", "objective": "OUTCOME_TRAFFIC", "status": "PAUSED",
      "special_ad_categories": [], "is_adset_budget_sharing_enabled": false}}},
    {"id": "adset", "do": "meta.post", "with": {"path": "{account}/adsets", "params": {
      "name": "DE 18-65 - Advantage+ audience", "campaign_id": "{{campaign.id}}", "status": "PAUSED",
      "optimization_goal": "LINK_CLICKS", "billing_event": "IMPRESSIONS",
      "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "daily_budget": 2000,
      "start_time": "2026-12-01T09:00:00+0000",
      "targeting": {"geo_locations": {"countries": ["DE"]}, "targeting_automation": {"advantage_audience": 1}},
      "dsa_beneficiary": "Example GmbH", "dsa_payor": "Example GmbH"}}},
    {"id": "creative", "do": "meta.post", "with": {"path": "{account}/adcreatives", "params": {
      "name": "Hero image - spring",
      "object_story_spec": {"page_id": "{page}", "link_data": {
        "image_hash": "{{img.hash}}", "link": "https://example.com/",
        "message": "Primary text of the ad.", "name": "Headline", "description": "Link description",
        "call_to_action": {"type": "LEARN_MORE"}}},
      "url_tags": "utm_source=facebook&utm_medium=paid&utm_campaign=traffic-de"}}},
    {"id": "ad", "do": "meta.post", "with": {"path": "{account}/ads", "params": {
      "name": "Hero image - spring", "adset_id": "{{adset.id}}",
      "creative": {"creative_id": "{{creative.id}}"}, "status": "PAUSED"}}}
  ]
}
```

No account id is written in the plan: the toolkit replaces `{account}`, `{page}`, `{pixel}` and `{instagram}` in paths and in parameter values with the ids from `ads/.env`. Params are written as JSON objects as above; the toolkit sends nested values to the Graph API as JSON text, which is what it expects for `targeting`, `object_story_spec` and `creative`.

| Field | Req. | Allowed values | Rule |
|---|---|---|---|
| campaign `objective` | yes | `OUTCOME_TRAFFIC`, `OUTCOME_SALES`, `OUTCOME_LEADS`, `OUTCOME_AWARENESS`, `OUTCOME_ENGAGEMENT`, `OUTCOME_APP_PROMOTION` | use only the six OUTCOME values; legacy values (`LINK_CLICKS`, `CONVERSIONS`) are still listed by the reference but the CLI accepts only OUTCOME ones |
| `status` (all objects) | yes | `PAUSED` | creation allows `ACTIVE`/`PAUSED`; the toolkit refuses anything but `PAUSED` |
| `special_ad_categories` | yes | array, `[]` for none | see section 1 |
| `is_adset_budget_sharing_enabled` | yes with ad-set budget | boolean | omit when the campaign carries the budget |
| `daily_budget` / `lifetime_budget` | one of them, at one level | integer, minor units | campaign or ad set, never both; lifetime needs `end_time`; weekly spend cannot exceed 7x daily. Use `daily_budget`: the toolkit refuses `lifetime_budget` unless the user has set `guardrails.max_total_budget`, and then the plan declares it as `"budget": {"total": N}`. A campaign budget stands for the ad sets under it; without one, the daily budgets of its ad sets add up. The sum over the plan must equal `budget.daily` and stay under the ceiling |
| `bid_strategy` | send it | `LOWEST_COST_WITHOUT_CAP`, `LOWEST_COST_WITH_BID_CAP`, `COST_CAP`, `LOWEST_COST_WITH_MIN_ROAS` | the reference and the CLI disagree on the default: always set it |
| `optimization_goal`, `billing_event` | yes | section 4 | `start_time` future ISO date-time with offset; `end_time` 0 = ongoing; creative `instagram_user_id` never with `instagram_actor_id` (2446149) |
| `targeting.geo_locations` | yes | `countries` array (ISO-2), regions, cities with `key` ids | required unless a custom audience is given |
| `targeting_automation.advantage_audience` | yes | `1` or `0` | with 1: `age_min` only 18-25, `age_max` fixed at 65 and cannot be set |
| `dsa_beneficiary`, `dsa_payor` | EU delivery | strings | see section 1 |
| `object_story_spec.page_id`, `link_data.image_hash` | yes (hash for an uploaded image) | Page id; hash `{{img.hash}}` | image up to 8 MB; jpg, png, gif, bmp, webp |
| `link_data.call_to_action.type` | optional | `LEARN_MORE`, `SHOP_NOW`, `SIGN_UP`, `BUY_NOW`, `BOOK_NOW`, `CONTACT_US`, `DOWNLOAD`, `GET_OFFER`, `GET_QUOTE`, `APPLY_NOW`, `SUBSCRIBE`, `NO_BUTTON` | objectives that need an external URL fail with error 100/2446383 without a CTA and link |
| `url_tags` | optional | query string, no leading `?` | appended to the clicked URL, e.g. `utm_source=facebook&utm_medium=paid&utm_campaign=traffic-de` |
| ad `creative`, `conversion_domain` | yes; sales | `{"creative_id": "..."}`; bare domain | `conversion_domain` is required by Meta for `OUTCOME_SALES` / `OFFSITE_CONVERSIONS` |

## 3. Variations

Change only the named steps; every other step stays as in section 2.

**Conversion objective** (campaign `objective` `OUTCOME_SALES`):

```jsonc
// adset params
"optimization_goal": "OFFSITE_CONVERSIONS",
"billing_event": "IMPRESSIONS",
"promoted_object": {"pixel_id": "{pixel}", "custom_event_type": "PURCHASE"},
// ad params
"conversion_domain": "example.com"
```

**Video creative**: add the upload step before the creative and use `video_data`:

```jsonc
{"id": "vid", "do": "meta.upload_video", "with": {"file": "ads/creatives/spot-9x16.mp4", "name": "Spot spring"}},
{"id": "thumb", "do": "meta.upload_image", "with": {"file": "ads/creatives/spot-9x16-thumb.jpg"}},
// creative params
"object_story_spec": {"page_id": "{page}", "video_data": {"video_id": "{{vid.id}}", "image_hash": "{{thumb.hash}}",
  "message": "Primary text", "title": "Headline",
  "call_to_action": {"type": "LEARN_MORE", "value": {"link": "https://example.com/"}}}}
```

This body ran live on 2026-11-25 with a system-user token: a 5-second 720x1280 clip of 2.4 MB (H.264, AAC, 24 fps), its thumbnail, creative and ad in one plan. The creative was accepted about ten seconds after the upload, without waiting. The thumbnail is a frame of the clip uploaded as an image; `image_url` in place of `image_hash` comes from Meta's pages and was not run. A longer or larger file may still be processing when the creative step runs (unverified). Safe choice for those: upload the video on its own before the plan. Run `meta upload-video --file FILE`, which only prints the file and its size; show that to the user, and after their yes run it again with `--yes`. Poll `meta get <VIDEO_ID> -p fields=status` until ready, put the id into the creative and drop the upload step. MP4, 24-60 fps, H.264 or H.265, AAC; Meta's pages say a width of at least 1200 px, yet the 720-pixel clip was accepted.

A removal leaves the video in the account's library. `meta delete "{account}/advideos" -p video_id=VIDEO_ID` shows what would go, and with `--yes` takes it out (run live). `meta delete VIDEO_ID` is refused with code 200: it asks for `pages_manage_posts`, which ads do not need. Read `meta get "{account}/adimages" -p fields=name,status` again some time after a removal as well: one deleted image was back in the library two days later and had to be deleted again.

**Campaign budget (CBO)**: campaign params get `"daily_budget": 2000` and `"bid_strategy": "LOWEST_COST_WITHOUT_CAP"` and no `is_adset_budget_sharing_enabled`; ad set params drop `daily_budget` and `bid_strategy`.

**Advantage+ audience off** (`advantage_audience` stays explicit): `"targeting": {"geo_locations": {"countries": ["DE"]}, "age_min": 25, "age_max": 54, "genders": [1, 2], "flexible_spec": [{"interests": [{"id": "6003139266461", "name": "Movies"}]}], "targeting_automation": {"advantage_audience": 0}}`. Find interest ids with `python3 ads/tools/ads.py meta search --type adinterest --q "movies"`. `genders`: 1 male, 2 female; `age_min` at least 13, `age_max` at most 65.

**Manual placements** (turns off the Advantage+ placement lever; omit all placement fields for Advantage+ placements): add to `targeting` `"publisher_platforms": ["facebook", "instagram"], "facebook_positions": ["feed", "story", "facebook_reels"], "instagram_positions": ["stream", "story", "reels"]`. Values: `publisher_platforms` facebook, instagram, threads, messenger, audience_network; `facebook_positions` feed, right_hand_column, marketplace, story, search, instream_video, facebook_reels, facebook_reels_overlay, profile_feed, notification; `instagram_positions` stream, story, explore_home, reels, profile_feed, ig_search, profile_reels; `device_platforms` mobile, desktop.

**Bid caps** (ad set): `"bid_strategy": "COST_CAP", "bid_amount": 500` or `"bid_strategy": "LOWEST_COST_WITH_BID_CAP", "bid_amount": 300`; `bid_amount` is in minor units and required for both. `LOWEST_COST_WITH_MIN_ROAS`: floor parameter unverified, do not use.

**Flexible (multi-asset) creative**: the ad set gets `"is_dynamic_creative": true`; the creative carries `asset_feed_spec`:

```jsonc
"asset_feed_spec": {"images": [{"hash": "{{img1.hash}}"}, {"hash": "{{img2.hash}}"}],
  "bodies": [{"text": "Primary text A"}, {"text": "Primary text B"}],
  "titles": [{"text": "Headline A"}, {"text": "Headline B"}], "descriptions": [{"text": "Description A"}],
  "link_urls": [{"website_url": "https://example.com/"}], "call_to_action_types": ["LEARN_MORE"], "ad_formats": ["SINGLE_IMAGE"]}
```

Each asset value must be unique (error 1815629). `asset_customization_rules` needs at least two rules. Videos go in `videos[{video_id, thumbnail_url}]`. Whether `object_story_spec` with only `page_id` is also needed beside `asset_feed_spec` is unverified; the dry run answers it. Advantage+ creative enhancements (`degrees_of_freedom_spec`): the required `degrees_of_freedom_type` value is unverified, leave the spec out.

## 4. Objectives, optimisation goals, billing events

| Objective | `optimization_goal` | `billing_event` | What the official pages confirm |
|---|---|---|---|
| `OUTCOME_TRAFFIC` | `LINK_CLICKS` | `IMPRESSIONS` | confirmed (official examples, CLI recipe) |
| `OUTCOME_SALES` | `OFFSITE_CONVERSIONS` with `promoted_object` pixel + `custom_event_type` | `IMPRESSIONS` | goal and `promoted_object` confirmed; billing event unconfirmed |
| `OUTCOME_LEADS` | `LEAD_GENERATION` | - | goal exists; pairing unconfirmed |
| `OUTCOME_AWARENESS` | `REACH`, `IMPRESSIONS`, `AD_RECALL_LIFT` | `IMPRESSIONS` | goals exist; pairing unconfirmed |
| `OUTCOME_ENGAGEMENT` | `POST_ENGAGEMENT`, `THRUPLAY`, `ENGAGED_USERS`, `PAGE_LIKES` | `POST_ENGAGEMENT`, `THRUPLAY`, `PAGE_LIKES`, `IMPRESSIONS` | enums exist; pairing unconfirmed |
| `OUTCOME_APP_PROMOTION` | `APP_INSTALLS` | `APP_INSTALLS`, `IMPRESSIONS` | `promoted_object` needs `application_id` + `object_store_url`; pairing unconfirmed |

Meta's pages, as read, give no objective-to-goal compatibility matrix. Rule: when the pair is unconfirmed, the dry run (`validate_only`) tells you; never guess a second combination on a live account. `billing_event` enum: `APP_INSTALLS`, `CLICKS` (deprecated), `IMPRESSIONS`, `LINK_CLICKS`, `NONE`, `OFFER_CLAIMS`, `PAGE_LIKES`, `POST_ENGAGEMENT`, `THRUPLAY`, `PURCHASE`, `LISTING_INTERACTION`.

## 5. Dry run, apply, verify, activate, roll back

```bash
python3 ads/tools/ads.py launch plan --file ads/launch/traffic-de.json
python3 ads/tools/ads.py launch apply --file ads/launch/traffic-de.json --yes
python3 ads/tools/ads.py launch status --file ads/launch/traffic-de.json
python3 ads/tools/ads.py ledger --plan traffic-de --json
```

- `launch plan` checks the file (guard rails, references, budget ceiling) and prints the eight blocks. In VALIDATE each step gets one verdict: `ok ... validated by Meta` for a step whose references are all known (on a first run that is the campaign, sent with `validate_only`), `ok ... file found` for an upload, `wait` for a step that needs an id of an earlier step (`{{campaign.id}}`, `{{img.hash}}`): `validate_only` returns no id, so Meta checks that step during apply and the dry run checks it against the toolkit's rules only. `FAIL` blocks the plan and the command exits with code 2.
- A platform success on `validate_only` is not the final decision of ad review.
- `launch apply` runs the steps in order, all PAUSED, and writes each id to `ads/launch/ledger.jsonl`. It stops at the first failed step. Fix that step in the plan file, run `launch plan` again and show the new output to the user, and after their yes run `launch apply`: the toolkit refuses to apply a plan that changed since its last clean dry run, and it skips the steps already in the ledger, so nothing is created twice. A step that was applied may not be edited or renamed: the toolkit refuses a plan in which it differs from what was sent.
- A failure that says no clear answer came back (a timeout, a server error, an interrupted run) may have created the object anyway. `launch apply` then refuses to go on. Look for the object in the ad account by its name (`meta get "{account}/adsets" -p fields=id,name,status`, or `campaigns`, `ads`); if it is there, ask the user and delete it with `meta delete <ID>` (shown first without `--yes`). Found or not, `--resend` sends the create again, so ask first, then run `launch apply --file ... --yes --resend STEP`.
- To start over, `launch rollback --remove --yes` deletes what was created and clears the ledger for this plan: run it only when the user asks for removal. If one object cannot be deleted, the command goes on with the others, ends with an error that names what is left, and finishes on a second run.
- A path never carries parameters: `{account}/campaigns?status=ACTIVE` is refused, and so are `batch` calls, a nested `adset_spec` or `campaign_spec` and a parameter named `method`, because the paused rule and the budget ceiling read the parameters of each call.
- A plan step writes to an edge of the ad account, `{account}/campaigns`, `{account}/adsets`, `{account}/adcreatives`, `{account}/ads`: a plan only creates. A write to an object id (a new budget, a status, a copy) is a single command, shown to the user first. An ad set hangs under a campaign of the same plan and an ad under an ad set of the same plan: to add one to a campaign that already exists, use `meta post` commands one by one, after reading that campaign's budget. A campaign without a budget needs one on each of its ad sets, or the plan is refused.
- Previews (valid 24 hours, iframe in `body`): `python3 ads/tools/ads.py meta get "<AD_ID>/previews" -p ad_format=MOBILE_FEED_STANDARD`.
`ad_format`: `DESKTOP_FEED_STANDARD`, `MOBILE_FEED_STANDARD`, `INSTAGRAM_STANDARD`, `INSTAGRAM_STORY`, `INSTAGRAM_REELS`, `FACEBOOK_REELS_MOBILE`. The per-ad `previews` edge is unverified on the official page; the documented route also works before any object exists:

```bash
python3 ads/tools/ads.py meta get "{account}/generatepreviews" -p ad_format=MOBILE_FEED_STANDARD -p 'creative={"object_story_spec":{"page_id":"<PAGE_ID>","link_data":{"link":"https://example.com/","message":"Hi","image_hash":"<HASH>"}}}'
```

- Read back before spending:
```bash
python3 ads/tools/ads.py meta get "<AD_ID>" -p fields=effective_status,ad_review_feedback,issues_info,failed_delivery_checks
python3 ads/tools/ads.py meta get "<CAMPAIGN_ID>" -p fields=name,objective,status,advantage_state_info
```

`effective_status` values: `ACTIVE`, `PAUSED`, `PENDING_REVIEW`, `DISAPPROVED`, `PREAPPROVED`, `PENDING_BILLING_INFO`, `CAMPAIGN_PAUSED`, `ADSET_PAUSED`, `IN_PROCESS`, `WITH_ISSUES`, `ARCHIVED`, `DELETED`. Before activation every object must read `PAUSED` (parents `CAMPAIGN_PAUSED` / `ADSET_PAUSED` on the children is normal).
- Show the previews, the budget and the audience to the user, then:
```bash
python3 ads/tools/ads.py launch activate --file ads/launch/traffic-de.json
python3 ads/tools/ads.py launch activate --file ads/launch/traffic-de.json --yes
python3 ads/tools/ads.py launch rollback --file ads/launch/traffic-de.json --yes
python3 ads/tools/ads.py launch rollback --file ads/launch/traffic-de.json --remove --yes
```

The first line changes nothing: it prints what would be enabled and the budget of the plan. With `--yes`, `activate` starts spend and needs the user's explicit go, given after they have seen what was created and with the daily budget stated in words. New ads sit in `PENDING_REVIEW` until approved. `rollback` pauses what the plan created; `--remove` deletes the ads, ad sets and the campaign instead and is run only when the user asks for removal. After activation read `effective_status` again: `WITH_ISSUES` or `DISAPPROVED` is a stop, not a wait.

## 6. Other official routes

### `meta ads` CLI (Meta Ads CLI, PyPI package `meta-ads`, command `meta`)

An official alternative, not a replacement: it has no ledger, no budget ceiling and no rollback, so use the toolkit unless it is unavailable. `creative create --image` / `--video` uploads the file itself. It needs Python 3.12 or later and is pinned to the previous API version (SDK `facebook-business` below 27, so v26): v27-only behaviour is not reachable. Everything is created PAUSED. Objects created this way are not in the toolkit ledger: write every returned id to a note in `ads/launch/`. Each create and each upload is a write to the ad account: show the user the full command and what it will create, and run it only after their yes, one command at a time.

```bash
pip install meta-ads
export ACCESS_TOKEN="$META_ACCESS_TOKEN" APP_ID="$META_APP_ID" APP_SECRET="$META_APP_SECRET" AD_ACCOUNT_ID="$META_AD_ACCOUNT_ID"
meta -o json ads page list
meta -o json ads campaign create --name "Traffic DE - spring" --objective OUTCOME_TRAFFIC --daily-budget 2000 --bid-strategy LOWEST_COST_WITHOUT_CAP
meta -o json ads adset create --campaign-id "<CAMPAIGN_ID>" --name "DE 18-65" --optimization-goal LINK_CLICKS --billing-event IMPRESSIONS --targeting-countries DE --dsa-beneficiary "Example GmbH" --dsa-payor "Example GmbH"
meta -o json ads creative create --name "Hero image" --page-id "<PAGE_ID>" --image ads/creatives/hero-1x1.png --body "Primary text of the ad." --title "Headline" --link-url https://example.com/ --call-to-action LEARN_MORE
meta -o json ads ad create --adset-id "<AD_SET_ID>" --name "Hero image" --creative-id "<CREATIVE_ID>"
```

Activation is `meta ads campaign update "<CAMPAIGN_ID>" --status ACTIVE`, then `adset` and `ad` the same way: it starts spend, so it needs the same explicit approval as `launch activate`, with the daily budget stated in words. Pause with `--status PAUSED`. `--execution-options validate_only` on the campaign command is the dry run. `--special-ad-categories NONE` is unverified: omit the flag for none. Also: `--targeting` (JSON or `@file.json`), `--pixel-id`, `--custom-event-type`, `--promoted-object`, `--instagram-user-id`, `--url-tags`, `--conversion-domain`, `--dynamic-creative`. Token: system user, Admin or Employee role.

### `meta-ads` MCP server (the plugin's server, Meta-hosted)

The plugin's `meta-ads` server signs in with `META_ACCESS_TOKEN` as a bearer token: a user token, or a system-user token of the Employee role (Admin tokens are refused), with the scope `ads_mcp_management` plus `ads_read` or `ads_management`. OAuth without a token and without an app works on a server the user adds themselves (see the Meta key guide of `init-project`). Meta opens the server account by account: `ads_get_ad_accounts` returns `is_ads_mcp_enabled`, `account_status`, `is_queryable` and `has_payment_method` for every ad account the login reaches. Call it first and work only in an account that is `ACTIVE` and queryable. A business can also limit what an agent may do in an ad account (Business settings > Integrations > Ads MCP server), so a refused write can be such a rule.

| Purpose | Tools |
|---|---|
| Create | `ads_create_campaign`, `ads_create_ad_set`, `ads_create_creative`, `ads_create_ad`: a campaign is created as a draft, see below |
| Start or change spend | `ads_activate_entity` (starts spend), `ads_boost_ig_post`; `ads_update_entity` can change status and budget: treat all three as spending |
| Look up | `ads_get_ad_accounts`, `ads_get_ad_account_pages`, `ads_get_user_pages`, `ads_get_ig_accounts`, `ads_get_datasets`, `ads_get_dataset_stats`, `ads_get_ad_entities`, `ads_get_creatives`, `ads_get_ad_images`, `ads_get_ad_videos`, `ads_get_ad_preview` |
| Diagnose | `ads_get_errors`, `ads_get_help_article` (searches Meta's Business Help Center), `ads_account_get_activity_logs` |

**Drafts** (run of 2026-11-22). `ads_create_campaign` does not create a live campaign and does not create it paused:

- The result says `"status": "DRAFT"`. Its `spec` shows the status the campaign would be published with. The tool took no status, and the `spec` said `ACTIVE`.
- Read a draft with `ads_get_ad_entities` and `object_state` `draft`. With `live` the draft is not returned.
- Make the draft paused before anything publishes it: `ads_update_entity` with `fields` `{"status":"PAUSED"}`, then read the draft back. A new campaign takes only active or paused: `DELETED` is stored on the draft with error 1487564. Setting `PAUSED` on a draft and publishing a draft were not exercised here.
- Discard a draft with `ads_update_entity` and `discard_draft_changes` `true`: the first call returns a `discard_preview` and a `confirmation_token`, the second call with that token removes the draft.
- Every result carries an `ads_manager_url` where the user reviews the draft.

The live tool list has upload tools (`ads_creative_upload_media`, and `ads_create_upload_url` with `ads_finalize_upload`). They were not exercised here: the toolkit's `meta upload-image` and `meta upload-video` are the tested way. Meta's help page names four creative types for `ads_create_creative`: single image, single video, carousel and product media carousel. Parameter schemas are not documented: read them from the server's tool list. Each tool also takes context fields that describe the request (`advertiser_request` and others): they are not settings. Roll out in phases, with the user's yes before each write: one read call; then show the full request of the campaign (name, objective, budget, special ad category), create the draft after their yes and set it paused; the same for the ad set, the creative and the ad; review in `ads_get_ad_preview`; and `ads_activate_entity` only after a second, explicit go with the daily budget stated in words. Add up the daily budgets yourself and keep them under `guardrails.max_daily_budget`: the server knows no ceiling.

## 7. Limits and errors

**Rate limits**: two layers per ad account, an account score (read 1 point, write 3, decays over 300 s) and hourly business-use-case quotas. After each write the response header `X-Business-Use-Case-Usage` carries `call_count`, `total_time` and `estimated_time_to_regain_access` (minutes): at 90 or more, wait that long.

| Limit | Limited Access (default) | Full Access |
|---|---|---|
| Account score max | 60, block 300 s | 9000, block 60 s |
| `ads_management` per hour per account | 300 + 40 x active ads | 100,000 + 40 x active ads |
| `ads_insights` per hour | 600 + 400 x active ads | 190,000 + 400 x active ads |

On Limited Access 60 points is about 20 writes: space out launches and never run several plans back to back. Further limits: ad set budget change 4 per hour per ad set (613/1487632, 1-hour block); one edit per object per 30 s (613/4841018); mutation rate 100 per app and account (613/5044001); spend-limit changes 10 per day.

**Errors** (rely on `code` and `error_subcode`; the text changes)

| Code / subcode | Meaning | Fix |
|---|---|---|
| 190 | token invalid or expired | regenerate the system-user token |
| 200 | permission missing | scope or asset assignment (Page, pixel, ad account) missing |
| 294 | managing ads needs `ads_management` and an allowed app | check the scope and the app's access tier |
| 100 | invalid parameter | read `error_subcode` and `error_user_msg` |
| 100 / 1487694, 2446394 | targeting option no longer available | re-find ids with `meta search` |
| 100 / 1815946 | radius with several locations | one location per ad set or no radius |
| 100 / 3858258 | image not downloaded | image URL must be public and not blocked by robots.txt |
| 2446383 | objective needs an external URL | add `link` and a call to action |
| 2446149 | `instagram_user_id` and `instagram_actor_id` both sent | send one |
| 2635 | API version deprecated | set a live version in `ads/config.json` |
| 368 | action judged abusive | stop retrying; read the policy |
| 17, 4, 613, 80000, 80003, 80004, 80014 | rate limits | wait per the table above |


**A rejected ad**: creation succeeds, then `effective_status` becomes `DISAPPROVED` or `WITH_ISSUES`. Read `ad_review_feedback`, `issues_info` and `failed_delivery_checks` (command in section 5); the MCP tool `ads_get_errors` diagnoses blocking issues. Fix the creative, create a new creative and update the ad's `creative`; do not retry the same content. An ad that is `PENDING_BILLING_INFO` needs a payment method, not a new creative.
