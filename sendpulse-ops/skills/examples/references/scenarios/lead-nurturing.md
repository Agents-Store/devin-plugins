# Lead Nurturing Scenarios

Multi-channel lead nurturing patterns using Sendpulse CRM, chatbots, and email.

## Scenario 1: Lead Capture & Qualification

**Trigger:** New lead comes in via chatbot or form.

### Step 1: Create CRM Contact
```
Tool: crm_contacts_create
Input: {
  "emails": [{"value": "lead@company.com"}],
  "name": "New Lead",
  "phones": [{"value": "+380501234567"}]
}
-> {id: "contact_lead"}
```

### Step 2: Add to Email List
```
Tool: email_addressbooks_emails_create
Input: {
  "id": "<leads-addressbook-id>",
  "emails": [{"email": "lead@company.com", "variables": {"name": "New Lead", "source": "chatbot", "stage": "new"}}]
}
```

### Step 3: Create Deal in Pipeline
```
Tool: crm_pipelines_list
-> Find "Sales Pipeline", first step "New Lead"

Tool: crm_deals_create
Input: {
  "name": "Lead - company.com",
  "pipeline_id": "<pipeline-id>",
  "step_id": "<new-lead-step>",
  "contact_id": "contact_lead"
}
-> {id: "deal_lead"}
```

### Step 4: Start Qualification Flow
```
Tool: chatbots_flows_run
Input: {"flow_id": "<qualification-flow>", "contact_id": "<chatbot-contact-id>"}
```

### Step 5: Tag as New Lead
```
Tool: chatbots_contacts_tags_set
Input: {"contact_id": "<chatbot-contact-id>", "tags": ["new-lead", "qualification"]}

Tool: email_tags_emails_pin
Input: {"tag_id": "<new-lead-tag>", "emails": ["lead@company.com"]}
```

## Scenario 2: Lead Qualification (After Chatbot Flow)

**Trigger:** Chatbot flow completes qualification questions.

### Step 1: Update Contact Variables
```
Tool: chatbots_contacts_variables_set
Input: {
  "contact_id": "<contact-id>",
  "variables": [
    {"name": "company_size", "value": "50-200"},
    {"name": "budget", "value": "10000-50000"},
    {"name": "timeline", "value": "Q2 2026"}
  ]
}
```

### Step 2: Progress Deal
```
Tool: crm_deals_pipelines_change
Input: {"id": "<deal-id>", "pipeline_id": "<pipeline-id>", "step_id": "<qualified-step>"}

Tool: crm_deals_update
Input: {"id": "<deal-id>", "amount": 25000}

Tool: crm_deals_comments_create
Input: {"id": "<deal-id>", "text": "Qualified via chatbot. Company 50-200 employees. Budget $10-50K. Timeline Q2 2026."}
```

### Step 3: Update Email Segment
```
Tool: email_addressbooks_emails_variables_update
Input: {"id": "<addressbook-id>", "email": "lead@company.com", "variables": {"stage": "qualified", "score": "high"}}
```

## Scenario 3: Email Nurture Sequence

**Trigger:** Lead is qualified but not ready to buy.

### Week 1: Educational Content
```
Tool: smtp_emails_send
Input: {
  "email": {
    "subject": "5 Ways to Improve Your Workflow",
    "from": {"name": "Acme", "email": "content@acme.com"},
    "to": [{"email": "lead@company.com"}],
    "html": "<h2>Improve Your Workflow</h2><p>Here are 5 proven strategies...</p>"
  }
}
```

### Week 2: Case Study
```
Tool: smtp_emails_send
Input: {
  "email": {
    "subject": "How BigCorp Saved 40% with Acme",
    "from": {"name": "Acme", "email": "content@acme.com"},
    "to": [{"email": "lead@company.com"}],
    "html": "<h2>Customer Success Story</h2><p>Learn how BigCorp transformed...</p>"
  }
}
```

### Week 3: Offer
```
Tool: chatbots_contacts_messages_t_send
Input: {
  "contact_id": "<contact-id>",
  "messages": [{"type": "text", "text": "Hi! Ready to explore how Acme can help your team? Book a free demo: acme.com/demo"}]
}

Tool: smtp_emails_send
Input: {
  "email": {
    "subject": "Ready for a Demo?",
    "from": {"name": "Acme Sales", "email": "sales@acme.com"},
    "to": [{"email": "lead@company.com"}],
    "html": "<h2>Let's Talk</h2><p>Book your personalized demo today...</p>"
  }
}
```

## Scenario 4: Conversion & Close

**Trigger:** Lead requests demo or shows buying signals.

### Step 1: Move Deal to Proposal Stage
```
Tool: crm_deals_pipelines_change
Input: {"id": "<deal-id>", "pipeline_id": "<pipeline-id>", "step_id": "<proposal-step>"}
```

### Step 2: Create Task for Sales Rep
```
Tool: crm_tasks_create
Input: {
  "name": "Prepare proposal for lead@company.com",
  "board_id": "<sales-board>",
  "step_id": "<todo-step>",
  "due_date": "2026-03-01"
}
```

### Step 3: Send Confirmation
```
Tool: chatbots_contacts_messages_t_send
Input: {
  "contact_id": "<contact-id>",
  "messages": [{"type": "text", "text": "Great news! Our team is preparing a personalized proposal for you. Expect it within 2 business days."}]
}
```

### Step 4: Add Notes
```
Tool: crm_deals_comments_create
Input: {"id": "<deal-id>", "text": "Lead requested demo. Moving to proposal stage. Assigned to sales team."}

Tool: chatbots_contacts_notes_create
Input: {"contact_id": "<chatbot-contact-id>", "text": "Demo requested. High intent. Proposal being prepared."}
```

## Lead Scoring with Tags

Use tags across channels to track lead engagement:

| Tag | Meaning | Where |
|-----|---------|-------|
| `new-lead` | Just captured | Chatbot + Email |
| `qualified` | Passed qualification | Chatbot + Email |
| `engaged` | Opened 3+ emails | Email |
| `demo-requested` | Requested demo | CRM + Chatbot |
| `proposal-sent` | Proposal delivered | CRM |
| `customer` | Closed deal | All channels |

## Key Tools for Lead Nurturing

| Stage | Primary Tools |
|-------|--------------|
| Capture | `crm_contacts_create`, `email_addressbooks_emails_create` |
| Qualify | `chatbots_flows_run`, `chatbots_contacts_variables_set` |
| Nurture | `smtp_emails_send`, `chatbots_contacts_messages_{channel}_send` |
| Convert | `crm_deals_pipelines_change`, `crm_tasks_create` |
| Track | `email_tags_emails_pin`, `chatbots_contacts_tags_set`, `crm_deals_comments_create` |
