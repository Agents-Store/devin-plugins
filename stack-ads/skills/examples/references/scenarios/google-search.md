# Scenario: first Google Search campaign for a SaaS

The project is "Acme Invoices", invoicing for freelancers in Germany and Austria. The user says: "Get us the first paying trials from Google. 1,000 EUR for the first month." Firecrawl, Gemini, Google Ads and Search Console are configured.

## 1. Brief (`product-brief`)

Read the repository, then the live site:

```bash
python3 ads/tools/ads.py firecrawl map https://example.com --limit 100
python3 ads/tools/ads.py firecrawl scrape https://example.com/de --formats markdown,branding --out ads/research/raw/site-home.json
python3 ads/tools/ads.py firecrawl scrape https://example.com/de/preise --formats markdown --out ads/research/raw/site-pricing.json
python3 ads/tools/ads.py google search --query "SELECT conversion_action.name, conversion_action.category, conversion_action.status FROM conversion_action WHERE conversion_action.status = 'ENABLED'"
```

Ask what the sources cannot answer: the target cost per trial (15 EUR), the conversion event (trial sign-up, already a conversion action), regulated category (none). Write `ads/brief.md` and `ads/brand.json`; the user confirms.

## 2. Keywords (`market-research`)

Free sources first. Research cost so far: 3 Firecrawl credits.

```bash
python3 ads/tools/ads.py gsc query --start 2026-08-10 --end 2026-11-08 --dimensions query --row-limit 500 --format csv --out ads/research/raw/gsc-queries.csv
python3 ads/tools/ads.py google geo --query "Germany,Austria" --locale en
python3 ads/tools/ads.py google keyword-ideas --keywords "rechnungssoftware,rechnung schreiben programm" --geo 2276,2040 --language 1001 --limit 300 --format csv --out ads/research/raw/kp-ideas.csv
```

Sort the result into clusters (brand, solution, problem, irrelevant) and write `ads/research/keywords.md` with volumes, bid ranges, match types, landing pages and the negative list. Finding: "rechnungssoftware" terms cost about 1.80 EUR a click; "rechnung vorlage" terms are cheap, numerous and want a free template, so they become negatives.

## 3. Plan (`media-plan`)

Arithmetic: 1,000 EUR a month is about 33 EUR a day. At 1.80 EUR a click and an assumed 12 percent click-to-trial rate, a trial costs 15 EUR and the budget buys about 15 trials a week. That is below what conversion bidding needs at the start, so the plan bids on clicks with a ceiling and switches after 30 conversions. One solution campaign at 28 EUR a day, one brand campaign at 5 EUR. EU delivery: the political advertising declaration is "no".

The user approves the budget table. Status in `ads/plan/media-plan.md`: approved.

## 4. Copy (`ad-copy`)

For each ad group: 15 headlines of at most 30 characters, 4 descriptions of at most 90, three of the headlines with the keyword, sitelinks and callouts. Save `ads/plan/copy/google.json`, run the length check of the skill, show the table with counts. The user removes one claim that is not approved yet.

## 5. Launch file (`launch-campaign`)

Account checks first, then build `ads/launch/de_search_solution_202612.json` from the complete Search plan in the Google launch reference (section 2): budget, campaign with `"status": "PAUSED"` and the EU declaration, geo criteria, the campaign-level negatives from `ads/research/keywords.md`, ad groups, keywords, responsive search ads. Resource names carry `{customer}`, never the account id.

```bash
python3 ads/tools/ads.py doctor --live --only google
python3 ads/tools/ads.py launch plan --file ads/launch/de_search_solution_202612.json
```

Google validates the whole request (`validateOnly`). The first run fails:

```text
VALIDATE
  FAIL create: mutate_operations[7].ad_group_ad_operation.create.ad.responsive_search_ad.headlines[4].text: Too long. (stringLengthError=TOO_LONG)
```

Shorten that headline in the copy pack and the plan, and run the dry run again; a changed plan always gets a new one. Now all lines read `ok`. Show the eight blocks and summarise: one campaign, two ad groups, 34 keywords, 28 EUR a day, at most about 851 EUR a month, Germany and Austria, starts 1 December. "Apply this plan? Everything is created paused."

## 6. Apply and verify

After the user's yes:

```bash
python3 ads/tools/ads.py launch apply --file ads/launch/de_search_solution_202612.json --yes
python3 ads/tools/ads.py launch status --file ads/launch/de_search_solution_202612.json
```

The campaign exists with status `PAUSED`. The user opens it in Google Ads and looks at the ads and keywords.

## 7. Activate

First show what would be switched on. Without `--yes` nothing changes: Google validates the status change, and the toolkit prints the campaign and the budget of the plan.

```bash
python3 ads/tools/ads.py launch activate --file ads/launch/de_search_solution_202612.json
```

"Activate de_search_solution_202612? Up to 28 EUR a day, about 851 EUR a month, from 1 December." After a clear yes:

```bash
python3 ads/tools/ads.py launch activate --file ads/launch/de_search_solution_202612.json --yes
```

Next day, check that the ads passed review and that impressions arrive. First report after seven days (`performance-report`).

## What this scenario shows

- Research cost three Firecrawl credits; the paid keyword service was not needed.
- The dry run caught a text one character too long before anything existed.
- The user approved three times: the budget, the apply, the activation.
