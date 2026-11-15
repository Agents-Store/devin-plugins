# Audience and geo research recipes

Exact calls to find targeting ids and size audiences on Meta, TikTok and Google, and a template for the targeting spec the next step reads. Raw output goes to `ads/research/raw/`, the spec to `ads/research/audiences.md`.

## Contents

- Meta
- TikTok
- Google
- Targeting spec template

Run every command from the project root. Targeting ids change: resolve them at research time and validate them again just before launch.

## Meta

`{account}` in a path becomes the ad account id from `ads/.env`. All research calls are reads and cost nothing.

### Interests, geo and categories

```bash
python3 ads/tools/ads.py meta search --type adinterest --q running -p limit=10
python3 ads/tools/ads.py meta search --type adgeolocation --q Berlin -p 'location_types=["city"]'
python3 ads/tools/ads.py meta get search -p type=adinterestsuggestion -p 'interest_list=["Basketball"]'
python3 ads/tools/ads.py meta get search -p type=adinterestvalid -p 'interest_fbid_list=["1234567890"]'
python3 ads/tools/ads.py meta get search -p type=adTargetingCategory -p class=behaviors
```

- `adinterest` (`q`): `id`, `name`, `path`, audience size. `adinterestsuggestion` (`interest_list`, case sensitive): related interests with `audience_size`. `adinterestvalid` (`interest_fbid_list`): is the id still valid.
- `adgeolocation` (`q`, optional `location_types`: `country`, `country_group`, `region`, `city`, `zip`, `geo_market`, `electoral_district`; also `match_country_code`, `country_code`, `region_id`): returns `key`. Put the `key` in targeting, not the name.
- `adTargetingCategory` needs `class`: `interests`, `behaviors`, `demographics`, `life_events`, `industries`, `income`, `family_statuses`, `user_device`, `user_os`. Also `adlocale` (language ids) and `targetingoptionstatus` (`NORMAL`, `NON-DELIVERABLE`, `DEPRECATING`).
- `limit` defaults to 8; results are not exhaustive: search several words. Validate every interest id with `adinterestvalid` right before the ad set is created: interests were consolidated and names change.
- Docs: https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/reference/targeting-search.md

### Reach and delivery estimates

Write the targeting spec once, then estimate. Keys inside `geo_locations` come from `adgeolocation`.

```bash
cat > ads/research/raw/spec-meta.json <<'EOF'
{"geo_locations": {"cities": [{"key": "<KEY>"}]},
 "age_min": 25, "age_max": 45,
 "interests": [{"id": "<ID>", "name": "Running"}]}
EOF
python3 ads/tools/ads.py meta get "{account}/reachestimate" \
  -p "targeting_spec=$(jq -c . ads/research/raw/spec-meta.json)" -p optimize_for=IMPRESSIONS
python3 ads/tools/ads.py meta get "{account}/delivery_estimate" \
  -p "targeting_spec=$(jq -c . ads/research/raw/spec-meta.json)" -p optimization_goal=REACH
```

- `reachestimate` needs `targeting_spec` and `optimize_for`; its response fields are not documented: read the response as it comes and save it.
- `delivery_estimate` needs `optimization_goal` and `targeting_spec`; `promoted_object` is optional. The daily curve, budget guardrail and daily active user estimate were removed in v26: do not look for them. The names of the monthly audience bounds are unverified.
- Suggestions from an ad account: `{account}/targetingsuggestions` with `-p 'targeting_list=[{"type":"interests","id":"<ID>"}]'`.
- Docs: https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/guides/reach-estimate.md

## TikTok

`advertiser_id` is added to every call. IDs from here feed the ad group: `location_ids`, `interest_category_ids`, `action_category_ids`, `purchase_intention_keyword_ids`, `languages`.

```bash
python3 ads/tools/ads.py tiktok get search/region/
python3 ads/tools/ads.py tiktok get tool/language/
python3 ads/tools/ads.py tiktok get tool/interest_category/
python3 ads/tools/ads.py tiktok get tool/action_category/
python3 ads/tools/ads.py tiktok get targeting/search/ -p targeting_type=INTEREST_AND_BEHAVIOR \
  -p 'sub_targeting_types=["GENERAL_INTEREST","HASHTAG_INTERACTION"]' -p search_keywords=running
python3 ads/tools/ads.py tiktok get tool/hashtag/recommend/ -p 'keywords=["running","marathon"]'
python3 ads/tools/ads.py tiktok get discovery/trending_list/ -p discovery_type=HASHTAG
```

| Path | What it gives | Notes |
|---|---|---|
| `tool/language/`, `tool/interest_category/`, `tool/action_category/` | language codes, general interest categories, behaviour categories | enum lists |
| `search/region/` | all locations the advertiser can target, with `parent_id` and `region_level` | only needs the advertiser |
| `tool/region/` | locations for a given objective and placement | needs `placements` and `objective_type`; `level_range`: `ALL`, `TO_COUNTRY`, `TO_PROVINCE`, `TO_CITY`, `TO_DISTRICT` |
| `targeting/search/` | interests, behaviours and hashtags by keyword | `targeting_type=INTEREST_AND_BEHAVIOR` is required; `sub_targeting_types`: `GENERAL_INTEREST`, `ADDITIONAL_INTEREST`, `PURCHASE_INTENTION`, `VIDEO_INTERACTION`, `CREATOR_INTERACTION`, `HASHTAG_INTERACTION`; `language` defaults to `en` |
| `tool/hashtag/recommend/` | hashtags for seed keywords | at most 10 keywords |
| `discovery/trending_list/` | top 200 popular hashtags | |
| `tool/search_keyword/keyword_idea/` | search ads keyword ideas | at most 10 keywords, English only |

- Behaviour ids from `targeting/search/` go to `action_category_ids`, together with `action_scene`: `VIDEO_RELATED`, `CREATOR_RELATED`, `HASHTAG_RELATED`.
- A path for interest keywords named `tool/interest_keyword/recommend/` does not exist in the current docs: use `targeting/search/`.

Audience size. This is a POST that only estimates and creates nothing: the toolkit treats a path ending in `estimate` as a read, so it runs without `--yes`.

```bash
cat > ads/research/raw/req-tt-size.json <<'EOF'
{"objective_type": "TRAFFIC", "optimization_goal": "<GOAL>",
 "placements": ["<PLACEMENT>"], "location_ids": ["<LOCATION_ID>"]}
EOF
python3 ads/tools/ads.py tiktok post ad/audience_size/estimate/ --data @ads/research/raw/req-tt-size.json
```

The body mirrors the ad group create body: add `operating_systems` and the interest ids to narrow it. Check the response for an error naming a missing field and add it; the exact required set is not documented in the notes.

- Docs: https://business-api.tiktok.com/portal/docs/search-for-or-list-targeting-categories-and-hashtags-for-interests-and-behaviors/v1.3

## Google

Search campaigns target by keywords, geo and, optionally, audience segments. Audiences matter for Performance Max, Demand Gen and remarketing.

### Geo targets

```bash
python3 ads/tools/ads.py google geo --query "New York" --country US --locale en
```

- Returns `geoTargetConstants/<id>`, `name`, `canonicalName`, `countryCode`, `targetType`, `status`. Up to 25 names per call. Use the resource name in the launch plan.
- A GAQL alternative: `google search --query "SELECT geo_target_constant.id, geo_target_constant.name, geo_target_constant.canonical_name, geo_target_constant.country_code, geo_target_constant.target_type FROM geo_target_constant WHERE geo_target_constant.name = 'Paris'"`.
- Radius targeting: at most 800 km (500 miles).
- Docs: https://developers.google.com/google-ads/api/docs/targeting/location-targeting

### Languages and audience segments

```bash
python3 ads/tools/ads.py google search --query "SELECT language_constant.id, language_constant.code, language_constant.name, language_constant.targetable FROM language_constant"
python3 ads/tools/ads.py google search --query "SELECT audience.id, audience.name, audience.status FROM audience"
```

- `languageConstants/1000` is English. Search campaigns no longer accept a language criterion; the language id is still used for keyword research.
- The `audience` query fields are unverified: if the call is rejected, drop the fields one by one.
- Reusable segments: `Audience` resources group remarketing lists (`user_list`), `user_interest`, `custom_audience`, `combined_audience` and lookalike segments (Demand Gen). Performance Max passes them as an audience signal, Demand Gen as an ad group criterion. Building them is a launch step, not research.
- Customer Match uploads need allowlisting: do not plan on them without confirming access.

## Targeting spec template

Save this to `ads/research/audiences.md`, one block per platform, with real ids filled in. The media plan and launch steps read it as is.

```text
# Targeting spec

## Meta
geo:        <adgeolocation keys>, type: country | region | city
languages:  <adlocale ids> or none
age:        <min>-<max>
genders:    all | male | female
interests:  <id> <name> (validated <date>)
behaviours: <id> <name> or none
exclusions: <existing customers, converters, interests to exclude>
estimate:   reach <low>-<high>, optimize_for <goal>, checked <date>

## TikTok
geo:        <location_ids>
languages:  <language codes>
age:        <age groups>
interests:  <interest_category_ids>
behaviours: <action_category_ids> + <action_scene>
hashtags:   <hashtag ids or names>
exclusions: <categories or audiences to exclude>
estimate:   audience size <value>, checked <date>

## Google
geo:        <geoTargetConstants ids>
languages:  <languageConstants ids>
age:        <age ranges, or none for Search>
keywords:   see ads/research/keywords.md, <ad group themes>
audiences:  <segment names or ids>, mode: observation | targeting
exclusions: <negative keywords, excluded places, excluded audiences>
```

Mark any id that could not be resolved as `UNRESOLVED` instead of guessing it.
