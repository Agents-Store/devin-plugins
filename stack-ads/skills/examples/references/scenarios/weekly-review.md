# Scenario: weekly review of running campaigns

Two campaigns have run for seven days: Google Search and Meta. The media plan sets a target of 15 EUR per trial and a stop rule: "after 300 clicks without 15 trials, pause and review the landing page". The user asks: "How are the ads doing? What should we change?"

## 1. Scope

Period 1 to 7 December. The campaigns started on 1 December, so this first report has no earlier week to compare with: the baseline is the plan's targets, 15 EUR per trial and the stop rule. From the second report on, the comparison is the week before. Targets from `ads/plan/media-plan.md`. Ask for the user's own count: "How many trials with a paid UTM does your database show for 1 to 7 December?" Answer: 31.

```bash
python3 ads/tools/ads.py ledger
python3 ads/tools/ads.py doctor --only google,meta
```

## 2. Pull (`performance-report`)

```bash
Q='SELECT campaign.name, campaign.status, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM campaign WHERE segments.date BETWEEN "2026-12-01" AND "2026-12-07" AND campaign.status != "REMOVED"'
python3 ads/tools/ads.py google search --query "$Q" --out ads/reports/raw/google-campaigns.json
T='SELECT search_term_view.search_term, campaign.name, metrics.clicks, metrics.cost_micros, metrics.conversions FROM search_term_view WHERE segments.date BETWEEN "2026-12-01" AND "2026-12-07" AND metrics.cost_micros > 0 AND metrics.conversions = 0 ORDER BY metrics.cost_micros DESC LIMIT 100'
python3 ads/tools/ads.py google search --query "$T" --format csv --out ads/reports/raw/google-terms.csv
python3 ads/tools/ads.py meta insights --level campaign --since 2026-12-01 --until 2026-12-07 --fields campaign_name,spend,impressions,clicks,frequency,actions -p 'action_attribution_windows=["7d_click","1d_view"]' --out ads/reports/raw/meta-campaigns.json
```

From the second report on, the same pulls are repeated for the comparison week.

## 3. Read the numbers

- Google: 242.50 EUR, 389 clicks, 30 conversions: 8.08 EUR per trial, under the target. Thirty conversions is indicative, not proof.
- Meta: 99.50 EUR, 164 clicks, 4 conversions: 24.88 EUR per trial. Four conversions in the first week of learning supports no verdict.
- Platforms report 34 trials, the database 31: tracking is plausible, and the two platforms are not summed as "34 customers".
- Search terms: 41 EUR went to queries with "muster", "vorlage word" and "kostenlos download" (people wanting a free template), no trial among them. The launch list of negatives had "rechnung vorlage" but missed these variants.
- The stop rule does not fire: more than 15 trials within 300 clicks.

## 4. Report and recommendations

Write `ads/reports/2026-12-08.md` in the format of the skill. Recommendations, none applied yet:

| Action | Evidence | Risk |
|---|---|---|
| Add three negative keywords to the solution campaign | 41 EUR a week without a trial | may block a few relevant searches |
| Leave Meta untouched until 21 December | 4 conversions; an edit restarts learning | 100 EUR a week on an unproven channel |
| Switch the search campaign to conversion bidding | it reached the 30 conversions the plan set for the switch | a bidding change restarts learning for a few days |
| No budget change this week | one change at a time, so next week's numbers can be read | slower growth |

The user chooses the first action now and the bidding switch for next week.

## 5. Carry out the change (`launch-campaign`)

A change to a running campaign is a write, so it gets its own dry run. Read the campaign's resource name from the ledger and write the body to `ads/launch/negatives-20261208.json`; `{customer}` is filled by the toolkit:

```json
{
  "mutateOperations": [
    {"campaignCriterionOperation": {"create": {
      "campaign": "customers/{customer}/campaigns/<CAMPAIGN_ID>",
      "negative": true,
      "keyword": {"text": "vorlage", "matchType": "PHRASE"}}}},
    {"campaignCriterionOperation": {"create": {
      "campaign": "customers/{customer}/campaigns/<CAMPAIGN_ID>",
      "negative": true,
      "keyword": {"text": "muster", "matchType": "PHRASE"}}}},
    {"campaignCriterionOperation": {"create": {
      "campaign": "customers/{customer}/campaigns/<CAMPAIGN_ID>",
      "negative": true,
      "keyword": {"text": "kostenlos download", "matchType": "PHRASE"}}}}
  ]
}
```

```bash
python3 ads/tools/ads.py google mutate --file ads/launch/negatives-20261208.json
```

Without `--yes` Google only validates. Show the user the result and the three keywords, and after their yes:

```bash
python3 ads/tools/ads.py google mutate --file ads/launch/negatives-20261208.json --yes
```

Note the change with its date in the report, so next week's numbers can be read against it.

## 6. Next date

"Next report on 15 December. Meta gets its verdict on 21 December. The switch of the search campaign to conversion bidding comes next week as its own change: a dry run, shown, and a new approval."

## What this scenario shows

- Every verdict carries its data volume; four conversions are called what they are.
- The user's own count is the yardstick, not the sum of the platforms' claims.
- Even a small edit to a live campaign goes through validation and approval.
