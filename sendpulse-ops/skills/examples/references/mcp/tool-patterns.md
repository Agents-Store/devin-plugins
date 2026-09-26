# MCP Tool Call Patterns

Common patterns for Sendpulse MCP tool calls organized by product area.

## Chatbot Patterns

### Pattern 1: Bot Discovery
```
Tool: chatbots_account_show
Input: {}
-> Returns: plan info, message limits

Tool: chatbots_bots_list
Input: {}
-> Returns: [{id, name, channel_type}, ...]

Tool: chatbots_bots_statistics_show
Input: {"bot_id": "bot_abc123"}
-> Returns: subscribers, messages_sent, engagement
```

### Pattern 2: Channel-Specific Campaign
```
# Telegram
Tool: chatbots_bots_campaigns_t_send
Input: {"bot_id": "bot_abc", "messages": [{"type": "text", "text": "Campaign message"}]}

# WhatsApp
Tool: chatbots_bots_campaigns_wa_send
Input: {"bot_id": "bot_def", "messages": [{"type": "text", "text": "Campaign message"}]}

# Instagram
Tool: chatbots_bots_campaigns_i_send
Input: {"bot_id": "bot_ghi", "messages": [{"type": "text", "text": "Campaign message"}]}

# Messenger
Tool: chatbots_bots_campaigns_m_send
Input: {"bot_id": "bot_jkl", "messages": [{"type": "text", "text": "Campaign message"}]}

# Viber
Tool: chatbots_bots_campaigns_v_send
Input: {"bot_id": "bot_mno", "messages": [{"type": "text", "text": "Campaign message"}]}
```

### Pattern 3: Contact Direct Message
```
# Step 1: Look up contact
Tool: chatbots_contacts_show
Input: {"contact_id": "contact_123"}
-> Check channel_type in response

# Step 2: Send on correct channel
Tool: chatbots_contacts_messages_{channel}_send
Input: {"contact_id": "contact_123", "messages": [{"type": "text", "text": "Hello!"}]}
```

### Pattern 4: Automation Flow Execution
```
Tool: chatbots_flows_list
Input: {"bot_id": "bot_abc"}
-> Returns: [{id, name, status}, ...]

Tool: chatbots_flows_run
Input: {"flow_id": "flow_xyz", "contact_id": "contact_123"}
-> Triggers the automation
```

## CRM Patterns

### Pattern 5: Contact Lifecycle
```
# Create
Tool: crm_contacts_create
Input: {"emails": [{"value": "user@example.com"}], "name": "John Doe", "phones": [{"value": "+380501234567"}]}
-> Returns: {id: "contact_abc"}

# Search
Tool: crm_contacts_list_by_email
Input: {"email": "user@example.com"}
-> Returns: contact record

# Update
Tool: crm_contacts_update
Input: {"id": "contact_abc", "name": "John D. Doe"}

# View deals
Tool: crm_contacts_deals_list
Input: {"id": "contact_abc"}
-> Returns: [{deal_id, name, amount, step}, ...]

# Add note
Tool: crm_contacts_comments_create
Input: {"id": "contact_abc", "text": "Called — interested in premium plan"}
```

### Pattern 6: Pipeline Setup
```
# Create pipeline
Tool: crm_pipelines_create
Input: {"name": "B2B Sales"}
-> Returns: {id: "pipeline_abc"}

# Add stages
Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipeline_abc", "name": "Lead", "position": 1}
-> Returns: {id: "step_1"}

Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipeline_abc", "name": "Qualified", "position": 2}
-> Returns: {id: "step_2"}

Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipeline_abc", "name": "Proposal", "position": 3}
Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipeline_abc", "name": "Negotiation", "position": 4}
Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipeline_abc", "name": "Closed Won", "position": 5}
```

### Pattern 7: Deal Management
```
# Create deal
Tool: crm_deals_create
Input: {"name": "Enterprise License", "pipeline_id": "pipeline_abc", "step_id": "step_1", "amount": 15000, "contact_id": "contact_abc"}
-> Returns: {id: "deal_xyz"}

# Progress deal
Tool: crm_deals_pipelines_change
Input: {"id": "deal_xyz", "pipeline_id": "pipeline_abc", "step_id": "step_2"}

# Add comment
Tool: crm_deals_comments_create
Input: {"id": "deal_xyz", "text": "Qualification call completed — budget confirmed"}

# Add product
Tool: crm_products_deals_add
Input: {"deal_id": "deal_xyz", "product_id": "prod_001", "quantity": 10, "price": 1500}
```

## Email Patterns

### Pattern 8: Full Campaign Launch
```
# Check balance
Tool: email_balance_show
Input: {}
-> Returns: {balance, currency}

# List addressbooks
Tool: email_addressbooks_list
Input: {"limit": 50}
-> Returns: [{id, name, subscriber_count}, ...]

# Check cost
Tool: email_addressbooks_cost
Input: {"id": "list_abc"}
-> Returns: {cost}

# List templates
Tool: email_templates_list
Input: {}
-> Returns: [{id, name}, ...]

# List senders
Tool: email_senders_list
Input: {}
-> Returns: [{email, name, status}, ...]

# Create campaign
Tool: email_campaigns_create
Input: {
  "name": "March Newsletter",
  "subject": "Your monthly update",
  "sender_email": "news@acme.com",
  "sender_name": "Acme Corp",
  "addressbook_id": "list_abc",
  "template_id": "tmpl_xyz"
}
-> Returns: {id: "campaign_123"}
```

## SMTP Patterns

### Pattern 9: Transactional Email
```
# Check not unsubscribed
Tool: smtp_unsubscribes_is_unsubscribed
Input: {"email": "customer@example.com"}
-> Returns: {is_unsubscribed: false}

# Send
Tool: smtp_emails_send
Input: {
  "email": {
    "subject": "Order #12345 Confirmed",
    "from": {"name": "Acme Store", "email": "orders@acme.com"},
    "to": [{"name": "Customer", "email": "customer@example.com"}],
    "html": "<h1>Order Confirmed</h1><p>Thank you for your purchase!</p>"
  }
}
-> Returns: {id: "msg_abc"}

# Verify
Tool: smtp_emails_show
Input: {"id": "msg_abc"}
-> Returns: {status, opened, clicked}
```

### Pattern 10: Bounce & Unsubscribe Monitoring
```
Tool: smtp_bounces_total
Input: {}
-> Returns: {total}

Tool: smtp_bounces_list
Input: {}
-> Returns: [{email, type, reason, date}, ...]

Tool: smtp_unsubscribes_list
Input: {"limit": 100}
-> Returns: [{email, date}, ...]
```
