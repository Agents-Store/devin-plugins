---
name: media-plan
description: This skill should be used when the user asks to "build a media plan", "plan the ad campaign", "which platform should we advertise on", "how should we split the ad budget", "is this budget enough". Writes the plan only: for creating ads use launch-campaign, for results performance-report.
---

# Media plan

Decide where the money goes before anything is created: platforms, objectives, budget per campaign, structure, what is measured, and whether the product is allowed to run as planned. The output is `ads/plan/media-plan.md`: one page the user approves and the `launch-campaign` skill executes line by line.

A plan is finished when a person who has not seen the conversation could launch from it, and when the budget of every campaign can reach the number of results its platform needs to learn.

Inputs: `ads/brief.md`, the files in `ads/research/`, `ads/config.json` (markets, currency, budget ceiling). Without a brief run the `product-brief` skill; without research write the plan from the brief and mark targeting and costs as assumptions.

Numbers for floors, learning thresholds, pairings and regional rules: [budgets-tracking-compliance.md](references/budgets-tracking-compliance.md). Read the section before quoting a number; they change, and several differ by currency.

## Step 1: Check what is possible today

Three facts limit the plan more than any strategy, so collect them first:

```bash
python3 ads/tools/ads.py doctor --live --only google,gsc,meta,tiktok
```

- **Accounts**: a platform without working access cannot be launched from here. Plan it only if the user will finish its setup (`init-project`), and say so in the plan.
- **Tracking**: take the conversion state from the brief. A conversion campaign needs an event that fires; without one, plan a traffic objective first and list the tracking fix as a prerequisite.
- **Creative**: TikTok needs vertical video; Search needs none. A plan that requires assets nobody can produce is not a plan.

## Step 2: Choose platforms

Start from where the demand is, not from a wish to be everywhere.

| Situation in the brief and research | Start with | Reason |
|---|---|---|
| People already search for the solution, and keywords have volume | Google Search | captures existing intent; the fastest signal on whether the offer converts |
| Visual or impulse product, broad consumer audience | Meta | creates demand; the algorithm finds buyers from broad targeting and good creative |
| Audience under 35, product that shows well in short video | TikTok | cheap reach if native-looking video exists |
| Many products with a feed, or an established account with conversion history | Google Performance Max, Meta sales campaigns | automation needs history and a feed to work with |
| Niche B2B audience | Google Search first, Meta retargeting second | intent is rare, so buy it where it is expressed |
| Local service | Google Search with a tight radius | local intent is in search |

Then cut to what the budget can feed. One campaign that learns beats three that never leave the learning phase. As a rule: first test on one platform, at most two; add the next when the first has a stable cost per result.

## Step 3: Do the budget arithmetic

For each planned campaign compute the smallest daily budget that makes sense, with the formulas of the reference (per ad set on Meta, per ad group or Smart+ campaign on TikTok, per campaign on Google Demand Gen). In short: the budget must buy the platform's learning volume. That is about 50 optimisation events per week per ad set on Meta and per ad group on TikTok. On Google it depends on the bidding: 30 conversions in 30 days for target CPA, about 50 in a month for Demand Gen, at least six weeks of running for Performance Max. Google Search has no formula: plan it from the keyword CPCs.

Work through it in this order:

1. Daily budget available = monthly budget / 30.4.
2. Expected cost per result: from the keyword CPCs and an assumed conversion rate, or from past accounts. Label it as an estimate.
3. Results the budget can buy per week = daily budget x 7 / cost per result.
4. If that is below the learning volume: optimise for an earlier, more frequent event (landing page view, add to cart, lead instead of sale), or reduce the number of campaigns and ad sets, or lengthen the test. Do not launch a split that cannot reach the event count: it spends the money and teaches nothing.
5. Check each budget against the platform minimum and against `guardrails.max_daily_budget` in `ads/config.json`. The published minimums are in US dollars and some are doubled in certain countries, Germany and Austria among them on Meta: read the account's real minimum with the commands of the reference. The toolkit refuses a campaign whose daily budgets add up to more than the ceiling. If the plan needs more, ask the user whether to raise the ceiling in the file; never raise it yourself, because the ceiling is the user's limit on their own money. Plan daily budgets: lifetime budgets are switched off in the toolkit until the owner sets `guardrails.max_total_budget`.
6. Reserve part of the budget (10 to 20 percent is a common choice) for a second creative round after the first results.

A platform may spend more than the daily budget on a single day and even out over the week or month. State the monthly maximum in the plan so the number does not surprise anyone.

## Step 4: Fix the structure

Keep it as simple as the product allows; consolidation gives the algorithms more data per unit.

| Platform | Default structure for a first test |
|---|---|
| Google Search | one campaign per market and language; ad groups by keyword cluster from `ads/research/keywords.md` (brand apart from the rest); one responsive search ad per ad group with all headline slots filled; negatives at campaign level |
| Meta | one campaign per objective; one ad set per market with Advantage+ audience; three to five ads that differ in angle, not in button colour |
| TikTok | Smart+ for sales, leads and app installs; the manual flow for traffic, reach and video views; one ad group; three to five videos |

Name everything by one convention so reports can be read later, for example `market_objective_audience_yyyymm`: `de_search_solution_202612`. Write the names into the plan.

For each campaign record: objective, optimisation goal and bidding, targeting source (the row of `ads/research/audiences.md` or the keyword cluster), placements, schedule with start and end date, landing page with UTM parameters, and the assets it needs.

## Step 5: Define tracking

- One primary conversion event per campaign, named as the platform names it, and where it fires.
- UTM parameters for every landing URL: `utm_source` (google, facebook, tiktok), `utm_medium=paid`, `utm_campaign` equal to the campaign name. They make the site's own analytics a second witness beside the platform's numbers.
- What will be compared with what: platform conversions against orders or leads in the product's own system. Platforms count differently, so name the source of truth now.
- Prerequisites the user must complete on the site (pixel, consent mode, conversion action), each with the owner and the check that proves it works. The reference lists them per platform.

## Step 6: Run the compliance gate

Stop and resolve these before a plan is called ready. A rejected or restricted ad wastes days, and some categories carry legal duties.

| Question | Consequence |
|---|---|
| Housing, employment, credit or financial products? | declare the special ad category on Meta and the special industry on TikTok where the account offers it, and accept the targeting limits; which limits apply (age, gender, postcode, lookalikes) depends on the platform and the country: read the compliance table of the reference |
| Politics, elections or social issues? | not allowed for EU delivery on any of the three platforms, and TikTok bans paid political ads everywhere; elsewhere it needs authorisation: stop and ask the user |
| Delivery in the EU? | Meta needs the legal names of the advertiser (the API fields still say beneficiary) and of the payer; Google needs the EU political advertising declaration on every campaign; consent mode applies to tracking |
| Health, alcohol, gambling, dating, crypto, weapons, tobacco? | platform policies restrict or forbid them by country: read the reference and the platform policy before planning |
| Audience under 18? | targeting limits on every platform |
| Claims in the copy ("best", "guaranteed", numbers)? | must be provable on the landing page |

## Step 7: Write `ads/plan/media-plan.md`

<example>
# Media plan: Acme Invoices, December 2026

Status: draft for approval. Budget ceiling per campaign: 50 EUR a day (ads/config.json).

## Decision
Start with Google Search in DE and AT. From 18 December add Meta as a traffic campaign, if the search cost per trial is at or below 15 EUR. TikTok not planned: no pixel, no video yet.

## Budget, December (31 days)
| Campaign | Platform | Daily | Days | Maximum | Share |
|---|---|---|---|---|---|
| de_search_solution_202612 | Google Search | 30 EUR | 31 | 930 EUR | 62% |
| de_search_brand_202612 | Google Search | 5 EUR | 31 | 155 EUR | 10% |
| de_meta_trial_202612 | Meta | 20 EUR | 14 | 280 EUR | 19% |
| Reserve for a second creative round | | | | 135 EUR | 9% |
| Total | | | | 1,500 EUR | |

Arithmetic, search: CPC 1.80 EUR (keywords.md, DataForSEO 2026-11) at an assumed 12% click-to-trial rate gives 15 EUR per trial. 30 EUR a day buys 2 trials a day, 14 a week; the 30 conversions that conversion bidding needs arrive after about 15 days. So: bid on clicks first, switch after 30 trials.

Arithmetic, Meta: at 15 EUR per trial, 20 EUR a day buys about 9 trials a week, far below the 50 a week a conversion campaign needs (that would take about 107 EUR a day). So Meta starts as a traffic campaign optimised for link clicks, and is judged on cost per landing-page visit and on the trials the product database attributes to it.

## Campaigns
### de_search_solution_202612
- Objective and bidding: maximise clicks with a 2.50 EUR bid ceiling, switch to maximise conversions after 30 conversions
- Targeting: Germany and Austria, German; clusters "solution" and "problem" (keywords.md), phrase and exact match; negatives list attached
- Ads: one responsive search ad per ad group, copy pack `ads/plan/copy/google.json`
- Landing: https://example.com/de?utm_source=google&utm_medium=paid&utm_campaign=de_search_solution_202612
- Schedule: 2026-12-01 to 2026-12-31

### de_meta_trial_202612
- Objective and goal: traffic (`OUTCOME_TRAFFIC`), optimised for link clicks; not a conversion campaign at this budget
- Targeting: Germany, Advantage+ audience; three image ads, one per angle
- Landing: https://example.com/de/freelancer?utm_source=facebook&utm_medium=paid&utm_campaign=de_meta_trial_202612
- Schedule: 2026-12-18 to 2026-12-31

## Tracking
- Conversion: `sign_up` (Google Ads conversion action "Trial sign-up", fires, primary)
- Source of truth: trial accounts in the product database, compared weekly
- To do before launch: none for Google; Meta pixel event `CompleteRegistration` must fire on the thank-you page (owner: site developer; check: `last_fired_time` moves)

## Compliance
Not a special category. EU delivery: Google declaration "no political advertising"; Meta advertiser and payer "Acme Software GmbH".

## Risks and assumptions
- The 12% click-to-trial rate is an assumption. Stop rule: after 300 clicks without 15 trials, pause and review the landing page.

## What happens next
1. Copy and creatives (ad-copy, ad-creatives). 2. Launch plan files, dry run, approval. 3. First report after 7 days.
</example>

## Step 8: Get approval

Show the user the decision, the budget table and the open prerequisites, and ask for explicit approval of the budget. The plan is the user's commitment of money: nothing is launched from a draft.

Write the status line `Status: approved YYYY-MM-DD` only after the user has said so in this conversation; with no user present it stays a draft. This approval covers the plan. It is not permission to create or enable anything: `launch-campaign` asks again after its dry run and again before activation.

Then offer the next step: `ad-copy`, `ad-creatives` for campaigns with visuals, and `launch-campaign` when the assets exist.

## Rules

- Never present a forecast as a result: a guess read as a measurement leads to the wrong budget. Every cost and volume in the plan names its source or says "assumption".
- Do not plan a conversion campaign on an event that does not fire: it spends money and gives the platform nothing to learn from. Plan the fix, or a different goal.
- A budget above the ceiling is the user's decision, written into `ads/config.json` on the user's instruction: the ceiling is their limit on their own money, and lifting it to make a plan pass defeats it.
- Compliance questions are answered by the user, not assumed from the product name: the name does not say whether a product falls into a restricted category, and a wrong guess gets the account restricted.
