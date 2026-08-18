# Worked Scenarios — full walkthroughs

All commands use the `gws` CLI. IDs from one step feed the next — pipe JSON through `jq`. Confirm before writes; use `--dry-run` to preview.

---

## 1. Inbox triage → tasks

Turn this morning's unread mail into actionable Google Tasks.

```bash
# See unread inbox (sender, subject, date) as JSON
gws gmail +triage

# Pick a message and convert it into a task
gws workflow +email-to-task --message-id 18f0a1b2c3d4e5f6
```

Skills: `gws-gmail` → `gws-gmail-triage`, `gws-workflow` → `gws-workflow-email-to-task`.

---

## 2. Sheet → report doc → email the link

Read figures from a spreadsheet, write a short doc, share it, and email the link.

```bash
# Read the data (note the DOUBLE quotes around the range because of the '!')
gws sheets +read --spreadsheet 1AbCdEf... --range "Q2!A1:D20"

# Create a doc and append the summary text
DOC_ID=$(gws docs documents create --json '{"title": "Q2 Summary"}' | jq -r '.documentId')
gws docs +write --document "$DOC_ID" --text "Q2 revenue up 12% QoQ. Details in the linked sheet."

# Share the doc with a teammate
gws drive permissions create \
  --params "{\"fileId\": \"$DOC_ID\"}" \
  --json '{"role": "reader", "type": "user", "emailAddress": "lead@example.com"}'

# Email the link
gws gmail +send --to lead@example.com --subject "Q2 summary" \
  --body "Summary doc: https://docs.google.com/document/d/$DOC_ID"
```

Skills: `gws-sheets`, `gws-docs`, `gws-drive`, `gws-gmail`.

---

## 3. Spreadsheet rows → calendar events

Bulk-create events from a sheet where each row is an event.

```bash
# Inspect the source rows
gws sheets +read --spreadsheet 1AbCdEf... --range "Events!A2:D50"

# For each row, create an event (loop in your shell / agent)
gws calendar +insert \
  --summary "Kickoff" \
  --start "2026-07-01T10:00:00" \
  --end "2026-07-01T11:00:00"
```

Skills: `recipe-create-events-from-sheet`, `gws-sheets`, `gws-calendar` → `gws-calendar-insert`. The `recipe-create-events-from-sheet` skill spells out the column mapping.

---

## 4. Meeting prep brief

One command assembles your next meeting's agenda, attendees, and linked docs.

```bash
gws workflow +meeting-prep
```

Skill: `gws-workflow` → `gws-workflow-meeting-prep`. Timezone comes from your Google account; override with `--timezone America/New_York`.

---

## 5. New deck + share with the team

```bash
# Create the presentation
PRES_ID=$(gws slides presentations create --json '{"title": "Quarterly Review Q2"}' | jq -r '.presentationId')

# Give the team write access
gws drive permissions create \
  --params "{\"fileId\": \"$PRES_ID\"}" \
  --json '{"role": "writer", "type": "user", "emailAddress": "team@example.com"}'
```

Skills: `gws-slides`, `gws-drive`. See also `recipe-create-presentation`.

---

## 6. Monday standup / weekly digest

```bash
# Today's meetings + open tasks as a standup summary
gws workflow +standup-report

# This week's meetings + unread email count
gws workflow +weekly-digest
```

Skills: `gws-workflow` → `gws-workflow-standup-report`, `gws-workflow-weekly-digest`.

---

## Composing your own

1. Pick the service skill (`gws-<service>`) — it lists resources and helper (`+`) commands.
2. Run `gws <service> --help` to see Discovery methods + helpers together.
3. Run `gws schema <service>.<resource>.<method>` to learn exact `--params` / `--json` shapes.
4. Chain steps by extracting IDs with `jq`, and prefer `--dry-run` on anything destructive.
