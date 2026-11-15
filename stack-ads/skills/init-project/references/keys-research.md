# Research keys: Firecrawl, Apify, DataForSEO

How to get the three research keys and put them in `ads/.env`. Facts verified on 2026-11-14; prices and plan limits change, so re-check the linked page before quoting a number to the user.

| Service | Variable(s) in `ads/.env` | Free to start? | Time to obtain (estimate) |
|---|---|---|---|
| Firecrawl | `FIRECRAWL_API_KEY` | Yes: 1,000 credits per month, no card | 2 min |
| Apify | `APIFY_TOKEN` | Yes: $5 usage per month, no card | 3 min |
| DataForSEO | `DATAFORSEO_USERNAME`, `DATAFORSEO_PASSWORD` | Partly: $1 trial credit; real use needs a $50 first top-up | 5 min, plus the payment |

## Contents

- Firecrawl
- Apify
- DataForSEO
- After all three

## Firecrawl

Used for: reading the user's site and competitor pages, brand kit (colours, fonts, logo), screenshots, web search.

**Cost to start**
- Free: $0, no card, 1,000 credits per month, 2 concurrent requests. No pay-as-you-go: at zero credits calls fail with 402.
- Hobby: $19 per month, 5,000 credits, pay-as-you-go available. Standard: $99, 100,000 credits.

Credits per call: scrape 1 per page, map 1 per call, search 2 per 10 results, structured extraction (`--schema`, `--prompt`) +4 per page. Branding and screenshots add nothing: markdown plus branding plus screenshot plus extraction on one page is about 5 credits. Free limit: 10 requests per minute for scrape, map and search.

**Create the key**

1. Open `https://www.firecrawl.dev/signin?view=signup` and sign up.
2. Open `https://www.firecrawl.dev/app/api-keys` (sidebar: API Keys).
3. Create a key (the button label is unverified). The key starts with `fc-`.
4. Copy it. Keep at least one active key at all times: create the new key before revoking the old one.

**Fill in**

```text
FIRECRAWL_API_KEY=fc-...
```

**Verify**
```bash
python3 ads/tools/ads.py doctor --live --only firecrawl
python3 ads/tools/ads.py firecrawl scrape https://example.com --formats markdown
```

**First errors**

| Symptom | Cause | Fix |
|---|---|---|
| 401 `Unauthorized: Invalid token` or `Token missing` | key missing, revoked, or an empty `Bearer` value | re-copy the key into `ads/.env`; no stray space or quote |
| 402 `Payment Required: Insufficient credits` | monthly credits spent on Free | wait for the monthly refresh, or upgrade to a paid plan and enable pay-as-you-go |
| 429 `Rate limit exceeded` or `Concurrency limit reached` | Free allows 10 requests per minute and 2 at once | run one call at a time; honour `Retry-After` |
| 403 `UNSUPPORTED_SITE` | site not supported | use another source |
| map, crawl or agent fail with "not supported by the keyless free tier" | no key reached the request | fix `FIRECRAWL_API_KEY`; only scrape and search work without a key |

**Key hygiene**

- In the dashboard open the key menu, choose **Set limit**, and set a credit limit per day, week or month, then **Save**.
- One key per project; rename it (**Rename**) to the project name. All keys of a team share the same credits and rate counters.
- Never paste the key into a plan, commit, screenshot or chat. If it leaks, create a new key first, then revoke the old one.

Official page: `https://docs.firecrawl.dev/dashboard.md`

## Apify

Used for: public ad libraries (Meta, TikTok, Google), social content, reviews, via ready-made Actors.

**Cost to start**
- Free: $0, no card, $5 prepaid usage per month. Access blocks until the next cycle once it is spent; unused credit expires.
- Starter: $19 per month plus pay-as-you-go, $19 prepaid, overage allowed up to your usage limit.

Most Store Actors charge per event (per result, per start) or per usage. Scale: $5 buys about 860 ads from the Meta ads Actor at $0.0058 each; enough to demo, not to monitor. Always cap a run: `apify run` takes `--max-usd` and `--max-items`, and stops at `guardrails.max_research_usd_per_call` in `ads/config.json`.

**Create the token**

1. Open Apify Console, then **Settings > API & Integrations** (`https://console.apify.com/settings/integrations`).
2. In **Personal API tokens** select **Create a new token**.
3. Enter a description, for example the project name. Optionally switch on **Limit token permissions** and set an expiration date.
4. Select **Create**, copy the token at once, then select **Done**. The value is shown only once.

**Fill in**

```text
APIFY_TOKEN=<token>
```

**Verify**

```bash
python3 ads/tools/ads.py doctor --live --only apify
python3 ads/tools/ads.py apify actor apify/facebook-ads-scraper
```

The second command prints the Actor's pricing and input fields and costs nothing.

**First errors**

| Symptom | Cause | Fix |
|---|---|---|
| 402 `x402-payment-required` "Request not authenticated" | no token reached the request | check `APIFY_TOKEN` in `ads/.env` |
| 401 or 403 on a run | token revoked, expired, or scoped without Run on that Actor | create a new token, or add Run |
| run log says "insufficient permissions" | scoped token with restricted run access | choose **Full access** for the Actor's own run token, or widen the scope |
| run stops early with few items | the `--max-usd` or `--max-items` cap was reached | raise the cap on purpose; check the price with `apify actor` first |

**Key hygiene**

- Prefer a scoped token: switch on **Limit token permissions**, allow Run on the chosen Actors, and keep access to default run storages on so the run's dataset can be read.
- Set an expiration date; give each token its own description and never reuse it elsewhere.
- Lost token: it cannot be shown again; rotate it (optional 24 h grace) or create a new one.
- Send the token in an `Authorization: Bearer` header, never in a URL query.

Official page: `https://docs.apify.com/integrations/api`

## DataForSEO

Used for: keyword volumes, CPC and bid ranges, competitors' paid keywords, ad blocks in search results.

**Cost to start**

- Pay as you go, no subscription. Registration adds a $1 trial credit, enough to test a few calls.
- Minimum top-up is $50; the balance does not expire. Without it only the trial credit and the Sandbox work.
- Sandbox: pass `--sandbox` to `dataforseo post` or `dataforseo get`. It is free, returns dummy data with the real structure, and still needs the credentials.
- Extra trial accounts break the terms and pause access (error `40201`).

**Create the credentials**

1. Create a free account in the DataForSEO dashboard (app.dataforseo.com). Verify the account when asked.
2. Open **API Access** in the left menu.
3. Read the **API login** there (the sign-up address by default; it can be edited in the same section).
4. Read the **API password**. It is generated for you and differs from the account password. It is shown only for the first 24 hours after registration: copy it now. Later, click **Send by e-mail** to receive it again at the sign-up address.

**Fill in**

```text
DATAFORSEO_USERNAME=<API login>
DATAFORSEO_PASSWORD=<API password, not the account password>
```

**Verify**

```bash
python3 ads/tools/ads.py doctor --live --only dataforseo
python3 ads/tools/ads.py dataforseo get appendix/user_data
```

The second call is free; it returns the balance and the price list.

**First errors**

| Symptom | Cause | Fix |
|---|---|---|
| 401 or code `40100` | account password used, or a stray space in the value | use the API password from **API Access** |
| `40104` | account not verified | finish verification in the dashboard |
| `40207` | an IP whitelist is on | add the current address in **API Access**, or switch the whitelist off |
| `40404` in Sandbox | no prepared dummy data for that task | use a documented Sandbox endpoint, or run live on the trial credit |
| live calls rejected, balance near zero | trial credit used up | top up at least $50 under **Billing** |

**Key hygiene**

- Set daily cost limits per API in the dashboard **Settings** page so a loop cannot drain the balance.
- Turn on the IP whitelist in **API Access** when the machine has a fixed address. Check spend under **Usage**.
- If the password leaks, treat the account as exposed: check **Usage**, then look in **API Access** for a way to renew it (the renewal path is unverified). Never put the login and password in a URL.

Official page: `https://docs.dataforseo.com/v3/auth/`

## After all three
```bash
python3 ads/tools/ads.py keys
python3 ads/tools/ads.py doctor --live --only firecrawl,apify,dataforseo
```

`keys` shows each variable as set or missing, never its value. `ads/.env` stays out of git.
