---
name: examples
description: Complete walkthroughs of advertising a project with stack-ads, from getting the first key to a weekly review of running campaigns.
argument-hint: "[first-keys | google-search | meta-tiktok-video | weekly-review]"
disable-model-invocation: true
---

# stack-ads walkthroughs

End-to-end scenarios that show how the skills and the toolkit fit together on a real task. Each one is a sequence of decisions and commands with the points where the user must approve.

Requested scenario: `$ARGUMENTS`. If it is one of `first-keys`, `google-search`, `meta-tiktok-video` or `weekly-review`, read `references/scenarios/` plus that name plus `.md`. If it is empty or matches none of them, show the table and ask which one fits.

## Scenarios

| Scenario | Situation | Skills used |
|---|---|---|
| [First keys](references/scenarios/first-keys.md) | nothing is set up; the user wants to know what to get and where | `init-project` |
| [Google Search for a SaaS](references/scenarios/google-search.md) | a product people already search for; first campaign with a small budget | `product-brief`, `market-research`, `media-plan`, `ad-copy`, `launch-campaign` |
| [Meta and TikTok with generated video](references/scenarios/meta-tiktok-video.md) | a visual consumer product; images and a short video are generated | `ad-creatives`, `launch-campaign` |
| [Weekly review](references/scenarios/weekly-review.md) | campaigns have run for a week; decide what to stop, fix and shift | `performance-report`, `launch-campaign` |

Walk through the chosen scenario as an explanation. The files use an invented product and example values, so nothing in them is run as written. Run a command on the user's own project only when the user asks to apply the scenario to it, and then every dry run, apply and activation stops for a fresh, specific approval under the money rules of `launch-campaign`: running this skill is not approval.

## The pattern behind every scenario

1. **Know the product** before spending: `ads/brief.md` first.
2. **Spend on research on purpose**: state the price before a paid call.
3. **Decide on paper**: the media plan carries the budget and is approved by the user.
4. **Prepare, then show**: copy and creatives are checked by program and by eye before the user sees them.
5. **Create paused**: `launch plan`, approval, `launch apply --yes`.
6. **Spend on a second approval**: `launch activate` shows what would be switched on, `launch activate --yes` does it.
7. **Measure against the target**, with the data volume beside every verdict.

## Values used in the examples

The scenarios use an invented product, "Acme Invoices" at `example.com`, the markets DE and AT, and EUR. Account ids never appear: the toolkit fills `{customer}`, `{account}`, `{page}`, `{pixel}` and `{advertiser}` from `ads/.env`.
