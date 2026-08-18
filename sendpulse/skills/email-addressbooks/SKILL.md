---
name: email-addressbooks
description: Email addressbook and subscriber management — create addressbooks, add/remove subscribers, manage variables, check sending costs. Use when managing mailing lists, subscriber data, or email list segmentation.
---

# Email Addressbooks

This skill covers mailing list management, subscriber lifecycle, and list segmentation.

## Available Tools

| Tool | Description |
|------|-------------|
| `email_addressbooks_list` | List all mailing lists |
| `email_addressbooks_show` | Get mailing list details |
| `email_addressbooks_create` | Create a new mailing list |
| `email_addressbooks_update` | Update mailing list name |
| `email_addressbooks_delete` | Delete a mailing list |
| `email_addressbooks_cost` | Calculate campaign cost for a list |
| `email_addressbooks_emails_list` | List subscribers in a list |
| `email_addressbooks_emails_show` | Get subscriber details |
| `email_addressbooks_emails_create` | Add subscribers to a list |
| `email_addressbooks_emails_delete` | Remove subscribers from a list |
| `email_addressbooks_emails_unsubscribe` | Unsubscribe an email |
| `email_addressbooks_emails_total` | Get total subscriber count |
| `email_addressbooks_emails_phone_update` | Update subscriber phone number |
| `email_addressbooks_emails_variables_update` | Update subscriber custom variables |
| `email_addressbooks_variables_list` | List available variables in a list |
| `email_addressbooks_variables_emails_list` | Find subscribers by variable value |
| `email_addressbooks_campaigns_list` | List campaigns sent to a list |

## Addressbook Management

### List Addressbooks
```
Tool: email_addressbooks_list
Input: {"limit": 100, "offset": 0}

Returns mailing lists with IDs, names, and subscriber counts.
```

### Create Addressbook
```
Tool: email_addressbooks_create
Input: {"name": "Newsletter Subscribers"}

Returns new addressbook ID.
```

### Get Addressbook Details
```
Tool: email_addressbooks_show
Input: {"id": "<addressbook-id>"}

Returns list name, creation date, subscriber count, and status.
```

### Update Addressbook
```
Tool: email_addressbooks_update
Input: {"id": "<addressbook-id>", "name": "Weekly Newsletter"}
```

### Delete Addressbook
```
Tool: email_addressbooks_delete
Input: {"id": "<addressbook-id>"}

Permanently removes the list and all subscriber associations.
```

### Calculate Sending Cost
```
Tool: email_addressbooks_cost
Input: {"id": "<addressbook-id>"}

Returns estimated cost of sending a campaign to this list.
```

## Subscriber Management

### List Subscribers
```
Tool: email_addressbooks_emails_list
Input: {"id": "<addressbook-id>", "limit": 100, "offset": 0}

Returns subscribers with email, variables, and status.
```

### Add Subscribers
```
Tool: email_addressbooks_emails_create
Input: {
  "id": "<addressbook-id>",
  "emails": [
    {"email": "user1@example.com", "variables": {"name": "Alice", "city": "Kyiv"}},
    {"email": "user2@example.com", "variables": {"name": "Bob", "city": "Lviv"}}
  ]
}

Adds one or more subscribers with optional custom variables.
```

### Get Subscriber Details
```
Tool: email_addressbooks_emails_show
Input: {"id": "<addressbook-id>", "email": "user@example.com"}

Returns subscriber status, variables, and metadata.
```

### Remove Subscribers
```
Tool: email_addressbooks_emails_delete
Input: {"id": "<addressbook-id>", "emails": ["user@example.com"]}
```

### Unsubscribe
```
Tool: email_addressbooks_emails_unsubscribe
Input: {"id": "<addressbook-id>", "emails": ["user@example.com"]}

Marks as unsubscribed (different from delete — preserves record).
```

### Get Total Count
```
Tool: email_addressbooks_emails_total
Input: {"id": "<addressbook-id>"}

Returns total number of subscribers in the list.
```

### Update Subscriber Phone
```
Tool: email_addressbooks_emails_phone_update
Input: {"id": "<addressbook-id>", "email": "user@example.com", "phone": "+380501234567"}
```

### Update Subscriber Variables
```
Tool: email_addressbooks_emails_variables_update
Input: {"id": "<addressbook-id>", "email": "user@example.com", "variables": {"city": "Odesa", "plan": "premium"}}
```

## List Variables & Segmentation

### List Variables
```
Tool: email_addressbooks_variables_list
Input: {"id": "<addressbook-id>"}

Returns all custom variables defined for the list.
```

### Find Subscribers by Variable
```
Tool: email_addressbooks_variables_emails_list
Input: {"id": "<addressbook-id>", "variable_name": "city", "variable_value": "Kyiv"}

Returns subscribers matching the variable filter — useful for segmentation.
```

## Campaign History

### List Campaigns for Addressbook
```
Tool: email_addressbooks_campaigns_list
Input: {"id": "<addressbook-id>"}

Returns campaigns that were sent to this list.
```

## Common Workflows

### Create List and Import Subscribers
```
1. email_addressbooks_create(name="Product Launch") -> Get list ID
2. email_addressbooks_emails_create(id, emails=[...]) -> Add subscribers
3. email_addressbooks_emails_total(id) -> Verify count
```

### Segment by Variable
```
1. email_addressbooks_variables_list(id) -> See available variables
2. email_addressbooks_variables_emails_list(id, variable_name, variable_value) -> Get segment
```

### Pre-Campaign Check
```
1. email_addressbooks_emails_total(id) -> Check audience size
2. email_addressbooks_cost(id) -> Verify cost within budget
3. email_campaigns_create(...) -> Proceed with campaign
```

## Best Practices

1. **Check cost before sending** to avoid budget surprises
2. **Use variables** for personalization (name, city, plan, etc.)
3. **Unsubscribe rather than delete** to preserve records and comply with regulations
4. **Segment by variables** for targeted campaigns
5. **Verify subscriber count** after imports to confirm successful addition
