---
name: broadcast-pattern
description: This skill should be used when setting up real-time financial event notifications, configuring event subscribers, understanding event payload formats, or implementing the broadcast pub/sub system. Relevant for queries like "notify me when balance changes", "set up transaction alerts", "how does the event system work", or "configure WebSocket updates". Use this skill whenever the user asks about real-time updates, event notifications, webhooks, or any form of live data streaming from bank accounts.
---

# Broadcast Pattern Architecture

## Why Broadcast Matters

Users typically have accounts across multiple banks (Monobank personal card, PrivatBank business account, etc.) and expect a unified, real-time view. Without a broadcast system, each component — dashboard, budget tracker, notification system — would independently poll each bank, creating redundant API calls that hit rate limits. The broadcast pattern solves this: one sync fetches the data, and events fan out to every subscriber that needs it.

## How It Works

A single publisher emits financial events during sync operations. Multiple subscribers receive events based on their subscription filters. Think of it as a newsroom wire: one reporter files a story, every desk that subscribed to that beat gets it.

For the complete BroadcastHub implementation code (WebSocket server, polling endpoints, file writer), read `references/implementation.md`.

## Event Types Reference

Nine event types flow through the system, grouped by domain.

### Core Events (Account & Transaction)

These fire during every sync cycle. They are the backbone — most subscribers care about at least one of these.

| Event | Trigger | Latency Target | Typical subscriber |
|-------|---------|---------------|---------------------|
| `balance_updated` | Bank balance sync completes for an account | <5s | Dashboard widget, net-worth tracker |
| `transaction_added` | New transaction detected during sync | <5s | Budget monitor, categorization engine |
| `budget_alert` | Spending crosses a threshold (50/75/90/100%) | <1s after transaction_added | Notification system, user-facing alerts |
| `sync_complete` | All accounts finished syncing | Immediate | Dashboard "last updated" indicator |

### Payment Events

| Event | Trigger | Latency Target |
|-------|---------|---------------|
| `payment_prepared` | Payment created and sent for mobile signing | <2s |
| `payment_completed` | Payment successfully processed by bank | On status change |

### Salary & Payslip Events

| Event | Trigger | Latency Target |
|-------|---------|---------------|
| `salary_registry_created` | Salary registry submitted to bank | <2s |
| `salary_registry_status_changed` | Registry processing status updated | On status change |
| `payslips_sent` | Payslips distributed to employees' mobile apps | <5s |

## Event Payload Structure

Every event follows a common base format. This consistency allows subscribers to parse any event generically, then branch on `type` for payload-specific logic.

```typescript
interface BroadcastEvent {
  id: string;              // UUID v4 — for deduplication
  type: EventType;         // Determines payload shape
  timestamp: string;       // ISO 8601 — when the event was emitted
  accountId?: string;      // Source account (absent for sync_complete)
  payload: Record<string, unknown>;
}
```

### Key payload examples

**balance_updated** — includes delta so subscribers can show "+₴50" without calculating it themselves:

```json
{
  "id": "evt_abc123",
  "type": "balance_updated",
  "timestamp": "2026-03-23T14:30:00Z",
  "accountId": "acc_mono_1234",
  "payload": {
    "institutionName": "Monobank",
    "accountName": "Чорна картка ****1234",
    "currentBalance": 15432.10,
    "availableBalance": 15200.00,
    "currency": "UAH",
    "previousBalance": 15382.10,
    "delta": 50.00
  }
}
```

**transaction_added** — pre-categorized so subscribers do not need to re-categorize:

```json
{
  "id": "evt_def456",
  "type": "transaction_added",
  "timestamp": "2026-03-23T14:30:01Z",
  "accountId": "acc_mono_1234",
  "payload": {
    "transactionId": "txn_789",
    "amount": -345.67,
    "category": "Groceries",
    "subcategory": "Supermarkets",
    "merchantName": "Сільпо",
    "date": "2026-03-22",
    "pending": false,
    "location": { "city": "Kyiv", "region": "Kyiv" }
  }
}
```

**budget_alert** — includes remaining budget so the user sees actionable numbers:

```json
{
  "id": "evt_ghi789",
  "type": "budget_alert",
  "timestamp": "2026-03-23T14:30:02Z",
  "accountId": null,
  "payload": {
    "category": "Dining",
    "budgetAmount": 500.00,
    "spentAmount": 475.67,
    "percentUsed": 95.1,
    "threshold": 90,
    "period": "monthly",
    "periodStart": "2026-03-01",
    "periodEnd": "2026-03-31",
    "remainingBudget": 24.33
  }
}
```

**sync_complete** — summarizes the entire sync so subscribers know what changed:

```json
{
  "id": "evt_jkl012",
  "type": "sync_complete",
  "timestamp": "2026-03-23T14:30:05Z",
  "payload": {
    "accountsSynced": ["acc_mono_1234", "acc_mono_5678", "acc_privat_3456"],
    "failedAccounts": [],
    "totalBalanceUAH": 120782.40,
    "transactionsAdded": 12,
    "syncDurationMs": 4200,
    "nextSyncScheduled": "2026-03-23T15:30:00Z"
  }
}
```

## Subscriber Registration

Subscribers declare which events and accounts they care about. Filtering happens at the publisher, so subscribers only receive relevant events — reducing noise and processing overhead.

```typescript
interface Subscription {
  subscriberId: string;
  eventTypes: EventType[];       // Which events to receive
  accountFilter?: string[];      // Empty = all accounts
  callbackType: "websocket" | "polling" | "file";
  callbackTarget: string;
}
```

**Example — a dashboard widget that only cares about balance changes on one account:**

```javascript
broadcaster.subscribe({
  subscriberId: "dashboard-balance-widget",
  eventTypes: ["balance_updated", "sync_complete"],
  accountFilter: ["acc_mono_1234"],
  callbackType: "websocket",
  callbackTarget: "ws://localhost:8765"
});
```

Deregister with `broadcaster.unsubscribe("dashboard-balance-widget")`.

### Filtering logic

```javascript
function shouldDeliver(event, subscription) {
  if (!subscription.eventTypes.includes(event.type)) return false;
  if (subscription.accountFilter?.length > 0 && event.accountId) {
    return subscription.accountFilter.includes(event.accountId);
  }
  return true;
}
```

## Delivery Mechanisms

Three mechanisms exist, each for a different use case:

- **WebSocket** (preferred) — <5s latency, ideal for live dashboards
- **HTTP polling** (fallback) — 5s intervals, for environments where WebSocket is unavailable
- **File-based JSONL** — for CLI consumers and audit logs, append-only

For the complete implementation code for all three mechanisms, read `references/implementation.md`.

## Event Ordering and Delivery Guarantees

- Events are emitted in order within a single sync cycle
- Each event has a monotonically increasing sequence number within a session
- **At-most-once delivery** for WebSocket (no ack/retry) — acceptable because balance updates self-correct on next sync
- **At-least-once delivery** for file-based (append is atomic on most filesystems) — subscribers should deduplicate by event `id`
- Dead letter handling: events for disconnected WebSocket subscribers are queued for 5 minutes, then dropped
- File-based events persist until manually rotated

## Rate Limiting During Bulk Sync

During initial connect or historical backfill (e.g., 90 days of transactions), hundreds of events can fire at once. Batching prevents overwhelming subscribers and downstream systems.

- Maximum 100 events per second
- Buffer events and flush every 100ms
- `sync_complete` fires only after all batched events are delivered
