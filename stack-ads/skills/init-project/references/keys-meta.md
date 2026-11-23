# How to get Meta (Facebook and Instagram) access

How to get every Meta variable of `ads/.env` for a user who has never used the Marketing API: a system-user token for their own ad account, ids found through the toolkit, and the optional official CLI and MCP server. Facts verified 2026-11-14.

## Contents

- What you need
- Cheapest path: advertise from your own ad account
- Token lifetime
- Find the ids
- Access tiers
- Verify
- Official `meta ads` CLI
- Official Meta MCP server
- First-day errors

## What you need

| Item | Variable | Where it comes from |
|---|---|---|
| System-user access token | `META_ACCESS_TOKEN` | Business Settings > System Users > Generate token |
| Ad account id, digits only, no `act_` prefix | `META_AD_ACCOUNT_ID` | Ads Manager > account Settings > Account overview, or `meta get me/adaccounts` |
| Facebook Page id | `META_PAGE_ID` | `meta get {account}/promote_pages` |
| App id | `META_APP_ID` | App Dashboard of the app you create |
| App secret | `META_APP_SECRET` | App Dashboard > App Settings > Basic |
| Pixel (dataset) id, optional | `META_PIXEL_ID` | `meta get {account}/adspixels` |
| Instagram account id, optional | `META_INSTAGRAM_USER_ID` | `meta get {account}/instagram_accounts` |

Pixel is needed only for conversion campaigns; the Instagram id only for Instagram placements.

## Cheapest path: advertise from your own ad account

Developer account, app, business portfolio, system user. Standard access to `ads_read` and `ads_management` is enough for your own ad account; no App Review.

1. Register a Meta developer account: `https://developers.facebook.com/docs/development/register`.
2. Create an app at `https://developers.facebook.com/apps/creation/`: app name, contact e-mail, select use cases, choose or create a business portfolio (or connect it later), then Go to dashboard. Add the Marketing API product to the app (the exact use-case label for it is unverified). Use cases cannot be removed once added.
3. Business Suite > Business Settings > Users > **System Users** > Add. Role: **Employee**.
   - Employee, not Admin: the official Meta MCP server rejects tokens of Admin-role system users. The CLI and the Graph API accept both, so Employee works everywhere.
   - Limit per business at Limited access: 1 normal system user plus 1 admin system user.
4. Business Settings > **Apps** > the app > Assign Users: add the system user with Full control.
5. Business Settings > Accounts > **Ad Accounts** > the ad account > Add People: add the system user with full control of the ad account.
6. Same screen, **Assign Assets**: add the Page, the pixel (dataset) and, for catalogs, the catalog. A missing asset shows up later as error 200.
7. System Users > the user > **Generate token**: pick the app, tick the scopes below, copy the token into `META_ACCESS_TOKEN`. It is shown once.

| Scope | Why |
|---|---|
| `ads_management` | create and change campaigns, ad sets, ads, creatives |
| `ads_read` | read insights (the MCP server needs it or `ads_management`) |
| `business_management` | business portfolio and asset reads |
| `pages_show_list`, `pages_read_engagement`, `pages_manage_ads` | list Pages, read them, run ads from a Page |
| `read_insights` | reporting reads |
| `catalog_management` | only when the user uses catalogs |
| `ads_mcp_management` | only for the Meta MCP server (see below) |
| `instagram_basic` | optional, for Instagram tools of the MCP server; unverified for REST creative creation |

The app and the system user must belong to the same business portfolio. Tokens are invalidated by a password change or by revoked permissions.

"Require App Secret" (App Settings > Advanced > Security) makes Meta refuse any call without an `appsecret_proof`. The toolkit signs every call with it as soon as `META_APP_SECRET` is in `ads/.env`, so the setting is safe to switch on for toolkit-only use and is a sound hardening step. Leave it off when the secret is not stored, and when you also use the `meta` CLI or the MCP server with this token: whether those clients send the proof is not documented.

## Token lifetime

| Token type | Lifetime |
|---|---|
| Short-lived user token (Graph API Explorer) | one to two hours; for a quick test only |
| Long-lived user token | about 60 days; extend in the Access Token Debugger or by server-side code exchange |
| System-user token | official page says it does not expire; the token API has `set_token_expires_in_60_days` for an expiring variant |

Ask the user: the Generate token dialog may offer 60 days or never (unverified on an official page). Unattended or scheduled runs: choose the token that does not expire. 60-day token: tell the user to regenerate it before the date and rerun `doctor --live --only meta`.

Inspect a token (app, expiry, scopes) at `https://developers.facebook.com/tools/debug/accesstoken`.

## Find the ids

Fill `META_ACCESS_TOKEN` first, then `META_AD_ACCOUNT_ID`. `{account}` in a path becomes `act_` plus `META_AD_ACCOUNT_ID`.

```bash
python3 ads/tools/ads.py meta get me/adaccounts -p fields=id,name,account_status,currency
python3 ads/tools/ads.py meta get {account}/promote_pages -p fields=id,name
python3 ads/tools/ads.py meta get {account}/adspixels -p fields=id,name,last_fired_time
python3 ads/tools/ads.py meta get {account}/instagram_accounts
```

| Command | Result | Notes |
|---|---|---|
| `meta get me/adaccounts ...` | ids as `act_<digits>`; store only the digits | Standard Graph edge, unverified on an official page. If it fails or lists nothing, read the number in Ads Manager > Settings > Account overview |
| `meta get {account}/promote_pages` | Page `id` for `META_PAGE_ID` | Edge exists on the ad account |
| `meta get {account}/adspixels` | pixel `id` for `META_PIXEL_ID` | `last_fired_time` empty means the pixel never received an event |
| `meta get {account}/instagram_accounts` | Instagram id for `META_INSTAGRAM_USER_ID` | The `connected_instagram_accounts` edge also exists. The creative field is `instagram_user_id`; never send it together with `instagram_actor_id` (error 2446149) |

A Page or Instagram account that does not appear is not assigned to the ad account or system user: repeat step 6. No pixel exists: create one with `meta post {account}/adspixels -p name=Pixel`: it prints what it would send, and after the user's yes add `--yes`. Errors 6200 and 6202 mean one already exists or more than one.

## Access tiers

| Tier | How | What it gives |
|---|---|---|
| Limited (`development_access`) | automatic with the Marketing API product | enough for your own ad account; tight rate limits; 1 + 1 system users; Business Manager and catalog APIs limited |
| Full (`standard_access`) | App Review: "+Upgrade" on the Marketing API Access Tier | light limits; 10 + 1 system users; full Business Manager and catalog APIs |

- Limited limits: ad-account score max 60 (read = 1, write = 3, decay 300 s), then blocked 300 s: about 20 writes in a burst. Hourly `ads_management` quota per account: 300 + 40 x active ads. Launch in small batches.
- Full limits: score max 9000, block 60 s; quota 100,000 + 40 x active ads.
- Full needed when: managing other people's ad accounts, many launches per hour, or catalogs and Business Manager APIs at scale. Criteria: at least 500 Marketing API calls in the last 15 days and an error rate under 15% over the last 500 calls.
- Business Verification: "required if your app accesses sensitive data"; whether own-account use needs it is not stated officially (unverified). Do not start it unless Meta asks.
- Every call, at every tier, hits production data; there is no ad sandbox. Create paused objects only.

## Verify

```bash
python3 ads/tools/ads.py doctor --live --only meta
```

It makes one read-only call. On failure it prints where to get the missing key. Rerun after each fix.

## Official `meta ads` CLI

Optional. It uploads media itself and creates everything `PAUSED`. Needs Python 3.12 or later.

```bash
pip install meta-ads
# or, macOS and Linux:
# brew tap facebook/fb && brew trust facebook/fb && brew install facebook/fb/meta-ads
meta --version
```

The CLI reads its own variable names. Map them from the plugin's variables in a terminal of your own, not through the agent: the lines below put every key of `ads/.env` into the environment of that shell, where each program started from it can read them. Close the shell when you are done.

```bash
set -a; . ads/.env; set +a
export ACCESS_TOKEN="$META_ACCESS_TOKEN" AD_ACCOUNT_ID="$META_AD_ACCOUNT_ID"
export APP_ID="$META_APP_ID" APP_SECRET="$META_APP_SECRET"
meta auth status
meta -o json ads page list
```

Precedence is flags, then the environment, then a project `.env`. `meta auth status` shows a masked token. There is no OAuth. Whether the CLI expects `AD_ACCOUNT_ID` with or without `act_` is unverified: if it rejects the digits, retry with the prefix. Package name is `meta-ads` (PyPI page: `https://pypi.org/project/meta-ads/`); other names found online are wrong. Docs: `https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/setup/get-started.md`.

## Official Meta MCP server

The plugin declares it as the `meta-ads` server (URL `https://mcp.facebook.com/ads`) and signs in with `META_ACCESS_TOKEN` as a bearer token, so one token serves the toolkit and the server. After the token is in `ads/.env`, run `python3 ads/tools/ads.py env sync-claude` and restart the session.

| Path | Needs |
|---|---|
| Bearer token (what the plugin configures) | a user token or an Employee-role system-user token with `ads_mcp_management` plus `ads_read` or `ads_management`; a token of an Admin system user is refused. More tools unlock with `ads_management`, `catalog_management`, `business_management`, `pages_show_list`, `instagram_basic` |
| OAuth in the MCP client (no token) | add the server yourself, without a header: `claude mcp add --transport http meta-ads-oauth https://mcp.facebook.com/ads`, then open `/mcp`, pick it and authenticate. A Meta app is not required. With your own app: use case "Create & manage ads with ads MCP server", and pass the app id as OAuth client id. The plugin's confirmation hook watches only its own `meta-ads` server: on a server you add yourself, approve each write in the normal permission prompt |

Check it after `python3 ads/tools/ads.py env sync-claude` and a restart of the session: `/mcp` shows whether `meta-ads` connected and lists its tools. Do not test the token with a hand-written `curl`: a token on a command line is visible to other processes and ends up in the transcript.

- Meta opens the server account by account, and the beta or GA status is not stated on its pages. `ads_get_ad_accounts` returns `is_ads_mcp_enabled` for every ad account, with `account_status` and `is_queryable`: read them first. Not enabled looks like: the sign-in works but tools are missing or calls are refused for the account.
- Then use the toolkit's `meta` commands instead; every operation in this plugin works without the MCP server.
- The live tool list has upload tools; this plugin has not exercised them, so upload with `meta upload-image` and `meta upload-video`.
- `ads_create_campaign` creates a draft that would publish as active: set it paused before it is published (Meta launch reference of the `launch-campaign` skill, section 6). `ads_activate_entity` starts spend, so ask the user first.
- On a remote or headless machine the OAuth sign-in ends on an address that does not load: run `claude mcp login --no-browser meta-ads-oauth` in a terminal of your own and paste that address there within 5 minutes. If it starts with `http://127.0.0.1`, write `localhost` in its place.

## First-day errors

Rely on the code, not the text. Docs: `https://developers.facebook.com/documentation/ads-commerce/marketing-api/error-reference.md`.

| Code | Meaning | Fix |
|---|---|---|
| "Unable to create" when you add an ad account (no code) | the ad account creation limit of the business portfolio is used up: a new portfolio may create one ad account, three once a campaign has delivered and a payment was made, and a closed account keeps counting | read the limit under Business settings > Business info (`https://www.facebook.com/business/help/1253008271714847`). Ways on: ask for access to an ad account of another portfolio (Ad accounts > Assign partner), contact support from Business Support Home, or appeal a disabled account in Account Quality. Do not open a new portfolio to get around a disabled account: Meta treats that as evasion |
| ad account `UNSETTLED`, `DISABLED` or `CLOSED` | unpaid balance, a policy restriction, or the account was closed | pay the balance in Billing, appeal in Account Quality, or reactivate the account; work in an `ACTIVE` account meanwhile |
| 190 | token invalid or expired | regenerate the token; check it in the debugger; was the password changed? |
| 200 | permission missing | scope not ticked or asset not assigned to the system user: redo steps 5 to 7 |
| 200 / 1870034 | Custom Audience terms not accepted | a normal user accepts them once in Ads Manager |
| 200 / 5258001 to 5258009 | API access disrupted | open the app's Data Use Checkup, Data Protection Assessment or reactivate the app |
| 294 | managing ads needs `ads_management` and an allowed app | add the scope; check the app's access tier |
| 100 | invalid parameter | read `error_subcode` and `error_user_msg` |
| 100 / 33 | unsupported post request | make the system user Admin of the ad account that owns the audience |
| 368 | action judged abusive | stop retrying; review the policy; contact Meta support |
| 17, 613, 80000, 80003, 80004, 80014, 4 | rate limit | wait; check the `X-Business-Use-Case-Usage` header (`estimated_time_to_regain_access`, minutes) |
| 2635 | API version retired | `doctor` or the toolkit's version in `ads/config.json` is old |
| 1815199 | ad account has no access to the Instagram account | assign the Instagram account to the ad account |
| 2446149 | `instagram_user_id` and `instagram_actor_id` both sent | send one |
