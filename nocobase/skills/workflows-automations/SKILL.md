---
name: workflows-automations
description: Workflow engine — triggers, node types, conditions, variables, approval flows. This skill should be used when the user asks to create workflows, set up triggers, build approval flows, or automate business processes.
---

# Workflows & Automations

Expert guidance on NocoBase workflow engine — triggers, node types, execution modes, variables, and common automation patterns.

## Workflow Types

| Type | Trigger | Use Case |
|------|---------|----------|
| Collection event | Record created/updated/deleted | Notifications, validations, cascading updates |
| Schedule | Cron expression | Reports, cleanup, data sync |
| Action | User clicks button | Manual approval, batch processing |

## Trigger Configuration

### Collection Event Trigger
```
Trigger: Collection event
Collection: orders
Event: afterCreate
Condition: {{ $context.data.total > 1000 }}
Mode: async (recommended for non-blocking)
```

Events: `afterCreate`, `afterUpdate`, `afterDelete`, `beforeCreate`, `beforeUpdate`, `beforeDelete`

### Schedule Trigger
```
Trigger: Schedule
Expression: "0 9 * * 1-5"  (weekdays at 9:00 AM)
Mode: async
```

Common cron patterns:
- Every hour: `0 * * * *`
- Daily at 9 AM: `0 9 * * *`
- Weekdays at 9 AM: `0 9 * * 1-5`
- Every Monday: `0 0 * * 1`
- First of month: `0 0 1 * *`

### Action Trigger
```
Trigger: Action (button click)
Collection: purchase_requests
Button label: "Submit for Approval"
```

## Node Types

### Condition
Branching logic based on expressions.
```
Node: Condition
Expression: {{ $context.data.amount > 10000 }}
True branch → Manager Approval
False branch → Auto Approve
```

### Calculation
Compute values and store in variables.
```
Node: Calculation
Expression: {{ $context.data.price * $context.data.quantity * (1 - $context.data.discount / 100) }}
Variable: lineTotal
```

### Query
Fetch records from a collection.
```
Node: Query
Collection: contacts
Filter: { email: {{ $context.data.contactEmail }} }
Result variable: contactRecord
```

### Create Record
```
Node: Create
Collection: notifications
Data: {
  title: "New order #{{ $context.data.id }}",
  message: "Order created by {{ $context.data.createdBy.name }}",
  type: "order"
}
```

### Update Record
```
Node: Update
Collection: orders
Filter: { id: {{ $context.data.id }} }
Data: {
  status: "approved",
  approvedAt: {{ NOW() }}
}
```

### Delete Record
```
Node: Delete
Collection: temp_records
Filter: { createdAt: { $lt: {{ DATEADD(NOW(), -30, 'days') }} } }
```

### HTTP Request
```
Node: Request
Method: POST
URL: https://hooks.slack.com/services/xxx
Body: {
  "text": "New order #{{ $context.data.id }} - ${{ $context.data.total }}"
}
```

### Manual (Approval)
```
Node: Manual
Assignees: {{ $context.data.department.manager }}
Actions: Approve, Reject
Timeout: 48 hours
```

### Loop
```
Node: Loop
Target: {{ $jobsData.queryResult }}
Loop body nodes: Process each record
```

### Parallel Branch
```
Node: Parallel
Branches:
  - Branch A: Send email notification
  - Branch B: Create audit log
  - Branch C: Update dashboard
(All execute simultaneously)
```

### Delay
```
Node: Delay
Duration: 24 hours
Then: Send follow-up email
```

## Variable System

### Context Variables
| Variable | Description |
|----------|-------------|
| `$context.data` | Trigger record data |
| `$context.user` | Current user |
| `$context.params` | Action parameters |

### Job Variables
| Variable | Description |
|----------|-------------|
| `$jobsData.nodeKey` | Output from a specific node |
| `$jobsData.queryResult` | Result of Query node |
| `$jobsData.calculationResult` | Result of Calculation node |

### System Functions
| Function | Description |
|----------|-------------|
| `NOW()` | Current datetime |
| `DATEADD(date, n, unit)` | Add time to date |
| `DATEDIFF(date1, date2, unit)` | Difference between dates |

## Common Workflow Patterns

### Record Create → Notify
```
Trigger: orders.afterCreate
1. Query: Get order creator details
2. Request: POST to Slack webhook
   Body: "New order #{{$context.data.id}} by {{$jobsData.query.name}}"
```

### Record Update → Cascade
```
Trigger: deals.afterUpdate
Condition: status changed to "Won"
1. Update: Set all related tasks to "Completed"
2. Create: Add entry to revenue_log
3. Request: Notify sales team
```

### Scheduled Cleanup
```
Trigger: Schedule (daily at 2 AM)
1. Query: Find records older than 90 days with status "Draft"
2. Loop: For each record
   2a. Delete: Remove record
3. Create: Add cleanup log entry
```

### Approval Flow
```
Trigger: Action (Submit button)
1. Update: Set status to "Pending Approval"
2. Condition: amount > 10000?
   Yes → Manual: Assign to Director
   No → Manual: Assign to Manager
3. Condition: Approved?
   Yes → Update: status = "Approved"
   No → Update: status = "Rejected"
4. Request: Send notification
```

## Execution Modes

| Mode | Description | Use When |
|------|-------------|----------|
| Sync | Blocks until complete | Before-event validation |
| Async | Non-blocking | After-event notifications, heavy processing |

## Error Handling in Workflows

### HTTP Request Failures
```
Trigger: orders.afterCreate
1. Request: POST to external API
2. Condition: Check request result
   - Success → Continue normal flow
   - Failure → Create: Log error to error_logs collection
              → Request: Send alert to admin webhook
              → Delay: 5 minutes
              → Request: Retry the original request
```

### Missing Data Handling
```
Trigger: contacts.afterCreate
1. Condition: {{ $context.data.email != null }}
   - True → Request: Send welcome email
   - False → Create: Log "missing email" to audit_logs
```

### Cascading Error Prevention
```
Trigger: orders.afterUpdate
1. Query: Get related order_items
2. Condition: {{ $jobsData.queryResult.length > 0 }}
   - True → Loop: Update each item
   - False → (skip, no items to update)
```

## Variable Passing Between Nodes

### Using $context.data
Access trigger record fields:
```
{{ $context.data.id }}          // Record ID
{{ $context.data.status }}      // Field value
{{ $context.data.createdBy }}   // Creator reference
```

### Using $jobsData
Access output from previous nodes:
```
{{ $jobsData.queryNodeKey }}              // Full query result
{{ $jobsData.queryNodeKey[0].name }}      // First result's name field
{{ $jobsData.calculationNodeKey }}        // Calculation result
```

### Chaining Multiple Conditions
```
Trigger: deals.afterUpdate
1. Condition: status changed?
   - Yes:
     2. Condition: new status == "Won"?
        - Yes:
          3. Calculate: commission = amount * 0.05
          4. Create: commission_record
          5. Request: Notify sales team
        - No:
          2b. Condition: new status == "Lost"?
              - Yes:
                3b. Create: lost_reason_record
                4b. Request: Notify manager
              - No: (skip)
   - No: (skip, no status change)
```

## Best Practices

1. **Use async mode** — unless you need to block the user operation
2. **Add conditions early** — filter out irrelevant triggers to save processing
3. **Test incrementally** — build one node at a time and test
4. **Use variables** — pass data between nodes via the variable system
5. **Handle errors** — add condition nodes to check for null/missing data before using them
6. **Log important events** — create audit trail records in workflows
7. **Keep workflows focused** — one workflow per business process
8. **Use parallel branches** — for independent actions (notify + log simultaneously)
9. **Check for null** — always verify query results are not empty before accessing fields
10. **Retry on failure** — for HTTP requests, add retry logic with delay nodes
