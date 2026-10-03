---
name: agents-playground
description: Use this skill when the user wants to test or debug a Microsoft Teams bot locally on Teams SDK 2.1 — Microsoft 365 Agents Playground (`agentsplayground`), accepting unauthenticated local requests (`dangerouslyAllowUnauthenticatedRequests`), the "No credentials configured … all incoming requests will be rejected" warning, mock activities, logs, replacing the deprecated DevTools. Triggers on "Agents Playground", "test Teams bot locally", "No credentials configured", "dangerouslyAllowUnauthenticatedRequests", "Teams DevTools replacement".
---

# Local testing with the Microsoft 365 Agents Playground

The in-process DevTools plugin is deprecated and its npm package is marked so. A freshly scaffolded project does not use it: `new App()` has no plugins, one server on port 3978, and no second port. The local test tool is now the **Microsoft 365 Agents Playground** — a separate CLI that sends real HTTP requests to `/api/messages`, so you can chat with the bot and mock activities without a tunnel, a bot registration or a Teams client.

If an older project still lists the DevTools plugin, remove it from the `App` options and drop the package from `package.json`.

## 1. Install

```bash
npm install -g @microsoft/m365agentsplayground      # provides the `agentsplayground` command
```

It installs globally, not as a project dependency. A standalone binary exists too (`winget install agentsplayground`).

## 2. Let the bot accept its requests

The Playground does not send a Bot Framework token. The SDK rejects unauthenticated requests by default (it logs `No credentials configured … All incoming requests will be rejected`), so a local run needs an explicit opt-in. The safest place is the environment of your local shell or `.env`, not the code:

```bash
# .env — local development only, never in a deployed environment
DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS=true
```

The option form exists too:

```ts
import { App } from '@microsoft/teams.apps';

const app = new App({
  dangerouslyAllowUnauthenticatedRequests: process.env.NODE_ENV === 'development',
});
```

- The flag disables inbound token validation **even when credentials are configured**, and the SDK logs a warning saying so. That is the point of the long name — never ship it enabled.
- `skipAuth` is a deprecated alias of the same option; the quickstart pages still show it.
- Do not open the port to the network while the flag is on.

## 3. Run

Start the bot (`npm run dev`, port 3978), then in a second terminal:

```bash
agentsplayground -e http://localhost:3978/api/messages -c emulator
```

The UI is at `http://localhost:56150`. Flags:

| Flag | Meaning |
|---|---|
| `-e, --app-endpoint` | The bot's messaging endpoint |
| `-c, --channel-id` | `emulator`, `webchat`, `msteams`, `directline` or `agents` — `msteams` mimics Teams payloads most closely |
| `--client-id`, `--client-secret`, `--tenant-id` | Credentials, when the bot validates tokens |
| `-p, --port` | Port of the Playground UI (default 56150) |

`agentsplayground --help` lists the rest.

## 4. What to use it for

| You want to | Use |
|---|---|
| Chat with the bot | The compose box; personal chat, group chat and channel views in the sidebar |
| Test a membership change, reaction, invoke or other non-message activity | **Mock an Activity** menu |
| See the HTTP exchange | The **Log Panel** (top right): request and response bodies |
| See your own logging | The bot's terminal: `log.info(...)`, and `LOG_LEVEL=debug` for SDK debug lines |
| Check a card renders | Send it from a handler; design in the Adaptive Card Designer first |

Replacing the old tool: the DevTools "Activities" view maps to the Log Panel, "Chat" to the compose box, "Cards" to the Designer plus a send from the bot.

## 5. What it cannot do

- **Sign-in and SSO.** Those flows need the Bot Framework token service and the Teams client. Test `addOAuthFlow` handlers in Teams (`authentication`).
- **Teams-only UI.** Tabs, dialogs, message-extension menus and the AI label are Teams client features; the Playground shows the raw payloads, not the rendering.
- **Auth.** It proves your handlers, not your credentials, endpoint or manifest. For those use `teams app doctor` (`cli-recipes`) and a test in Teams.

## 6. The path to Teams

When the handlers behave, register the bot and test in the client: `teams app create --name … --endpoint https://<tunnel-host>/api/messages --env .env`, a tunnel to port 3978, then the install link from `teams app get <id> --install-link`. Turn the unauthenticated flag off before this step. The standard flow is in the vendored official guide `teams-sdk-teams-dev`.

## Common pitfalls

- **The bot answers `401` or logs "All incoming requests will be rejected"** — neither credentials nor the opt-in flag are set.
- **Nothing happens in the Playground** — the endpoint must be the full `/api/messages` URL, and the bot must be running on that port.
- **Streaming behaves differently than in Teams** — the 1:1-only rule and the two-minute window belong to the Teams service; judge streaming in Teams.
- **A deployed bot accepts anything** — the flag leaked into a deployed environment. Remove it and check the host's environment variables.
