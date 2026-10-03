# CRM Data Operations

Step-by-step scenario for managing contacts, deals, and activities in a NocoDB-backed CRM.

## Scenario Overview

You have three tables in your NocoDB base:
- **Contacts** -- people and companies
- **Deals** -- sales opportunities linked to contacts
- **Activities** -- calls, emails, meetings linked to deals

## Step 1 -- Discover the schema

Before any operation, confirm table names and field structure.

```
Tool: mcp__plugin_nocodb-ops_nocodb__getTablesList
Parameters: (none)
```

Then get the schema for each table:

```
Tool: mcp__plugin_nocodb-ops_nocodb__getTableSchema
Parameters:
  tableId: "m_contacts"
```

## Step 2 -- Find contacts by status

Pull all active leads created in the past month.

```
Tool: mcp__plugin_nocodb-ops_nocodb__queryRecords
Parameters:
  tableId: "m_contacts"
  where: "(Status,eq,Lead)~and(Created,isWithin,pastMonth)"
  fields: ["Name", "Email", "Company", "Phone", "Created"]
  pageSize: 100
  sort: [{ "field": "Created", "direction": "desc" }]
```

## Step 3 -- Create a new deal

After qualifying a lead, create a deal record.

```
Tool: mcp__plugin_nocodb-ops_nocodb__createRecords
Parameters:
  tableId: "m_deals"
  records: [
    {
      "fields": {
        "Title": "Acme Corp - Enterprise Plan",
        "Value": 45000,
        "Stage": "Qualification",
        "Owner": "Sarah",
        "Expected Close": "2025-06-30"
      }
    }
  ]
```

## Step 4 -- Update deal stage

Move a deal forward in the pipeline after a successful demo.

```
Tool: mcp__plugin_nocodb-ops_nocodb__updateRecords
Parameters:
  tableId: "m_deals"
  records: [
    {
      "id": 42,
      "fields": {
        "Stage": "Proposal",
        "Notes": "Demo completed. Sending proposal by Friday."
      }
    }
  ]
```

## Step 5 -- Log an activity

Record a follow-up call against the deal.

```
Tool: mcp__plugin_nocodb-ops_nocodb__createRecords
Parameters:
  tableId: "m_activities"
  records: [
    {
      "fields": {
        "Type": "Call",
        "Subject": "Follow-up on proposal",
        "DealId": 42,
        "Date": "2025-04-06",
        "Notes": "Client requested pricing breakdown by department."
      }
    }
  ]
```

## Step 6 -- Aggregate pipeline value

Calculate total value of deals in active stages.

```
Tool: mcp__plugin_nocodb-ops_nocodb__aggregate
Parameters:
  tableId: "m_deals"
  aggregations: [{ "field": "Value", "type": "sum" }]
  filterGroups: [{ "alias": "Open pipeline", "where": "(Stage,neq,Closed Won)~and(Stage,neq,Closed Lost)" }]
```

## Step 7 -- Count deals by stage

Check how many deals are at each pipeline stage -- one call, one count per distinct value:

```
Tool: mcp__plugin_nocodb-ops_nocodb__groupByRecords
Parameters:
  tableId: "m_deals"
  fieldId: "<Stage field id from getTableSchema>"
```

The answer lists each stage (Qualification, Proposal, Negotiation, Closed Won, Closed Lost) with its count. For a single stage, `countRecords` with `filter: { "field": "Stage", "operator": "eq", "value": "Qualification" }` works too.

## Step 8 -- Find stale deals

Identify deals that have not been updated in 30 days.

```
Tool: mcp__plugin_nocodb-ops_nocodb__queryRecords
Parameters:
  tableId: "m_deals"
  where: "(Stage,neq,Closed Won)~and(Stage,neq,Closed Lost)~and(Updated,lt,daysAgo,30)"
  fields: ["Title", "Stage", "Owner", "Value", "Updated"]
  sort: [{ "field": "Updated", "direction": "asc" }]
```

Note: `(Updated,lt,daysAgo,30)` keeps only deals last updated **before** 30 days ago; sorting `Updated` ascending puts the longest-untouched deals first. (`isWithin,pastNumberOfDays,30` would select the opposite -- deals touched in the last 30 days.)

## Summary

This workflow covers the core CRM data cycle:

1. Discover tables and fields
2. Query contacts with filters
3. Create deal records
4. Update deal progression
5. Log related activities
6. Aggregate pipeline metrics
7. Monitor stale opportunities
