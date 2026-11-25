# Ads error look-up: cause and fix by service

Use this file when a toolkit command, an API call or an MCP server returns an error. Find the service, match the message in "what you see", apply the fix. Facts were verified on 2026-11-14; a row marked "(unverified)" or "(error text not in the notes)" has a cause that was not confirmed on an official page.

## Contents

- First steps for any failure
- Google Ads
- Search Console
- Meta
- TikTok
- OpenAI
- Gemini
- fal.ai
- Firecrawl
- Apify
- DataForSEO
- MCP servers of the plugin
- Dated deadlines, next six months

## First steps for any failure

1. Check the one service. `doctor --live` makes one cheap read-only call and, for a missing or rejected key, prints where to get one. `--only` takes `firecrawl, apify, dataforseo, openai, gemini, fal, google, gsc, meta, tiktok`.

```bash
python3 ads/tools/ads.py doctor --live --only google,gsc
python3 ads/tools/ads.py keys
```

2. Read the toolkit exit code: 1 = the service returned an error, the message carries its code and text, find it below; 2 = wrong usage or a guard rail refused the call (spend ceiling, not paused, budget above `guardrails.max_daily_budget`), fix the command; whether a ceiling in `ads/config.json` is raised is the user's decision, never a way past the refusal; 3 = a required key is missing, fill it in `ads/.env` (`keys` shows which; for MCP also run `env sync-claude`).
3. Do not trust the HTTP status alone: TikTok and DataForSEO answer HTTP 200 with the real status in the body, Google Ads with `partialFailure` returns failures inside a success, a Meta `validate_only` pass is not the final ad review.
4. After a write that ended in a timeout or a server error, do not repeat it at once: the platform may have applied it. Read back what exists first (`launch status`, the ledger, a read call by name).
5. Keep the request id with the report: Google Ads header `request-id`; TikTok `request_id` in the body; OpenAI header `x-request-id`; fal.ai header `x-fal-request-id` and the queue `request_id`; DataForSEO `tasks[].id` with `tasks[].status_code`; Apify the run `id`. Meta, Firecrawl, Gemini and Search Console document none in the notes: keep the full error body.

## Google Ads

Reference: `https://developers.google.com/google-ads/api/docs/get-started/common-errors`. Developer tokens were sunset on 2026-09-09: access levels belong to the Cloud project that owns the OAuth client. A `developer-token` header is optional and ignored; doc pages that still call it required are stale.

| What you see | Cause | Fix |
|---|---|---|
| `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION` (`ACTION_NOT_PERMITTED` in API v24 and earlier) | project has Test access, call targets a production account | use a test account, or apply for Explorer on the API Overview page of the project that owns the OAuth client |
| `USER_PERMISSION_DENIED` | the user has no access to the account, usually a manager id is missing | set `GOOGLE_ADS_LOGIN_CUSTOMER_ID` (10 digits, no hyphens) in `ads/.env`; check `google customers` |
| `NOT_ADS_USER` | the Google login that gave the consent has no Google Ads account; often it is the login that owns the Cloud project | `google login` again and pick the login that opens `ads.google.com`, or add this login to the account |
| **Publish app** greyed out on the Audience page of the OAuth app | Branding lacks the application home page, the privacy policy link or the authorized domain | Google key guide, Step 3 |
| `CUSTOMER_NOT_ENABLED` | sign-up unfinished, or account cancelled or deactivated | finish or reactivate in the Google Ads UI; read `customer.status` with `google search` |
| `CUSTOMER_NOT_FOUND`; `CLIENT_CUSTOMER_ID_INVALID` | account just created; hyphens in the id | wait 5 minutes, retry every 30 s; digits only in `GOOGLE_ADS_CUSTOMER_ID` |
| `invalid_grant` | refresh token expired or revoked; a consent screen in "Testing" expires tokens after 7 days | set the consent screen to "In production", then `google login` and `google login --redirect-url URL` |
| `ACCESS_TOKEN_SCOPE_INSUFFICIENT`; `OAUTH_TOKEN_INVALID`; `GOOGLE_ACCOUNT_COOKIE_INVALID`; `NOT_ADS_USER` | token lacks the `adwords` scope, is wrong or expired, or the Google account has no Ads access | `google login --scopes ads`, finish with `--redirect-url`; invite the account in the Ads UI under Admin, Access and security |
| consent ends without a usable refresh token (error text not in the notes) | refresh tokens for the Ads scope need a user who signs in with a passkey; a new passkey can carry a 7-day delay | create a passkey, or use a service account |
| `google keyword-ideas` fails on Explorer access: "This method is not allowed for use with explorer access" (`DEVELOPER_TOKEN_NOT_APPROVED`) | Explorer cannot call the KeywordPlan services | apply for Basic (needs OAuth brand verification: consent screen External, In production) |
| `RESOURCE_EXHAUSTED` | daily operations over the level limit (Explorer 2,880 production, Basic 15,000, Standard unlimited; a rejected request still counts), or a 64 MB response | wait for the sliding 24 h window; apply for a higher level; select fewer fields |
| `RESOURCE_TEMPORARILY_EXHAUSTED` | QPS limit per customer id and per project; Planning services allow 1 QPS | back off 2 s, 4 s, 8 s with jitter; fewer parallel calls |
| `TOO_MANY_MUTATE_OPERATIONS`; `DEADLINE_EXCEEDED`, `INTERNAL_ERROR`, `TRANSIENT_ERROR` | over 10,000 operations in one request; oversize request or backend | split the request. A read: retry after about 30 s with backoff. A write: it may have been applied, so check what exists before repeating it (troubleshoot skill, step 5) |

### Policy and validation errors in a mutate

Run `google mutate --file FILE` without `--yes` first: it sends `validateOnly`. Each error carries a `fieldPath`.

| What you see | Cause | Fix |
|---|---|---|
| `REQUIRED_FIELD_MISSING`, `TOO_LONG`, `LINE_TOO_WIDE`, `DUPLICATE_CAMPAIGN_NAME`, `DUPLICATE_ADGROUP_NAME` | field missing, over a length limit, or name already used | fix the field in `fieldPath`; unique names |
| `BID_TOO_MANY_FRACTIONAL_DIGITS`, `NON_MULTIPLE_OF_MINIMUM_CURRENCY_UNIT`, `MONEY_AMOUNT_LESS_THAN_CURRENCY_MINIMUM_CPC` | micros not a multiple of the currency unit, or too small | round to the currency's minimum unit |
| `CampaignBudgetError.BUDGET_BELOW_PER_DAY_MINIMUM` | Demand Gen daily budget under 5 USD or the local equivalent | read `currency_constant.demand_gen_info.minimum_budget_per_day_micros` with `google search` |
| `ContextError.OPERATION_NOT_PERMITTED_FOR_CONTEXT` | language criterion on a Search campaign (rejected since Sept 2026); or AI Max final-URL expansion without text automation | remove the language criterion; opt in to text automation first |
| missing EU political advertising declaration | EU targeting without a declaration | ask the user for the declaration (it is a legal statement, recorded in the media plan) and set `containsEuPoliticalAdvertising` on the campaign to their answer |
| `CampaignError.AI_MAX_MUST_BE_ENABLED`, `CANNOT_SET_CAMPAIGN_KEYWORD_MATCH_TYPE` | AI Max rules | enable AI Max first; use the ad-group `disable_search_term_matching` |
| `AssetError.NAME_REQUIRED_FOR_ASSET_TYPE`, often beside `RESOURCE_NOT_FOUND` and `NOT_ENOUGH_..._ASSET` | an image asset without a `name` | give every image asset its own `name`, run the dry run again, then read what is left |
| `ASPECT_RATIO_NOT_ALLOWED`; asset group missing assets; `DUPLICATE_ASSET` | wrong image ratio; asset group below its minimums; same image bytes twice in a request | fix the ratio; send all required `AssetGroupAsset` links in the same request; create the asset once, link it by temp id |
| `AdGroupAdError.AD_SHARING_NOT_ALLOWED`; `CUSTOMER_NOT_ALLOWLISTED_FOR_THIS_FEATURE` | one ad linked to several ad groups (v23 and later); offline conversions, Customer Match, session attributes moved to the Data Manager API | create separate ads; do not use those services here |
| `PolicyFindingError` (ad), `PolicyViolationError` (keyword) | policy violation on create | exemption request below |

Policy exemption: read `policy_finding_details.policy_topic_entries[].topic` for an ad, `policy_violation_details.key` for a keyword (only if `is_exemptible`). An exemption request resends the same create with `policyValidationParameter.ignorablePolicyTopics` on the `AdGroupAdOperation`, or `exemptPolicyViolationKeys` on the `AdGroupCriterionOperation`, and files a review request; the content does not serve until approved. It is the user's decision: explain the finding, propose the request, run `google mutate` without `--yes` first, and send it only after their explicit approval. When the finding is right, change the text instead.

### Known issues open on 2026-11-13

| What you see | Cause | Fix |
|---|---|---|
| Explorer or Basic application rejected for a brand-verified project | project is on Free Trial, or its billing account is suspended or disabled | upgrade the project to the paid tier, or use another brand-verified project |
| `AUTHORIZATION_ERROR` on production after upgrading access after 2026-09-09 | the project used a Test-access token before the sunset; fix is rolling out | wait, or create a new Cloud project and apply for Explorer there |

## Search Console

Reference: `https://developers.google.com/webmaster-tools/limits`

| What you see | Cause | Fix |
|---|---|---|
| `invalid_grant` on refresh | Testing-mode 7-day expiry; token revoked, unused for 6 months, or session control (`invalid_rapt`) | `google login --scopes gsc`, then `--redirect-url`; set the consent screen to "In production" |
| "Access blocked" at consent; `admin_policy_enforced` | user not in the consent screen's Test users; a Workspace admin restricted the service | add the user under Audience, Test users; the admin allowlists the OAuth client |
| 429 or "quota exceeded" | Search Analytics 1,200 queries per minute per site; URL Inspection 2,000 per day and 600 per minute per site | back off; for the load quota (10-minute chunks) wait 15 minutes |
| 403 "User does not have sufficient permission for site" (unverified) | the account is not a user of that property, or the property form differs | add it under Users and permissions; set `GSC_SITE_URL` exactly as `gsc sites` lists it |

## Meta

Reference: `https://developers.facebook.com/documentation/ads-commerce/marketing-api/error-reference.md`. Branch on the code, not the text.

| What you see | Cause | Fix |
|---|---|---|
| "Unable to create" when you add an ad account in Business settings | the ad account creation limit of the business portfolio is used up; a closed or disabled account keeps its place | Meta key guide, first-day errors |
| 100 / 1885183 "Ads creative post was created by an app that is in development mode" | the Meta app is not published | publish it (Meta key guide, step 3), then `launch apply` again: applied steps are skipped |
| "No permissions available" when generating a system-user token | the system user has no role on the app | Business settings > Apps > the app > Assign people > the system user, Full control |
| `META_PAGE_ID` missing and `{account}/promote_pages` is empty | the account has never advertised for a Page | `meta get me/accounts -p fields=id,name,tasks` lists the Pages the system user may advertise for |
| 190 | invalid or expired token; a long-lived user token lasts about 60 days | system-user token with `ads_management`, `ads_read`, `pages_show_list`, `pages_read_engagement`, `pages_manage_ads`, `business_management` in `META_ACCESS_TOKEN` |
| 200 naming `pages_manage_posts` when deleting a video | `meta delete VIDEO_ID` acts on the video object and asks for a Page permission that ads do not need | `meta delete "{account}/advideos" -p video_id=ID --yes` takes it out of the ad account's library |
| 200 | permission error: scope or asset missing | regenerate the token with those scopes; assign app, ad account, Page and pixel to the system user |
| 200 / 1870034 | Custom Audience terms not accepted | accept them in the ad account as a regular user, not a system user |
| 200 / 5258001-5258009 | API access disrupted or deactivated | complete Data Use Checkup, Data Protection Assessment, developer registration; reactivate the app |
| 294 | managing ads needs `ads_management` and an allow-listed app (access tier) | request the permission and the tier for the app |
| 368 | action judged abusive or disallowed | stop retrying; review the policy; contact support |
| 17, 613, 4, 80000, 80003, 80004, 80014 | ad-account score or hourly quota; read = 1 point, write = 3; Development tier blocks 300 s at score 60, Full Access 60 s at 9,000 | wait, then slow down; batch bulk launches on a Development-tier app (about 20 writes, then a block) |
| 613 / 5044001, 4841018, 1487225 | over 100 mutations per second; concurrent edits of one object within 30 s; ad creation tied to the daily spend limit | slow down; one edit per object per 30 s; raise the account spend limit |

### Validation subcodes

Run `meta post PATH ...` without `--yes`: creations are sent with `validate_only` and return `{"success":true}`.

| What you see | Cause | Fix |
|---|---|---|
| 100 | generic invalid parameter | read `error_subcode` and `error_user_msg` |
| 100 / 1487694 | targeting category no longer available | search again with `meta search --type adinterest --q TEXT` |
| 2446394, 2446712, 2446867, 2446880, 2641 | targeting options removed; store-visits optimization removed; `campaigns_per_country` cap; WhatsApp number disconnected; restricted location | remove the option; use reach or store sales; use a standard conversions campaign; reconnect; change the geo |
| creation fails for EU delivery (error text not in the notes) | EU delivery needs `dsa_beneficiary` and `dsa_payor`, or account defaults | send both, or set both account defaults |

### Ad review rejections

A `validate_only` pass is not the final decision. Read the state with `meta get AD_ID -p fields=effective_status,ad_review_feedback,issues_info,failed_delivery_checks`.

| What you see | Cause | Fix |
|---|---|---|
| `DISAPPROVED` | policy rejection; reasons in `ad_review_feedback` and `issues_info` | change the creative or copy named there, then create a new ad |
| `PENDING_BILLING_INFO` | no payment method on the ad account | add billing in the Meta UI |
| `CAMPAIGN_PAUSED`, `ADSET_PAUSED` | not an error: the toolkit creates everything paused, or the parent was paused on purpose | nothing to fix. Starting delivery is the user's decision: `launch activate` runs only after their explicit approval, as the launch-campaign skill describes |

## TikTok

Reference: `https://business-api.tiktok.com/portal/docs/return-codes-appendix/v1.3`. The `code` in the body wins over the HTTP status. HTTP 404 means a missing trailing slash or the wrong method; HTTP 5xx means retry after about 5 minutes.

| What you see | Cause | Fix |
|---|---|---|
| "Invalid Developer Status" in the developer portal | the developer registration is not approved yet | wait for the approval (up to 3 business days), then create the app |
| the identity list has no `TT_USER` and no `BC_AUTH_TT` entry | no TikTok account is linked to the ad account, so no ad can be built for TikTok placement | link one: TikTok launch reference, section 2 |
| `40000`, `40002`, `40011` | invalid or incompatible parameters; too many ids in one request | read `message`, fix the field; batch (status updates take 1-20 ids) |
| `40001`, `40125` | no permission for the operation; missing scopes | add the scope, or use the right `advertiser_id` |
| `40007`, `40300`, `40301` | object or advertiser not found | check `TIKTOK_ADVERTISER_ID` and the ids in the call |
| `40101`, `40113` | app id or secret mismatch; app blocked | check `TIKTOK_APP_ID` and `TIKTOK_APP_SECRET` in My Apps |
| `40102`, `40105`, `40106`, `40104` | access token expired, invalid, mismatched with the advertiser, or empty | authorize again, then `tiktok oauth-exchange --auth-code CODE --write` |
| `40118`, `40119`, `40124` | app not allowlisted for the feature; developer and advertiser in different companies; developer profile not approved | contact the TikTok representative; fix the account link |
| `40110`; `40202`; `40502` | authorization code cancelled, used or expired; write conflict; maximum number of ads reached | repeat the authorization and exchange the new code; retry; another ad group, or delete ads |
| `40900` to `40914`, `40901`, `40902`, `40903` | upload errors (signature, missing, empty, too large, type, duplicate name); video still transcoding; cannot fetch the URL | fix or rename the file; wait and retry; fix the URL |
| `40008`, `40009`, `40013`, `40014` | endpoint or feature not in the sandbox | test in production (sandbox ends 2026-12-01) |
| budget rejected (code not in the notes) | campaign minimum is 20 USD in the guide, 50 USD in the currency table | use 50 USD as the safe minimum until verified |
| `40100`, `40016` | app-level throttle: Basic 10 QPS, 600 per minute; `ad/create/` Basic 5 QPS, 150 per minute | back off; after a per-minute breach wait 5 minutes; the daily quota resets at 00:00 UTC; ask for a higher tier in My Apps |
| `40133` | per-advertiser throttle | lower the rate; serialize writes |
| `50000`, `50002`, `51305`, `60001` | TikTok-side error, satellite service error, maintenance | a read: retry after about 5 minutes. A write: it may have landed, so check what exists before repeating it; the toolkit marks such a step uncertain. Then file a ticket |

### Review

Read the state with `tiktok get ad/review_info/ -p 'ad_ids=["AD_ID"]'`: `review_status` is `ALL_AVAILABLE` (can deliver), `PART_AVAILABLE` (some countries) or `UNAVAILABLE`; `reject_info` holds the reason.

| What you see | Cause | Fix |
|---|---|---|
| `AD_STATUS_AUDIT_DENY`, `ADGROUP_STATUS_AUDIT_DENY` | rejected: language not accepted in the location, unsupported prompts such as "swipe up", low media quality or no clear audio, creative name not matching the landing page, unauthorized brands or copyright | change the creative and create a new ad. An appeal (`adgroup/appeal/` with the ad group id) is the user's decision when the rejection looks wrong: propose it, run it without `--yes` first, and send it only on their instruction |
| `AD_STATUS_TRANSCODING_FAIL`; `AD_STATUS_MUSIC_AUTHORIZATION_MISSING`, `AD_STATUS_ASSET_AUTHORIZATION_LOST` | video not processed; audio or asset rights missing | re-encode and upload again; replace the audio or asset |
| ad with a Custom Identity fails (error text not in the notes) | since 2026-01-15 non-Spark Custom Identity ads cannot be created on TikTok placements | use a Spark identity (`TT_USER`, `BC_AUTH_TT`) |

## OpenAI

Reference: `https://developers.openai.com/api/docs/guides/error-codes`. Retry 429 rate, 500, 503 with backoff; never retry 401, 403, spend limits or 400 moderation. Classify a 429 by `error.code` first.

| What you see | Cause | Fix |
|---|---|---|
| 400 `moderation_blocked`, `image_generation_user_error` | prompt or reference image refused | change what is being asked for; do not reword the same request to get past the filter |
| 401 Incorrect API key | key wrong or revoked; no organization; IP not on the allowlist | new key in `OPENAI_API_KEY`; call from an allowed address |
| 403 "organization must be verified" (unverified wording) | image models may need API Organization Verification | complete it in the developer console |
| 429 `credit_balance_exhausted` | prepaid credits used up | add credits |
| 429 `organization_spend_limit_exceeded`, `project_spend_limit_exceeded`, `organization_usage_limit_exceeded` | spend or usage limit reached | raise the limit, or ask for a higher approved limit |
| 429 rate limit reached, `slow_down` | request or token rate | wait `Retry-After` seconds; lower the rate gradually |
| 500, 503 `server_is_overloaded` | server side | retry with backoff, honour `Retry-After` |
| model not found, or a retired model refused | the model was retired | `python3 ads/tools/ads.py models --provider openai --pick` |
| `video --provider openai` | OpenAI has no video API since 2026-09-24 | `--provider gemini` or `fal` |

## Gemini

Reference: `https://ai.google.dev/gemini-api/docs/api-errors`. Retry only 408, 429 and 5xx.

| What you see | Cause | Fix |
|---|---|---|
| 400 `invalid_request`, `parameter_unknown` | malformed or unknown parameter, or an over-complex schema | drop fields from old recipes (`sampleCount`, `negativePrompt`) |
| 400 `safety`, `prohibited_content`, `blocklist`, `spii`, `recitation`, `jailbreak` | generation blocked | change what is being asked for; do not reword the same request to get past the filter |
| 400 or 200 `image_safety`, `image_prohibited_content`, `image_recitation`, `image_other`, `no_image` | image blocked or none produced | change the concept (real people and brand names are a common cause); do not reword the same request to get past the filter |
| 401 `authentication` | key missing, invalid or expired; unrestricted standard keys are rejected since 2026-05-28 | new key in AI Studio (new keys are auth keys), or restrict the old key to the Gemini API |
| 402 `payment_required` | prepaid balance is 0 | buy credits; do not retry |
| 403 `permission_denied` | no permission, restricted project, leaked or blocked key, billing past due, `FREE_TIER_VERIFICATION_REQUIRED` | verify the project in AI Studio; fix billing; new key |
| 404 `not_found`, `model_not_found` | the model was shut down | `python3 ads/tools/ads.py models --provider gemini --pick` |
| 429 `rate_limit_exceeded`, `too_many_requests` | per-minute limit, or the Tier 1 spend limit (10 USD per 10 minutes) | backoff 1 s, 2 s, 4 s, 8 s with jitter |
| 429 `quota_exceeded` | daily quota | wait for the midnight Pacific reset, or raise the tier |

## fal.ai

Reference: `https://fal.ai/docs/documentation/model-apis/errors.md`

| What you see | Cause | Fix |
|---|---|---|
| 401 or 403, `rejected_key`, `permission_denied`, `resource_restricted` | bad key; key preset or model restriction; locked account or spending limit | new key in `FAL_KEY` with the `API` preset; add credits (a balance under the lock threshold locks the account) |
| 404 on result or status | request expired (kept 1 h, 6 min if over 10 KB) or unknown; unknown model | download media right after `COMPLETED`; `fal schema MODEL` checks the id |
| 405 on status, result or cancel | URL built from the full model path | use `status_url`, `response_url`, `cancel_url` from the submit response |
| `COMPLETED` but no output | `COMPLETED` also covers failed and cancelled runs | read the HTTP status of the result call |
| 422 `content_policy_violation` | prompt or image refused | change what is being asked for; do not reword the same request to get past the filter; not retryable |
| 422 `image_too_small`, `file_too_large`, `unsupported_*_format`, `one_of`, `missing`, `value_error` | input outside the model's limits or wrong field | read `loc` and `ctx` in `detail`; `fal schema MODEL` lists limits |
| 429 `concurrent_requests_limit` (sync API); 429 on submit | new accounts run 2 requests at once (up to 40 with paid use); `fal_max_queue_length` reached | use the queue, back off; raise the queue length |
| 500, 503, 504, `runner_*`, `generation_timeout`, `request_timeout` | server, runner or partner API | retry when `X-Fal-Needs-Retry` is 1; not billed |
| a model id that worked last month is not found | the endpoint is deprecated or retired | `models --provider fal --pick`; see deadlines |

## Firecrawl

Reference: `https://docs.firecrawl.dev/api-reference/errors.md`. The body is `{"success":false,"error":...}`; a 429 carries `Retry-After`. Debug aid: the dashboard Activity Logs "Debug issue" button.

| What you see | Cause | Fix |
|---|---|---|
| 400 `Invalid URL`, validation error; `THIRD_PARTY_DATA_UNSUPPORTED_*` | bad body or non-http(s) URL; provider-served URL with an unsupported option (actions, screenshot, branding) | fix the payload (`details`); scrape the record page, drop the option |
| 401 `Invalid token`, `Token missing` | key missing or revoked | new key in `FIRECRAWL_API_KEY` |
| 402 `Insufficient credits` | credits used up | enable pay-as-you-go or upgrade |
| 403 `Forbidden`, `UNSUPPORTED_SITE`; `SCRAPE_PROMPT_INJECTION_DETECTED` | no permission; site not supported; `checkPromptInjection` hit | another source; inspect the page, or retry without the check |
| 403 `THIRD_PARTY_DATA_TERMS_REQUIRED`, `_NOT_ENABLED` | an org admin must enable or accept terms | the admin does it; an agent must not accept |
| 410 | `/extract` was removed, or an agent result was deleted | `firecrawl scrape URL --schema @FILE` (scrape with a `json` format) |
| 429 `Rate limit exceeded`, `Concurrency limit reached` | per-minute limit per team (Free: 10 scrape, 2 crawl) | honour `Retry-After`; upgrade the plan |
| 408, 500, 502, 503, 504 | page slower than `timeout`; server or gateway | raise the timeout; retry with backoff; use crawl for long jobs |

## Apify

Reference: `https://docs.apify.com/api/v2`. The error body is `{"error":{"type":...,"message":...}}`.

| What you see | Cause | Fix |
|---|---|---|
| 400 `invalid-request`, `invalid-value` | body is not a JSON object; a parameter value is wrong | send an object with `Content-Type: application/json`; check fields with `apify actor ACTOR` |
| 401 `token-not-provided`, `user-or-token-not-found` | token missing, invalid, expired or rotated | new token in `APIFY_TOKEN` |
| 404 `record-not-found`; 405 `method-not-allowed` | Actor, run or store not found; wrong HTTP method | spelling `username~name` and token access; fix the method |
| 408 | a synchronous run exceeded 300 s | bound the run with `--max-items` and `--timeout`; the ceiling belongs to the synchronous endpoint |
| 429 `rate-limit-exceeded` | per-resource limit (60 requests per second by default) | back off with jitter |
| exit 2 from `apify run` | a guard rail refused: the cost cap | narrow the run with `--max-items`, or ask the user whether this call may cost more and pass `--max-usd`; the default in `ads/config.json` is theirs to change |

## DataForSEO

Reference: `https://docs.dataforseo.com/v3/appendix/errors.md`. HTTP is 200 except 401, 402, 404, 500: check the top-level `status_code` and every `tasks[].status_code` (20000 is OK).

| What you see | Cause | Fix |
|---|---|---|
| 40100 | not authorized | API login and API password from the API Access page in `DATAFORSEO_USERNAME` and `DATAFORSEO_PASSWORD`, not the account password |
| 40104; 40200, 40210 | account not verified; payment required or balance too low | verify in the dashboard; add funds (minimum 50 USD) |
| 40202, 40209 | over 10,000 requests per minute; over 30 simultaneous requests (Labs and similar) | slow down; lower concurrency |
| 40203, 40205, 40206, 40207 | daily cost limit; duplicate-task limit; IP not whitelisted | raise the limit in the dashboard API settings; cache results; add the address on the API Access page |
| 40000, 40006 | more than one task in a Live POST; over 100 tasks in one POST | one task per Live call; batch by 100 |
| 40102 | no search results | not an account error: treat as empty |
| 40105, 40401, 40403 | task deleted, not found, results older than a month | post the task again |
| 40400, 40402, 40404 | not found or invalid path; no prepared sandbox data | `PATH` starts after `v3/`; use the documented sandbox example, or drop `--sandbox` |
| 40501, 40502, 40503, 40506 | invalid or unknown field; empty or invalid body | `location_code`, not names; body must be a JSON array of objects; remove unknown keys |
| 50301 | third-party API unavailable (for example Google Ads "Too many requests") | retry later; Google Ads Live is limited to 12 per minute |
| 50401, 50402 | Live task timed out after 120 s; target page took over 50 s | post again; try another page |

## MCP servers of the plugin

Run `/mcp` in the session to see which server shows "failed" or "needs authentication".

| What you see | Cause | Fix |
|---|---|---|
| "failed", a `${VAR}` stays unresolved | the variable is missing from `.claude/settings.local.json` | `python3 ads/tools/ads.py keys`, fill `ads/.env`, then `env sync-claude` and restart the session (the env block is read at launch); it refuses (exit 2) if that file is not ignored by git |
| `tiktok-ads` shows "needs authentication" | OAuth not completed or expired | `/mcp`, pick the server, finish the browser sign-in. Access token 24 h, refresh 30 days, authorization window 30 days |
| `meta-ads` answers 401 or 403, or lists no tools | the server signs in with `META_ACCESS_TOKEN`: the token lacks `ads_mcp_management`, belongs to an Admin system user (only the Employee role is accepted), or the account is not enabled for the server yet | generate an Employee system-user token with `ads_mcp_management` plus `ads_read` or `ads_management`, `env sync-claude`, restart. Not enabled for the account: use the toolkit's `meta` commands |
| `dataforseo` fails with "command not found: npx" or exits at start | Node missing or old: this server runs through `npx` and needs Node 20 or later. `firecrawl` and `apify` are hosted servers and need no Node | install Node 20 or later |
| "command not found: pipx" (Google Ads server) | pipx missing; the server starts as `pipx run`; Python 3.10 or later, 3.12 suggested | install pipx and Python 3.12 |
| Google Ads server starts, every call fails | `GOOGLE_APPLICATION_CREDENTIALS` must hold the full path of a credentials file and `GOOGLE_CLOUD_PROJECT` the project id | `python3 ads/tools/ads.py google export-adc` writes the file and stores its path; set `GOOGLE_CLOUD_PROJECT` in `ads/.env`; then `env sync-claude` and restart |
| `firecrawl` or `apify` answers 401 | the key in the `Authorization` header is wrong or was revoked | `doctor --live --only firecrawl,apify` names the rejected key; replace it in `ads/.env`, `env sync-claude`, restart |
| no tool to create or enable a campaign on the Google Ads server | it reads, creates assets and uploads video only | `google mutate` or `launch` |
| `meta-ads`: `ads_create_campaign` answers `"status": "DRAFT"` | the server creates drafts, and a campaign draft would publish as active | set the draft paused, review it at the `ads_manager_url` of the answer; discard it with `discard_draft_changes` and the returned `confirmation_token` (Meta launch reference, section 6) |
| a TikTok tool named in the reference is missing from the tool list | on the layered server most tools run through the dispatcher | `tool_list`, `tool_get`, then `tool_execute` (TikTok launch reference, section 7) |
| the sign-in link of a server expires, or the browser ends on a `localhost` address that does not load | remote or headless session; the link lives 5 minutes | `claude mcp login --no-browser <server>` in a terminal of your own, then paste the address the browser ended on |
| TikTok server lists too few tools; write calls fail in bursts | a client once dropped tools above 256 (fixed 2026-07-20); 6 QPS per tool, one Smart+ ad write per 5 s per ad | refresh the tool list; space the calls. The plugin already uses the layered server, and a sign-in is valid for one server path only |

## Dated deadlines, next six months

Window 2026-11-14 to 2027-05-14. The ids are a snapshot of 2026-11-14; run `models --pick` for the live list instead of copying them.

<!-- example-only -->
| Date | Service | What starts failing | Fix |
|---|---|---|---|
| 2026-11-10 (past) | Meta | API v24 expired; calls move to the next version unless the endpoint changed (header `X-Ad-Api-Version-Warning`) | use a current version in `ads/config.json` |
| 2026-11-15 | Apify | store listing: one page, limit 100, `offset` ignored, unknown `category` gives 400 | category ids; narrow with `search` |
| 2026-12-01 | TikTok | sandbox accounts deprecated | test with a real, paused account |
| 2026-12-01 | OpenAI | `gpt-image-1.5`, `gpt-image-1-mini`, `chatgpt-image-latest` shut down | `models --provider openai --pick` |
| 2026-12-10 15:00 UTC | Firecrawl | `/extract` answers 410 | scrape with a `json` format |
| 2026-12-11 | OpenAI | `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-pro`, `o3`, `o3-pro` shut down | `models --pick` |
| 2026-12-18 | Gemini | `gemini-3.1-flash-tts-preview` and the 2.5 preview TTS models shut down | `models --provider gemini --kind speech --pick` |
| 2027-01-01 | TikTok | `campaign/create/`, `adgroup/create/`, `ad/create/` stop creating legacy manual Sales, App Promotion, Lead Generation campaigns | use the Smart+ endpoints |
| 2027-01-04 | fal.ai | all Wan 2.2 and Wan VACE endpoints retired | `minimax/h3-max/*`, `fal-ai/wan/v2.7/*` |
| 2027-01-06 | OpenAI | `tts-1`, `tts-1-hd`, `gpt-4o-mini-tts` shut down (the announced successor is not served by the speech endpoint) | `speech --provider gemini` or `fal` |
| 2027-01-14 | OpenAI | `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `gpt-4.1-mini` shut down | `models --pick` |
| 2027-02 (tentative month) | Google Ads | API v23 requests fail | use v26 or newer |
| 2027-02-10 | OpenAI | `gpt-image-2` shut down | `models --pick` |
| 2027-02-23 | Meta | API v25 expires | v26 or v27 |
| 2027-02-26 | OpenAI | `whisper-1`, the `gpt-4o-transcribe` family shut down | `gpt-transcribe` |
| 2027-03-15 | Gemini | `gemini-2.5-flash-image` shut down | `gemini-3.1-flash-lite-image` |
| 2027-05 (tentative month) | Google Ads | API v24 requests fail | use v26 or newer |
| 2027-05-07 | Gemini | `gemini-3.1-flash-lite` shut down | `gemini-3.5-flash-lite` |
<!-- /example-only -->

No date announced: Google Ads will reject the `developer-token` header in a future major version, so keep it out of calls. A fal.ai endpoint marked `deprecated` can still resolve but is hidden from default searches.
