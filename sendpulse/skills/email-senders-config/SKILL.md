---
name: email-senders-config
description: Email sender management, email tags, blacklist management, and account balance. Use when configuring senders, managing email tags, handling blacklisted addresses, or checking account balance.
---

# Email Senders & Configuration

This skill covers sender verification, email tags, blacklist management, email information, and account balance.

## Available Tools

### Senders
| Tool | Description |
|------|-------------|
| `email_senders_list` | List all verified sender addresses |
| `email_senders_create` | Add a new sender email |
| `email_senders_delete` | Remove a sender email |
| `email_senders_code_send` | Send verification code to sender email |
| `email_senders_code_activate` | Activate sender with verification code |

### Email Information
| Tool | Description |
|------|-------------|
| `email_emails_list` | Get info for multiple email addresses |
| `email_emails_show` | Get info for a single email |
| `email_emails_show_details` | Get detailed info for a single email |
| `email_emails_delete` | Delete email from all lists |
| `email_emails_statistics_list` | Get statistics for multiple emails |
| `email_emails_statistics_show` | Get statistics for a single email |

### Tags
| Tool | Description |
|------|-------------|
| `email_tags_list` | List all email tags |
| `email_tags_create` | Create a new tag |
| `email_tags_update` | Update a tag |
| `email_tags_delete` | Delete a tag |
| `email_tags_emails_pin` | Assign tags to email addresses |
| `email_tags_emails_unpin` | Remove tags from email addresses |
| `email_tags_phones_pin` | Assign tags to phone numbers |
| `email_tags_phones_unpin` | Remove tags from phone numbers |

### Blacklist
| Tool | Description |
|------|-------------|
| `email_blacklist_emails_list` | List blacklisted email addresses |
| `email_blacklist_emails_add` | Add emails to blacklist |
| `email_blacklist_emails_delete` | Remove emails from blacklist |

### Balance
| Tool | Description |
|------|-------------|
| `email_balance_show` | Get account balance |
| `email_balance_show_detail` | Get detailed balance breakdown |

## Sender Management

### List Senders
```
Tool: email_senders_list
Input: {}

Returns all verified sender email addresses.
```

### Add and Verify New Sender
```
Step 1: Add sender
Tool: email_senders_create
Input: {"email": "news@acme.com", "name": "Acme News"}

Step 2: Send verification code
Tool: email_senders_code_send
Input: {"email": "news@acme.com"}

Step 3: Activate with code (user provides code from email)
Tool: email_senders_code_activate
Input: {"email": "news@acme.com", "code": "123456"}
```

### Remove Sender
```
Tool: email_senders_delete
Input: {"email": "old-sender@acme.com"}
```

## Email Information

### Look Up Email Details
```
Tool: email_emails_show
Input: {"email": "user@example.com"}

Returns subscription status, lists membership, and basic info.
```

### Detailed Email Info
```
Tool: email_emails_show_details
Input: {"email": "user@example.com"}

Returns full details including all variables, tags, and history.
```

### Email Statistics
```
Tool: email_emails_statistics_show
Input: {"email": "user@example.com"}

Returns open rates, click rates, and engagement history.
```

### Delete Email Globally
```
Tool: email_emails_delete
Input: {"email": "user@example.com"}

Removes email from ALL lists. Use with caution.
```

## Tag Management

### List Tags
```
Tool: email_tags_list
Input: {}

Returns all tags with IDs and names.
```

### Create Tag
```
Tool: email_tags_create
Input: {"name": "VIP Customer"}

Returns new tag ID.
```

### Assign Tag to Emails
```
Tool: email_tags_emails_pin
Input: {"tag_id": "<tag-id>", "emails": ["user1@example.com", "user2@example.com"]}
```

### Remove Tag from Emails
```
Tool: email_tags_emails_unpin
Input: {"tag_id": "<tag-id>", "emails": ["user1@example.com"]}
```

### Assign Tag to Phones
```
Tool: email_tags_phones_pin
Input: {"tag_id": "<tag-id>", "phones": ["+380501234567"]}
```

### Update/Delete Tags
```
Tool: email_tags_update
Input: {"id": "<tag-id>", "name": "Premium Customer"}

Tool: email_tags_delete
Input: {"id": "<tag-id>"}
```

## Blacklist Management

### View Blacklist
```
Tool: email_blacklist_emails_list
Input: {}

Returns all blacklisted email addresses.
```

### Add to Blacklist
```
Tool: email_blacklist_emails_add
Input: {"emails": ["spam@example.com", "bounced@example.com"]}

Prevents sending to these addresses across all campaigns.
```

### Remove from Blacklist
```
Tool: email_blacklist_emails_delete
Input: {"emails": ["rehabilitated@example.com"]}
```

## Account Balance

### Check Balance
```
Tool: email_balance_show
Input: {}

Returns current email credit balance.
```

### Detailed Balance
```
Tool: email_balance_show_detail
Input: {}

Returns breakdown by plan, bonus credits, and expiration dates.
```

## Common Workflows

### Set Up New Sender
```
1. email_senders_create(email, name) -> Add sender
2. email_senders_code_send(email) -> Send verification
3. (User checks inbox for code)
4. email_senders_code_activate(email, code) -> Activate
5. email_senders_list() -> Verify it appears
```

### Tag-Based Segmentation
```
1. email_tags_create(name="Premium") -> Create tag
2. email_tags_emails_pin(tag_id, emails=[...]) -> Assign to subscribers
3. Use tag filters in campaign targeting
```

### Clean Up Blacklist
```
1. email_blacklist_emails_list() -> Review blocked emails
2. email_blacklist_emails_delete(emails=[...]) -> Remove false positives
```

### Pre-Campaign Readiness Check
```
1. email_balance_show() -> Sufficient credits?
2. email_senders_list() -> Sender verified?
3. email_blacklist_emails_list() -> Review blacklist
4. Proceed with campaign creation
```

## Best Practices

1. **Verify senders** before creating campaigns — unverified senders block sending
2. **Check balance regularly** to avoid failed campaigns
3. **Use tags** for subscriber segmentation across all lists
4. **Blacklist bounced emails** to improve deliverability scores
5. **Review email statistics** to identify disengaged subscribers
6. **Use `email_emails_delete` carefully** — it removes from ALL lists permanently
