# Scenario: Meta and TikTok with generated images and video

The project sells a reusable water bottle online, market Germany. Brief, research and an approved media plan exist: a Meta sales campaign at 30 EUR a day and a TikTok test at 50 EUR a day. For the TikTok test the user raised `guardrails.max_daily_budget` in `ads/config.json` to 50 on purpose. The user says: "Make the creatives and get both campaigns ready." Gemini, fal.ai and Meta are configured; TikTok has a developer app and a token.

## 1. Shot list and cost (`ad-creatives`)

Three angles from the copy pack (keeps cold 24 hours, fits a bike holder, one bottle instead of 300 plastic ones). Per angle: one 4:5 image and one 9:16 image for Meta. For TikTok: two 9:16 videos of 8 seconds in total, for the two strongest angles. Estimate: 12 draft images and 6 finals at a few cents each, 2 clips at about one dollar each, about 3 USD together. The user agrees to that figure, including the two clips.

```bash
python3 ads/tools/ads.py doctor --live --only gemini,fal,meta,tiktok
python3 ads/tools/ads.py models --pick
```

## 2. Images from the real product

The product photo goes in as a reference, so the bottle is the real bottle:

```bash
python3 ads/tools/ads.py image --prompt "This bottle on a bike holder on a gravel road at golden hour, bottle in the middle third, sky above and road below left empty, no text, no logos added" --ref ads/brand/bottle.png --aspect 9:16 --n 2 --name bike-9x16
python3 ads/tools/ads.py image --prompt "This bottle on a kitchen counter next to ice cubes, morning light, clean background, no text" --ref ads/brand/bottle.png --aspect 4:5 --fit 1080x1350 --n 2 --name cold-4x5
python3 ads/tools/ads.py analyze --prompt "List every word visible in the image exactly as written. Is the bottle's shape and logo the same as a plain steel bottle with a round cap? Any distorted objects?" --file ads/creatives/bike-9x16.png
```

One draft shows a second, invented logo on the cap: rejected, regenerated with "the cap is plain steel, no marking". The finals are checked against the safe zones and the list in `ads/plan/creatives.md`.

## 3. Video

A clip from an approved still keeps the product consistent:

```bash
python3 ads/tools/ads.py video --prompt "Single continuous shot. The bike starts rolling, the bottle stays sharp in its holder, dust in warm light, natural sound of gravel, no on-screen text, no dialogue" --image ads/creatives/bike-9x16.png --aspect 9:16 --seconds 8 --name bike-reel
python3 ads/tools/ads.py speech --text "Vierundzwanzig Stunden kalt. Auch auf Schotter." --out ads/creatives/vo-bike-de.wav
```

Watch each clip before it is used: generated video invents details. Mark all files as AI-generated in the list; TikTok needs that disclosure set on the ad.

## 4. Meta launch file (`launch-campaign`)

Account checks from the Meta reference (account status, payment method, Page, pixel with a recent purchase event). The plan `ads/launch/de_meta_sales_202612.json` follows the reference: image uploads, campaign `OUTCOME_SALES` with `"status": "PAUSED"`, an ad set with Advantage+ audience, the pixel as `{pixel}`, the legal names for EU delivery, one creative and one ad per image.

```bash
python3 ads/tools/ads.py meta get "{account}" -p fields=account_status,currency,funding_source
python3 ads/tools/ads.py meta get "{account}/adspixels" -p fields=id,name,last_fired_time
python3 ads/tools/ads.py launch plan --file ads/launch/de_meta_sales_202612.json
```

The dry run validates the campaign with Meta and marks the dependent steps `wait`. The user reads the eight blocks and approves.

```bash
python3 ads/tools/ads.py launch apply --file ads/launch/de_meta_sales_202612.json --yes
python3 ads/tools/ads.py launch status --file ads/launch/de_meta_sales_202612.json
```

Apply stops at the ad set with Meta error 100: the daily budget is below the account's minimum for the chosen optimisation. Nothing was duplicated: campaign and uploads are in the ledger.

A budget change is a change to what the user approved, so stop and say so: "Meta's minimum for this goal is 35 EUR a day; the plan says 30." The user decides to go to 35 and the media plan is updated. Then edit the plan file, run `launch plan` again, show it in full and ask "Apply this changed plan?". The toolkit would refuse the apply otherwise: the file changed after its last dry run. After the yes, `launch apply` skips the finished steps and creates the rest.

## 5. TikTok launch file

Sales campaigns on TikTok use the Smart+ flow. Look up what the plan needs, then build `ads/launch/de_tiktok_sales_202612.json` from the Smart+ skeleton of the TikTok reference: video and cover uploads, campaign, ad group with `{pixel}`, ad, all with `"operation_status": "DISABLE"`.

```bash
python3 ads/tools/ads.py tiktok get identity/get/ -p identity_type=TT_USER
python3 ads/tools/ads.py tiktok get pixel/list/
python3 ads/tools/ads.py tiktok get search/region/
python3 ads/tools/ads.py launch plan --file ads/launch/de_tiktok_sales_202612.json
```

Tell the user plainly what this dry run is worth: TikTok has no validation mode, so the toolkit checked its own rules only, and `apply` into disabled objects is the real test. After approval:

```bash
python3 ads/tools/ads.py launch apply --file ads/launch/de_tiktok_sales_202612.json --yes
```

## 6. Activation, one platform at a time

The user looks at both paused campaigns in the platforms' interfaces. Each activation gets its own preview, its own question and its own yes. Without `--yes` the command only lists what it would enable and the budget of the plan:

```bash
python3 ads/tools/ads.py launch activate --file ads/launch/de_meta_sales_202612.json
```

"Activate de_meta_sales_202612? Up to 35 EUR a day, about 1,064 EUR a month."

```bash
python3 ads/tools/ads.py launch activate --file ads/launch/de_meta_sales_202612.json --yes
```

The same for TikTok, after its own preview: "Activate de_tiktok_sales_202612? Up to 50 EUR a day, about 1,520 EUR a month."

```bash
python3 ads/tools/ads.py launch activate --file ads/launch/de_tiktok_sales_202612.json
python3 ads/tools/ads.py launch activate --file ads/launch/de_tiktok_sales_202612.json --yes
```

Review states are checked an hour later and the next day. A rejected TikTok ad names its reason; fix the creative and create a new ad rather than resubmitting the same file.

## Without a TikTok developer app

The `tiktok-ads` MCP server signs in through OAuth and can create the same campaign, but it has no dry run, no ledger and no budget ceiling. Then the money rules are applied by hand: show the full request before each write and wait for the user's yes to that one call, create everything disabled, add up the daily budgets and keep them under the ceiling, note every returned id in `ads/launch/`, and enable only after a second approval.

## What this scenario shows

- The real product photo as reference, and a model check of every image, caught an invented logo.
- The ledger made a failed apply safe to repeat.
- A dry run is only as strong as the platform's validation; say so instead of implying more.
