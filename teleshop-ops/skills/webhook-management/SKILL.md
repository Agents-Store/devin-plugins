---
name: webhook-management
description: Webhook CRUD, event types, testing, delivery logs, statistics, and toggle. Use when setting up webhooks for order/payment notifications or debugging webhook delivery.
---

# Webhook Management

This skill covers all webhook operations — creating webhooks for event notifications, testing delivery, viewing logs and statistics, and managing webhook lifecycle.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_webhooks` | List all configured webhooks |
| `get_webhook_events` | Get available webhook event types |
| `get_webhook` | Get single webhook details |
| `create_webhook` | Create a new webhook endpoint |
| `update_webhook` | Update webhook URL, events, or settings |
| `delete_webhook` | Delete a webhook |
| `test_webhook` | Send a test event to a webhook |
| `get_webhook_sample_payload` | Get sample payload for an event type |
| `get_webhook_logs` | Get webhook delivery logs |
| `get_webhook_secret` | Get webhook signing secret for verification |
| `get_webhook_stats` | Get webhook delivery statistics |
| `toggle_webhook` | Enable or disable a webhook |

## Discovering Available Events

```
Tool: get_webhook_events
Input: {}

Returns list of available event types (e.g., order.created, order.updated,
payment.completed, etc.)
```

## Creating Webhooks

### Create Webhook for Order Events
```
Tool: create_webhook
Input: {
  "url": "https://your-server.com/webhooks/teleshop",
  "events": ["order.created", "order.updated"]
}
```

### Step-by-Step Webhook Setup
```
1. get_webhook_events() -> See all available event types
2. create_webhook(url, events) -> Create webhook
3. get_webhook_secret(id) -> Get signing secret for payload verification
4. test_webhook(id) -> Send test event to verify delivery
5. get_webhook_logs(id) -> Check delivery status
```

## Managing Webhooks

### List All Webhooks
```
Tool: list_webhooks
Input: {}
```

### Get Webhook Details
```
Tool: get_webhook
Input: {"id": 1}
```

### Update Webhook
```
Tool: update_webhook
Input: {
  "id": 1,
  "url": "https://new-server.com/webhooks",
  "events": ["order.created", "order.updated", "payment.completed"]
}
```

### Enable/Disable Webhook
```
Tool: toggle_webhook
Input: {"id": 1}

Toggles between enabled and disabled state.
```

### Delete Webhook
```
Tool: delete_webhook
Input: {"id": 1}
```

## Testing and Debugging

### Send Test Event
```
Tool: test_webhook
Input: {"id": 1}

Sends a test payload to the webhook URL to verify it's receiving events correctly.
```

### Get Sample Payload
```
Tool: get_webhook_sample_payload
Input: {"event": "order.created"}

Returns example payload structure for the specified event type.
Useful for building webhook handlers before going live.
```

### View Delivery Logs
```
Tool: get_webhook_logs
Input: {"id": 1}

Returns delivery history with: timestamps, HTTP status codes,
response times, success/failure status.
```

### View Delivery Statistics
```
Tool: get_webhook_stats
Input: {"id": 1}

Returns aggregate stats: total deliveries, success rate,
average response time, failure count.
```

## Webhook Security

### Get Signing Secret
```
Tool: get_webhook_secret
Input: {"id": 1}

Returns the HMAC signing secret for this webhook.
Use this to verify incoming webhook payloads are authentic.
```

## Common Workflows

### Set Up Order Notification Webhook
```
1. get_webhook_events() -> List available events
2. create_webhook(url="https://...", events=["order.created"]) -> Create
3. get_webhook_secret(id) -> Save secret for verification
4. test_webhook(id) -> Verify delivery works
5. get_webhook_logs(id) -> Confirm test was received
```

### Debug Failing Webhook
```
1. list_webhooks() -> Find the webhook
2. get_webhook_stats(id) -> Check success/failure rates
3. get_webhook_logs(id) -> Find failed deliveries and error codes
4. test_webhook(id) -> Test with fresh request
5. If URL changed: update_webhook(id, url="https://new-url.com")
```

### Temporarily Disable Webhook
```
1. toggle_webhook(id) -> Disable
2. ... (do maintenance) ...
3. toggle_webhook(id) -> Re-enable
4. test_webhook(id) -> Verify it's working again
```

### Preview Webhook Payloads
```
1. get_webhook_events() -> List events
2. get_webhook_sample_payload(event="order.created") -> See payload format
3. get_webhook_sample_payload(event="payment.completed") -> See another
```

## Best Practices

1. **Always get signing secret** and verify payloads in your webhook handler
2. **Test webhook** after creation to ensure your endpoint is reachable
3. **Check logs** regularly for delivery failures
4. **Use toggle** instead of delete when temporarily disabling
5. **Subscribe only to needed events** to reduce unnecessary traffic
6. **Review sample payloads** before building webhook handlers
7. **Monitor stats** to catch delivery degradation early
