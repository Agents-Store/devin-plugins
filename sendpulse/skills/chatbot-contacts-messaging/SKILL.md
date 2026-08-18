---
name: chatbot-contacts-messaging
description: Chatbot contact management, direct messaging across channels, contact variables, tags, and notes. Use when sending messages to contacts, managing contact data, or looking up subscribers.
---

# Chatbot Contacts & Messaging

This skill covers chatbot contact lookup, direct messaging on all channels, and contact metadata management.

## Available Tools

| Tool | Description |
|------|-------------|
| `chatbots_contacts_show` | Get contact details by ID |
| `chatbots_contacts_list_by_var_id` | Find contacts by variable ID |
| `chatbots_contacts_list_by_var_name` | Find contacts by variable name |
| `chatbots_chats_messages_list` | List messages from a specific chat |
| `chatbots_contacts_messages_t_send` | Send Telegram message to contact |
| `chatbots_contacts_messages_m_send` | Send Messenger message to contact |
| `chatbots_contacts_messages_wa_send` | Send WhatsApp message to contact |
| `chatbots_contacts_messages_lc_send` | Send Live Chat message to contact |
| `chatbots_contacts_messages_i_send` | Send Instagram message to contact |
| `chatbots_contacts_messages_v_send` | Send Viber message to contact |
| `chatbots_contacts_variables_set` | Set variable values on a contact |
| `chatbots_contacts_tags_set` | Assign tags to a contact |
| `chatbots_contacts_notes_list` | List operator notes for a contact |
| `chatbots_contacts_notes_create` | Create an operator note on a contact |

## Channel Suffix Reference

| Channel | Suffix | Message Tool |
|---------|--------|--------------|
| Telegram | `_t` | `chatbots_contacts_messages_t_send` |
| Messenger | `_m` | `chatbots_contacts_messages_m_send` |
| WhatsApp | `_wa` | `chatbots_contacts_messages_wa_send` |
| Instagram | `_i` | `chatbots_contacts_messages_i_send` |
| Viber | `_v` | `chatbots_contacts_messages_v_send` |
| Live Chat | `_lc` | `chatbots_contacts_messages_lc_send` |

## Contact Lookup

### Get Contact Details
```
Tool: chatbots_contacts_show
Input: {"contact_id": "<contact-id>"}

Returns contact info including name, channel, variables, tags, subscription status.
```

### Find Contacts by Variable
```
Tool: chatbots_contacts_list_by_var_name
Input: {"variable_name": "email", "variable_value": "user@example.com", "bot_id": "<bot-id>"}

Returns contacts matching the variable filter.
```

```
Tool: chatbots_contacts_list_by_var_id
Input: {"variable_id": "<var-id>", "variable_value": "VIP", "bot_id": "<bot-id>"}

Alternative lookup using variable ID instead of name.
```

## Sending Direct Messages

### Step 1: Identify Contact and Channel
```
Tool: chatbots_contacts_show
Input: {"contact_id": "<contact-id>"}

Check the contact's channel to select the correct sending tool.
```

### Step 2: Send Message

**Telegram:**
```
Tool: chatbots_contacts_messages_t_send
Input: {"contact_id": "<contact-id>", "messages": [{"type": "text", "text": "Hello!"}]}
```

**WhatsApp:**
```
Tool: chatbots_contacts_messages_wa_send
Input: {"contact_id": "<contact-id>", "messages": [{"type": "text", "text": "Hello!"}]}
```

**Instagram:**
```
Tool: chatbots_contacts_messages_i_send
Input: {"contact_id": "<contact-id>", "messages": [{"type": "text", "text": "Hello!"}]}
```

**Messenger:**
```
Tool: chatbots_contacts_messages_m_send
Input: {"contact_id": "<contact-id>", "messages": [{"type": "text", "text": "Hello!"}]}
```

**Viber:**
```
Tool: chatbots_contacts_messages_v_send
Input: {"contact_id": "<contact-id>", "messages": [{"type": "text", "text": "Hello!"}]}
```

**Live Chat:**
```
Tool: chatbots_contacts_messages_lc_send
Input: {"contact_id": "<contact-id>", "messages": [{"type": "text", "text": "Hello!"}]}
```

## Contact Metadata

### Set Variables
```
Tool: chatbots_contacts_variables_set
Input: {"contact_id": "<contact-id>", "variables": [{"name": "city", "value": "Kyiv"}]}

Assign or update custom variable values on a contact.
```

### Set Tags
```
Tool: chatbots_contacts_tags_set
Input: {"contact_id": "<contact-id>", "tags": ["VIP", "newsletter"]}

Assign tags for segmentation and filtering.
```

### List Notes
```
Tool: chatbots_contacts_notes_list
Input: {"contact_id": "<contact-id>"}

Returns operator notes with timestamps and content.
```

### Create Note
```
Tool: chatbots_contacts_notes_create
Input: {"contact_id": "<contact-id>", "text": "Called customer, interested in premium plan."}

Add an internal note visible to operators.
```

## Chat History

### List Chat Messages
```
Tool: chatbots_chats_messages_list
Input: {"chat_id": "<chat-id>"}

Returns message history for a specific chat conversation.
```

## Common Workflows

### Message a Known Contact
```
1. chatbots_contacts_show(contact_id) -> Verify contact and channel
2. chatbots_contacts_messages_{channel}_send(contact_id, messages) -> Send
```

### Find and Message by Email
```
1. chatbots_contacts_list_by_var_name(variable_name="email", variable_value="user@example.com", bot_id) -> Find contact
2. chatbots_contacts_messages_{channel}_send(contact_id, messages) -> Send
```

### Enrich Contact Data
```
1. chatbots_contacts_show(contact_id) -> View current data
2. chatbots_contacts_variables_set(contact_id, variables) -> Update fields
3. chatbots_contacts_tags_set(contact_id, tags) -> Add tags
4. chatbots_contacts_notes_create(contact_id, text) -> Add notes
```

## Best Practices

1. **Always verify the channel** via `contacts_show` before sending to avoid tool mismatch
2. **Use variable search** to find contacts by email, phone, or custom fields
3. **Tag contacts** after interactions for segmentation
4. **Add notes** for important interactions so other operators have context
5. **Check chat history** before messaging to maintain conversation continuity
