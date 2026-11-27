# Google Ads launch reference

Exact request bodies and rules for creating a Google Ads campaign (Search, Performance Max, Demand Gen) through a launch plan of the toolkit (`python3 ads/tools/ads.py`, see the toolkit reference of `init-project`). Facts checked 2026-11-14 against the v26 REST discovery document and the official guides.

## Contents

1. Before you build the plan
2. Search campaign: complete plan and field table
3. Variations: bidding, negatives, assets, AI Max
4. Performance Max
5. Demand Gen
6. Look-ups: geo, conversion actions, audiences
7. Dry run, apply, verify, activate, roll back
8. The official MCP server in a launch
9. Limits and errors

Only the Search body in section 2 is the official Google sample plus geo, keywords and an extra ad group field; on 2026-11-23 it was validated, applied paused, read back and removed on a production account. Every other body here was composed from the v26 field definitions and never run against a live account. Run `launch plan` on each one and rely on the validation result, not on this text.

## 1. Before you build the plan

| Check | Rule | How |
|---|---|---|
| Access level | Production accounts need Explorer or higher on the Cloud project that owns the OAuth client. Test access reaches test accounts only. A dry run (`validateOnly`) on a production account also needs Explorer. Keyword Planner (`google keyword-ideas`) needs Basic. | `python3 ads/tools/ads.py google customers`. Error `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION` means Test access: use a test account or apply for Explorer on the project's Google Ads API overview page. |
| Account usable | `customer.status` must be `ENABLED`; `CANCELED` gives `CUSTOMER_NOT_ENABLED`. Note currency and time zone. | GAQL below |
| Billing | The Search guide requires an approved billing setup. The API gives no specific error for a missing one; the symptom is a campaign that never serves. Billing is set in the Google Ads web interface (Billing and payments). | Ask the user. Unverified read-back: `SELECT billing_setup.id, billing_setup.status FROM billing_setup` (may be blocked at Explorer). |
| Conversion action | Needed for Maximize conversions, Target CPA, Performance Max and Demand Gen: at least one ENABLED action that is primary and counts in the conversions metric. | GAQL in section 6 |

```bash
python3 ads/tools/ads.py google search --query "SELECT customer.id, customer.currency_code, customer.time_zone, customer.status, customer.test_account, customer.manager FROM customer"
```

API version: the toolkit calls v26 (current; v23 is sunset in February 2027). The version is one value, `api.google_ads` in `ads/config.json`; change it there, never in a plan. Google applies the latest minor of the called major, so a field can appear inside v26 without notice.

Never send a `developer-token` header or look for a token: developer tokens ended on 2026-09-09. Use `GOOGLE_ADS_LOGIN_CUSTOMER_ID` only when the account is reached through a manager account (missing it gives `USER_PERMISSION_DENIED`). Customer ids are 10 digits, no hyphens.

## 2. Search campaign: complete plan

Save as `ads/launch/search-example-us.json`. Keep `{customer}` as written: the toolkit replaces it with `GOOGLE_ADS_CUSTOMER_ID` from `ads/.env`, so no account id is stored in a plan.

A plan step is applied whole or not at all: operations that use temporary ids must succeed or fail together, and the toolkit refuses `partialFailure: true` in a plan. `budget.daily` of the plan and `amountMicros` of the campaign budget must agree and stay under `guardrails.max_daily_budget`.

```json
{
  "name": "search-example-us",
  "platform": "google",
  "objective": "Search campaign for the example product, United States",
  "budget": {"daily": 20, "currency": "USD"},
  "landing_url": "https://example.com/",
  "steps": [
    {"id": "create", "do": "google.mutate", "with": {
      "partialFailure": false,
      "mutateOperations": [
        {"campaignBudgetOperation": {"create": {"resourceName": "customers/{customer}/campaignBudgets/-1",
          "name": "Example Search budget", "deliveryMethod": "STANDARD", "amountMicros": "20000000", "explicitlyShared": false}}},
        {"campaignOperation": {"create": {"resourceName": "customers/{customer}/campaigns/-2",
          "name": "Example Search US", "advertisingChannelType": "SEARCH", "status": "PAUSED", "manualCpc": {},
          "campaignBudget": "customers/{customer}/campaignBudgets/-1",
          "networkSettings": {"targetGoogleSearch": true, "targetSearchNetwork": true,
            "targetContentNetwork": false, "targetPartnerSearchNetwork": false},
          "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"}}},
        {"campaignCriterionOperation": {"create": {"campaign": "customers/{customer}/campaigns/-2",
          "location": {"geoTargetConstant": "geoTargetConstants/2840"}}}},
        {"adGroupOperation": {"create": {"resourceName": "customers/{customer}/adGroups/-3",
          "campaign": "customers/{customer}/campaigns/-2", "name": "Example ad group",
          "type": "SEARCH_STANDARD", "status": "ENABLED", "cpcBidMicros": "1500000"}}},
        {"adGroupCriterionOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "status": "ENABLED",
          "keyword": {"text": "example product", "matchType": "EXACT"}}}},
        {"adGroupCriterionOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "status": "ENABLED",
          "keyword": {"text": "buy example product", "matchType": "PHRASE"}}}},
        {"adGroupCriterionOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "status": "ENABLED",
          "keyword": {"text": "example product online", "matchType": "BROAD"}}}},
        {"adGroupAdOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "status": "ENABLED",
          "ad": {"finalUrls": ["https://example.com/"],
            "responsiveSearchAd": {
              "headlines": [{"text": "Example Product"}, {"text": "Free Shipping Over $50"}, {"text": "Shop The Example Range"}],
              "descriptions": [{"text": "Order today and get free returns for 30 days."}, {"text": "Trusted by thousands of customers."}],
              "path1": "shop", "path2": "deals"}}}}}
      ]}}
  ]
}
```

The campaign is the only paused object: ad groups, keywords and ads are created `ENABLED` under it and nothing serves while the campaign is paused, so enabling the campaign launches everything. `launch activate` and `launch rollback` therefore act on the campaign, and on any ad group, asset group or ad that the plan itself created `PAUSED`. Keywords are not switched: create them `ENABLED`.

This holds only for a campaign the same request creates. A plan adds nothing to a campaign it did not create: the new object would spend from a budget the plan neither sets nor checks, and no rollback could take a keyword or a criterion back. Such an addition is a single command (`google mutate`, shown without `--yes` first). There, a new ad group, asset group or ad under a campaign that already exists would serve at once, so the toolkit refuses it unless it is created `PAUSED`; enabling it is one more single command with `--activate`, after the user's approval. A keyword, a location or another criterion, and an asset link take effect the moment they are created: tell the user before they decide that it changes what the budget is spent on. Inside one plan, a later step may build on the campaign an earlier step created; an ad group, asset group or ad it adds there is created `PAUSED`, and `launch activate` enables it with the campaign.

`containsEuPoliticalAdvertising` is in the sample as `DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING`. That value is the advertiser's legal declaration, not a default: take it from the compliance answers of the approved media plan, and when the plan gives none, ask the user before the dry run.

### Field table

| Field | Need | Allowed values and rule |
|---|---|---|
| `resourceName` with a negative id | only on a resource that a later operation references | `customers/<id>/<collection>/-N`. Each negative id is unique across all resource types in the request (reuse gives `DUPLICATE_TEMP_IDS`). Reference only after it is defined: keep the order budget, campaign, criteria, ad group, keywords, ad. |
| budget `name`, `amountMicros` | required | Unique name. Micros are a string; 1,000,000 = one currency unit, a multiple of the currency's minimum unit. |
| budget `explicitlyShared` | set it | The API default is `true`; `false` gives a dedicated budget. |
| campaign `name` | required | Unique among campaigns (`DUPLICATE_CAMPAIGN_NAME`). |
| campaign `status` | required by the toolkit | `PAUSED`. The API default is ENABLED, the toolkit refuses it. |
| `advertisingChannelType` | required | `SEARCH`. |
| bidding | required, one of | `manualCpc` (needs `cpcBidMicros` on the ad group), `targetSpend`, `maximizeConversions`, `maximizeConversionValue`, `targetImpressionShare`, `biddingStrategy` (portfolio name). Section 3. |
| `campaignBudget` | required | The budget's resource name. In a plan it is a budget created in the same step: the toolkit refuses a new campaign on a budget the plan does not create, because the amount would not be checked. |
| `networkSettings` | set it | `targetSearchNetwork` needs `targetGoogleSearch`. `targetContentNetwork` is Display Expansion. Keep `targetPartnerSearchNetwork` false. |
| `containsEuPoliticalAdvertising` | always send | `CONTAINS_EU_POLITICAL_ADVERTISING` or `DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING`. Required unless every positive location is outside the EU. It is the advertiser's legal declaration: the value comes from the user (the compliance answers of the media plan), never from this file. A campaign that does contain such advertising is not delivered in the EU: stop and tell the user. |
| geo criterion `location.geoTargetConstant` | required in practice | `geoTargetConstants/<id>`, from section 6. Repeat the operation per location; add `"negative": true` to exclude. |
| language criterion | do not send | Search campaigns reject `language` criteria since September 2026 (`OPERATION_NOT_PERMITTED_FOR_CONTEXT`). Language comes from the ads and keywords. |
| ad group `type`, `cpcBidMicros` | required, with `manualCpc` | `SEARCH_STANDARD`. The bid is in micros; omit it with automated bidding. |
| keyword `text`, `matchType` | required | At most 80 characters and 10 words. `EXACT`, `PHRASE`, `BROAD`. |
| RSA `headlines` | required | 3 to 15, each at most 30 characters. `pinnedField` (for example `HEADLINE_1`) is optional. |
| RSA `descriptions` | required | 2 to 4, each at most 90 characters. |
| RSA `path1`, `path2`; ad `finalUrls` | paths optional; URL required | Paths at most 15 characters each. At least one URL, at most 2,084 bytes. |

## 3. Variations

Replace the bidding line of the campaign; drop `cpcBidMicros` from the ad group when you leave `manualCpc`.
```jsonc
// Maximize clicks (works without conversion tracking)
"targetSpend": {"cpcBidCeilingMicros": "2000000"}
// Maximize conversions (needs a primary conversion action)
"maximizeConversions": {}
// Target CPA = Maximize conversions with a target
"maximizeConversions": {"targetCpaMicros": "15000000"}
```

`TARGET_CPA` and `TARGET_ROAS` as separate strategies exist only as portfolio strategies. Enhanced CPC is deprecated on Search. The conversion history that Target CPA needs is not documented in the API pages (unverified): start with Maximize conversions.

```jsonc
// Negative keyword on the campaign, after the campaign operation
{"campaignCriterionOperation": {"create": {"campaign": "customers/{customer}/campaigns/-2", "negative": true, "keyword": {"text": "free", "matchType": "BROAD"}}}}
// Sitelink: create the asset, then link it (unused negative ids)
{"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-10", "finalUrls": ["https://example.com/pricing"],
  "sitelinkAsset": {"linkText": "Pricing", "description1": "See all plans", "description2": "Cancel anytime"}}}},
{"campaignAssetOperation": {"create": {"campaign": "customers/{customer}/campaigns/-2", "asset": "customers/{customer}/assets/-10", "fieldType": "SITELINK"}}}
// Callout: same two steps
{"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-11", "calloutAsset": {"calloutText": "Free shipping"}}}},
{"campaignAssetOperation": {"create": {"campaign": "customers/{customer}/campaigns/-2", "asset": "customers/{customer}/assets/-11", "fieldType": "CALLOUT"}}}
```

Limits: `linkText` 1 to 25 characters; `description1` and `description2` 1 to 35 characters, both or neither; `calloutText` 1 to 25. Other types (`structuredSnippetAsset`, `callAsset`, `promotionAsset`, `priceAsset`) link the same way with `fieldType` `STRUCTURED_SNIPPET`, `CALL` and so on.

AI Max is an optimisation layer on a Search campaign, not a campaign type. Add to the campaign body:

```jsonc
"aiMaxSetting": {"enableAiMax": true},
"assetAutomationSettings": [
  {"assetAutomationType": "TEXT_ASSET_AUTOMATION", "assetAutomationStatus": "OPTED_IN"},
  {"assetAutomationType": "FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION", "assetAutomationStatus": "OPTED_IN"}
],
"textGuidelines": {"termExclusions": ["free"],
  "messagingRestrictions": [{"restrictionText": "Do not mention competitors", "restrictionType": "RESTRICTION_BASED_EXCLUSION"}]}
// ad group, to switch search term matching off: "aiMaxAdGroupSetting": {"disableSearchTermMatching": true}
```

Rules: opting in to automation without `enableAiMax` gives `AI_MAX_MUST_BE_ENABLED`; final-URL expansion without text automation gives `OPERATION_NOT_PERMITTED_FOR_CONTEXT`; never set `keywordMatchType` on the campaign (deprecated). `termExclusions`: at most 25 items of 30 characters; `messagingRestrictions`: at most 40 of 300 characters.

## 4. Performance Max

Validated, not launched: on 2026-11-25 Google accepted a plan of this shape in the dry run (`maximizeConversions`, one location, one search theme, no audience signal). Nothing was created from it, so the `launch plan` validation stays its test.

Docs: https://developers.google.com/google-ads/api/performance-max/getting-started and https://developers.google.com/google-ads/api/performance-max/create-campaign. A plan step is applied whole or not at all. Aspect ratios are checked when an asset is linked (`ASPECT_RATIO_NOT_ALLOWED`), not when it is created.

- Needs conversion tracking on the account. Bidding is only `maximizeConversionValue` (optional `targetRoas`, 3.5 = 350 percent) or `maximizeConversions` (optional `targetCpaMicros`). No portfolio strategy. Leave `advertisingSubChannelType` unset.
- Budget: daily and `explicitlyShared: false`. At most 100 Performance Max campaigns per account and 100 asset groups per campaign.
- Brand guidelines are on by default (`brandGuidelinesEnabled`, immutable, settable only at creation): the business name and logo are linked to the campaign with `campaignAssetOperation` (`BUSINESS_NAME` once, `LOGO` one to five, optional `LANDSCAPE_LOGO`), not to the asset group. Put these operations directly after the campaign operation. With guidelines off they go on the asset group.
- Order in one mutate: budget, all asset operations, campaign, campaign assets, asset group, asset group assets (one consecutive block), then optional criteria and signals. The asset group and its minimum assets travel in the same request.
- Identical bytes in two create operations give `DUPLICATE_ASSET`: create an image once and link it once per use, and use different files for the logo and the square image.

| Asset group field | Min and max | Limit |
|---|---|---|
| `HEADLINE` | 3 to 15 | 30 characters |
| `LONG_HEADLINE` | 1 to 5 | 90 characters |
| `DESCRIPTION` | 2 to 5 | 90 characters; at least one at most 60 is advised by Google but not enforced here |
| `MARKETING_IMAGE` | 1 to 20 | 1.91:1, 1200x628 advised, minimum 600x314, up to 5120 KB |
| `SQUARE_MARKETING_IMAGE` | 1 to 20 | 1:1, 1200x1200 advised, minimum 300x300 |
| `PORTRAIT_MARKETING_IMAGE` | optional, up to 20 | 4:5, minimum 480x600 |
| `LOGO` (campaign level) | 1 to 5 | 1:1, minimum 128x128 |
| `BUSINESS_NAME` (campaign level) | exactly 1 | 25 characters |
| `YOUTUBE_VIDEO` | optional, up to 15 | at least 10 seconds |

An image asset carries its file through the toolkit: `{"@base64": "ads/creatives/<file>.png"}` inside `imageAsset.data` is replaced by the base64 content before sending. To reuse an asset that already exists (for example one made with the MCP server in section 8), pass its resource name, `customers/{customer}/assets/111`, in place of a temporary one.

An `imageAsset` needs a `name` beside its `resourceName`; a `textAsset` and a `youtubeVideoAsset` do not. Without it Google answers `NAME_REQUIRED_FOR_ASSET_TYPE` and, in the same reply, fails whatever leans on an asset of the request: `RESOURCE_NOT_FOUND`, `REQUIRED_LOGO_ASSET_NOT_LINKED`, even `NOT_ENOUGH_HEADLINE_ASSET` with all headlines in place. Add the name, run the dry run again, and only then read what is left. Give every image its own name: Google documents `DUPLICATE_ASSET_NAME`, although its validation let a repeated name pass (a real create with one was not tried).

Uploading an image whose bytes already exist in the account returns the existing asset and silently drops the new name (seen live on 2026-11-25: the second plan of a pair got the asset ids of the first test back). Do not rely on the name to tell two plans' assets apart. A rollback leaves such shared assets alone in any case.

An asset cannot be deleted: the API has `create` and `update` for it and no `remove`. After `launch rollback --remove` the campaign and its budget are `REMOVED` and the assets stay in the account's library, unused and free of charge.

```jsonc
// inside "with": {"partialFailure": false, "mutateOperations": [ ... ]}; ids -10 to -19 are assets
[
  {"campaignBudgetOperation": {"create": {"resourceName": "customers/{customer}/campaignBudgets/-1", "name": "Example PMax budget", "deliveryMethod": "STANDARD", "amountMicros": "30000000", "explicitlyShared": false}}},
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-10", "textAsset": {"text": "Example Brand"}}}},
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-11", "name": "Example logo 1x1", "imageAsset": {"data": {"@base64": "ads/creatives/logo-1x1.png"}}}}},
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-12", "textAsset": {"text": "Headline one"}}}},
  // same shape: -13, -14 headlines; -15 long headline; -16, -17 descriptions (textAsset)
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-18", "name": "Example landscape 1200x628", "imageAsset": {"data": {"@base64": "ads/creatives/landscape-1200x628.png"}}}}},
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-19", "name": "Example square 1200x1200", "imageAsset": {"data": {"@base64": "ads/creatives/square-1200x1200.png"}}}}},
  {"campaignOperation": {"create": {"resourceName": "customers/{customer}/campaigns/-2", "name": "Example PMax US", "status": "PAUSED", "advertisingChannelType": "PERFORMANCE_MAX",
    "campaignBudget": "customers/{customer}/campaignBudgets/-1", "maximizeConversionValue": {}, "brandGuidelinesEnabled": true,
    "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"}}},
  {"campaignAssetOperation": {"create": {"campaign": "customers/{customer}/campaigns/-2", "asset": "customers/{customer}/assets/-10", "fieldType": "BUSINESS_NAME"}}},
  {"campaignAssetOperation": {"create": {"campaign": "customers/{customer}/campaigns/-2", "asset": "customers/{customer}/assets/-11", "fieldType": "LOGO"}}},
  {"assetGroupOperation": {"create": {"resourceName": "customers/{customer}/assetGroups/-3", "campaign": "customers/{customer}/campaigns/-2", "name": "Asset group 1", "finalUrls": ["https://example.com/"], "status": "ENABLED"}}},
  // one consecutive block, nothing in between
  {"assetGroupAssetOperation": {"create": {"assetGroup": "customers/{customer}/assetGroups/-3", "asset": "customers/{customer}/assets/-12", "fieldType": "HEADLINE"}}},
  // same shape: -13, -14 HEADLINE; -15 LONG_HEADLINE; -16, -17 DESCRIPTION; -18 MARKETING_IMAGE; -19 SQUARE_MARKETING_IMAGE
  // signals after the asset group assets, one per operation
  {"assetGroupSignalOperation": {"create": {"assetGroup": "customers/{customer}/assetGroups/-3", "searchTheme": {"text": "running shoes"}}}},
  {"assetGroupSignalOperation": {"create": {"assetGroup": "customers/{customer}/assetGroups/-3", "audience": {"audience": "customers/{customer}/audiences/123"}}}},
  {"campaignCriterionOperation": {"create": {"campaign": "customers/{customer}/campaigns/-2", "location": {"geoTargetConstant": "geoTargetConstants/2840"}}}}
]
```

If a validation error names the geo operation or the campaign assets, move that operation directly after the campaign operation. Retail (feed) Performance Max needs `shoppingSetting.merchantId` and a listing group filter tree: not covered here.

## 5. Demand Gen

Run live on 2026-11-25 with the multi-asset image ad, the second sample of this section: created paused, read back, removed. The video ad, the first sample, passed Google's validation the same day and was not created.

Docs: https://developers.google.com/google-ads/api/docs/demand-gen/create-campaign

| Rule | Value |
|---|---|
| Minimum daily budget | 5 USD or the local equivalent; below it `BUDGET_BELOW_PER_DAY_MINIMUM`. Read the exact minimum for the account currency in section 6. Google advises at least 15 times the target CPA. |
| Budget | `explicitlyShared: false`, daily or total. A total budget (`totalAmountMicros`) is a lifetime budget: the toolkit refuses it unless the user has set `guardrails.max_total_budget` in `ads/config.json`, and the plan must declare it as `"budget": {"total": N}`. |
| Channel | `DEMAND_GEN`; no sub type. Conversion goals must exist. |
| Bidding | Maximize clicks (`targetSpend`), `maximizeConversions`, `targetCpa` (`{"targetCpaMicros": "..."}`), target ROAS. |
| Ad group | Do not set `type`. Channels go in `demandGenAdGroupSettings.channelControls.selectedChannels`. |
| Video ad | `videos`, `logoImages` and `businessName` (an object `{"text": "..."}`) are all required; plus headlines, long headlines and descriptions. |
| Multi-asset ad | `businessName` (a plain string, 25 characters), 1 to 5 headlines (30), 1 to 5 descriptions (90), 1 to 5 `logoImages` (1:1, 128x128 minimum), and at least one marketing image (1.91:1) or square image. |
| Images, videos | Reference an asset as `{"asset": "customers/{customer}/assets/-11"}`. A video asset needs an existing YouTube video: `youtubeVideoAsset.youtubeVideoId`, 11 characters. An image asset needs a `name` (section 4). |
| Location and language | Campaign level only if you create the campaign with `demandGenCampaignSettings.upgradedTargeting` (immutable); otherwise on the ad group. |

```jsonc
// inside "with": {"partialFailure": false, "mutateOperations": [ ... ]}
[
  {"campaignBudgetOperation": {"create": {"resourceName": "customers/{customer}/campaignBudgets/-1", "name": "Example DG budget", "deliveryMethod": "STANDARD", "amountMicros": "20000000", "explicitlyShared": false}}},
  {"campaignOperation": {"create": {"resourceName": "customers/{customer}/campaigns/-2", "name": "Example Demand Gen US", "status": "PAUSED", "advertisingChannelType": "DEMAND_GEN",
    "campaignBudget": "customers/{customer}/campaignBudgets/-1", "maximizeConversions": {}, "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"}}},
  {"adGroupOperation": {"create": {"resourceName": "customers/{customer}/adGroups/-3", "campaign": "customers/{customer}/campaigns/-2", "name": "Example DG ad group", "status": "ENABLED",
    "demandGenAdGroupSettings": {"channelControls": {"selectedChannels": {"gmail": false, "discover": false, "display": false, "youtubeInFeed": true, "youtubeInStream": true, "youtubeShorts": true}}}}}},
  // location and language sit on the ad group here; without them the ad group targets every country
  {"adGroupCriterionOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "location": {"geoTargetConstant": "geoTargetConstants/2840"}}}},
  {"adGroupCriterionOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "language": {"languageConstant": "languageConstants/1000"}}}},
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-10", "youtubeVideoAsset": {"youtubeVideoId": "YOUTUBE_ID_11CH"}}}},
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-11", "name": "Example logo 1x1", "imageAsset": {"data": {"@base64": "ads/creatives/logo-1x1.png"}}}}},
  {"adGroupAdOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "status": "ENABLED",
    "ad": {"name": "Example video ad", "finalUrls": ["https://example.com/"], "demandGenVideoResponsiveAd": {
      "businessName": {"text": "Example Brand"}, "videos": [{"asset": "customers/{customer}/assets/-10"}], "logoImages": [{"asset": "customers/{customer}/assets/-11"}],
      "headlines": [{"text": "Shoes built to run"}], "longHeadlines": [{"text": "Light, fast, comfortable running shoes"}],
      "descriptions": [{"text": "Free returns for 30 days"}]}}}}}
]
```

The multi-asset image ad, in the shape that ran live: channels that show images, image assets in place of the video.

```jsonc
// inside "with": {"partialFailure": false, "mutateOperations": [ ... ]}
[
  {"campaignBudgetOperation": {"create": {"resourceName": "customers/{customer}/campaignBudgets/-1", "name": "Example DG image budget", "deliveryMethod": "STANDARD", "amountMicros": "20000000", "explicitlyShared": false}}},
  {"campaignOperation": {"create": {"resourceName": "customers/{customer}/campaigns/-2", "name": "Example Demand Gen images UK", "status": "PAUSED", "advertisingChannelType": "DEMAND_GEN",
    "campaignBudget": "customers/{customer}/campaignBudgets/-1", "maximizeConversions": {}, "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"}}},
  {"adGroupOperation": {"create": {"resourceName": "customers/{customer}/adGroups/-3", "campaign": "customers/{customer}/campaigns/-2", "name": "Example DG image ad group", "status": "ENABLED",
    "demandGenAdGroupSettings": {"channelControls": {"selectedChannels": {"gmail": true, "discover": true, "display": false, "youtubeInFeed": false, "youtubeInStream": false, "youtubeShorts": false}}}}}},
  {"adGroupCriterionOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "location": {"geoTargetConstant": "geoTargetConstants/2826"}}}},
  {"adGroupCriterionOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "language": {"languageConstant": "languageConstants/1000"}}}},
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-10", "name": "Example landscape 1200x628", "imageAsset": {"data": {"@base64": "ads/creatives/landscape-1200x628.png"}}}}},
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-11", "name": "Example square 1200x1200", "imageAsset": {"data": {"@base64": "ads/creatives/square-1200x1200.png"}}}}},
  {"assetOperation": {"create": {"resourceName": "customers/{customer}/assets/-12", "name": "Example logo 1x1", "imageAsset": {"data": {"@base64": "ads/creatives/logo-1x1.png"}}}}},
  {"adGroupAdOperation": {"create": {"adGroup": "customers/{customer}/adGroups/-3", "status": "ENABLED",
    "ad": {"name": "Example image ad", "finalUrls": ["https://example.com/"], "demandGenMultiAssetAd": {
      "businessName": "Example Brand", "headlines": [{"text": "Shoes built to run"}, {"text": "Made for long distances"}],
      "descriptions": [{"text": "Free returns for 30 days"}, {"text": "Find your size in a minute"}],
      "marketingImages": [{"asset": "customers/{customer}/assets/-10"}], "squareMarketingImages": [{"asset": "customers/{customer}/assets/-11"}],
      "logoImages": [{"asset": "customers/{customer}/assets/-12"}]}}}}}
]
```

Audience targeting needs `audienceSetting.useAudienceGrouped: true` on the ad group (immutable) and an `adGroupCriterionOperation` with `audience` set to an audience resource name (unverified in a live run). The campaign stays PAUSED until activation, even though the ad is created ENABLED. The EU declaration in the samples is a placeholder for the user's answer, as in section 2.

Seen live on 2026-11-26 on a Demand Gen campaign with the image ad above: Google added an ad of its own to the image ad group, type `DEMAND_GEN_VIDEO_RESPONSIVE_AD`, named "(<ad name>) auto-generated video ad". It was approved, did not appear in the change history, and went away with the campaign. Treat an extra ad in the group as normal. On the same campaign `startDateTime` and `endDateTime` (for example "2026-11-26 00:00:00", in the account time zone) and `targetSpend` (Maximize clicks) were accepted.

## 6. Look-ups

Geo ids: resolve names, then use `geoTargetConstants/<id>` in the criterion. Known ids: `2840` United States, `21167` New York state. Never guess an id.

```bash
python3 ads/tools/ads.py google geo --query "Berlin" --country DE --locale en
```

```bash
python3 ads/tools/ads.py google search --query "SELECT conversion_action.id, conversion_action.name, conversion_action.status, conversion_action.type, conversion_action.category, conversion_action.primary_for_goal, conversion_action.include_in_conversions_metric FROM conversion_action WHERE conversion_action.status = 'ENABLED'"
python3 ads/tools/ads.py google search --query "SELECT audience.id, audience.name, audience.status FROM audience"
python3 ads/tools/ads.py google search --query "SELECT currency_constant.code, currency_constant.demand_gen_info.minimum_budget_per_day_micros FROM currency_constant WHERE currency_constant.code = 'USD'"
```

The audience field names are unverified: if the query fails, read the real fields with `metadata_get_resource_metadata` of the MCP server (section 8). Bidding and the conversions metric use only actions with `include_in_conversions_metric = true`; goal-level bidding uses `primary_for_goal`. If no row qualifies, do not use conversion bidding, Performance Max or Demand Gen: use Search with Maximize clicks or tell the user to set up tracking first. Language criteria (`SELECT language_constant.id, language_constant.name FROM language_constant`; English is `languageConstants/1000`) are for Demand Gen and Performance Max only, never Search.

## 7. Dry run, apply, verify, activate

```bash
python3 ads/tools/ads.py launch plan --file ads/launch/search-example-us.json
```

`launch plan` validates the plan and sends the body with `validateOnly` (nothing is created; it needs Explorer on production accounts). Read the eight blocks, above all PRECHECK and VALIDATE. Exit code 2 means the plan is blocked: a guard rail (paused status, a budget above the ceiling, a declared budget that differs from what the steps carry) or a rejection by Google's validation; the lines marked `FAIL` say which. `launch apply` runs only after a clean dry run of the same plan, with the same files, account ids and currency: after any edit, run `launch plan` again and show it.

Reading a validation error: the platform returns a list of errors, each with an error code (`REQUIRED_FIELD_MISSING`, `TOO_LONG`, `DUPLICATE_TEMP_IDS` ...), a message, and a `location.fieldPathElements` list. The first element names `mutate_operations` and carries `index`: the position of the failing operation, counted from 0, in `mutateOperations` of the step. The next elements give the field path inside it (for example `campaign_operation`, `create`, `contains_eu_political_advertising`). Open that operation, fix the named field, and run the dry run again. An error `TEMP_ID_RESOURCE_HAD_ERRORS` is a side effect: fix the first error of the list, the parent.

```bash
python3 ads/tools/ads.py launch apply --file ads/launch/search-example-us.json --yes
python3 ads/tools/ads.py launch status --file ads/launch/search-example-us.json
```

`launch apply` creates everything in one request, with the campaign paused, and records the resource names in `ads/launch/ledger.jsonl`. If the request ends without a clear answer (a timeout, a server error), the campaign may exist although the ledger does not hold it: `launch apply` then refuses to run again until you have looked for the campaign by name with the query below. If it is there, it is paused: remove it only with the user's agreement (`google mutate` with a `remove` operation, shown without `--yes` first). Found or not, `--resend` sends the request again, so ask the user before it. Check what was created before spending anything:

```bash
python3 ads/tools/ads.py google search --query "SELECT campaign.id, campaign.name, campaign.status, campaign.primary_status, campaign.contains_eu_political_advertising, campaign_budget.amount_micros, ad_group_ad.ad_strength, ad_group_ad.policy_summary.approval_status, ad_group_ad.status FROM ad_group_ad WHERE campaign.name = 'Example Search US' AND ad_group_ad.status != 'REMOVED'"
python3 ads/tools/ads.py google search --query "SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.status, ad_group_criterion.approval_status FROM ad_group_criterion WHERE campaign.name = 'Example Search US' AND ad_group_criterion.type = 'KEYWORD'"
```

Expected: campaign PAUSED, budget as planned, keywords present, ad approval status `APPROVED` or `APPROVED_LIMITED`. `DISAPPROVED` is a policy problem: change the text. A policy exemption request (resend with `policyValidationParameter.ignorablePolicyTopics` on the ad operation, or `exemptPolicyViolationKeys` on a keyword operation) asks Google to review a policy decision in the advertiser's name, and nothing serves until it is approved. It is the user's call: propose it, and send it only after their yes, through `google mutate` without `--yes` first and with `--yes` after.

```bash
python3 ads/tools/ads.py launch activate --file ads/launch/search-example-us.json
python3 ads/tools/ads.py launch activate --file ads/launch/search-example-us.json --yes
python3 ads/tools/ads.py launch rollback --file ads/launch/search-example-us.json --yes
python3 ads/tools/ads.py launch rollback --file ads/launch/search-example-us.json --remove --yes
```

The first line changes nothing: Google validates the status change, and the toolkit prints what would be enabled and the budget of the plan. Show that to the user. With `--yes`, `launch activate` enables the campaigns the plan created, which starts spend: run it only after the user's explicit yes to the daily budget stated in words. After it, run the first query again and confirm `campaign.status` is `ENABLED` and the ad is `ENABLED`. `launch rollback` pauses what the plan created; `--remove` removes it instead, only when the user asks for removal. Reusing a name after a failed apply: remove first, or names clash (`DUPLICATE_CAMPAIGN_NAME`).

## 8. The official MCP server in a launch

The plugin's `google-ads` MCP server is Google's official server (pre-1.0; tool names changed in v0.0.6, so check the tool list before relying on a name). It complements the toolkit: it reads, and it creates assets; it cannot create or change a campaign. Its writes go into the ad account without the toolkit's ledger, so before each one tell the user what will be created and wait for their yes.

| Tool | Can do |
|---|---|
| `customers_list_accessible_customers`, `metadata_get_resource_metadata` | List reachable accounts; field names and types (use before a query with an unverified field). |
| `search_search` | Read through a structured query (`customer_id`, `resource`, `fields`, `conditions`, `orderings`, `limit`, `login_customer_id`): reporting and read-back. |
| `assets_create_asset` | Create TEXT, IMAGE (up to 20 MB), YOUTUBE_VIDEO, SITELINK, CALLOUT, STRUCTURED_SNIPPET assets (PRICE, PROMOTION, CALL via extra parameters). |
| `assets_upload_video_asset` | Upload a video file to YouTube through the Ads account (stdio only); returns an upload id, then the video id once processed. |
| `labels_manage_labels`, `labels_manage_label_associations` | Labels. |

Every write of the server is validated first and returns a checksum; the confirm call must repeat the same parameters and the checksum.

It cannot create or change campaigns, ad groups, ads, budgets, bids or keywords, and it cannot link an asset to a campaign, ad group or asset group. So linking stays in the plan: create the asset with the MCP server after the user's yes, read its resource name with `search_search` (resource `asset`), and put `customers/{customer}/assets/<id>` in `assetGroupAssetOperation`, `campaignAssetOperation` or an ad.

Use it for: a video for Demand Gen or Performance Max (otherwise the user uploads it to YouTube and you pass the 11-character id); an image you want to keep out of the plan; reporting after launch. The video upload has no dry run and puts the file on the YouTube channel of the account: name the file and the channel to the user and upload only after their yes.

## 9. Limits and errors

| Limit | Value |
|---|---|
| Daily operations per Cloud project | Test 15,000 (test accounts); Explorer 2,880 production and 15,000 test; Basic 15,000; Standard unlimited. Over it: `RESOURCE_EXHAUSTED`. |
| What counts | Each operation of a mutate, each search request (once). Rejected requests count too, so a dry run, an apply and a retry all spend operations. The Search plan above is 8 operations; a Performance Max plan is 25 or more. |
| Per request | 10,000 mutate operations (`TOO_MANY_MUTATE_OPERATIONS`); responses up to 64 MB. |
| Rate | Per customer and per project; `RESOURCE_TEMPORARILY_EXHAUSTED`: wait and retry with backoff (2, 4, 8 seconds). |

| Error | Cause and fix |
|---|---|
| `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION`, `CUSTOMER_NOT_ENABLED` | Test access on a production account: apply for Explorer or use a test account. Account unfinished or cancelled: finish sign-up in the Google Ads interface. |
| `USER_PERMISSION_DENIED`, `CLIENT_CUSTOMER_ID_INVALID` | Set `GOOGLE_ADS_LOGIN_CUSTOMER_ID` to the manager's id; ids are digits only, no hyphens. |
| `invalid_grant` | Refresh token expired; the consent screen is still in Testing (7-day tokens). Publish it, then run `google login` again. |
| `OPERATION_NOT_PERMITTED_FOR_CONTEXT` | Language criterion on Search, or AI Max final-URL expansion without text automation. Remove or opt in first. |
| `MISSING_EU_POLITICAL_ADVERTISING_SELF_DECLARATION` | Add `containsEuPoliticalAdvertising` to the campaign. |
| `DUPLICATE_TEMP_IDS`, `TEMP_ID_RESOURCE_HAD_ERRORS` | Reused negative id, or a parent failed. Use unique ids; fix the first error. |
| `REQUIRED_FIELD_MISSING`, `TOO_LONG`, `LINE_TOO_WIDE` | See the field path; check the character limits in sections 2 and 4. |
| `NAME_REQUIRED_FOR_ASSET_TYPE` | An image asset without a `name`. Add it first (section 4): the other errors of the same reply usually follow from it. |
| `DUPLICATE_CAMPAIGN_NAME`, `DUPLICATE_ADGROUP_NAME`, `BID_TOO_MANY_FRACTIONAL_DIGITS`, `NON_MULTIPLE_OF_MINIMUM_CURRENCY_UNIT` | Unique names; round micros to the currency's minimum unit. |
| `BUDGET_BELOW_PER_DAY_MINIMUM` | Demand Gen budget under the minimum: query it (section 6). |
| `AI_MAX_MUST_BE_ENABLED`, `CANNOT_SET_CAMPAIGN_KEYWORD_MATCH_TYPE` | Enable AI Max first; drop `keywordMatchType`. |
| `ASPECT_RATIO_NOT_ALLOWED`, missing asset group assets, `DUPLICATE_ASSET` | Wrong image ratio, or minimum assets absent: send all required links in the same request. Same bytes twice: create once, link by temporary id. |
| `AD_SHARING_NOT_ALLOWED`, `PolicyFindingError`, `PolicyViolationError` | Same ad in several ad groups: create separate ads. Policy violation: change the content. |
