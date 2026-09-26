---
name: crm-contacts
description: CRM contact management — create, update, search, list deals for contacts, and add comments. Use when working with CRM contacts, customer records, or contact-deal relationships.
---

# CRM Contacts

This skill covers CRM contact lifecycle — creating, searching, updating, and managing relationships with deals.

## Available Tools

| Tool | Description |
|------|-------------|
| `crm_contacts_list` | List CRM contacts with filtering |
| `crm_contacts_list_by_email` | Find contact by email address |
| `crm_contacts_show` | Get detailed contact information |
| `crm_contacts_create` | Create a new CRM contact |
| `crm_contacts_update` | Update contact fields |
| `crm_contacts_deals_list` | List deals associated with a contact |
| `crm_contacts_comments_create` | Add a comment/note to a contact |

## Listing & Searching

### List All Contacts
```
Tool: crm_contacts_list
Input: {"limit": 50, "offset": 0}

Returns contacts with name, email, phone, and custom fields.
Supports pagination with limit/offset.
```

### Find Contact by Email
```
Tool: crm_contacts_list_by_email
Input: {"email": "user@example.com"}

Returns contact matching the email address.
```

### Get Contact Details
```
Tool: crm_contacts_show
Input: {"id": "<contact-id>"}

Returns full contact record including custom fields, tags, and metadata.
```

## Creating & Updating

### Create Contact
```
Tool: crm_contacts_create
Input: {
  "emails": [{"value": "user@example.com"}],
  "phones": [{"value": "+380501234567"}],
  "name": "John Doe"
}

Returns new contact ID.
```

### Update Contact
```
Tool: crm_contacts_update
Input: {
  "id": "<contact-id>",
  "name": "John Updated",
  "phones": [{"value": "+380507654321"}]
}
```

## Relationships

### List Contact's Deals
```
Tool: crm_contacts_deals_list
Input: {"id": "<contact-id>"}

Returns all deals linked to this contact with amounts and pipeline stages.
```

### Add Comment to Contact
```
Tool: crm_contacts_comments_create
Input: {"id": "<contact-id>", "text": "Follow-up call completed. Interested in enterprise plan."}

Adds internal note visible in contact history.
```

## Common Workflows

### Create Contact and Start Deal
```
1. crm_contacts_create(emails, name, phones) -> Get contact ID
2. crm_deals_create(name, contact_id, pipeline_id) -> Link deal to contact
```

### Find Contact and Review History
```
1. crm_contacts_list_by_email(email) -> Find contact
2. crm_contacts_show(id) -> View full details
3. crm_contacts_deals_list(id) -> View associated deals
```

### Bulk Contact Lookup
```
1. crm_contacts_list(limit=100, offset=0) -> First page
2. crm_contacts_list(limit=100, offset=100) -> Next page
```

## Best Practices

1. **Search by email first** before creating to avoid duplicates
2. **Add comments** for important interactions to build contact history
3. **Link contacts to deals** to track revenue relationships
4. **Use pagination** for large contact lists
5. **Keep contact data updated** — phone, email, name changes
