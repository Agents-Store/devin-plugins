---
name: email-campaigns-templates
description: Email campaign creation, management, statistics, and template management. Use when creating email campaigns, designing templates, or analyzing campaign performance.
---

# Email Campaigns & Templates

This skill covers email campaign lifecycle and reusable template management.

## Available Tools

| Tool | Description |
|------|-------------|
| `email_campaigns_list` | List all email campaigns |
| `email_campaigns_show` | Get campaign details by ID |
| `email_campaigns_create` | Create a new email campaign |
| `email_campaigns_update` | Update a scheduled campaign |
| `email_campaigns_delete` | Cancel/delete a campaign |
| `email_campaigns_emails_show` | Get specific email details in a campaign |
| `email_campaigns_stats_countries` | Campaign stats by country |
| `email_campaigns_stats_referrals` | Campaign referral statistics |
| `email_templates_list` | List system and user templates |
| `email_templates_show` | Get template by ID |
| `email_templates_show_by_name_slug` | Get template by name slug |
| `email_templates_create` | Create a new email template |
| `email_templates_update` | Update an existing template |

## Campaign Management

### List Campaigns
```
Tool: email_campaigns_list
Input: {"limit": 50, "offset": 0}

Returns campaigns with name, status, send date, and open/click rates.
```

### Create Campaign
```
Tool: email_campaigns_create
Input: {
  "name": "March Newsletter",
  "subject": "Your monthly update from Acme Corp",
  "sender_email": "newsletter@acme.com",
  "sender_name": "Acme Corp",
  "addressbook_id": "<addressbook-id>",
  "template_id": "<template-id>",
  "send_date": "2026-03-01T10:00:00"
}

Returns campaign ID. Use send_date for scheduling, omit for immediate send.
```

### Get Campaign Details
```
Tool: email_campaigns_show
Input: {"id": "<campaign-id>"}

Returns full campaign configuration, status, and basic stats.
```

### Update Scheduled Campaign
```
Tool: email_campaigns_update
Input: {"id": "<campaign-id>", "subject": "Updated: March Newsletter", "send_date": "2026-03-02T10:00:00"}

Only works for campaigns not yet sent.
```

### Cancel Campaign
```
Tool: email_campaigns_delete
Input: {"id": "<campaign-id>"}

Cancels and removes the campaign. Cannot undo after sending.
```

## Campaign Analytics

### Country Statistics
```
Tool: email_campaigns_stats_countries
Input: {"id": "<campaign-id>"}

Returns open/click rates broken down by recipient country.
```

### Referral Statistics
```
Tool: email_campaigns_stats_referrals
Input: {"id": "<campaign-id>"}

Returns traffic sources and referral data from campaign links.
```

### Email Details in Campaign
```
Tool: email_campaigns_emails_show
Input: {"id": "<campaign-id>", "email": "user@example.com"}

Returns delivery status, opens, clicks for a specific recipient.
```

## Template Management

### List Templates
```
Tool: email_templates_list
Input: {}

Returns both system (built-in) and user-created templates.
```

### Get Template
```
Tool: email_templates_show
Input: {"id": "<template-id>"}

Returns template HTML, name, and metadata.
```

### Get Template by Slug
```
Tool: email_templates_show_by_name_slug
Input: {"name": "welcome-email"}

Alternative lookup using template name slug.
```

### Create Template
```
Tool: email_templates_create
Input: {
  "name": "Product Update",
  "body": "<html><body>{{name}}, check out our new features!</body></html>"
}

Returns new template ID. Use {{variable}} for personalization.
```

### Update Template
```
Tool: email_templates_update
Input: {"id": "<template-id>", "name": "Product Update v2", "body": "<html>...</html>"}
```

## Common Workflows

### Launch Email Campaign
```
1. email_balance_show() -> Check credits
2. email_addressbooks_list() -> Select target list
3. email_addressbooks_cost(addressbook_id) -> Verify cost
4. email_templates_list() -> Select template
5. email_senders_list() -> Select verified sender
6. email_campaigns_create(subject, addressbook_id, template_id, sender_email) -> Create
```

### Analyze Campaign Performance
```
1. email_campaigns_show(campaign_id) -> Basic stats
2. email_campaigns_stats_countries(campaign_id) -> Geographic breakdown
3. email_campaigns_stats_referrals(campaign_id) -> Referral sources
```

### Create and Use Templates
```
1. email_templates_create(name, body) -> Get template ID
2. email_campaigns_create(..., template_id) -> Use in campaign
```

## Template Personalization Variables

Templates support `{{variable_name}}` syntax for personalization:
- `{{name}}` — Subscriber name
- `{{email}}` — Subscriber email
- Custom variables from addressbook (e.g., `{{city}}`, `{{plan}}`)

## Best Practices

1. **Check balance before creating** campaigns to ensure sufficient credits
2. **Use templates** for consistent branding across campaigns
3. **Schedule campaigns** with send_date rather than sending immediately
4. **Review country stats** to optimize send times for different time zones
5. **Test with small lists** before sending to full addressbook
6. **Use personalization variables** for higher engagement
