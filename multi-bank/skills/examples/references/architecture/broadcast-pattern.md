# Broadcast Pattern — Detailed Architecture

## Overview

The broadcast pattern implements a one-to-many event distribution system where a single publisher (the Bank Sync Module) emits financial events to multiple subscribers (UI widgets, monitoring components, log consumers).

## Sequence Diagram: Balance Sync

```
User          BankSync       BankMCP       Publisher      Subscriber1    Subscriber2
  │               │              │             │               │              │
  │  /sync        │              │             │               │              │
  │──────────────▶│              │             │               │              │
  │               │  GET balance │             │               │              │
  │               │─────────────▶│             │               │              │
  │               │  { balance } │             │               │              │
  │               │◀─────────────│             │               │              │
  │               │              │  emit(      │               │              │
  │               │  balance_updated)          │               │              │
  │               │─────────────────────────▶│               │              │
  │               │              │             │  deliver()    │              │
  │               │              │             │──────────────▶│              │
  │               │              │             │  deliver()    │              │
  │               │              │             │──────────────────────────────▶│
  │               │              │             │               │              │
  │               │  GET txns    │             │               │              │
  │               │─────────────▶│             │               │              │
  │               │  [txns]      │             │               │              │
  │               │◀─────────────│             │               │              │
  │               │              │  emit(      │               │              │
  │               │  transaction_added) ×N     │               │              │
  │               │─────────────────────────▶│               │              │
  │               │              │             │  (filtered)   │              │
  │               │              │             │──────────────▶│              │
  │               │              │  emit(      │               │              │
  │               │  sync_complete)            │               │              │
  │               │─────────────────────────▶│               │              │
  │               │              │             │──────────────▶│              │
  │               │              │             │──────────────────────────────▶│
  │  "Sync done"  │              │             │               │              │
  │◀──────────────│              │             │               │              │
```

## Sequence Diagram: Budget Alert Flow

```
BankMCP       BankSync      Publisher     BudgetMonitor    AlertWidget
   │              │              │              │               │
   │  new txn     │              │              │               │
   │─────────────▶│              │              │               │
   │              │  emit(       │              │               │
   │              │  transaction_added)         │               │
   │              │─────────────▶│              │               │
   │              │              │  deliver()   │               │
   │              │              │─────────────▶│               │
   │              │              │              │  check budget │
   │              │              │              │  threshold    │
   │              │              │              │  crossed!     │
   │              │              │              │               │
   │              │              │  emit(       │               │
   │              │              │◀─────────────│               │
   │              │              │  budget_alert)               │
   │              │              │              │               │
   │              │              │  deliver()   │               │
   │              │              │─────────────────────────────▶│
   │              │              │              │               │  Show alert
```

## Publisher Implementation (Full)

```javascript
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const os = require('os');

class BroadcastHub {
  constructor(options = {}) {
    this.subscriptions = new Map();
    this.eventLog = [];
    this.maxLogSize = options.maxLogSize || 10000;
    this.eventsFile = path.join(os.homedir(), '.multi-bank', 'events.jsonl');
    this.deadLetterQueue = new Map(); // subscriberId -> events[]
    this.deadLetterTTL = options.deadLetterTTL || 5 * 60 * 1000; // 5 min
  }

  subscribe(subscription) {
    this.subscriptions.set(subscription.subscriberId, {
      ...subscription,
      subscribedAt: new Date().toISOString(),
    });

    // Deliver any queued dead letters
    const queued = this.deadLetterQueue.get(subscription.subscriberId);
    if (queued) {
      queued.forEach(event => this.deliver(subscription, event));
      this.deadLetterQueue.delete(subscription.subscriberId);
    }

    return { success: true, subscriberId: subscription.subscriberId };
  }

  unsubscribe(subscriberId) {
    const existed = this.subscriptions.delete(subscriberId);
    this.deadLetterQueue.delete(subscriberId);
    return { success: existed };
  }

  emit(event) {
    // Assign ID and timestamp if not set
    event.id = event.id || `evt_${crypto.randomUUID()}`;
    event.timestamp = event.timestamp || new Date().toISOString();

    // Add to in-memory log (bounded)
    this.eventLog.push(event);
    if (this.eventLog.length > this.maxLogSize) {
      this.eventLog = this.eventLog.slice(-this.maxLogSize);
    }

    // Append to file-based log
    this.appendToFile(event);

    // Deliver to matching subscribers
    let delivered = 0;
    for (const [id, sub] of this.subscriptions) {
      if (this.shouldDeliver(event, sub)) {
        try {
          this.deliver(sub, event);
          delivered++;
        } catch (err) {
          // Queue to dead letter
          this.queueDeadLetter(id, event);
        }
      }
    }

    return { eventId: event.id, deliveredTo: delivered };
  }

  shouldDeliver(event, sub) {
    if (!sub.eventTypes.includes(event.type)) return false;
    if (sub.accountFilter?.length > 0 && event.accountId) {
      return sub.accountFilter.includes(event.accountId);
    }
    return true;
  }

  deliver(sub, event) {
    switch (sub.callbackType) {
      case 'websocket':
        if (sub.ws?.readyState === 1) { // OPEN
          sub.ws.send(JSON.stringify(event));
        } else {
          throw new Error('WebSocket not open');
        }
        break;
      case 'file':
        // Already appended to events.jsonl
        break;
      case 'polling':
        // Stored in eventLog, retrieved via getEventsSince()
        break;
    }
  }

  queueDeadLetter(subscriberId, event) {
    if (!this.deadLetterQueue.has(subscriberId)) {
      this.deadLetterQueue.set(subscriberId, []);
    }
    this.deadLetterQueue.get(subscriberId).push(event);

    // Clean up old dead letters
    setTimeout(() => {
      const queue = this.deadLetterQueue.get(subscriberId);
      if (queue) {
        const idx = queue.indexOf(event);
        if (idx !== -1) queue.splice(idx, 1);
        if (queue.length === 0) this.deadLetterQueue.delete(subscriberId);
      }
    }, this.deadLetterTTL);
  }

  getEventsSince(timestamp) {
    const since = new Date(timestamp);
    return this.eventLog.filter(e => new Date(e.timestamp) > since);
  }

  getStatus() {
    return {
      subscribers: this.subscriptions.size,
      subscriptions: [...this.subscriptions.values()].map(s => ({
        id: s.subscriberId,
        eventTypes: s.eventTypes,
        callbackType: s.callbackType,
        subscribedAt: s.subscribedAt,
      })),
      eventLogSize: this.eventLog.length,
      deadLetterQueueSize: this.deadLetterQueue.size,
    };
  }

  appendToFile(event) {
    try {
      const dir = path.dirname(this.eventsFile);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.appendFileSync(this.eventsFile, JSON.stringify(event) + '\n');
    } catch (err) {
      console.error('Failed to append event to file:', err.message);
    }
  }
}

module.exports = { BroadcastHub };
```

## WebSocket Server Setup

```javascript
const WebSocket = require('ws');
const { BroadcastHub } = require('./broadcast-hub');

const hub = new BroadcastHub();
const wss = new WebSocket.Server({ port: 8765 });

wss.on('connection', (ws) => {
  console.log('New subscriber connected');

  ws.on('message', (data) => {
    const msg = JSON.parse(data);

    switch (msg.action) {
      case 'subscribe':
        hub.subscribe({ ...msg.subscription, ws, callbackType: 'websocket' });
        ws.send(JSON.stringify({ action: 'subscribed', subscriberId: msg.subscription.subscriberId }));
        break;

      case 'unsubscribe':
        hub.unsubscribe(msg.subscriberId);
        ws.send(JSON.stringify({ action: 'unsubscribed' }));
        break;

      case 'status':
        ws.send(JSON.stringify({ action: 'status', data: hub.getStatus() }));
        break;
    }
  });

  ws.on('close', () => {
    // Find and remove this subscriber
    for (const [id, sub] of hub.subscriptions) {
      if (sub.ws === ws) {
        hub.unsubscribe(id);
        break;
      }
    }
  });
});

console.log('Broadcast WebSocket server running on ws://localhost:8765');
```

## Subscriber Client Example

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8765');

ws.on('open', () => {
  // Subscribe to balance updates for Monobank account
  ws.send(JSON.stringify({
    action: 'subscribe',
    subscription: {
      subscriberId: 'my-dashboard',
      eventTypes: ['balance_updated', 'budget_alert'],
      accountFilter: ['acc_mono_1234'],
    },
  }));
});

ws.on('message', (data) => {
  const event = JSON.parse(data);

  if (event.action === 'subscribed') {
    console.log('Subscribed successfully');
    return;
  }

  // Handle financial events
  switch (event.type) {
    case 'balance_updated':
      console.log(`Balance: ${event.payload.accountName} = $${event.payload.currentBalance}`);
      break;
    case 'budget_alert':
      console.log(`ALERT: ${event.payload.category} at ${event.payload.percentUsed}% of budget`);
      break;
  }
});
```
