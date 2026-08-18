---
name: tabs
description: Use this skill when the user is building a static-hosted tab inside a Microsoft Teams app — serving a web page from the bot's server via `app.tab()`, using the `@microsoft/teams.client` SDK to call back into Teams, configuring tab context, or wiring a personal / channel / dialog tab. Triggers on "Teams tab", "static tab", "configurable tab", "Teams client SDK".
---

# Tabs — embedded web pages in Teams

A tab is a web page rendered inside Teams. The SDK ships two pieces:
- Server side: `app.tab('name', path)` serves static files from the bot's HTTP server.
- Client side: `@microsoft/teams.client` exposes the Teams context (theme, user, conversation) and helpers like `dialog.url.submit`.

## 1. Serve a static tab

```ts
import path from 'node:path';
import { App } from '@microsoft/teams.apps';

const app = new App({});
app.tab('settings', path.join(__dirname, '../public/settings'));
await app.start(3978);
```

`app.tab(name, dir)` mounts the directory at `/tabs/<name>`. Drop an `index.html` (or a bundled React/Vue build) in the directory and reference it from the manifest.

## 2. Manifest

```jsonc
{
  "staticTabs": [{
    "entityId": "settings",
    "name": "Settings",
    "contentUrl": "https://${BOT_HOST}/tabs/settings",
    "scopes": ["personal"]
  }],
  "configurableTabs": [{
    "configurationUrl": "https://${BOT_HOST}/tabs/configure",
    "scopes": ["team", "groupChat"]
  }],
  "validDomains": ["${BOT_HOST}"]
}
```

Personal tabs (`scopes: ['personal']`) appear in the left rail of a 1:1 chat with the app. Configurable tabs appear in channels / group chats and require a configuration page that calls `pages.config.setConfig` on save.

## 3. Client-side SDK

Inside the page:

```ts
import * as teams from '@microsoft/teams.client';

await teams.initialize();
const ctx = await teams.app.getContext();
console.log(ctx.theme, ctx.user, ctx.channel);

// Save configurable tab config:
teams.pages.config.setConfig({
  contentUrl: 'https://${BOT_HOST}/tabs/content?roomId=42',
  entityId: 'room-42',
  suggestedDisplayName: 'Room 42',
});
teams.pages.config.setValidityState(true);
```

The client SDK works only when the page is loaded inside the Teams app shell. In a regular browser, `initialize()` rejects — gate UI behind that check.

## 4. Auth from a tab — Nested App Authentication

```ts
import { PublicClientApplication } from '@azure/msal-browser';
import * as teams from '@microsoft/teams.client';

await teams.initialize();
const msal = new PublicClientApplication({
  auth: { clientId: 'AAD_CLIENT_ID', authority: 'https://login.microsoftonline.com/common' },
});

const accounts = msal.getAllAccounts();
const tokenResp = await msal.acquireTokenSilent({
  scopes: ['User.Read'],
  account: accounts[0],
});

const me = await fetch('https://graph.microsoft.com/v1.0/me', {
  headers: { Authorization: `Bearer ${tokenResp.accessToken}` },
}).then(r => r.json());
```

NAA delegates to the parent Teams app's auth — no popup, no redirect. See `authentication` for the full setup.

## 5. Server callbacks from a tab

Tabs cannot call the bot's `/api/messages` directly. Instead:
- Use NAA + Graph (no bot needed for personal data).
- Or expose a REST endpoint on the bot's server that validates the SSO token and persists state.

```ts
import express from 'express';
import { App } from '@microsoft/teams.apps';
import { ExpressAdapter } from '@microsoft/teams.apps/express';

const server = express();
server.use(express.json());

server.post('/api/tab/save', authMiddleware, async (req, res) => {
  await persist(req.body);
  res.json({ ok: true });
});

const app = new App({ plugins: [new ExpressAdapter({ app: server })] });
```

`authMiddleware` validates the bearer token. The token comes from `teams.authentication.getAuthToken()` on the client.

## 6. Open a dialog from a tab

```ts
const result = await teams.dialog.url.open({
  title: 'Pick a value',
  url: 'https://${BOT_HOST}/tabs/picker',
  size: { width: 400, height: 300 },
});
```

The picker page calls `teams.dialog.url.submit(value)` to close itself and resolve the promise.

## Common pitfalls

- **Tab loads blank in Teams** — `validDomains` is missing the host. The Teams shell silently refuses to render.
- **`teams.initialize()` rejects in the browser** — expected. Detect with `try/catch` and render a "open in Teams" fallback.
- **NAA returns `interaction_required`** — fall back to `msal.acquireTokenPopup` (Teams 2.x desktop client) or surface a sign-in button.
- **Channel-tab config never persists** — `pages.config.setValidityState(true)` was not called.
