# Scenario: first keys, from nothing

The user installed the plugin in a project and asks: "What do I need to start advertising here, and where do I get it?" Nothing is configured.

## 1. Create the workspace

Run the `init` command of the `init-project` skill (step 1 there). It creates `ads/`, an empty `ads/.env` and the toolkit copy. Then see the starting point:

```bash
python3 ads/tools/ads.py keys
python3 ads/tools/ads.py doctor
```

`doctor` lists ten services as "not configured" and prints, for each, where the key comes from and which guide in `ads/tools/guides/` covers it.

## 2. Ask once what the user wants to do

"Which platforms do you want to advertise on, do you want images or video generated, and how much research should we buy?"

Example answer: "Google Search only for now, a few images, keep it cheap."

That selects four services out of ten:

| Service | Why | Cost to start |
|---|---|---|
| Firecrawl | read the site and competitor pages | free plan, no card |
| Gemini | images; one creative key is enough | prepaid, small minimum |
| Google Ads | the campaign | free; production access to a live account may need approval |
| Search Console | real search queries as keyword seeds | free |

DataForSEO is left out: the Keyword Planner of the Google Ads account covers volumes once the Cloud project has Basic access. Say what the user gives up by skipping it (competitors' paid keywords).

## 3. One service at a time

For each service read its guide, then give numbered steps from it, one action per step. The user puts the value into `ads/.env` in their editor and says "done". Verify at once:

```bash
python3 ads/tools/ads.py doctor --live --only firecrawl
python3 ads/tools/ads.py doctor --live --only gemini
```

A `rejected` row prints the service's message and the fix. Typical first-day cases: a Gemini key on the free tier cannot make images until billing is linked; a Firecrawl key copied with a trailing space.

## 4. Google, the long one

Follow the Google key guide: a Cloud project, the two APIs enabled, the access level, the consent screen published, a Desktop OAuth client. With the client id and secret in `ads/.env`:

```bash
python3 ads/tools/ads.py google login
python3 ads/tools/ads.py google login --redirect-url 'PASTED_ADDRESS'
python3 ads/tools/ads.py google customers
python3 ads/tools/ads.py gsc sites
python3 ads/tools/ads.py doctor --live --only google,gsc
```

The user opens the printed address, allows access, and copies the address the browser ends on into the second command. `google customers` lists the accounts; the user chooses one and writes its ten digits to `GOOGLE_ADS_CUSTOMER_ID`. `gsc sites` gives the value for `GSC_SITE_URL`.

If `doctor` reports `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION`, the project still has Test access: the user applies for Explorer access (guide, step 2). Research, copy and creatives can proceed meanwhile; only the dry run against the live account waits.

## 5. The ceiling and the models

Ask: "What is the most a single campaign may ever spend per day?" Write the answer to `guardrails.max_daily_budget` in `ads/config.json`, and set `project.currency` to the currency of the Google Ads account. Then:

```bash
python3 ads/tools/ads.py models --pick
```

## 6. Optional: MCP servers

```bash
python3 ads/tools/ads.py env sync-claude
```

Restart the session and check `/mcp`. The `firecrawl` server works with the key just added; servers whose keys were skipped show as failed, which is harmless.

## 7. Report

"Working: Firecrawl, Gemini, Google Ads, Search Console. Skipped: Apify, DataForSEO, OpenAI, fal.ai, Meta, TikTok. Budget ceiling 30 EUR a day. Next: the product brief."

## What this scenario shows

- The user never pastes a key into the conversation; the toolkit reads `ads/.env`.
- Every key is verified with a live call the moment it is entered, so a typo is found now and not during a launch.
- Skipped services stay skipped until a later task needs one; then `doctor` says where to get it.
