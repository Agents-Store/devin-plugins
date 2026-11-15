# stack-ads (Devin plugin)

Paid advertising stack for any project. Researches the product and its market, derives targeting, writes ad copy, generates images, video and voice-over, launches paused campaigns on Google Ads, Meta and TikTok from a reviewed dry-run plan with budget ceilings and a rollback ledger, and reports results. Walks the user through obtaining every key. Integrates Google Ads, Search Console, Meta, TikTok, Firecrawl, Apify, DataForSEO, OpenAI, Gemini and fal.ai via MCP and one dependency-free toolkit.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (11)

- `ad-copy` — This skill should be used when the user asks to "write ad copy", "write headlines and descriptions", "shorten these ad texts", "more ad text variants", or needs texts for Google, Meta or TikTok ads. Text only: for images and video use ad-creatives, for creating ads launch-campaign.
- `ad-creatives` — This skill should be used when the user asks to "generate ad creatives", "make ad images", "create a video for the ad", "add a voice-over", "resize for Stories", or needs media files for Google, Meta or TikTok ads. Not for ad text (ad-copy) or uploading (launch-campaign).
- `examples` — Complete walkthroughs of advertising a project with stack-ads, from getting the first key to a weekly review of running campaigns.
- `full-campaign` — This skill should be used when the user asks to "advertise this project", "run ads from scratch", "take this product from zero to running ads", "do the whole campaign end to end", or to continue an unfinished campaign checklist. For one step use that step's skill.
- `init-project` — This skill should be used when the user asks to "set up ads for this project", "connect Google Ads, Meta or TikTok", "where do I get the Meta, Google Ads or Firecrawl key", "set the ads budget ceiling", or when a key for advertising is missing. For the whole path use full-campaign.
- `launch-campaign` — This skill should be used when the user asks to "launch the campaign", "create the campaign in Google Ads, Meta or TikTok", "run the dry run", "activate, pause or roll back the campaign", or edit a live campaign. Not for budgets (media-plan), results (performance-report), full path (full-campaign).
- `market-research` — This skill should be used when the user asks to "research ad competitors", "find keywords for ads", "what are competitors advertising", "estimate CPC and search volume", "find interest ids for Meta or TikTok" before a media plan. Not for SEO audits or the product brief.
- `media-plan` — This skill should be used when the user asks to "build a media plan", "plan the ad campaign", "which platform should we advertise on", "how should we split the ad budget", "is this budget enough". Writes the plan only: for creating ads use launch-campaign, for results performance-report.
- `performance-report` — This skill should be used when the user asks "how are the ads performing", "make an ads report", "compare Google, Meta and TikTok results", "why is the cost per lead so high". Read-only: for API errors use troubleshoot, to change a campaign launch-campaign. Not for SEO reports.
- `product-brief` — This skill should be used when the user asks to "write the ad brief", "describe the product for advertising", "what do we sell and to whom", "extract the brand kit", or when ads/brief.md is missing. For competitors, keywords or platform audiences use market-research.
- `troubleshoot` — This skill should be used when the user reports "the ads command failed", "API error from Google Ads, Meta or TikTok", "my ad was rejected", "the key is rejected", "the MCP server is not connecting". Not for obtaining a key (init-project) or weak results (performance-report).

## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- hooks — Devin plugins do not support hooks
- MCP servers — Devin plugins do not support MCP server declarations

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/stack-ads
