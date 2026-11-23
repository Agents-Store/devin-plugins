# Ads workspace

This folder was created by the stack-ads plugin. It holds everything about advertising this project.

| Path | What it holds |
|---|---|
| `config.json` | project facts, budget ceilings (`guardrails`), API versions, chosen generation models |
| `.env` | keys of the services (ignored by git) |
| `brief.md`, `brand.json`, `brand/` | product, audience, offer, brand kit, the real logo and product images |
| `research/` | competitors, keywords, audiences; `raw/` keeps untouched API output and stays out of git |
| `plan/` | media plan, copy packs in `copy/`, the creative list |
| `creatives/` | generated images, video, audio; `manifest.jsonl` lists how each file was made |
| `launch/` | launch plans, dry-run output, `ledger.jsonl` with every object created in an ad account |
| `reports/` | performance reports; `raw/` keeps the pulls and stays out of git |
| `tools/` | the toolkit, copied from the plugin (ignored by git); guides for obtaining keys are in `tools/guides/` |

Check the setup:

```bash
python3 ads/tools/ads.py doctor --live
```

Four rules protect the budget. `launch apply` runs only on a plan whose dry run was clean, and only while the plan, the files it sends, the account ids and the currency are what that dry run looked at. Every campaign is created paused and is enabled only by `launch activate`. A daily budget above `guardrails.max_daily_budget` in `config.json` (one number, or one per platform in that platform's currency) is refused, for one object and for the sum of a plan; a lifetime budget is refused until `guardrails.max_total_budget` is set. You raise these numbers on purpose; the tool never does. A write that ended without a clear answer is not sent again until someone has looked in the ad account.
