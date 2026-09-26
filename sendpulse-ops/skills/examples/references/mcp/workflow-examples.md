# End-to-End Workflow Examples

Complete multi-step workflows demonstrating real-world Sendpulse operations.

## Example 1: Set Up Multi-Channel Chatbot Environment

**Goal:** Discover bots, check stats, and send a test campaign on Telegram.

```
Step 1: Check account
Tool: chatbots_account_show
-> Verify plan supports Telegram campaigns

Step 2: List bots
Tool: chatbots_bots_list
-> Find Telegram bot: {id: "bot_tg_001", name: "My Store Bot", channel: "telegram"}

Step 3: Check statistics
Tool: chatbots_bots_statistics_show
Input: {"bot_id": "bot_tg_001"}
-> 5,230 subscribers, 89% delivery rate

Step 4: List available tags
Tool: chatbots_bots_tags_list
Input: {"bot_id": "bot_tg_001"}
-> ["active", "VIP", "newsletter"]

Step 5: Send test campaign
Tool: chatbots_bots_campaigns_t_send
Input: {
  "bot_id": "bot_tg_001",
  "messages": [{"type": "text", "text": "New arrivals are here! Check out our latest collection."}]
}
-> Campaign sent to 5,230 subscribers
```

## Example 2: Create Complete Sales Pipeline with First Deal

**Goal:** Set up a B2B sales pipeline and create the first deal with a contact.

```
Step 1: Create pipeline
Tool: crm_pipelines_create
Input: {"name": "B2B Enterprise Sales"}
-> {id: "pipe_001"}

Step 2: Add stages
Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipe_001", "name": "Lead", "position": 1}
-> {id: "step_lead"}

Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipe_001", "name": "Discovery", "position": 2}
-> {id: "step_disc"}

Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipe_001", "name": "Proposal", "position": 3}
-> {id: "step_prop"}

Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipe_001", "name": "Negotiation", "position": 4}
Tool: crm_pipelines_steps_create
Input: {"pipeline_id": "pipe_001", "name": "Closed Won", "position": 5}

Step 3: Create contact
Tool: crm_contacts_create
Input: {"emails": [{"value": "cto@bigcorp.com"}], "name": "Jane Smith", "phones": [{"value": "+1555123456"}]}
-> {id: "contact_jane"}

Step 4: Create deal
Tool: crm_deals_create
Input: {
  "name": "BigCorp Enterprise License",
  "pipeline_id": "pipe_001",
  "step_id": "step_lead",
  "amount": 50000,
  "currency": "USD",
  "contact_id": "contact_jane"
}
-> {id: "deal_bigcorp"}

Step 5: Add products
Tool: crm_products_list
-> [{id: "prod_ent", name: "Enterprise License", price: 25000}]

Tool: crm_products_deals_add
Input: {"deal_id": "deal_bigcorp", "product_id": "prod_ent", "quantity": 2, "price": 25000}

Step 6: Add initial note
Tool: crm_deals_comments_create
Input: {"id": "deal_bigcorp", "text": "Initial contact via LinkedIn. CTO interested in Q2 deployment."}
```

## Example 3: Launch Email Newsletter Campaign

**Goal:** Create an addressbook, import subscribers, and launch a newsletter campaign.

```
Step 1: Check balance
Tool: email_balance_show
-> {balance: 50000, currency: "emails"}

Step 2: Create addressbook
Tool: email_addressbooks_create
Input: {"name": "Weekly Newsletter - Tech"}
-> {id: "list_tech"}

Step 3: Add subscribers
Tool: email_addressbooks_emails_create
Input: {
  "id": "list_tech",
  "emails": [
    {"email": "user1@example.com", "variables": {"name": "Alice", "role": "Developer"}},
    {"email": "user2@example.com", "variables": {"name": "Bob", "role": "Designer"}},
    {"email": "user3@example.com", "variables": {"name": "Carol", "role": "Manager"}}
  ]
}

Step 4: Verify count
Tool: email_addressbooks_emails_total
Input: {"id": "list_tech"}
-> {total: 3}

Step 5: Check cost
Tool: email_addressbooks_cost
Input: {"id": "list_tech"}
-> {cost: 3}

Step 6: Select template
Tool: email_templates_list
-> [{id: "tmpl_newsletter", name: "Weekly Newsletter"}, ...]

Step 7: Verify sender
Tool: email_senders_list
-> [{email: "newsletter@acme.com", name: "Acme Newsletter", status: "active"}]

Step 8: Create campaign
Tool: email_campaigns_create
Input: {
  "name": "Tech Newsletter - Week 9",
  "subject": "This Week in Tech: AI, Cloud, and More",
  "sender_email": "newsletter@acme.com",
  "sender_name": "Acme Newsletter",
  "addressbook_id": "list_tech",
  "template_id": "tmpl_newsletter",
  "send_date": "2026-03-02T09:00:00"
}
-> {id: "campaign_w9"}
```

## Example 4: Send Order Confirmation (Transactional)

**Goal:** Send an order confirmation email via SMTP with delivery verification.

```
Step 1: Check unsubscribe status
Tool: smtp_unsubscribes_is_unsubscribed
Input: {"email": "customer@example.com"}
-> {is_unsubscribed: false}

Step 2: Send confirmation email
Tool: smtp_emails_send
Input: {
  "email": {
    "subject": "Order #ORD-2026-0042 Confirmed",
    "from": {"name": "Acme Store", "email": "orders@acme.com"},
    "to": [{"name": "John Customer", "email": "customer@example.com"}],
    "html": "<h1>Order Confirmed!</h1><p>Thank you for your order #ORD-2026-0042.</p><ul><li>Product: Widget Pro x2 - $49.98</li><li>Shipping: Free</li><li>Total: $49.98</li></ul><p>Expected delivery: March 5, 2026</p>"
  }
}
-> {id: "smtp_msg_042"}

Step 3: Verify delivery
Tool: smtp_emails_show
Input: {"id": "smtp_msg_042"}
-> {status: "delivered", sent_at: "2026-02-25T14:30:00"}
```

## Example 5: Cross-Platform Contact Enrichment

**Goal:** Find a CRM contact, check their chatbot data, tag them, and add notes.

```
Step 1: Find CRM contact
Tool: crm_contacts_list_by_email
Input: {"email": "vip@bigcorp.com"}
-> {id: "contact_vip", name: "VIP Customer", emails: [...]}

Step 2: View deals
Tool: crm_contacts_deals_list
Input: {"id": "contact_vip"}
-> [{name: "Enterprise License", amount: 50000, step: "Negotiation"}]

Step 3: Find chatbot contact
Tool: chatbots_contacts_list_by_var_name
Input: {"variable_name": "email", "variable_value": "vip@bigcorp.com", "bot_id": "bot_tg_001"}
-> {contact_id: "chat_contact_vip"}

Step 4: Set VIP tag on chatbot contact
Tool: chatbots_contacts_tags_set
Input: {"contact_id": "chat_contact_vip", "tags": ["VIP", "enterprise"]}

Step 5: Set variables
Tool: chatbots_contacts_variables_set
Input: {"contact_id": "chat_contact_vip", "variables": [{"name": "deal_value", "value": "50000"}]}

Step 6: Add CRM note
Tool: crm_contacts_comments_create
Input: {"id": "contact_vip", "text": "Tagged as VIP in Telegram bot. Active in negotiation for $50K deal."}

Step 7: Tag email
Tool: email_tags_emails_pin
Input: {"tag_id": "tag_vip", "emails": ["vip@bigcorp.com"]}
```
