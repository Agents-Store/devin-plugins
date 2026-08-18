# Transactions in PayloadCMS

How Payload wraps DB transactions per request, and the patterns that keep them atomic.

## What Payload Does Automatically

For every API request Payload opens a transaction on the configured DB adapter (when supported):
- **Postgres / SQLite** — always transactional via Drizzle.
- **MongoDB** — only on replica sets, when `transactionOptions` is set.

The transaction commits when the request handler returns, rolls back if it throws. The transaction ID lives on `req.transactionID`.

## Threading `req` Through Nested Operations

Operations that don't receive `req` open their own connection — they will not see uncommitted changes from the outer request, and they will not roll back together. Every nested Local API call that should be atomic must include `req`:

```ts
// Inside a hook
afterChange: [
  async ({ doc, req }) => {
    // Both writes commit or roll back together
    await req.payload.update({
      collection: 'inventory',
      id: doc.product,
      data: { stock: { decrement: doc.quantity } },
      req,
    })

    await req.payload.create({
      collection: 'audit-log',
      data: { event: 'order.created', orderId: doc.id },
      req,
    })
  },
]
```

Drop `req` only when you genuinely want a side write to commit independently (rare).

## Manual Transactions

For multi-step orchestrations outside the request flow (cron, scripts, scheduled jobs), open one yourself:

```ts
import { payload } from 'payload'

const transactionID = await payload.db.beginTransaction()

try {
  const req = { transactionID } as any

  await payload.create({ collection: 'orders', data: orderData, req })
  await payload.update({ collection: 'inventory', id, data: stockData, req })

  await payload.db.commitTransaction(transactionID)
} catch (err) {
  await payload.db.rollbackTransaction(transactionID)
  throw err
}
```

## Isolation Levels (Postgres / SQLite)

Set per adapter via `transactionOptions`:

```ts
postgresAdapter({
  pool: { connectionString: '...' },
  transactionOptions: {
    isolationLevel: 'read committed',   // 'read uncommitted' | 'read committed' | 'repeatable read' | 'serializable'
    deferrable: false,
    readOnly: false,
  },
})

sqliteAdapter({
  client: { url: 'file:./payload.db' },
  transactionOptions: { behavior: 'immediate' },  // 'deferred' | 'immediate' | 'exclusive'
})
```

For most apps `read committed` is fine. Use `serializable` if you have strict consistency requirements (financial ledgers, race-sensitive counters).

## MongoDB Caveats

- Single-node MongoDB has **no transactions**. Use a replica set in dev:
  ```bash
  mongod --replSet rs0 --port 27017
  # In a mongosh session:
  rs.initiate()
  ```
- Set `transactionOptions: {}` (or any object) on `mongooseAdapter` to enable.
- Cross-shard transactions require MongoDB 4.2+.

## Patterns That Break Transactions

| Anti-pattern | Why it breaks | Fix |
| --- | --- | --- |
| Calling `req.payload.xxx()` without passing `req` | New connection, separate transaction | Pass `req` |
| Using a `fetch()` call to a Payload REST endpoint inside a hook | Different HTTP request, different transaction | Use Local API with `req` |
| Background jobs reading data still uncommitted by the request | Uncommitted reads invisible to other connections | Defer to `afterChange` and pass `req` if you must |
| Setting `overrideAccess: true` then doing security-sensitive nested writes | Bypasses access AND can mask transaction context issues | Pass `req` AND `user` AND `overrideAccess: false` when relevant |

## Testing for Atomicity

Force a failure mid-hook and verify nothing committed:

```ts
hooks: {
  beforeChange: [({ data }) => {
    if (data.title === 'TRIGGER_ROLLBACK') throw new Error('boom')
    return data
  }],
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.create({ collection: 'audit', data: { x: 1 }, req })
    },
  ],
}
```

Now in a test:
1. `payload.create({ collection: 'posts', data: { title: 'TRIGGER_ROLLBACK' } })` — should throw.
2. Confirm `payload.find({ collection: 'audit' }).totalDocs === 0` afterward.

If a row appears in `audit`, you're missing `req` somewhere.
