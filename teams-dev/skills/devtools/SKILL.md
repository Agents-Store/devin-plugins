---
name: devtools
description: Use this skill when the user is inspecting a Microsoft Teams bot locally — using `DevtoolsPlugin`, the activity inspector at `http://localhost:3979/devtools`, viewing MCP requests, or debugging incoming activities and outgoing responses. Triggers on "Teams DevTools", "DevtoolsPlugin", "localhost:3979", "activity inspector Teams", "Teams MCP inspector".
---

# DevTools — inspecting a Teams bot locally

`@microsoft/teams.dev` ships `DevtoolsPlugin`, a local-only HTTP server that records every activity going in and out of the bot, plus MCP traffic if `McpPlugin` is enabled. It is the fastest way to see why a card did not render or why a handler did not fire.

## 1. Enable

```ts
import { App } from '@microsoft/teams.apps';
import { DevtoolsPlugin } from '@microsoft/teams.dev';

const app = new App({
  plugins: process.env.NODE_ENV === 'production' ? [] : [new DevtoolsPlugin()],
});

await app.start();
```

Keep it out of production: it exposes activity content (which may include PII or secrets) on a local port. The `NODE_ENV` guard above is a safe default.

## 2. Where it lives

The plugin starts a second HTTP server on port `3979` by default. Open `http://localhost:3979/devtools` in your browser. The page is a thin shell — most data lives in a websocket fed by the plugin.

Customise the port if 3979 is taken:

```ts
new DevtoolsPlugin({ port: 4979 });
```

## 3. What you can inspect

- **Activities tab** — every inbound and outbound activity in chronological order, with full JSON payload, conversation id, and timing. Filter by route name (`message`, `dialog.submit.*`, …).
- **Handlers tab** — registered routes and which handler files registered them.
- **Logs tab** — anything emitted by the per-handler `log` object — `log.info`, `log.warn`, `log.error`.
- **MCP tab** — present only when `McpPlugin` is registered. Lists tools/resources and the latest request/response cycles.
- **Cards tab** — preview of every Adaptive Card the bot has sent in the current session, useful for verifying schema versions and missing inputs.

## 4. Replaying an activity

In the Activities tab, hover an inbound activity and click **Replay**. The plugin re-emits the JSON to your local server. Combine with `nodemon` to iterate on a handler change without sending a new message from Teams.

## 5. Debugging with `log`

```ts
app.on('message', async ({ activity, log, send }) => {
  log.info('received', { text: activity.text, from: activity.from.id });
  try {
    await send(`echo: ${activity.text}`);
    log.info('sent ok');
  } catch (err) {
    log.error('send failed', { err });
    throw err;
  }
});
```

DevTools renders `log` entries beside the activity that triggered them — much easier to follow than scrolling through `console.log` output.

## 6. Capturing for bug reports

Click the export button in the Activities tab to dump the current session to JSON. Trim secrets before sharing — the export contains tokens.

## Common pitfalls

- **`http://localhost:3979/devtools` shows a blank page** — the plugin failed to start (port already in use). Check the server logs for `EADDRINUSE`.
- **No activities appear** — DevTools is reachable but the bot endpoint in the Teams Developer Portal points elsewhere. Re-run `teams app update --endpoint`.
- **MCP tab is missing** — `McpPlugin` not registered, or registered after `start()`.
- **Cards do not show in the Cards tab** — they were sent as raw activity JSON instead of via `cardAttachment('adaptive', card)`; the plugin only intercepts builder output.
