---
name: chatbot-management
description: Chatbot bots, statistics, tags, campaigns, flows, and dialogs. Use when managing bots, sending chatbot campaigns, running automation flows, or viewing bot statistics.
---

# Chatbot Management

This skill covers chatbot bot management, campaign sending across channels, automation flows, and dialog tracking.

## Available Tools

| Tool | Description |
|------|-------------|
| `chatbots_account_show` | Get chatbot account plan and message limits |
| `chatbots_bots_list` | List all connected bots across channels |
| `chatbots_bots_statistics_show` | Get statistics for a specific bot |
| `chatbots_bots_tags_list` | List tags created for a bot |
| `chatbots_bots_campaigns_t_send` | Send campaign via Telegram |
| `chatbots_bots_campaigns_m_send` | Send campaign via Messenger |
| `chatbots_bots_campaigns_wa_send` | Send campaign via WhatsApp |
| `chatbots_bots_campaigns_i_send` | Send campaign via Instagram |
| `chatbots_bots_campaigns_v_send` | Send campaign via Viber |
| `chatbots_dialogs_list` | List dialogs from all channels |
| `chatbots_flows_list` | List automation flows for a bot |
| `chatbots_flows_run` | Run a flow for a specific contact |

## Channel Suffix Reference

| Channel | Suffix | Campaign Tool |
|---------|--------|---------------|
| Telegram | `_t` | `chatbots_bots_campaigns_t_send` |
| Messenger | `_m` | `chatbots_bots_campaigns_m_send` |
| WhatsApp | `_wa` | `chatbots_bots_campaigns_wa_send` |
| Instagram | `_i` | `chatbots_bots_campaigns_i_send` |
| Viber | `_v` | `chatbots_bots_campaigns_v_send` |

## Viewing Account & Bots

### Check Account Plan
```
Tool: chatbots_account_show
Input: {}

Returns account pricing plan, message limits, and usage.
```

### List All Bots
```
Tool: chatbots_bots_list
Input: {}

Returns list of all connected bots with their IDs, names, and channels.
```

### Get Bot Statistics
```
Tool: chatbots_bots_statistics_show
Input: {"bot_id": "<bot-id>"}

Returns subscriber count, message stats, and engagement metrics.
```

### List Bot Tags
```
Tool: chatbots_bots_tags_list
Input: {"bot_id": "<bot-id>"}

Returns tags available for segmenting bot subscribers.
```

## Sending Campaigns

### Step 1: Identify Bot and Channel
```
Tool: chatbots_bots_list
Input: {}

Find the bot ID for the target channel.
```

### Step 2: Send Campaign
Select the correct tool based on channel:

**Telegram:**
```
Tool: chatbots_bots_campaigns_t_send
Input: {"bot_id": "<bot-id>", "messages": [...]}
```

**WhatsApp:**
```
Tool: chatbots_bots_campaigns_wa_send
Input: {"bot_id": "<bot-id>", "messages": [...]}
```

**Instagram:**
```
Tool: chatbots_bots_campaigns_i_send
Input: {"bot_id": "<bot-id>", "messages": [...]}
```

**Messenger:**
```
Tool: chatbots_bots_campaigns_m_send
Input: {"bot_id": "<bot-id>", "messages": [...]}
```

**Viber:**
```
Tool: chatbots_bots_campaigns_v_send
Input: {"bot_id": "<bot-id>", "messages": [...]}
```

## Automation Flows

### List Flows
```
Tool: chatbots_flows_list
Input: {"bot_id": "<bot-id>"}

Returns list of flows with IDs, names, and status.
```

### Run a Flow for a Contact
```
Tool: chatbots_flows_run
Input: {"flow_id": "<flow-id>", "contact_id": "<contact-id>"}

Triggers the automation flow for the specified contact.
```

## Dialogs

### List All Dialogs
```
Tool: chatbots_dialogs_list
Input: {}

Returns dialogs across all channels with status and last message.
```

## Common Workflows

### Discover Bots and Stats
```
1. chatbots_account_show() -> Check plan limits
2. chatbots_bots_list() -> List all bots
3. chatbots_bots_statistics_show(bot_id) -> Get stats per bot
```

### Send Multi-Channel Campaign
```
1. chatbots_bots_list() -> Identify bots by channel
2. chatbots_bots_campaigns_{channel}_send(bot_id, messages) -> Send
3. chatbots_bots_statistics_show(bot_id) -> Verify delivery
```

### Trigger Automation Flow
```
1. chatbots_flows_list(bot_id) -> Find target flow
2. chatbots_flows_run(flow_id, contact_id) -> Execute
```

## Best Practices

1. **Always list bots first** to confirm bot IDs before sending
2. **Match channel suffix** to the bot's actual channel type
3. **Check account limits** before sending large campaigns
4. **Use flows** for complex multi-step automations instead of direct messages
5. **Review statistics** after campaigns to measure effectiveness
