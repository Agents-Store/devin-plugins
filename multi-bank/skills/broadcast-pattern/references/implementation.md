# Broadcast Pattern — Implementation Details

## Publisher Implementation (BroadcastHub)

```javascript
class BroadcastHub {
  constructor() {
    this.subscriptions = new Map();
    this.eventLog = [];
  }

  subscribe(subscription) {
    this.subscriptions.set(subscription.subscriberId, subscription);
  }

  unsubscribe(subscriberId) {
    this.subscriptions.delete(subscriberId);
  }

  emit(event) {
    event.id = event.id || crypto.randomUUID();
    event.timestamp = event.timestamp || new Date().toISOString();
    this.eventLog.push(event);

    for (const [id, sub] of this.subscriptions) {
      if (this.shouldDeliver(event, sub)) {
        this.deliver(sub, event);
      }
    }
  }

  shouldDeliver(event, sub) {
    if (!sub.eventTypes.includes(event.type)) return false;
    if (sub.accountFilter?.length && event.accountId) {
      return sub.accountFilter.includes(event.accountId);
    }
    return true;
  }

  deliver(sub, event) {
    switch (sub.callbackType) {
      case 'websocket': sub.ws?.send(JSON.stringify(event)); break;
      case 'file': emitToFile(event); break;
      case 'polling': /* stored in eventLog, polled via API */ break;
    }
  }
}
```

## Delivery Mechanisms

### 1. WebSocket (preferred)

Set up a WebSocket server using the `ws` library:

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8765 });

wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    const msg = JSON.parse(data);
    if (msg.action === 'subscribe') {
      registry.add({ ...msg.subscription, ws });
    }
  });
});

function broadcast(event) {
  for (const sub of registry.getMatching(event)) {
    if (sub.ws.readyState === WebSocket.OPEN) {
      sub.ws.send(JSON.stringify(event));
    }
  }
}
```

Latency: <5 seconds from bank sync to subscriber delivery.

### 2. HTTP Polling (fallback)

For environments where WebSocket is unavailable:

```javascript
// Server endpoint
app.get('/api/events', (req, res) => {
  const since = new Date(req.query.since);
  const events = eventStore.filter(e => new Date(e.timestamp) > since);
  res.json({ events, serverTime: new Date().toISOString() });
});

// Client polls every 5 seconds
setInterval(async () => {
  const res = await fetch(`/api/events?since=${lastPollTime}`);
  const { events, serverTime } = await res.json();
  events.forEach(handleEvent);
  lastPollTime = serverTime;
}, 5000);
```

### 3. File-based (CLI consumers)

For script and CLI consumers, events are appended to a JSONL file:

```javascript
const fs = require('fs');
const path = require('path');

const EVENTS_FILE = path.join(os.homedir(), '.multi-bank', 'events.jsonl');

function emitToFile(event) {
  fs.appendFileSync(EVENTS_FILE, JSON.stringify(event) + '\n');
}

// Consumer reads new lines (tail -f equivalent)
function tailEvents(callback) {
  let position = fs.statSync(EVENTS_FILE).size;
  fs.watchFile(EVENTS_FILE, () => {
    const stream = fs.createReadStream(EVENTS_FILE, { start: position });
    let buffer = '';
    stream.on('data', (chunk) => { buffer += chunk; });
    stream.on('end', () => {
      const lines = buffer.split('\n').filter(Boolean);
      lines.forEach(line => callback(JSON.parse(line)));
      position = fs.statSync(EVENTS_FILE).size;
    });
  });
}
```
