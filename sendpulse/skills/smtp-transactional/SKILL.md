---
name: smtp-transactional
description: SMTP transactional email sending, bounce management, unsubscribe handling, IP and sender domain management. Use when sending transactional emails, managing bounces, or configuring SMTP infrastructure.
---

# SMTP Transactional Email

This skill covers sending transactional emails via SMTP and managing delivery infrastructure.

## Available Tools

### Sending
| Tool | Description |
|------|-------------|
| `smtp_emails_send` | Send a transactional email |
| `smtp_emails_list` | List sent SMTP emails |
| `smtp_emails_show` | Get details of a sent email |
| `smtp_emails_show_list` | Get details for multiple sent emails |
| `smtp_emails_total` | Get total count of sent SMTP emails |

### Bounces
| Tool | Description |
|------|-------------|
| `smtp_bounces_list` | List bounced emails (24-hour window) |
| `smtp_bounces_total` | Get total bounce count |

### Unsubscribes
| Tool | Description |
|------|-------------|
| `smtp_unsubscribes_list` | List unsubscribed emails |
| `smtp_unsubscribes_create` | Add email to unsubscribe list |
| `smtp_unsubscribes_delete` | Remove email from unsubscribe list |
| `smtp_unsubscribes_resubscribe` | Re-subscribe an email address |
| `smtp_unsubscribes_is_unsubscribed` | Check if email is unsubscribed |

### Infrastructure
| Tool | Description |
|------|-------------|
| `smtp_ips_list` | List dedicated IP addresses |
| `smtp_senders_list` | List SMTP sender emails |
| `smtp_senders_create` | Add a new SMTP sender |
| `smtp_senders_domains_list` | List allowed sender domains |
| `smtp_senders_domains_create` | Add a new sender domain |

## Sending Transactional Emails

### Send Email
```
Tool: smtp_emails_send
Input: {
  "email": {
    "subject": "Order Confirmation #12345",
    "from": {"name": "Acme Store", "email": "orders@acme.com"},
    "to": [{"name": "John Doe", "email": "john@example.com"}],
    "html": "<h1>Thank you for your order!</h1><p>Order #12345 confirmed.</p>"
  }
}

Returns message ID for tracking delivery.
```

### List Sent Emails
```
Tool: smtp_emails_list
Input: {"limit": 50, "offset": 0}

Returns sent emails with delivery status, timestamps, and IDs.
```

### Get Email Details
```
Tool: smtp_emails_show
Input: {"id": "<email-id>"}

Returns full delivery details including opens, clicks, and status.
```

### Total Sent Count
```
Tool: smtp_emails_total
Input: {}

Returns total number of SMTP emails sent.
```

## Bounce Management

### List Recent Bounces
```
Tool: smtp_bounces_list
Input: {}

Returns bounced emails from the last 24 hours with bounce type and reason.
```

### Get Bounce Count
```
Tool: smtp_bounces_total
Input: {}

Returns total number of bounced emails.
```

## Unsubscribe Management

### Check Unsubscribe Status
```
Tool: smtp_unsubscribes_is_unsubscribed
Input: {"email": "user@example.com"}

Returns true/false — always check before sending.
```

### List Unsubscribed
```
Tool: smtp_unsubscribes_list
Input: {"limit": 100, "offset": 0}

Returns all unsubscribed email addresses.
```

### Unsubscribe an Email
```
Tool: smtp_unsubscribes_create
Input: {"emails": ["user@example.com"]}

Prevents future SMTP emails to this address.
```

### Re-subscribe
```
Tool: smtp_unsubscribes_resubscribe
Input: {"email": "user@example.com"}

Allows sending again — use only with explicit consent.
```

### Remove from Unsubscribe List
```
Tool: smtp_unsubscribes_delete
Input: {"emails": ["user@example.com"]}

Alternative to resubscribe.
```

## Infrastructure Configuration

### List Dedicated IPs
```
Tool: smtp_ips_list
Input: {}

Returns allocated IP addresses for SMTP sending.
```

### List SMTP Senders
```
Tool: smtp_senders_list
Input: {}

Returns configured SMTP sender email addresses.
```

### Add SMTP Sender
```
Tool: smtp_senders_create
Input: {"email": "transactional@acme.com"}
```

### List Sender Domains
```
Tool: smtp_senders_domains_list
Input: {}

Returns domains authorized for SMTP sending.
```

### Add Sender Domain
```
Tool: smtp_senders_domains_create
Input: {"domain": "acme.com"}

Adds domain — requires DNS verification (SPF/DKIM).
```

## Common Workflows

### Send Order Confirmation
```
1. smtp_unsubscribes_is_unsubscribed(email) -> Check not unsubscribed
2. smtp_emails_send(subject, from, to, html) -> Send email
3. smtp_emails_show(message_id) -> Verify delivery
```

### Monitor Delivery Health
```
1. smtp_bounces_total() -> Check bounce rate
2. smtp_bounces_list() -> Review recent bounces
3. smtp_unsubscribes_list() -> Review unsubscribes
4. email_blacklist_emails_add(emails) -> Blacklist hard bounces
```

### Set Up SMTP Infrastructure
```
1. smtp_senders_domains_create(domain) -> Add domain
2. (Configure SPF/DKIM in DNS)
3. smtp_senders_create(email) -> Add sender
4. smtp_senders_list() -> Verify setup
5. smtp_ips_list() -> Check dedicated IPs
```

## Best Practices

1. **Check unsubscribe status** before sending transactional emails
2. **Monitor bounces daily** and blacklist hard bounces
3. **Use dedicated IPs** for better deliverability reputation
4. **Set up SPF/DKIM** on sender domains for authentication
5. **Keep sender domains consistent** with your brand
6. **Re-subscribe only with explicit consent** to comply with regulations
7. **Use HTML templates** with plain text fallback for maximum compatibility
