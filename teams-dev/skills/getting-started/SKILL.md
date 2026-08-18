---
name: getting-started
description: Use this skill when the user wants to scaffold their first Microsoft Teams app or bot project, asks "how do I start a Teams bot in TypeScript", or needs to run a fresh `teams project new` template end-to-end — from CLI scaffold to a working echo bot reachable from a Teams client.
---

# Getting Started — your first Teams app in TypeScript

Walks a developer from an empty directory to a working Teams bot answering messages, in roughly 10 minutes. All steps assume the `setup` skill has already been completed (Node 18+, `@microsoft/teams.cli@preview` installed, signed in via `teams auth login`).

## 1. Scaffold the project

Pick a template that matches the goal:

| Template | What you get | Use when |
|---|---|---|
| `echo` (default) | Bot that echoes user messages | Bots from scratch — pick this for learning |
| `ai` | Bot with `ChatPrompt` + `OpenAIChatModel` wired up | LLM-powered assistants |
| `graph` | Bot with SSO + `api.graph` calls | Apps that read M365 data |
| `tab` | Static-hosted React tab | Embedded web UI (no bot loop) |

```bash
teams project new typescript demo-bot --template echo
cd demo-bot
npm install
```

The CLI creates:

```
demo-bot/
├── src/
│   └── index.ts          # App entry point + handlers
├── appPackage/
│   ├── manifest.json     # Teams app manifest (consumed by sideload)
│   └── color.png / outline.png   # icons
├── .env                  # BOT_ID, BOT_PASSWORD placeholders
├── package.json          # npm scripts: dev, build, start
└── tsconfig.json
```

## 2. Read the entry point

`src/index.ts` after `--template echo`:

```ts
import { App } from '@microsoft/teams.apps';
import { DevtoolsPlugin } from '@microsoft/teams.dev';

const app = new App({
  plugins: [new DevtoolsPlugin()],
});

app.on('message', async ({ send, activity }) => {
  await send(`You said: ${activity.text}`);
});

(async () => {
  await app.start(+(process.env.PORT ?? 3978));
})();
```

Key facts:
- `App` is the only required import. Plugins (`DevtoolsPlugin`, `McpPlugin`, etc.) are optional extras.
- `app.on('message', ...)` is the universal message handler. The handler context exposes `send`, `activity`, `log`, `stream`, `api`, and `next`.
- Default port is `3978`. The DevTools plugin runs a second server on `3979`.

## 3. Expose a public HTTPS endpoint

Teams requires HTTPS to reach the bot. Two options:

```bash
# Option A: Microsoft devtunnel
devtunnel host -p 3978 --allow-anonymous
# Copies a https://<id>.devtunnels.ms URL — save it.

# Option B: ngrok
ngrok http 3978
# Copies a https://<id>.ngrok.io URL — save it.
```

Update the bot endpoint registered with Teams to point at the tunnel:

```bash
teams app update <teamsAppId> --endpoint "https://<tunnel-host>/api/messages"
```

Get `<teamsAppId>` from `teams app list`. If you have not yet registered a bot, follow `deployment` → `references/bot-infra-setup.md`.

## 4. Run

```bash
npm run dev
```

You should see two servers come up:
- `Bot listening on http://localhost:3978`
- `DevTools available at http://localhost:3979/devtools`

Open the DevTools URL in a browser to inspect activities as they arrive. See the `devtools` skill for the UI walkthrough.

## 5. Sideload into Teams

1. Open the [Teams Developer Portal](https://dev.teams.microsoft.com/).
2. Find your app (auto-registered by the CLI on `teams project new`).
3. Click **Preview in Teams** → confirm sideload.
4. Open a 1:1 chat with the bot and send a message — it should echo back.

If the bot does not reply, jump to `troubleshoot`.

## 6. Iterate

- Add new handlers in `src/index.ts` — `app.on('install.add', ...)`, `app.on('dialog.submit.<id>', ...)`, `app.on('message.ext.query', ...)`. See `sdk-patterns` for the full routing table.
- Send Adaptive Cards instead of plain text — see `adaptive-cards`.
- Add an AI loop — see `ai-agents`.
- Add SSO / Graph — see `authentication` + `graph-integration`.

## Common first-run errors

- **No reply in Teams** — the endpoint registered with the app does not match the tunnel URL. Re-run `teams app update --endpoint`.
- **`401 Unauthorized` in server logs** — `BOT_ID` and `BOT_PASSWORD` in `.env` are wrong or missing. Re-run `deployment/references/bot-infra-setup.md`.
- **`Cannot find module '@microsoft/teams.apps'`** — `npm install` was not run inside the project directory.
- **DevTools shows no activity** — the tunnel is down or pointing to the wrong port. Restart `devtunnel host -p 3978` and re-update the endpoint.
