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
Tool: mcp__nocodb__getTablesList
Parameters: (none)
```

Then get the schema for each table:

```
Tool: mcp__nocodb__getTableSchema
Parameters:
  tableId: "m_contacts"
```

## Step 2 -- Find contacts by status

Pull all active leads created in the past month.

```
Tool: mcp__nocodb__queryRecords
Parameters:
  tableId: "m_contacts"
  where: "(Status,eq,Lead)~and(Created,isWithin,pastMonth)"
  fields: "Name,Email,Company,Phone,Created"
  pageSize: 100
  sort: "-Created"
```

## Step 3 -- Create a new deal

After qualifying a lead, create a deal record.

```
Tool: mcp__nocodb__createRecords
Parameters:
  tableId: "m_deals"
  records: [
    {
      "Title": "Acme Corp - Enterprise Plan",
      "Value": 45000,
      "Stage": "Qualification",
      "Owner": "Sarah",
      "Expected Close": "2025-06-30"
    }
  ]
```

## Step 4 -- Update deal stage

Move a deal forward in the pipeline after a successful demo.

```
Tool: mcp__nocodb__updateRecords
Parameters:
  tableId: "m_deals"
  records: [
    {
      "Id": 42,
      "Stage": "Proposal",
      "Notes": "Demo completed. Sending proposal by Friday."
    }
  ]
```

## Step 5 -- Log an activity

Record a follow-up call against the deal.

```
Tool: mcp__nocodb__createRecords
Parameters:
  tableId: "m_activities"
  records: [
    {
      "Type": "Call",
      "Subject": "Follow-up on proposal",
      "DealId": 42,
      "Date": "2025-04-06",
      "Notes": "Client requested pricing breakdown by department."
    }
  ]
```

## Step 6 -- Aggregate pipeline value

Calculate total value of deals in active stages.

```
Tool: mcp__nocodb__aggregate
Parameters:
  tableId: "m_deals"
  aggregation: [{"field": "Value", "type": "sum"}]
  where: "(Stage,neq,Closed Won)~and(Stage,neq,Closed Lost)"
```

## Step 7 -- Count deals by stage

Check how many deals are at each pipeline stage.

```
Tool: mcp__nocodb__countRecords
Parameters:
  tableId: "m_deals"
  where: "(Stage,eq,Qualification)"
```

Repeat for each stage: Qualification, Proposal, Negotiation, Closed Won, Closed Lost.

## Step 8 -- Find stale deals

Identify deals that have not been updated in 30 days.

```
Tool: mcp__nocodb__queryRecords
Parameters:
  tableId: "m_deals"
  where: "(Stage,neq,Closed Won)~and(Stage,neq,Closed Lost)~and(Updated,isWithin,pastNumberOfDays,30)"
  fields: "Title,Stage,Owner,Value,Updated"
  sort: "Updated"
```

Note: To find stale deals (NOT updated recently), query all open deals sorted by `Updated` ascending -- the oldest-updated appear first.

## Summary

This workflow covers the core CRM data cycle:

1. Discover tables and fields
2. Query contacts with filters
3. Create deal records
4. Update deal progression
5. Log related activities
6. Aggregate pipeline metrics
7. Monitor stale opportunities
