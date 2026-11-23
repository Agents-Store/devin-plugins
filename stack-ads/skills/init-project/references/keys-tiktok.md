# How to get TikTok Ads access

How to get TikTok access for a user who has never used the TikTok Marketing API: the official MCP server (no keys) and the developer app that the toolkit's direct API calls need. Facts verified 2026-11-14.

## Contents

- Which route
- Route 1: official TikTok for Business MCP server
- Route 2: developer app for the toolkit
- What you need (variables)
- Find the ids
- Verify
- Before launch
- First-day errors

## Which route

| Need | Route |
|---|---|
| Interactive work in Claude Code, no developer account, no keys | 1: MCP server |
| Toolkit commands `tiktok get`, `tiktok post`, `tiktok report`, uploads, `launch` plans; unattended or scheduled runs | 2: developer app and long-term token |
| Both | Do route 1 first (minutes), route 2 later (days of review) |

The toolkit's `tiktok ...` commands read `TIKTOK_ACCESS_TOKEN`; the MCP server's OAuth does not feed them. Route 2 is required for any `ads.py tiktok` command.

## Route 1: official TikTok for Business MCP server

Docs: `https://business-api.tiktok.com/portal/docs/tiktok-ads-mcp-server/v1.3`

| Item | Value |
|---|---|
| Server in this plugin | `tiktok-ads`, the layered server (about 40 core tools, others on demand) |
| Full server | about 400 tools, heavy on context; the layered one is the token-conscious choice |
| Sign-in | OAuth 2.0 with PKCE inside the MCP client; consent with your TikTok for Business account |
| Needs | a TikTok for Business account with an ad account; no developer app, no API key |
| Lifetime | user authorization 30 days, then authorize again; MCP access token 24 hours, refresh token 30 days |
| Limits | 6 requests per second per tool per user; a Smart+ ad create, update or status call: one operation per 5 seconds per ad |

Authorize in Claude Code:

1. Open `/mcp`.
2. Pick `tiktok-ads`.
3. Choose Authenticate; sign in to TikTok for Business in the browser and confirm the consent screen.
4. Back in `/mcp` the server shows as connected. Repeat every 30 days.

On a remote or headless machine the browser ends on a `localhost` address that does not load. That is expected: copy the whole address from the address bar and hand it to the client. `claude mcp login --no-browser tiktok-ads`, run in a terminal of your own, prints the sign-in link and takes the pasted address. The link is good for 5 minutes, so open it only when you can finish in one go.

Ads on TikTok placement need a TikTok account linked to the ad account. When `identity_get` lists only a `CUSTOMIZED_USER` identity, link one first: the TikTok launch reference of the `launch-campaign` skill, section 2, has the two steps (`tiktok_identity_connect_ui`, then `bc_asset_advertiser_assign`).

If the account has no ad account yet, create one first (Route 2, step 2). If tools are missing for an account type or region, availability can vary; use the toolkit instead. Whether MCP write operations are limited for some account types is unknown (unverified).

## Route 2: developer app for the toolkit

Docs: `https://business-api.tiktok.com/portal/docs/marketing-api-authorization/v1.3`

| Step | Do | Wait |
|---|---|---|
| 1 | Create a TikTok for Business account on the Developers portal: e-mail or phone, password, verification code | none |
| 2 | Create an ad account in Ads Manager: country, industry, legal business name, time zone, currency, billing and payment method | approval, usually under 24 hours; ads cannot run before it |
| 3 | Register as a developer (portal > Become a Developer) | up to 3 business days |
| 4 | Create a developer app (portal > Create an App) | 2 to 3 business days |
| 5 | Advertiser authorization: get `auth_code` | minutes |
| 6 | Exchange the code for a token with the toolkit | seconds |

Step 3, developer registration. Rejections come from these rules, so prepare them:

- Communication e-mail: a verified company-domain address. Personal or temporary e-mail is rejected.
- User type (Technology Company, Direct Advertiser or Agency) must match the company data.
- Company website: public, working, own domain matching the e-mail domain. No shortened links, social, hosting or e-commerce domains, personal sites. Personal accounts and individual developers are not onboarded.
- Primary Developer Location: where the development team sits.
- Use-case description: be specific, or it may be rejected.

Step 4, the app:

1. Fields: app name (a developer-app name, not a mobile-app name), description ("Intended Uses" plus "Developer App Access Controls: internal only or shared with external accounts"), advertiser redirect URL (up to 10; for example `https://example.com/callback`; a new URL creates a new authorization URL), scope of permission. Then Confirm.
2. Scopes to select (they must match the description):

| Scope | Id | Why |
|---|---|---|
| Ads Management | 2 | campaigns, ad groups, ads |
| Reporting | 4 | `tiktok report` |
| Creative Management | 6 | video and image upload |
| Audience Management | 3 | audiences |
| Pixel Management | 8 | pixels |
| Ad Account Management | 1 | account details |
| Measurement | 5 | Events API; only if used |

3. Status: red button top right > My Apps > Verification Status. A rejected app can be edited and resubmitted. Scopes change later without a new app: My Apps > the app > Scope of permission > edit > Submit (review again 2 to 3 business days). Limit: 5 developer apps per developer.
4. Scope "TikTok Accounts" needs a separate Accounts API application form first. Not needed here.

Step 5, authorization:

1. Portal > My Apps > the app > Basic Information > copy the **Advertiser authorization URL**.
2. The owner of the ad account opens it, reviews permissions, accepts the agreement, Confirm, Send Code (sent to the e-mail of the ad account), enters the code, Confirm. An agency can do this for a client.
3. TikTok redirects to your redirect URL with `auth_code=...` appended. Use the `auth_code` value. It is valid for 1 hour and works once (error 40110 otherwise).

Step 6, exchange. Put `TIKTOK_APP_ID` and `TIKTOK_APP_SECRET` (My Apps > Basic Information) into `ads/.env` first, then:

```bash
python3 ads/tools/ads.py tiktok oauth-exchange --auth-code CODE --write
```

`--write` stores the long-term token as `TIKTOK_ACCESS_TOKEN` in `ads/.env`, and `TIKTOK_ADVERTISER_ID` too when the token covers exactly one ad account. The token does not expire, so there is nothing to refresh; it stops working only if the advertiser revokes access or the app is blocked. Without `--write` the command only trades the code. Never paste the app secret or token into chat, logs or URLs.

## What you need (variables)

| Item | Variable | Where it comes from |
|---|---|---|
| Long-term access token | `TIKTOK_ACCESS_TOKEN` | `tiktok oauth-exchange --write` |
| Ad account id | `TIKTOK_ADVERTISER_ID` | Ads Manager account menu, or the list below |
| App id | `TIKTOK_APP_ID` | My Apps > the app > Basic Information |
| App secret | `TIKTOK_APP_SECRET` | same page |
| Pixel id, optional | `TIKTOK_PIXEL_ID` | Ads Manager > Tools > Events, or `tiktok get pixel/list/` |

The MCP route needs none of these.

## Find the ids

| Id | How |
|---|---|
| Advertiser id | Ads Manager: top bar, right side, open the account-name dropdown; it shows name and id. Also in the token response (`advertiser_ids`) |
| All authorized advertiser ids | `python3 ads/tools/ads.py tiktok get oauth2/advertiser/get/` returns `advertiser_id` and `advertiser_name` for every ad account the token covers. It needs only the token, the app id and the app secret in `ads/.env`: the toolkit adds `app_id` and `secret` to `oauth2/` reads, and no advertiser id |
| Pixel id | Ads Manager > Tools > Events > Data sources > click the pixel. Or `tiktok get pixel/list/` (returns `pixel_id`, `pixel_code`, `pixel_name`); the ad group uses `pixel_id`, the Events API uses `pixel_code` |
| Identity id (for Spark Ads) | `tiktok get identity/get/ -p identity_type=TT_USER` returns `identity_list` with `identity_id`, `username` |
| Business Center id | `tiktok get bc/get/`, or `owner_bc_id` in `tiktok get advertiser/info/`; the UI path is unverified |

Set `TIKTOK_ADVERTISER_ID` before the `tiktok get` calls: the toolkit adds it to every call. A pixel does not exist yet: Ads Manager > Tools > Events > Connect data source > Web > Next > domain URL > Manual Setup > TikTok Pixel + Events API > name > Create.

## Verify

```bash
python3 ads/tools/ads.py doctor --live --only tiktok
python3 ads/tools/ads.py tiktok get advertiser/info/ -p 'advertiser_ids=["{advertiser}"]'
```

The first makes one read-only call and prints where to get a missing key. The second returns currency, time zone, status and balance of the account; `{advertiser}` is filled from `TIKTOK_ADVERTISER_ID`. Currency is fixed per ad account.

## Before launch

- **Sandbox is gone.** TikTok deprecates sandbox accounts by 2026-12-01 and tells developers to test in production. The sandbox never had Smart+ endpoints. Test on the real ad account with objects created disabled (`"operation_status": "DISABLE"`, which the toolkit enforces) and a small budget.
- **Trailing slash.** Every endpoint path ends with `/` (`campaign/get/`). A missing slash or wrong HTTP method returns HTTP 404.
- **Check `code`, not HTTP status.** HTTP 200 can carry `code` other than 0. HTTP 4xx means a wrong path or method; HTTP 5xx means retry after about 5 minutes.
- **Sales, App Promotion and Lead Generation** campaigns move to the Upgraded Smart+ endpoints (`smart_plus/...`): manual creation stops on 2027-01-01 (one guide page says 2026-12-31; treat 2026-12-31 as the safe date). Smart+ campaign management may need account allowlisting, shown as error 40118 (current status unverified).
- **Minimum budgets conflict in the docs.** Guide text says 20 USD; the per-currency table lists 50 USD for a campaign. Use 50 USD or the equivalent as the safe minimum.
- **Rate limits.** Default app tier: 10 requests per second, 600 per minute, 864,000 per day. After a per-minute breach wait 5 minutes; the daily count resets at 00:00 UTC. `ad/create/` is tighter: 5 per second.

## First-day errors

Docs: `https://business-api.tiktok.com/portal/docs/return-codes-appendix/v1.3`

| Code | Meaning | Fix |
|---|---|---|
| "Invalid Developer Status" on **Create an App** (portal message, no code) | the developer registration of step 3 is not approved yet | wait for the approval (up to 3 business days), then create the app |
| 40101 | app id or secret wrong, or bad `auth_code` | recheck My Apps > Basic Information; redo authorization |
| 40102 | access token expired | authorize again and rerun `oauth-exchange --write` |
| 40104 | access token empty | `TIKTOK_ACCESS_TOKEN` missing; run `oauth-exchange --write` |
| 40105 | access token invalid | redo authorization |
| 40106 | token does not match the advertiser | authorize that advertiser, or fix `TIKTOK_ADVERTISER_ID` |
| 40110 | `auth_code` used, cancelled or older than 1 hour | open the Advertiser authorization URL again for a new code |
| 40113 | app blocked, or wrong app id or secret | check the app status and credentials |
| 40001 | no permission | add the scope in My Apps (review again) or authorize the right advertiser |
| 40125 | developer lacks permission or field unsupported | edit the scopes |
| 40124 | developer profile not approved | wait for the registration review |
| 40118 | app or advertiser not allowlisted for the feature | ask the TikTok representative to allowlist |
| 40119 | developer and advertiser are not the same company | authorize an advertiser of the same company |
| 40100, 40016 | app rate limit | back off; per-minute breach: wait 5 minutes |
| 40133 | advertiser rate limit | lower the request rate per advertiser |
| 40300, 40301 | advertiser does not exist or cannot be matched | check `TIKTOK_ADVERTISER_ID` |
| 40002 | parameter error | read `message` and fix the field |
| 40007 | object does not exist | check the ids |
| 40010 | wrong domain | base URL must be the production API host |
| 50000, 50002, 51305, 60001 | TikTok-side error or maintenance | wait about 5 minutes and retry |
