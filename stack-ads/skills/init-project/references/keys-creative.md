# Creative keys: OpenAI, Gemini, fal.ai

How to get the three creative-generation keys and put them in `ads/.env`. Facts verified on 2026-11-14; model names and prices change, so let `python3 ads/tools/ads.py models --pick` choose models and re-check the linked page before quoting a price.

| Service | Variable | Free to start? | Time to obtain (estimate) |
|---|---|---|---|
| OpenAI | `OPENAI_API_KEY` | No: prepaid credits, $5 minimum | 5 min, longer if Organization Verification is asked |
| Gemini | `GEMINI_API_KEY` | Key yes; images, video and music need the paid tier (prepay $5 minimum) | 5 min |
| fal.ai | `FAL_KEY` | No: prepaid credits (minimum purchase unverified) | 3 min |

One key is enough to start: Gemini covers image, video, voice, music and analysis; OpenAI has no video API; fal.ai has the widest catalogue.

## Contents

- OpenAI
- Gemini
- fal.ai
- After all three

## OpenAI

Used for: images (including text inside the image and edits with reference images), voice-over, analysis of creatives. OpenAI no longer offers video generation.

**Cost to start**
- Billing is prepaid credits. The minimum purchase is $5; that also moves the organization to the Build usage tier. Credits expire after one year and are non-refundable.
- Image models may need API Organization Verification (business and/or government-ID check). Which models, and how long it takes, is not documented (unverified).

**Create the key**
1. Sign up at `https://platform.openai.com`.
2. Open `https://platform.openai.com/settings/organization/billing/overview`, choose **Add payment details**, then **Buy credits** (at least $5). The balance can take a few minutes to update.
3. Open the project selector, choose **Create project**, enter a name, then **Create**.
4. Open `https://platform.openai.com/settings/organization`, select the project, open **API Keys**, choose **+ Create new secret key**.
5. Set permissions: **Restricted**, with each resource at None except what the toolkit calls (model requests, images, audio). **All** is the default.
6. Copy the key. The full value is shown once.

**Fill in**

```text
OPENAI_API_KEY=<key>
```

**Verify**

```bash
python3 ads/tools/ads.py doctor --live --only openai
python3 ads/tools/ads.py models --provider openai --kind image
```

**First errors**

| Symptom | Cause | Fix |
|---|---|---|
| 401 `Incorrect API key provided` | wrong or revoked key, or key expired | create a new key and re-copy it |
| 401 `IP not authorized` | the organization has an IP allowlist | call from an allowed address, or update the allowlist |
| 429 `credit_balance_exhausted` | no credits, or the purchase has not landed yet | buy credits; wait a few minutes; never retry in a loop |
| 429 `project_spend_limit_exceeded` or `organization_spend_limit_exceeded` | the monthly spend limit was reached | raise the limit under project **Limits** |
| 429 `Rate limit reached` or `slow_down` | too many calls | back off, honour `Retry-After` |
| 403 `Country, region, or territory not supported` | the account's country is not served | use another provider |
| 403 on image models, text mentions verification (wording unverified) | Organization Verification pending | complete it at `https://platform.openai.com/settings/organization/general` |
| 400 `moderation_blocked` | the prompt or reference image tripped moderation | edit the prompt or image; do not auto-retry |
| **+ Create new secret key** is greyed out | an admin restricts key creation or key types | ask an org admin, or use a service-account key |

**Key hygiene**

- A key's scopes only restrict; they never grant more than its owner has. Use **Restricted**.
- In project **Limits** set **Monthly spend limit** and **Alert when spend reaches**, and switch on **Enforce a hard limit**, so requests fail at the limit.
- Set an expiration date on the key. A deployed or scheduled job uses a service-account key (**Members**, **+ Service account**), not a personal one.
- One key per project and per use. Never paste it into a plan, commit, screenshot or chat. If it leaks, create a new key, switch over, then delete the old one.

Official page: `https://developers.openai.com/api/docs/guides/api-keys.md`

## Gemini

Used for: images, video, voice-over, music, analysis of images and video.

**Cost to start**
- The key itself is free and needs no card. The free tier covers only some text models.
- Image, video and music generation and the top text models have no free tier. Paid tier means: link a billing account and prepay at least $5 (maximum $5,000) at `https://aistudio.google.com/billing`. Credits expire after 12 months.
- Tier 1 (billing linked) caps cumulative billing at $250 and spend at $10 per 10 minutes. Tier 2 follows after $100 paid and 3 days; Tier 3 after $1,000 and 30 days.
- At a prepaid balance of $0 every key on that billing account stops at once (HTTP 402).

**Create the key**
1. Open `https://aistudio.google.com/api-keys` and sign in with a Google account. After you accept the terms, AI Studio creates a default project and key.
2. For another key choose **Create API key** and pick the project. The exact dialog fields are unverified.
3. To use an existing Google Cloud project: **Dashboard**, **Projects**, **Import projects**, select it, **Import**; then create the key on **API Keys**.
4. Enable the paid tier: on the **API keys** or **Projects** page click **Set up billing** in the Billing Tier column, accept the terms, confirm the payment method, then prepay at least $5.
5. Copy the key.

**Fill in**

```text
GEMINI_API_KEY=<key>
```

If `GOOGLE_API_KEY` is also exported in the shell, Google's SDKs prefer it. Unset it before running the toolkit.

**Verify**

```bash
python3 ads/tools/ads.py doctor --live --only gemini
python3 ads/tools/ads.py models --provider gemini --kind video
```

A successful model list does not prove generation works: billing or verification can still block it. Make one cheap image or `analyze` call as the real test.

**First errors**

| Symptom | Cause | Fix |
|---|---|---|
| 400 `failed_precondition` | billing not enabled | finish **Set up billing** |
| 401 `authentication` | key missing, expired, or an old unrestricted standard key | create a key in AI Studio (new keys are accepted) |
| 402 `payment_required` | prepaid balance is $0 | buy credits or enable auto-reload; do not retry |
| 403 `FREE_TIER_VERIFICATION_REQUIRED` | free project not yet verified | verify with a phone QR scan on `https://aistudio.google.com/verify`, or move the project to the paid tier |
| 403 `permission_denied` | leaked or blocked key, billing past due, or region not served | new key, fix billing, or check `https://ai.google.dev/gemini-api/docs/available-regions` |
| 404 `model_not_found` | the model was shut down | run `models --pick` again |
| 429 `rate_limit_exceeded` or `quota_exceeded` | per-minute or daily limit, or the Tier 1 spend limit | back off with jitter; the daily count resets at midnight Pacific; raise the tier |
| 400 `image_safety`, `prohibited_content` | generation blocked | rephrase the prompt |
| **Create API key** is greyed out | missing IAM rights on the Cloud project | ask for Project Editor, or create a new project outside an organization |

**Key hygiene**

- Restrict the key to the Gemini API: on the API Keys page hover the key labelled **Unrestricted**, choose **Add restrictions**, **Restrict to Gemini API only**, **Restrict key**.
- Send the key in a header, never in a URL query. If it leaks: new key, switch over, disable the old one, audit billing.
- Free-tier content may be used to improve Google products; paid-tier content is not.

Official page: `https://ai.google.dev/gemini-api/docs/api-key`

## fal.ai

Used for: a catalogue of image, video, avatar and audio models, run with `fal run`.

**Cost to start**
- Prepaid credits, bought at `https://fal.ai/dashboard/billing`. The minimum purchase and whether a key can be created before adding a card are unverified.
- Purchased credits expire after 365 days; free credits and coupons expire after one week to one year.
- A new account runs 2 requests at once; the limit rises with paid invoices (up to 40 without sales). Below the lock threshold the account is locked and requests are rejected until credits are added.

**Create the key**
1. Sign in at `https://fal.ai` and open `https://fal.ai/dashboard/keys`.
2. On a team account, pick the team in the top-left switcher first. A key belongs to the account that created it, and only team Admins create keys.
3. Click **Create Key** and enter a name.
4. Choose the preset **API**. It submits and reads requests, runs workflows and uploads files; nothing more.
5. Optionally set an expiration (1 hour to 1 year). Leave **Allowed models** empty: it cannot be changed after creation.
6. Copy the key at once; it is not shown again.

**Fill in**

```text
FAL_KEY=<key_id:key_secret>
```

Copy the whole value, with its colon. Requests use the header `Authorization: Key $FAL_KEY` (the word `Key`, not `Bearer`).

**Verify**

```bash
python3 ads/tools/ads.py doctor --live --only fal
python3 ads/tools/ads.py models --provider fal --kind image
python3 ads/tools/ads.py fal schema MODEL
```

`fal schema` prints a model's input fields and costs nothing.

**First errors**

| Symptom | Cause | Fix |
|---|---|---|
| 401 `rejected_key` | wrong, revoked or expired key | create a new key; check for a stray quote or space |
| 401 or 403 about a locked account | balance below the lock threshold | add credits at `https://fal.ai/dashboard/billing` |
| 403 `permission_denied` | the preset lacks the permission | recreate the key with the **API** preset |
| 403 `resource_restricted` | the key's Allowed models list excludes this model | create a key without that restriction |
| 404 on the result of an old request | results expire after about an hour | `fal run` downloads output at once; rerun the job |
| 422 `content_policy_violation` | prompt or image moderated | change the prompt or image; not retryable |
| 422 with `loc` and `type` | an input field is wrong | read `loc`; compare with `fal schema` |
| 429 `concurrent_requests_limit` | more than 2 requests at once on the direct endpoint | run jobs one by one; the queue waits instead of failing |

**Key hygiene**

- Use the **API** preset, not **FULL**: FULL can create and revoke keys. Set an expiry.
- Do not use **Allowed models** on the plugin's key: the model shortlist changes.
- Generated files sit on public CDN links; download them into `ads/creatives/` and do not send confidential briefs as prompts.
- Never paste the key into a plan, commit, screenshot or chat. If it leaks, create a new key, switch over, then revoke the old one.

Official page: `https://fal.ai/docs/documentation/model-apis/authentication/key-based.md`

## After all three

```bash
python3 ads/tools/ads.py keys
python3 ads/tools/ads.py doctor --live --only openai,gemini,fal
python3 ads/tools/ads.py models --pick
```

`keys` shows each variable as set or missing, never its value. `ads/.env` stays out of git.
