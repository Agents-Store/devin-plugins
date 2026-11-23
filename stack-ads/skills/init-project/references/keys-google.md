# Google keys: Google Ads API and Search Console API

How to get access to the Google Ads API and the Search Console API with one Google Cloud project and one OAuth client, and write the result into `ads/.env`. Facts verified 2026-11-14.

## Contents

- What you need
- Step 1: Cloud project and the two APIs
- Step 2: access level
- Step 3: OAuth consent screen
- Step 4: OAuth client
- Step 5: refresh token
- Step 6: customer id
- Step 7: Search Console property
- Step 8 (optional): official google-ads MCP server
- Verify
- Errors

## What you need

Developer tokens were abolished on 2026-09-09. Any guide that asks for a developer token, a manager (MCC) account to get one, or an API Center application is obsolete: do not send the user there. If a stored `developer-token` exists, it is ignored.

| Item | Variable in `ads/.env` | Where it comes from |
|---|---|---|
| OAuth client id | `GOOGLE_ADS_CLIENT_ID` | Step 4 |
| OAuth client secret | `GOOGLE_ADS_CLIENT_SECRET` | Step 4 |
| Refresh token | `GOOGLE_ADS_REFRESH_TOKEN` | Step 5, written by `google login` or `google import-adc` |
| Advertiser account, 10 digits, no dashes | `GOOGLE_ADS_CUSTOMER_ID` | Step 6 |
| Manager account id, only when the account is reached through a manager | `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Step 6 |
| Search Console property | `GSC_SITE_URL` | Step 7 |
| Cloud project id, MCP server only | `GOOGLE_CLOUD_PROJECT` | Step 1, used in Step 8 |
| Path of the ADC file, MCP server only | `GOOGLE_APPLICATION_CREDENTIALS` | written by `google export-adc` in Step 8 |

The Google user who signs in must have access to the Google Ads account and must have a passkey set up (a passkey created in the last 7 days may be refused). Ask the user to check this before Step 5. It is the login that opens the account at `ads.google.com`. It need not be the login that owns the Cloud project: the project and its OAuth client only identify the app, so the console can be used with one login and the consent of Step 5 given with another.

## Step 1: Cloud project and the two APIs

One project serves both APIs. The OAuth client must live in the same project in which the Google Ads API is enabled, because that project carries the access level.

1. Open `https://console.cloud.google.com/` and create or select a project. Note its project id (not the project number).
2. Open `https://console.cloud.google.com/google/ads-apis/overview` for the project and click **Enable**. This grants Test access.
3. Menu > **APIs & Services** > **Library** > search "Search Console API" > **Enable** (service name `searchconsole.googleapis.com`).
4. Billing on the project is optional; the API is free. A project unused for 90 days loses its access.

Docs: `https://developers.google.com/google-ads/api/docs/oauth/cloud-project`

## Step 2: access level

The access level belongs to the Cloud project and replaces the developer-token level. Enabling the API gives Test.

| Level | Reaches | Daily operations | How to get it | Review time |
|---|---|---|---|---|
| Test | test accounts only | 15,000 on test accounts | automatic when the API is enabled | none |
| Explorer | test and production | 2,880 on production, 15,000 on test | Overview page > **Upgrade access level** > Next level Explorer > **Apply for access** | automated, in most cases immediate |
| Basic | test and production | 15,000 | Overview page > Upgrade access level > Basic > Apply for access; needs brand verification first (below) | automated, minutes after verification and submit |
| Standard | test and production | unlimited | Overview page > **Start application**; audit, may need a demo login | about 10 business days |

- Explorer is enough to create campaigns (Search, Performance Max, Demand Gen), run `validateOnly` against production, and read reports. Start there.
- Keyword Planner (`google keyword-ideas`) needs Basic or higher. Explorer cannot call the keyword planning services, audience insights, reach planning, billing or account-creation services.
- A Test project that targets a production account fails with `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION`: apply for Explorer.
- Right after the approval a call can answer `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION` once more: repeat it before you conclude that the application failed.

Basic needs brand verification: Menu > **APIs & Services** > **OAuth consent screen** > **Overview** > **Get Started**, fill the project configuration. On **Audience** the user type must be External and the status In production (see Step 3). On **Branding** fill every required field > **Save** > **Verify Branding** (takes minutes) > **Publish branding**. Then apply for Basic on the Overview page.

Known issues (2026-11-13): an application is rejected on a Free Trial or suspended billing account; a project that used a Test token before 2026-09-09 can return `AUTHORIZATION_ERROR` after an upgrade. Fixes are in the Errors table.

Docs: `https://developers.google.com/google-ads/api/docs/api-policy/access-levels`

## Step 3: OAuth consent screen

1. Menu > **Google Auth platform** > **Branding** > **Get Started** if it says "not configured yet". Enter the app name and the support email, choose **External**, enter the contact email, accept the policy, **Create**.
2. **Data Access** > **Add or Remove Scopes** > add the scopes below > **Save**.
3. **Audience** > **Publish app** > confirm "Push to Production?". The status must read **In production**.

**Publish app** can be greyed out with "To publish your app, you must complete your configuration on the Branding page" while the three required fields are filled. Since autumn 2026 the button wakes up only when **Branding** also names an application home page, a privacy policy link and, under **Authorized domains**, the domain of those two links (Google's answer in its issue tracker, 2026-10-06; seen on 2026-11-23). Fill them, **Save**, then publish. Do not upload a logo: a logo starts a verification. A user with no site to name stays in **Testing**: add the Google login under **Audience** > **Test users** and repeat Step 5 every 7 days.

| Scope | Gives |
|---|---|
| `https://www.googleapis.com/auth/adwords` | Google Ads API |
| `https://www.googleapis.com/auth/webmasters.readonly` | Search Console read access |

Why In production: while the status is **Testing**, every refresh token dies after 7 days and calls fail with `invalid_grant`. Testing also requires every user to be listed under **Audience** > **Test users**, or sign-in ends with "Access blocked".

What the user sees in production: an "unverified app" warning at sign-in. Tell them to click **Advanced** > **Go to <app name> (unsafe)**. It is their own app. An unverified app has a lifetime cap of 100 users, which does not matter for one person.

Whether the Search Console scope needs OAuth verification in production is unverified. If sign-in is blocked for that reason, drop the Search Console scope from this client and ask the user to decide.

Docs: `https://support.google.com/cloud/answer/15549945`

## Step 4: OAuth client

1. Menu > **Google Auth platform** > **Clients** > **Create Client** (older consoles: **APIs & Services** > **Credentials** > **Create Credentials** > **OAuth client ID**).
2. Application type: **Desktop app**. Give it a name. Leave "Use this client for an AI-powered agent" off unless the user wants it (it cannot be changed later).
3. **Create**. Copy the client id and the client secret into `ads/.env`, or download the JSON and keep it for route (b) in Step 5.

```text
GOOGLE_ADS_CLIENT_ID=<client id ending in .apps.googleusercontent.com>
GOOGLE_ADS_CLIENT_SECRET=<client secret>
```

Docs: `https://developers.google.com/workspace/guides/create-credentials`

## Step 5: refresh token

Route (a) is the default. The tool prints the consent URL; the user opens it in any browser, on any machine, and pastes back the address the browser ends on. Nothing has to listen on the port, so it works on a remote or headless machine.

### Route (a): the toolkit

```bash
python3 ads/tools/ads.py google login --scopes ads,gsc
```

1. The command prints a consent URL. It opens Google's account chooser: the user picks the login that opens the Ads account at `ads.google.com`, passes the "Google hasn't verified this app" page (**Advanced** > **Go to <app name> (unsafe)**) and approves both scopes.
2. After approval the browser is sent to an address on port 8080 and shows a page that fails to load. That is expected. The user copies the full address from the address bar. An address on `accounts.google.com` is an intermediate page, the warning or the consent form, not the one to copy.
3. Exchange it. Quote the URL: it contains `&`.

```bash
python3 ads/tools/ads.py google login --redirect-url '<FINAL_REDIRECT_URL>'
```

The refresh token is stored in `ads/.env` as `GOOGLE_ADS_REFRESH_TOKEN`. Nothing is printed. Use `--scopes ads` or `--scopes gsc` for one service only. If the user has no Search Console, leave `gsc` out.

### Route (b): gcloud application-default login

Use it when `gcloud` is already installed. `--client-id-file` is mandatory: without it the token is issued under Google's own client, not the user's project.

```bash
gcloud auth application-default login \
  --client-id-file=client_secret.json \
  --scopes=https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform
```

- `client_secret.json` is the file downloaded in Step 4.
- The file is saved as `~/.config/gcloud/application_default_credentials.json` and holds the client id, the client secret and the refresh token.
- Keep `cloud-platform` in the list: the official Google Ads MCP guide requests it together with `adwords`. Whether gcloud requires it is unverified.

Import it into `ads/.env` (the second form names another file):

```bash
python3 ads/tools/ads.py google import-adc
python3 ads/tools/ads.py google import-adc --file '<PATH_TO_ADC_FILE>'
```

Docs: `https://developers.google.com/google-ads/api/docs/oauth/single-user-authentication`

## Step 6: customer id

- `GOOGLE_ADS_CUSTOMER_ID` is the account the campaigns run in. It is the 10-digit number shown as `123-456-7890` at the top of the Google Ads interface. Write it without dashes: dashes cause `CLIENT_CUSTOMER_ID_INVALID`.
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID` is the manager account id. Set it only when the signed-in user reaches the advertiser account through a manager account. Leave it empty when the user has direct access. A missing value in the manager case gives `USER_PERMISSION_DENIED`.

List what the credential reaches:

```bash
python3 ads/tools/ads.py google customers
```

The list shows the accounts the user can access directly. A client account under a manager is reached through it: manager id in `GOOGLE_ADS_LOGIN_CUSTOMER_ID`, client id in `GOOGLE_ADS_CUSTOMER_ID`.

A new production account needs billing set up in the Google Ads interface before ads serve.

## Step 7: Search Console property

`GSC_SITE_URL` must match a property the signed-in user can access, character for character.

| Property type | Value | Verified by |
|---|---|---|
| Domain property (all protocols and subdomains) | `sc-domain:example.com` | DNS TXT or CNAME record |
| URL-prefix property | `https://www.example.com/` with the trailing slash | DNS, HTML file, HTML tag, Analytics code or Tag Manager snippet |

Rules:
- Use the form that exists. If the user has both, prefer the domain property.
- The signed-in Google user must appear on the property. If the user is not the owner: an owner opens Search Console > the property > **Settings** > **Users and permissions** > **Add user**, enters the Google account email, and picks **Full** or **Restricted**. Read access is enough. Groups cannot be added; a property takes 100 non-owner users.

List the properties the credential sees and copy the value from the output:

```bash
python3 ads/tools/ads.py gsc sites
```

Docs: `https://support.google.com/webmasters/answer/9008080`

## Step 8 (optional): official google-ads MCP server

Google ships one MCP server, `google-ads-mcp` (Python, PyPI). It is pre-1.0: pin the version, tool names changed in 0.0.6.

| Needs | Detail |
|---|---|
| `pipx` | the server is started with `pipx run --spec google-ads-mcp==0.0.6 google-ads-mcp` |
| Python | 3.10 or later per PyPI; Google's own skill says 3.12; unverified, use 3.12 |
| An ADC file | `google export-adc` (below) writes it from the credentials already in `ads/.env`, whichever login route produced them. The file made by gcloud in route (b) works as well |
| `GOOGLE_CLOUD_PROJECT` | the project id from Step 1 |
| `GOOGLE_APPLICATION_CREDENTIALS` | the full path of the ADC file; `google export-adc` stores it for you. By hand, write the path in full: whether `~` is expanded in the MCP environment is unverified |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | only for a manager account; the same variable as in Step 6 |

What it can do: list accessible accounts, run structured GAQL reads, return resource metadata, create assets (text, image, YouTube video, sitelink, callout, structured snippet), upload video, manage labels. Every write runs `validateOnly` first and needs a confirm step with a checksum.

What it cannot do: create, change, pause or enable campaigns, ad groups, ads, budgets, bids or keywords; link assets to campaigns or asset groups; keyword planning. Use the toolkit (`google mutate`, `google keyword-ideas`) for those. The server needs no developer token.

Write the credentials file, hand the variables to Claude Code so `${VAR}` resolves, then restart the session:

```bash
python3 ads/tools/ads.py google export-adc
python3 ads/tools/ads.py env sync-claude
```

`google export-adc` writes `ads/.google-adc.json` (ignored by git, readable by the owner only) with the client id, the client secret and the refresh token, and stores its full path as `GOOGLE_APPLICATION_CREDENTIALS` in `ads/.env`. Set `GOOGLE_CLOUD_PROJECT` in `ads/.env` before the sync. The file is a credential: never commit or share it. If the server answers with a scope error, repeat the login through route (b), which adds the `cloud-platform` scope, run `google import-adc`, then `google export-adc` again.

Docs: `https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server`

## Verify

```bash
python3 ads/tools/ads.py doctor --live --only google,gsc
```

One read-only call per service. A missing key prints where to get it. Exit code 3 means a key is missing; 1 means Google rejected the call (the message carries its code). When both pass, run `google customers` and `gsc sites` once to confirm the ids.

## Errors

| Error | Cause | Fix |
|---|---|---|
| `invalid_grant` | consent screen still in Testing (7-day expiry), token revoked, or 6 months unused | Step 3: set In production, then redo Step 5 |
| "Access blocked" at sign-in | status Testing and the user is not under Test users | Publish to production (Step 3), or add the user under **Audience** > **Test users** |
| `admin_policy_enforced` | a Workspace admin restricted third-party apps | the admin allows the OAuth client, or the user signs in with a personal Google account |
| `ACCESS_TOKEN_SCOPE_INSUFFICIENT` | token lacks the `adwords` scope | redo Step 5 |
| `NOT_ADS_USER` | the Google login that gave the consent has no Google Ads account; often it is the login that owns the Cloud project | repeat Step 5 and pick the login that opens `ads.google.com`, or add this login to the account (Admin > Access and security) |
| `CLOUD_PROJECT_NOT_APPROVED_FOR_PRODUCTION` | project has Test access and the account is production | apply for Explorer on the project that owns the OAuth client (Step 2); right after the approval repeat the call once |
| `AUTHORIZATION_ERROR` on production just after an upgrade | known issue for projects that used a Test token before 2026-09-09 | wait, or new Cloud project and apply for Explorer there |
| Explorer or Basic application rejected | project on Free Trial or suspended billing | paid project, or another brand-verified project |
| `USER_PERMISSION_DENIED` | the account is reached through a manager | set `GOOGLE_ADS_LOGIN_CUSTOMER_ID` to the manager id |
| `CLIENT_CUSTOMER_ID_INVALID` | dashes in a customer id | digits only |
| `CUSTOMER_NOT_ENABLED` | sign-up not finished, or the account is cancelled | finish sign-up or reactivate in Google Ads |
| `RESOURCE_EXHAUSTED` | daily quota of the access level (24-hour window) | wait, or upgrade (Step 2) |
| Keyword Planner call refused: "not allowed for use with explorer access" (`DEVELOPER_TOKEN_NOT_APPROVED`) | project is on Explorer | apply for Basic (Step 2) |
| **Publish app** greyed out | Branding lacks the home page, the privacy policy link or the authorized domain | fill the three (Step 3), or stay in Testing with the login under Test users |
| `gsc sites` lists another site than expected, or none | the property belongs to another Google login than the one that gave the consent | add the consent login to the property (Step 7), then copy `GSC_SITE_URL` from `gsc sites` |
| Search Console 403 "does not have sufficient permission for site" (unverified wording) | the signed-in user is not on the property, or `GSC_SITE_URL` has the wrong form | add the user (Step 7); copy the value from `gsc sites` |
| `SERVICE_DISABLED` (unverified) | the API is not enabled in the OAuth client's project | enable it in Step 1 |
| 429 from Search Console | per-site or project quota | wait; for the load quota 15 minutes |
