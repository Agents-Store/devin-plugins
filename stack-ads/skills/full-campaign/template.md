# Campaign checklist

Project: (name)
Started: (date)
Path: (quick test | standard | broad, chosen after the brief)

Tick a work item when its result exists. Tick a gate only after the user answered it in this session, and write the answer with its date into the decision log.

A ticked gate is history, not approval. It records what was decided for the plan as it was then. The dry-run, apply and activation gates of stage 6 are asked again every time, and after any edit to a plan file they are unticked.

## 0. Setup (`init-project`)

- [ ] `ads/` workspace created, `ads/.env` ignored by git
- [ ] Platforms chosen: Google Ads / Meta / TikTok
- [ ] Keys verified with `doctor --live` (list the working services)
- [ ] `project` block of `ads/config.json` filled: name, url, markets, languages, currency of the ad accounts
- [ ] Budget ceiling set by the user in `ads/config.json` (`guardrails.max_daily_budget`)
- [ ] MCP servers connected (optional)
- [ ] Generation models picked (`models --pick`), when creatives are planned

## 1. Brief (`product-brief`)

- [ ] `ads/brief.md` written, every fact with a source
- [ ] `ads/brand.json` written, logo file saved
- [ ] Conversion event named and its tracking state known
- [ ] **Gate:** the user confirmed the brief
- [ ] Path chosen and logged

## 2. Research (`market-research`)

- [ ] **Gate:** research budget agreed
- [ ] `ads/research/competitors.md`
- [ ] `ads/research/keywords.md` (when search is planned)
- [ ] `ads/research/audiences.md`
- [ ] Research spend noted

## 3. Plan (`media-plan`)

- [ ] Platforms and objectives chosen
- [ ] Budget arithmetic done; each campaign can reach its learning volume
- [ ] Tracking prerequisites listed with owners
- [ ] Compliance gate answered by the user
- [ ] `ads/plan/media-plan.md` written
- [ ] **Gate:** the user approved the budget and the plan
- [ ] Status line of `media-plan.md` set to approved, with the date

## 4. Copy (`ad-copy`)

- [ ] **Gate:** the user agreed the angles
- [ ] Copy packs in `ads/plan/copy/`, lengths checked by program
- [ ] **Gate:** the user approved texts and claims

## 5. Creatives (`ad-creatives`), or "not needed" for a campaign without visuals

- [ ] Shot list with cost estimate
- [ ] **Gate:** the user approved the generation cost
- [ ] Files generated and checked (size, safe zones, text, brand, rights)
- [ ] `ads/plan/creatives.md` written
- [ ] **Gate:** the user approved the final assets; each file is marked approved in `creatives.md`

## 6. Launch (`launch-campaign`), once per campaign

Campaign: (name), platform: (platform), plan file: `ads/launch/(name).json`

- [ ] Account checks passed
- [ ] Plan file built from the platform reference
- [ ] Dry run clean and shown to the user in full
- [ ] **Gate:** the user approved applying this plan (asked in the session that applies it)
- [ ] Applied; everything paused; ids in the ledger
- [ ] Read back and compared with the plan; the user looked at it in the platform
- [ ] **Gate:** the user approved activation and the daily budget (asked in the session that activates)
- [ ] Activated; review state checked

## 7. Report (`performance-report`)

- [ ] Delivery check on day 2 or 3
- [ ] First report after 7 days
- [ ] **Gate:** the user chose the actions
- [ ] Next report date set

## Decision log

| Date | Decision | By |
|---|---|---|
| | | |

## Open items

| Item | Owner | Needed for |
|---|---|---|
| | | |
