# Ads toolkit reference (`ads/tools/ads.py`)

One command-line tool backs every skill of this plugin. It needs Python 3.9 or later and nothing else: no packages to install. `init-project` copies it into the project as `ads/tools/`, so the command is the same on every agent and in every shell.

## Contents

- Running it
- Workspace layout
- Setup commands
- Google Ads and Search Console
- Meta
- TikTok
- Creative generation
- Research
- Launch plans
- Plan file format
- Guard rails
- Exit codes

## Running it

```bash
python3 ads/tools/ads.py doctor
python3 ads/tools/ads.py <group> <command> --help
```

Run it from the project root. Keys come from `ads/.env`, then from a `.env` in the project root, and a variable already exported in the shell wins over both. No command prints a key.

A write never happens by accident: every command that changes something outside the project prints what it would do and stops, unless it carries `--yes`. Starting spend needs `--activate` as well. Flags are written in full: `--y` or `--act` is rejected, not guessed.

## Workspace layout

```text
ads/
  config.json        project facts, budget ceilings (guardrails), API versions, chosen models
  .env               keys (ignored by git)
  brief.md           product, audience, offer
  brand.json         colours, fonts, logo, tone
  brand/             the real logo and product images
  research/          competitors, keywords, audiences; raw/ holds untouched API output (ignored by git)
  plan/              media plan, copy/ with the copy packs, the creative list
  creatives/         generated images, video, audio and manifest.jsonl; inputs/ for fal.ai input files
  launch/            plan files, dry-run output, ledger.jsonl
  reports/           performance reports; raw/ holds the pulls (ignored by git)
  tools/             this toolkit (ignored by git)
```

## Setup commands

| Command | What it does |
|---|---|
| `init [--dir ads] [--update]` | Create the workspace, copy the toolkit into `ads/tools/`, write `ads/.env` from the template when it is missing. `--update` refreshes only the toolkit. |
| `keys [--json]` | List every variable: service, what it unlocks, set or missing. Values are never shown. |
| `doctor [--live] [--only NAMES] [--json]` | Check which keys are present. `--live` makes one cheap read-only call per configured service. For a missing or rejected key it prints where to get one. `NAMES` is a comma list of `firecrawl, apify, dataforseo, openai, gemini, fal, google, gsc, meta, tiktok`. |
| `env sync-claude [--settings PATH]` | Copy the keys from `ads/.env` into the `env` block of `.claude/settings.local.json`, so `${VAR}` in the plugin's MCP configuration resolves. Refuses when that file is not ignored by git. Restart the session afterwards. |

## Google Ads and Search Console

| Command | What it does |
|---|---|
| `google login [--port 8080] [--scopes ads,gsc]` | Print the consent URL for the OAuth client in `ads/.env`. |
| `google login --redirect-url URL` | Exchange the code in the pasted redirect URL and store the refresh token in `ads/.env`. |
| `google import-adc [--file PATH]` | Take client id, secret and refresh token from a gcloud application-default credentials file. |
| `google export-adc [--file PATH]` | Write the stored credentials as `ads/.google-adc.json` (ignored by git) and point `GOOGLE_APPLICATION_CREDENTIALS` at it, for the google-ads MCP server. |
| `google customers` | List the accounts the credential can reach. |
| `google search --query GAQL [--customer ID] [--format json\|csv] [--out FILE]` | Run a GAQL query (`googleAds:search`, all pages). |
| `google mutate --file FILE [--customer ID] [--partial-failure] [--yes] [--activate]` | Send a `googleAds:mutate` body. Without `--yes` it runs with `validateOnly`, also for a body that would switch something on: the output then carries a `note` that sending it needs `--activate` as well. `{customer}` in the body becomes the account id. With `--partial-failure`, a run in which Google applied only part of the request ends with exit code 1. |
| `google keyword-ideas (--keywords A,B \| --url URL) --geo IDS --language ID [--limit N] [--format json\|csv] [--out FILE]` | Keyword Planner ideas with volumes and bid ranges (needs Basic access). |
| `google geo --query NAMES [--country CC] [--locale LL]` | Resolve place names to geo target constants. |
| `google upload-conversions --file FILE --action ID [--source WEB] [--customer ID] [--yes]` | Click conversions through the Data Manager API (`events:ingest`). `FILE` is a CSV with a header line or a JSON list of rows: `gclid` (or `gbraid`, `wbraid`), `time` with its offset (`2026-11-26 12:00:00+00:00`), `value` in currency units, `currency` (default: the platform currency), `order_id`. `--action` is the numeric id of an `UPLOAD_CLICKS` or `WEBPAGE` conversion action; a `WEBPAGE` action needs `order_id` on every row. At most 2000 rows. Without `--yes` Google validates the rows and records nothing; with `--yes` it records them and returns a `requestId`. Needs the Data Manager API enabled and the `datamanager` scope (Google key guide, step 9). |
| `google upload-status --request-id ID` | Processing result of an upload: `PROCESSING`, `SUCCESS`, `PARTIAL_SUCCESS` or `FAILED`, with the reasons per row (click not found, too old, duplicate). Check 30 minutes after the upload. |
| `google call METHOD PATH [--data @FILE] [--yes]` | A read, or a conversion upload, by its REST path. Google keeps `uploadClickConversions` for existing integrations: a new one gets `CUSTOMER_NOT_ALLOWLISTED_FOR_THIS_FEATURE` and uses `google upload-conversions`. A reply with `partialFailureError` ends with exit code 1. `PATH` is relative to the API version root and carries no query string; `{customer}` in the path or the body becomes `GOOGLE_ADS_CUSTOMER_ID`. A `GET` and the methods `:search`, `:searchStream`, `:suggest...`, `:generate...` and `:list...` only read and run without `--yes`. The only writes it sends are `customers/{customer}:upload...` (conversions) and `offlineUserDataJobs` (customer lists), printed until `--yes` is added. Every `...:mutate` method, batch jobs, recommendations and experiments are refused: campaigns, budgets, ad groups, ads, keywords and assets change through `google mutate`, where the guard rails apply. |
| `gsc sites` | List verified Search Console properties. |
| `gsc query [--site SITE] --start DATE --end DATE [--dimensions query,page] [--row-limit N] [--type web] [--data-state final\|all] [--filter DIM:OP:VALUE] [--format json\|csv] [--out FILE]` | Search Analytics rows. `--site` defaults to `GSC_SITE_URL`. `--filter` repeats; `OP` is `contains`, `equals`, `notContains`, `notEquals`, `includingRegex` or `excludingRegex`. |

## Meta

In a path and in parameter values, `{account}` becomes `act_` plus `META_AD_ACCOUNT_ID`, `{page}` becomes `META_PAGE_ID`, `{pixel}` becomes `META_PIXEL_ID` and `{instagram}` becomes `META_INSTAGRAM_USER_ID`. A parameter value may be a JSON object or list; it is sent as JSON text. A path is written plain, such as `{account}/adsets` or an object id: parameters go into `-p` or `--data`, and a path that carries a query string is refused. When `META_APP_SECRET` is set, every call carries `appsecret_proof`.

| Command | What it does |
|---|---|
| `meta get PATH [-p KEY=VALUE]` | Graph API read. `-p` repeats. A parameter named `method` is refused in every Meta command: the Graph API would take it as an order to send another kind of request. |
| `meta post PATH [-p KEY=VALUE] [--data @FILE] [--yes] [--activate]` | Graph API write. Without `--yes`, creations of campaigns, ad sets, creatives and ads are sent with `validate_only`; other writes are only printed. Refused: `batch` and `adbatch` (calls inside a call), `adset_spec` and `campaign_spec` (a second object inside a call), and a copy (`ID/copies`) without `status_option=PAUSED` unless `--activate` is given. |
| `meta delete PATH [-p KEY=VALUE] [--yes]` | Graph API delete, printed until `--yes` is added. An image leaves the library by its hash: `meta delete {account}/adimages -p hash=HASH`. |
| `meta upload-image --file FILE [--yes]` | Upload to the ad account image library; prints the image hash. |
| `meta upload-video --file FILE [--name NAME] [--yes]` | Upload to the ad account video library; prints the video id. |
| `meta insights [--object ID] [--level account\|campaign\|adset\|ad] [--preset last_7d \| --since DATE --until DATE] [--fields LIST] [--breakdowns LIST] [-p KEY=VALUE] [--format json\|csv] [--out FILE]` | Insights rows, all pages. `-p` adds any other Insights parameter, such as `time_increment=1`. |
| `meta search --type TYPE --q TEXT [-p KEY=VALUE]` | Targeting search (`adinterest`, `adgeolocation`, `adTargetingCategory` and so on). |
| `meta ad-library --terms TEXT --countries CC[,CC] [--limit N] [--out FILE]` | Ad Library API search. |

## TikTok

`advertiser_id` is added to every call from `TIKTOK_ADVERTISER_ID` (and `app_id` with `secret` to `oauth2/` reads). In a body and in a parameter value, `{advertiser}` and `{pixel}` become `TIKTOK_ADVERTISER_ID` and `TIKTOK_PIXEL_ID`. The trailing slash of a path is added for you; a path with a query string is refused. A response with a `code` other than 0 is reported as an error even though TikTok answers it with HTTP 200.

| Command | What it does |
|---|---|
| `tiktok get PATH [-p KEY=VALUE]` | Marketing API read, for example `campaign/get/`. |
| `tiktok post PATH --data @FILE [--yes] [--activate]` | Marketing API write, printed until `--yes` is added. A path that ends in `get`, `list`, `search`, `estimate`, `recommend`, `check` or `info` only reads and runs without `--yes`. |
| `tiktok upload-video (--file FILE \| --url URL) [--name NAME] [--yes]` | Upload a video creative; prints `video_id`. |
| `tiktok upload-image --file FILE [--yes]` | Upload an image creative; prints `image_id`. |
| `tiktok report --level LEVEL --start DATE --end DATE [--metrics LIST] [--dimensions LIST] [--format json\|csv] [--out FILE]` | Integrated report. `LEVEL` is `AUCTION_ADVERTISER`, `AUCTION_CAMPAIGN`, `AUCTION_ADGROUP` or `AUCTION_AD`. |
| `tiktok oauth-exchange --auth-code CODE [--write]` | Trade an authorization code for a long-term token; `--write` stores it in `ads/.env`. |

## Creative generation

Model ids change every few months, so none is built in. `models --pick` asks the provider what exists today and stores the choice in `ads/config.json`; `--model` overrides it for one call.

| Command | What it does |
|---|---|
| `models [--provider openai\|gemini\|fal] [--kind image\|video\|speech\|music\|analysis] [--query TEXT] [--pick] [--json]` | List the generation models the key can use. `--pick` saves a default per kind. On fal.ai `--query` searches the whole catalogue, for example `--query "background removal"`. |
| `image --prompt TEXT [--provider P] [--model ID] [--aspect 1:1\|4:5\|9:16\|16:9\|1.91:1] [--size WxH] [--n N] [--quality low\|medium\|high] [--ref FILE] [--transparent] [--fit WxH] [--out DIR] [--name STEM]` | Generate images. `--ref` repeats and switches to editing with reference images. `--fit` also saves a copy scaled and centre-cropped to an exact pixel size (needs ffmpeg). |
| `video --prompt TEXT [--provider gemini\|fal] [--model ID] [--aspect 9:16\|16:9\|1:1] [--seconds N] [--resolution 720p\|1080p\|...] [--image FILE] [--out DIR] [--name STEM]` | Generate a short clip, optionally from a first frame. The resolution is passed to the provider as written (Gemini: 360p, 720p, 1080p, 4k); 720p is the default. |
| `speech --text TEXT [--provider P] [--model ID] [--voice NAME] [--out FILE]` | Generate a voice-over. |
| `music --prompt TEXT [--provider gemini\|fal] [--model ID] [--out FILE]` | Generate a music track or jingle. |
| `analyze --prompt TEXT (--file FILE \| --url URL) [--provider gemini\|openai] [--model ID]` | Describe an image or a video, such as a competitor ad. |
| `fal schema MODEL` | Print the input fields of a fal.ai model. |
| `fal run MODEL --input @FILE [--out DIR] [--name STEM]` | Run any fal.ai model through the queue and download what it returns. In the input, `{"@upload": "ads/creatives/photo.png"}` uploads that local file and puts its URL in place. |

Files go to `ads/creatives/` unless `--out` names another folder. With `--name hero` they are called `hero.png`, `hero-2.png` and so on, with the extension of the format the provider returned (`.png` or `.jpg`); without a name the file name is built from the prompt and a timestamp. An existing file is never overwritten: the next free number is used, and the command prints the paths it wrote. Every generated file is listed in `ads/creatives/manifest.jsonl` with provider, model, prompt and size. How the options map: on OpenAI `--aspect` and `--size` become a pixel size rounded to multiples of 16; on Gemini they become the nearest supported aspect ratio and a 1K, 2K or 4K tier, and `--n` makes one call per image; on fal.ai the tool reads the model's input fields and fills `aspect_ratio` or `image_size`, `num_images`, `duration` and `resolution` where the model has them.

## Research

| Command | What it does |
|---|---|
| `firecrawl scrape URL [--formats LIST] [--schema @FILE] [--prompt TEXT] [--out FILE]` | Scrape one page. `LIST` is a comma list of `markdown, links, branding, screenshot, html`. `--schema` adds structured extraction. |
| `firecrawl search QUERY [--limit N] [--out FILE]` | Web search. |
| `firecrawl map URL [--limit N] [--search TEXT]` | List the URLs of a site. |
| `apify actor ACTOR` | Show an Actor's pricing and input fields. |
| `apify run ACTOR --input @FILE [--max-usd X] [--max-items N] [--timeout SECONDS] [--out FILE]` | Run an Actor and save its dataset. The spend cap defaults to the value in `ads/config.json`. |
| `dataforseo post PATH --data @FILE [--sandbox] [--out FILE]` | Call a DataForSEO v3 endpoint; `PATH` starts after `v3/`. |
| `dataforseo get PATH [--sandbox]` | DataForSEO read. |

## Launch plans

| Command | What it does |
|---|---|
| `launch plan --file PLAN` | Dry run. Checks the plan, asks the platform to validate what it can, and prints the eight blocks: TARGET, PRECHECK, CHANGE, BACKUP, IMPACT, VALIDATE, ROLLBACK, APPLY. Exit code 2 when the plan is blocked. Each dry run is recorded in the ledger with a fingerprint of what it looked at: the plan, the files it sends, the account ids in `ads/.env` and the project currency. |
| `launch apply --file PLAN --yes [--resend STEP]` | Run the steps in order, everything paused, and record each created object in the ledger. Refused unless the last dry run was clean and nothing it looked at has changed since: a changed plan is a new plan. It stops at the first failed step. After a refusal by the platform, fix the step, run `launch plan` again, then apply: the steps already applied are skipped, and they may not be edited, renamed or deleted. After a step that ended without a clear answer, apply goes on only once the ad account has been checked and the step is named with `--resend`. |
| `launch status --file PLAN` | Read back what the plan created and its review state. |
| `launch diagnose --file PLAN [--json]` | Read-only delivery audit of what the plan created: why an approved, switched-on plan shows nothing. It reads only (Meta GET, Google `googleAds:search`, TikTok GET) and sends no write. Per object it checks status and parent state, review feedback and policy topics, issues, schedule, budget, and the account (state, payment, spend cap, balance); on Meta also the audience estimate and `ads_volume`; then the impressions since the last activation in the ledger. Every finding is `{level, object, check, state, detail, next}` with `state` ok, warn or fail; the table ends with one verdict line, `--json` prints the list. The alarm: everything approved, on and inside its schedule, and 0 impressions 6 hours or more after activation is a `fail` with the platform's suspects and next steps; sooner it is a `warn` "too early". A plan paused on purpose (`launch rollback` after the last activation) is judged on the stretch it was on: its paused objects are `ok`, and the hours it was switched on inside the schedule window count; 6 or more with 0 impressions is the same `fail`. A read that fails is a `warn` with the error text. Exit code 0 even with findings. |
| `launch activate --file PLAN [--yes]` | Without `--yes`: print what would be enabled and the budget of the plan; nothing changes. With `--yes`: enable what the plan created, parents first: the campaigns on Google, with what a later step of the plan created paused under them; campaign, ad sets and ads on Meta; campaign, ad groups and ads on TikTok. This starts spend. Refused while a step of the plan is not applied, and when the budget of the plan no longer passes the ceiling or the currency check. |
| `launch rollback --file PLAN [--remove] --yes` | Pause what the plan created, children first. `--remove` deletes it instead (Google: campaigns become `REMOVED`; Meta: ads, ad sets and campaign are deleted; TikTok: status `DELETE`) and clears the plan from the ledger, so a new launch starts with `launch plan`. Both go on past an object that fails, end with exit code 1 and name what is left: run the command again to finish. A removal does not clear a step that ended without a clear answer: that object is not in the ledger. A Meta removal also deletes the plan's creatives and the images it uploaded, after everything that uses them is gone; an image the library held before the upload (Meta keeps one image per hash) or whose age cannot be read stays, and the output names it. Meta brings a deleted image back, with its first `created_time`, when the same file is uploaded again, so such an image stays too. Videos, TikTok uploads and Google assets stay in the account library (a Google budget that is not shared is removed with its campaign); a Meta video is taken out with `meta delete "{account}/advideos" -p video_id=ID`. |
| `ledger [--plan NAME] [--json]` | Show the ledger: dry runs, sends, results and removals. |

## Plan file format

A plan is one JSON file per campaign in `ads/launch/`. Review it, dry-run it, then apply it.

```jsonc
{
  "name": "search-brand-de",                 // plain name (letters, digits, _ and -): file name and ledger key
  "platform": "google",                      // google | meta | tiktok
  "objective": "Brand search campaign, Germany",
  "budget": {"daily": 20, "currency": "EUR"},
  "landing_url": "https://example.com/",
  "steps": [
    {"id": "create", "do": "google.mutate", "with": {"mutateOperations": []}}
  ]
}
```

| `do` | `with` | Values later steps can use |
|---|---|---|
| `google.mutate` | a `googleAds:mutate` body (`mutateOperations`) | `{{ID.results.N}}`: resource name of the N-th operation, counted from 0 |
| `meta.post` | `path`, `params` | `{{ID.id}}` |
| `meta.upload_image` | `file` | `{{ID.hash}}` |
| `meta.upload_video` | `file`, optional `name` | `{{ID.id}}` |
| `tiktok.post` | `path`, `body` | every field of the response `data`, for example `{{ID.campaign_id}}` |
| `tiktok.upload_video` | `file` or `url`, optional `name` | `{{ID.video_id}}` |
| `tiktok.upload_image` | `file` | `{{ID.image_id}}` |

Inside `with`, the object `{"@base64": "ads/creatives/logo.png"}` is replaced by the file content in base64, which is how a Google image asset carries its data.

`budget` states what the campaign may spend, in whole units of the platform's currency (below): `daily`, or `total` for a lifetime budget. It is not a comment: the dry run adds up the budgets the steps really carry and blocks the plan when the sum differs from the declared number or exceeds the ceiling. Every campaign counts. A budget on a campaign stands for the ad sets or ad groups the plan puts under it; under a campaign without a budget of its own, or under one the plan does not create, theirs add up. Every campaign the plan creates must be limited this way: a TikTok campaign without a budget needs one on each of its ad groups, a Google campaign uses a budget created in the same step. `currency` must be `project.currency` of `ads/config.json`, and so must the currency of the ad account: the dry run compares the three.

A plan only creates campaigns and what hangs under them. Refused in a plan: a Google `update` or `remove` operation, and any operation that is no part of a campaign (a conversion action, a bidding strategy, an account-level exclusion); a Meta write to anything but `campaigns`, `adsets`, `adcreatives`, `ads`, `adimages` and `advideos` of the ad account; a TikTok route other than the campaign, ad group, ad and CTA-portfolio creates; and on every platform an ad group, ad set, ad, keyword, criterion or asset link that would join a campaign the plan did not create. Such changes are single commands, each shown to the user first. A step is all or nothing, so `partialFailure` is not accepted either. Once a step is applied its content is fixed: to change what it created, remove what the plan created and start again, or change the object with a single command.

Account ids never go into a plan. Write `{customer}` in Google resource names (`customers/{customer}/campaigns/-2`), `{account}`, `{page}`, `{pixel}` and `{instagram}` in Meta paths and parameters, `{advertiser}` and `{pixel}` in TikTok bodies; the toolkit fills them from `ads/.env`.

`launch plan` validates each step as far as it can. Google validates the whole mutate. Meta validates a step whose references are already known, so on a first run the campaign; the ad set, creative and ad are checked against the toolkit's own rules and by Meta during apply. TikTok has no validation mode, so its steps are checked against the toolkit's rules only.

## Guard rails

- **Dry run on record.** `launch apply` runs only on what a clean `launch plan` has looked at: the plan, the files it sends, the account ids and the currency. Changing any of them, or removing what the plan created, invalidates the dry run.
- **Requests are read as written.** What a request does is taken from its parameters. A Meta or TikTok path with a query string, a Meta `batch`, an object nested inside another call and a Meta parameter named `method` are refused, because the rules below could not see what they do. A Google body is rewritten to camelCase field names before it is judged and sent, and a status is accepted only as its name. A write names no account but the one in `ads/.env`.
- **Paused first.** A Google campaign must be created with `"status": "PAUSED"`; its ad groups, asset groups and ads may be created enabled in the same request, because they serve only once the campaign is enabled. In a later step of the plan, or in a single command under a campaign that already exists, they must be `PAUSED` as well. A Meta campaign, ad set and ad needs `status=PAUSED`, a Meta copy `status_option=PAUSED`. A TikTok campaign and ad group needs `"operation_status": "DISABLE"`, a manual TikTok ad on every entry of `creatives`. Anything else is refused. One call cannot be paused, a TikTok GMV Max campaign: it is refused in a plan and needs `--activate` outside one.
- **Currency per platform.** Budgets and ceilings are read in `project.currency`, or in `project.currencies.<platform>` when the ad accounts bill in different currencies: `"currencies": {"meta": "USD"}` with `"currency": "EUR"` reads Meta in dollars and Google and TikTok in euros. The dry run refuses a plan or an ad account whose currency differs from the one that applies.
- **Budget ceiling.** A daily budget above `guardrails.max_daily_budget` in `ads/config.json` is refused, for a single object and for the sum of a plan. The ceiling is one number, or one number per platform (`{"google": 50, "meta": 60}`), read in that platform's currency; a map without the plan's platform refuses every budget there. `guardrails.max_total_budget` takes the same two forms. The user raises the number in the file on purpose; the tool does not take it as a flag. A ceiling that is missing or zero refuses every budget: it is not read as "no limit". A budget is a plain number that is not negative; anything else is refused.
- **A plan only creates.** `launch plan` promises that nothing existing is modified, so a step that would change or remove something is refused. So is a new campaign that no budget in the plan limits, and anything that would join a campaign from elsewhere and spend from its budget.
- **Lifetime budgets are off.** A lifetime or total budget (Meta `lifetime_budget`, TikTok `BUDGET_MODE_TOTAL`, Google `totalAmountMicros`) is refused until the user sets `guardrails.max_total_budget`, and then up to that amount.
- **Two flags for spend.** `--yes` allows a write; enabling anything also needs `--activate` or `launch activate`. A single command can be shown without either flag: the preview says when sending it would need `--activate`. An automated rule (Meta `adrules_library`, TikTok `optimizer/rule`) can switch ads on later by itself, so creating one needs `--activate` as well.
- **An unknown outcome is not repeated.** A step is marked in the ledger before it is sent. If no clear answer comes back (a timeout, a server error, an interrupted run), the object may exist in the account, so `launch apply` stops and goes on only with `--resend STEP`, after someone has looked.
- **Ledger.** Every applied step is appended to `ads/launch/ledger.jsonl` with the ids the platform returned and a hash of the step, so `launch rollback` knows what to undo and an applied step cannot be edited unnoticed. The ledger holds no key and no account id.
- **Campaigns change in one place.** `google call` sends reads and conversion uploads only, so nothing reaches a Google campaign around `google mutate`.
- **Research spend.** `apify run` stops at `guardrails.max_research_usd_per_call`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | done |
| 1 | the service returned an error; the message carries its code and text |
| 2 | wrong usage, or a guard rail refused the call |
| 3 | a required key is missing |
