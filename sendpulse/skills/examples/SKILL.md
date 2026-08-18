---
name: examples
description: MCP tool call patterns, multi-channel marketing workflow examples, and scenario references. Use when you need reference implementations for Sendpulse operations.
---

# Examples & Patterns Repository

This skill contains reusable examples and patterns for Sendpulse MCP operations.

## Available Examples

### MCP Tool Examples
| File | Description |
|------|-------------|
| @references/mcp/tool-patterns.md | Common MCP tool call patterns across all product areas |
| @references/mcp/workflow-examples.md | End-to-end workflow examples with full tool sequences |

### Marketing Scenarios
| File | Description |
|------|-------------|
| @references/scenarios/ecommerce-automation.md | E-commerce automation: cart abandonment, order confirmation, post-purchase |
| @references/scenarios/lead-nurturing.md | Lead nurturing: capture, qualify, nurture, convert |

## Quick Reference Patterns

### Discover Chatbot Environment
```
1. chatbots_account_show() -> Check plan
2. chatbots_bots_list() -> List all bots
3. chatbots_bots_statistics_show(bot_id) -> Bot stats
```

### Send Chatbot Campaign
```
1. chatbots_bots_list() -> Find bot by channel
2. chatbots_bots_campaigns_{channel}_send(bot_id, messages) -> Send
```

### Message a Contact
```
1. chatbots_contacts_show(contact_id) -> Verify channel
2. chatbots_contacts_messages_{channel}_send(contact_id, messages) -> Send
```

### Create CRM Pipeline with Deals
```
1. crm_pipelines_create(name) -> Get pipeline ID
2. crm_pipelines_steps_create(pipeline_id, name, position) -> Add stages
3. crm_contacts_create(emails, name) -> Create contact
4. crm_deals_create(name, pipeline_id, step_id, contact_id) -> Create deal
```

### Launch Email Campaign
```
1. email_balance_show() -> Check credits
2. email_addressbooks_list() -> Select list
3. email_addressbooks_cost(addressbook_id) -> Check cost
4. email_templates_list() -> Select template
5. email_senders_list() -> Select sender
6. email_campaigns_create(subject, addressbook_id, template_id, sender_email) -> Create
```

### Send Transactional Email
```
1. smtp_unsubscribes_is_unsubscribed(email) -> Check status
2. smtp_emails_send(subject, from, to, html) -> Send
3. smtp_emails_show(message_id) -> Verify delivery
```

### Manage Subscriber Lifecycle
```
1. email_addressbooks_emails_create(addressbook_id, emails) -> Add subscriber
2. email_addressbooks_emails_variables_update(addressbook_id, email, variables) -> Enrich data
3. email_tags_emails_pin(tag_id, emails) -> Tag for segmentation
4. email_addressbooks_emails_unsubscribe(addressbook_id, emails) -> Unsubscribe when requested
```

### CRM Contact to Deal
```
1. crm_contacts_list_by_email(email) -> Find contact
2. crm_contacts_show(id) -> View details
3. crm_deals_create(name, contact_id, pipeline_id, step_id) -> Create deal
4. crm_products_deals_add(deal_id, product_id, quantity, price) -> Add products
```

## Channel Suffixes

| Channel | Suffix |
|---------|--------|
| Telegram | `_t` |
| Messenger | `_m` |
| WhatsApp | `_wa` |
| Instagram | `_i` |
| Viber | `_v` |
| Live Chat | `_lc` |

## Conventions

- All examples are copy-paste ready for MCP tool calls
- Tool names omit the `mcp__sendpulse__` prefix for brevity
- Channel suffix must match the contact's actual channel
- Check balance/credits before sending campaigns
- Always verify senders before using in campaigns
