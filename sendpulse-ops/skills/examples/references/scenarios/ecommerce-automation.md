# E-Commerce Automation Scenarios

Multi-channel marketing automation patterns for e-commerce businesses using Sendpulse.

## Scenario 1: Cart Abandonment Recovery

**Trigger:** Customer adds items to cart but doesn't complete purchase.

### Step 1: Send Chatbot Reminder (1 hour after abandonment)
```
Tool: chatbots_contacts_list_by_var_name
Input: {"variable_name": "email", "variable_value": "customer@example.com", "bot_id": "<bot-id>"}

Tool: chatbots_contacts_messages_t_send
Input: {
  "contact_id": "<contact-id>",
  "messages": [{"type": "text", "text": "Hey! You left some items in your cart. Complete your order now and get 10% off!"}]
}
```

### Step 2: Send Email Reminder (24 hours after abandonment)
```
Tool: smtp_emails_send
Input: {
  "email": {
    "subject": "You forgot something in your cart!",
    "from": {"name": "Acme Store", "email": "cart@acme.com"},
    "to": [{"email": "customer@example.com"}],
    "html": "<h2>Your cart is waiting</h2><p>Complete your purchase and save 10%...</p>"
  }
}
```

### Step 3: Update CRM
```
Tool: crm_contacts_comments_create
Input: {"id": "<contact-id>", "text": "Cart abandonment flow triggered. Items: Widget Pro x2."}
```

## Scenario 2: Order Confirmation + Upsell

**Trigger:** Customer completes purchase.

### Step 1: Send Order Confirmation (SMTP)
```
Tool: smtp_emails_send
Input: {
  "email": {
    "subject": "Order #12345 Confirmed!",
    "from": {"name": "Acme Store", "email": "orders@acme.com"},
    "to": [{"email": "customer@example.com"}],
    "html": "<h1>Thank you!</h1><p>Order #12345 has been confirmed...</p>"
  }
}
```

### Step 2: Create/Update CRM Deal
```
Tool: crm_deals_create
Input: {
  "name": "Order #12345",
  "pipeline_id": "<ecommerce-pipeline>",
  "step_id": "<confirmed-step>",
  "amount": 99.98,
  "contact_id": "<contact-id>"
}

Tool: crm_products_deals_add
Input: {"deal_id": "<deal-id>", "product_id": "<product-id>", "quantity": 2, "price": 49.99}
```

### Step 3: Tag Customer
```
Tool: email_tags_emails_pin
Input: {"tag_id": "<purchased-tag>", "emails": ["customer@example.com"]}

Tool: chatbots_contacts_tags_set
Input: {"contact_id": "<chat-contact-id>", "tags": ["customer", "purchased"]}
```

## Scenario 3: Post-Purchase Review Request

**Trigger:** 7 days after delivery.

### Chatbot Message
```
Tool: chatbots_contacts_messages_t_send
Input: {
  "contact_id": "<contact-id>",
  "messages": [{"type": "text", "text": "Hi! How are you enjoying your Widget Pro? We'd love to hear your feedback. Leave a review and get 15% off your next order!"}]
}
```

### Update CRM
```
Tool: crm_contacts_comments_create
Input: {"id": "<contact-id>", "text": "Review request sent via Telegram. 7 days post-delivery."}
```

## Scenario 4: Win-Back Campaign

**Trigger:** Customer hasn't purchased in 90 days.

### Step 1: Identify Inactive Customers
```
Tool: email_addressbooks_variables_emails_list
Input: {"id": "<addressbook-id>", "variable_name": "last_purchase_days", "variable_value": "90+"}
```

### Step 2: Send Email Campaign
```
Tool: email_campaigns_create
Input: {
  "name": "Win-Back - Q1 2026",
  "subject": "We miss you! Here's 20% off",
  "sender_email": "offers@acme.com",
  "addressbook_id": "<inactive-list-id>",
  "template_id": "<winback-template>"
}
```

### Step 3: Send Chatbot Message to Those on Telegram
```
Tool: chatbots_bots_campaigns_t_send
Input: {
  "bot_id": "<bot-id>",
  "messages": [{"type": "text", "text": "It's been a while! Use code COMEBACK20 for 20% off your next order."}]
}
```

## Key Tools for E-Commerce

| Use Case | Primary Tools |
|----------|--------------|
| Transactional emails | `smtp_emails_send` |
| Chatbot notifications | `chatbots_contacts_messages_{channel}_send` |
| Customer tagging | `email_tags_emails_pin`, `chatbots_contacts_tags_set` |
| Deal tracking | `crm_deals_create`, `crm_products_deals_add` |
| Segmentation | `email_addressbooks_variables_emails_list` |
| Campaigns | `email_campaigns_create`, `chatbots_bots_campaigns_{channel}_send` |
