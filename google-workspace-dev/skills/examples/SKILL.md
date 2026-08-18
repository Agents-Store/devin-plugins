---
name: examples
description: "Use when the user wants a worked end-to-end example of combining Google Workspace services with the gws CLI — e.g. \"show me an example\", \"how do I turn emails into tasks\", \"build a report from a sheet and email it\", \"prep for my next meeting\", \"create events from a spreadsheet\". Walks through multi-step scenarios that chain several gws-*/recipe-* skills."
---

# Google Workspace — Worked Scenarios

Each scenario chains several plugin skills into one outcome. They assume `gws` is installed and authenticated — if any command fails with a missing-binary or auth error, run **`google-workspace-setup`** first, and read **`gws-shared`** for global flags and security rules.

**Golden rules when running these (from `gws-shared`):**
- Confirm with the user before any write/delete; prefer `--dry-run` first.
- Wrap `--params`/`--json` values in single quotes; use **double** quotes for Sheets ranges containing `!` (e.g. `"Sheet1!A1:D10"`) so the shell doesn't expand history.
- Every response is JSON — pipe through `jq` to extract IDs for the next step.

## Scenario index

| # | Goal | Skills chained |
|---|------|----------------|
| 1 | Inbox triage → tasks | `gws-gmail` (`+triage`), `gws-workflow` (`+email-to-task`) |
| 2 | Sheet → report doc → email the link | `gws-sheets` (`+read`), `gws-docs` (`+write`), `gws-drive`, `gws-gmail` (`+send`) |
| 3 | Spreadsheet rows → calendar events | `recipe-create-events-from-sheet`, `gws-sheets`, `gws-calendar` (`+insert`) |
| 4 | Meeting prep brief | `gws-workflow` (`+meeting-prep`) |
| 5 | New deck + share with the team | `gws-slides`, `gws-drive` (permissions) |
| 6 | Monday standup / weekly digest | `gws-workflow` (`+standup-report`, `+weekly-digest`) |

Full step-by-step commands for each are in [`references/scenarios.md`](references/scenarios.md).

## Quick taste

```bash
# 1. Summarize unread mail, then convert one message into a task
gws gmail +triage
gws workflow +email-to-task --message-id MESSAGE_ID

# 2. Read a sheet range and email a teammate the takeaway
gws sheets +read --spreadsheet SPREADSHEET_ID --range "Q2!A1:D20"
gws gmail +send --to lead@example.com --subject "Q2 numbers" --body "See attached summary."

# 4. One-command brief for your next meeting
gws workflow +meeting-prep
```

For each service's full resource/method surface, load that service's skill (e.g. `gws-gmail`) and run `gws <service> --help` or `gws schema <service>.<resource>.<method>`.
