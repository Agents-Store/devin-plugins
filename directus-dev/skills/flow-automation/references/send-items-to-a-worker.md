# Send Item Keys to a Worker (and Do Not Loop)

A Flow that hands the changed items to an external worker (enrich a record, sync it, transcode a file) instead of only expiring a cache. It builds on [notify-external-app.md](notify-external-app.md): the same event trigger, the same `request` operation, the secret in a header read from `$env` through `FLOWS_ENV_ALLOW_LIST`. This file covers what is different when the receiver does real work. The template rendering, the condition and the Run Script claims below were checked against the code Directus 12.4.1 ships (`@directus/utils` 13.5.5, `@directus/api` 39.2.1) and run with `validatePayload` and `applyOptionsData`; the flow was not run end to end.

## The request body: ids, not the item

```json
{
  "name": "Call worker",
  "key": "call_worker",
  "type": "request",
  "options": {
    "method": "POST",
    "url": "https://app.example.com/api/jobs/enrich",
    "headers": [
      { "header": "Content-Type", "value": "application/json" },
      { "header": "x-webhook-secret", "value": "{{ $env.WORKER_WEBHOOK_SECRET }}" }
    ],
    "body": "{\"event\":\"{{ $trigger.event }}\",\"collection\":\"{{ $trigger.collection }}\",\"keys\":{{ $trigger.keys }}}"
  }
}
```

- `$trigger.keys` is **always an array**, also when one item changed. Inside a string, Directus renders an array or an object with `JSON.stringify`, so `"keys":{{ $trigger.keys }}` becomes `"keys":["a1","b2"]` and the body stays valid JSON. A body that consists of nothing but `{{ $trigger.keys }}` is not stringified: the option receives the raw array.
- `$trigger.event` is the event name, for example `articles.items.update`.
- Send the keys and let the worker read the item. On `items.update` the trigger payload holds only the fields that one request changed, and an item can change again before the worker starts.
- The `request` operation makes one HTTP call and does not retry. A non-2xx answer or a network error takes the `reject` path (`{{ $last }}` holds the error); add a `log` operation there, as in `notify-external-app.md`. Editors save the same item many times, so the receiver must treat a repeated key as normal: answer `2xx` quickly, do the work asynchronously, and make the work idempotent.

## The write-back loop

The worker writes its result into the same collection, that write is an `items.update`, and the Flow fires again. Stop it in two places.

**In the Flow**, put a `condition` operation between the trigger and the `request`, and make it require a field that only an editor changes. The condition takes **filter rules** (JSON, nested objects), not an expression such as `{{ $trigger.payload.body }} != null`:

```json
{
  "name": "Source field present",
  "key": "source_changed",
  "type": "condition",
  "options": {
    "filter": { "$trigger": { "payload": { "body": { "_nnull": true } } } }
  }
}
```

Connect the condition's `resolve` path to `call_worker` and leave `reject` empty. The condition requires every key it names to be present (`requireAll`), so:

| Trigger payload | Condition |
|-----------------|-----------|
| `items.create` with `body` | passes |
| `items.update` that edits `body` | passes |
| `items.update` the worker sent (`ai_summary`, `processing_status`, ...) | fails, the Flow ends |
| `items.update` that sets `body` to `null` | fails |

This holds only while the worker's write never includes the source field and an editor's edit of interest always does. An edit that touches only other fields (a status dropdown) does not start the worker; list more fields with `_or` if it should.

**In the receiver**, return early when the item is already processed (a result field set and newer than the source), so a second delivery, or a write-back that slipped through, costs one read.

## Signing the request

A Run Script (`exec`) operation runs in an isolated V8 context with `console`, `process.env` (only the allow-listed variables) and `module`: no `require`, no Node modules, no `crypto`, no network. It cannot compute an HMAC of the body. Use the shared secret in a header over HTTPS (the receiver compares with `crypto.timingSafeEqual`), or send a token made by the `json-web-token` operation (`sign`) and verify it on the receiver (the JWT route was not tried here). A real body signature needs a custom operation extension.
