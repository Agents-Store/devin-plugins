# Scenario: Find and Import a Community Workflow

Walkthrough: User needs a Notion-to-Google-Sheets sync workflow. We search the official library first, find a partial match, then search community sources for a better fit.

## User Request

> "I need a workflow that syncs new Notion database entries to a Google Sheets spreadsheet in real-time."

## Step 1: Search the Official Library

Start with the official n8n template library — it has the highest quality and easiest import path.

```
~~template_search("notion google sheets sync database")
```

**Results (hypothetical):**

| # | Template | Views | Nodes | Match Quality |
|---|----------|-------|-------|---------------|
| 1 | "Sync Notion DB to Google Sheets (manual)" | 8,200 | 5 | Partial — manual trigger only |
| 2 | "Notion to Sheets — one-time export" | 3,100 | 4 | Poor — one-time, not real-time |
| 3 | "Google Sheets to Notion sync" | 12,400 | 7 | Wrong direction |

**Assessment:** Template #1 is closest but uses a manual trigger instead of real-time sync. We need a webhook or polling trigger that fires when Notion changes.

Let's check template #1 in detail:

```
~~template_get(id={template_1_id})
```

**Analysis:**
- Trigger: Manual trigger (not what we want)
- Nodes: Notion (query DB) → Set (map fields) → Google Sheets (append row)
- Credentials: Notion API key, Google Sheets OAuth2
- The core logic (query + map + append) is right, but the trigger needs changing

**Decision:** We could modify this template, but let's check community sources for a ready-made real-time version first.

## Step 2: Search Community GitHub Repos

Target the largest community repositories for a better match.

### Search Zie619/n8n-workflows

```
~~search("site:github.com/Zie619/n8n-workflows notion google sheets sync")
```

**Result:** Found a workflow page at `zie619.github.io/n8n-workflows` mentioning "Notion Database to Google Sheets — Real-time Sync with Webhook".

### Fetch the raw JSON

```
~~scrape("https://zie619.github.io/n8n-workflows/?id={workflow_id}")
```

If the page contains the workflow JSON, extract it. If not, try the raw URL:

```
~~scrape("https://raw.githubusercontent.com/Zie619/n8n-workflows/main/workflows/{workflow_id}.json")
```

**Result:** Successfully fetched workflow JSON.

### Also check enescingoz/awesome-n8n-templates

```
~~search("site:github.com/enescingoz/awesome-n8n-templates notion sheets")
```

**Result:** Found `Notion/notion-to-google-sheets-realtime.json` in the repo.

```
~~scrape("https://raw.githubusercontent.com/enescingoz/awesome-n8n-templates/main/Notion/notion-to-google-sheets-realtime.json")
```

**Result:** Second workflow JSON fetched.

## Step 3: Analyze Both Community Workflows

### Workflow A (from Zie619)

Parse the JSON and examine:

```json
{
  "nodes": [
    { "type": "n8n-nodes-base.webhook", "name": "Notion Webhook" },
    { "type": "n8n-nodes-base.notion", "name": "Get Page Details" },
    { "type": "n8n-nodes-base.set", "name": "Map Fields" },
    { "type": "n8n-nodes-base.if", "name": "Check Duplicates" },
    { "type": "n8n-nodes-base.googleSheets", "name": "Find Existing Row" },
    { "type": "n8n-nodes-base.googleSheets", "name": "Append Row" },
    { "type": "n8n-nodes-base.googleSheets", "name": "Update Row" },
    { "type": "n8n-nodes-base.noOp", "name": "No Operation" }
  ]
}
```

**Analysis — Workflow A:**
- **Nodes:** 8 (reasonable complexity)
- **Trigger:** Webhook — receives Notion webhook events (real-time)
- **Logic:** Gets full page details, maps fields, checks for duplicates, appends or updates
- **Credentials needed:** Notion API key, Google Sheets OAuth2
- **Quality:** Good — handles both new entries and updates, has duplicate detection
- **Potential issue:** Requires setting up Notion webhook integration separately

### Workflow B (from enescingoz)

```json
{
  "nodes": [
    { "type": "n8n-nodes-base.scheduleTrigger", "name": "Every 5 Minutes" },
    { "type": "n8n-nodes-base.notion", "name": "Query Database" },
    { "type": "n8n-nodes-base.code", "name": "Filter New Entries" },
    { "type": "n8n-nodes-base.set", "name": "Map to Sheet Columns" },
    { "type": "n8n-nodes-base.googleSheets", "name": "Append Rows" }
  ]
}
```

**Analysis — Workflow B:**
- **Nodes:** 5 (simpler)
- **Trigger:** Schedule (every 5 minutes) — polling, not true real-time
- **Logic:** Polls Notion DB, filters for entries created since last run, appends to Sheets
- **Credentials needed:** Notion API key, Google Sheets OAuth2
- **Quality:** Good but not truly real-time — has up to 5-minute delay
- **Advantage:** Simpler setup, no external webhook configuration needed

### Comparison

| Aspect | Workflow A (Zie619) | Workflow B (enescingoz) |
|--------|-------------------|----------------------|
| Trigger | Webhook (real-time) | Schedule (5-min polling) |
| Complexity | 8 nodes | 5 nodes |
| Duplicate handling | Yes | Yes (via timestamp filter) |
| Update handling | Yes (append or update) | No (append only) |
| External setup | Notion webhook config needed | None |
| Credentials | Notion API + Google Sheets OAuth | Same |

**Decision:** Workflow A better matches the "real-time" requirement. Recommend it, but mention Workflow B as a simpler alternative if the user doesn't want to set up Notion webhooks.

## Step 4: Validate the Chosen Workflow

```
~~workflow_validate({workflow_A_json})
```

**Expected result:** Validation passes, or returns warnings about:
- Node `typeVersion` — may need updating if workflow is from an older n8n version
- Credential references — will be stripped during import (expected)

**If validation fails:** Check the error against the `troubleshoot` skill. Common fixes:
- Update `typeVersion` for deprecated node versions
- Fix connection references if node names changed
- Add missing `meta` fields

## Step 5: Import the Workflow

Since this is community JSON (not from the official library), use `~~workflow_create` instead of `~~template_deploy`.

```
~~workflow_create({
  name: "Notion to Google Sheets — Real-time Sync",
  workflow_json: {workflow_A_json},
  tags: ["community-import", "notion", "google-sheets"]
})
```

The workflow is created in **inactive** state.

## Step 6: Verify Import

```
~~workflow_list
```

Confirm "Notion to Google Sheets — Real-time Sync" appears in the list with status: inactive.

## Step 7: Set Up Credentials

### Notion API Key

1. Go to n8n Credentials > New > Notion API
2. Enter the Notion Internal Integration Token
   - Created at: https://www.notion.so/my-integrations
   - Must have access to the target database (share the DB with the integration)

### Google Sheets OAuth2

1. Go to n8n Credentials > New > Google Sheets OAuth2 API
2. Follow the OAuth flow:
   - Google Cloud Console project with Sheets API enabled
   - OAuth consent screen configured
   - Credential client ID and secret entered in n8n
   - Authorize and grant access

### Map credentials to workflow nodes

1. Open the workflow in n8n UI
2. Click "Get Page Details" node → select Notion credential
3. Click "Find Existing Row" node → select Google Sheets credential
4. Click "Append Row" node → select Google Sheets credential
5. Click "Update Row" node → select Google Sheets credential

## Step 8: Configure Notion Webhook (for Workflow A)

The webhook node generates a URL like:
```
https://your-n8n.example.com/webhook/{webhook-id}
```

Set up the Notion webhook:
1. In your Notion integration settings, add this webhook URL
2. Subscribe to "page_added" and "page_updated" events for the target database
3. Alternatively: use a Notion webhook service (like Notion's built-in automation or a third-party connector)

**Note:** Native Notion webhooks are limited. If the user can't set up webhooks, recommend Workflow B (polling) as a fallback.

## Step 9: Test

1. Open the workflow in n8n UI
2. Click "Execute Workflow" (or trigger by creating a test entry in Notion)
3. Check each node's output:
   - Webhook receives the event
   - Notion query returns the page details
   - Set node maps fields correctly
   - Google Sheets receives the new row
4. Verify the test row appears in Google Sheets

## Step 10: Activate

Once the test passes:
1. Activate the workflow in n8n UI
2. Create another Notion entry to verify the live workflow
3. Confirm the entry appears in Google Sheets within seconds

## Summary

- **Official library** had a partial match (manual trigger only)
- **Community search** found two better options
- **Chose Workflow A** from Zie619 for real-time webhook-based sync
- **Alternative:** Workflow B from enescingoz for simpler polling-based approach
- **Credentials:** Notion API + Google Sheets OAuth2
- **Extra setup:** Notion webhook configuration for real-time trigger
