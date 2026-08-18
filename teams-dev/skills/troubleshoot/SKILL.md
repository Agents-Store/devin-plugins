---
name: troubleshoot
description: Use this skill when the user is debugging a Microsoft Teams app problem — sideload failures, "bot did not reply", SSO `signin.token-exchange` errors, manifest validation, endpoint mismatches, Adaptive Card rendering issues, or any "why isn't my Teams bot working" question. Triggers on "Teams bot not responding", "sideload error", "Teams 401", "Teams 403", "Teams app manifest invalid".
---

# Troubleshooting Teams apps

A focused triage guide. Walk through the sections in order — most problems land in the first three.

For integrating Teams into an existing server (often the underlying cause of "no reply"), see `references/integrate-existing-server.md`.

## 1. Bot does not reply

| Symptom | Likely cause | Fix |
|---|---|---|
| Message is sent in Teams, server logs show nothing | Endpoint wrong | `teams app update <id> --endpoint "https://<host>/api/messages"` |
| Server logs show activity, `send` throws | Bot credentials wrong | Confirm `BOT_ID` / `BOT_PASSWORD` against `teams app get <id> --json` |
| DevTools shows inbound but no outbound | Handler returned before `send` | Add `log.info` lines to trace handler flow |
| Outbound shown in DevTools, nothing in Teams | Tunnel is down (devtunnel/ngrok) | Restart tunnel; re-run `teams app update --endpoint` with the new URL |

Always start with DevTools (`http://localhost:3979/devtools`). If the activity is not visible there, the request never reached your server — the problem is between Teams and your host.

## 2. Sideload errors

| Symptom | Likely cause | Fix |
|---|---|---|
| "Manifest validation failed" | Schema mismatch | Bump `manifestVersion` to match the features used (1.16+ for execute actions, etc.) |
| "App already installed" | Older sideload still active | Uninstall the app in Teams → reinstall |
| "Invalid icon" | Icon missing / wrong size | Ensure `color.png` (192×192) and `outline.png` (32×32) under `appPackage/` |
| "Tenant policy disallows sideloading" | Admin policy | Use a Developer Program tenant, or ask the admin to allow custom app uploads |

## 3. SSO failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `signin.token-exchange` never fires | OAuth connection name mismatch | Match `connectionName` in `OAuthCard` to the Bot Service config |
| Exchange returns "invalid resource" | `webApplicationInfo.resource` wrong | Set to `api://<host>/<AAD client id>` and re-deploy manifest |
| Graph call returns 401 | User token bound to wrong audience | Inspect the JWT at jwt.ms — `aud` must match the AAD app's API URI |
| Graph call returns 403 | Missing delegated permission | Add the scope in AAD → grant admin consent |

Full SSO setup: `references/integrate-existing-server.md` covers the integration angle; the dedicated `authentication/references/sso-setup.md` has the Azure-side checklist.

## 4. Adaptive Card issues

| Symptom | Likely cause | Fix |
|---|---|---|
| Card renders as plain text | Attachment shape wrong | Use `cardAttachment('adaptive', card)`; do not hand-build the envelope |
| `Action.Submit` does nothing | Bot has no `card.action.<id>` handler | Add `app.on('card.action.<id>', …)`; verify ids match |
| Input value missing in submission | Input has no `id` | Every `*Input` needs an id (first constructor arg) |
| Card looks fine in Designer but blank in Teams | Old client version | Confirm Teams desktop/web is up to date; some elements require client 1.5+ |

## 5. AI / streaming

| Symptom | Likely cause | Fix |
|---|---|---|
| Streaming flashes nothing in a channel | Streaming only works in 1:1 | Gate on `conversation.conversationType === 'personal'`; send the full text otherwise |
| OpenAI returns 401 | Wrong key | Confirm `OPENAI_API_KEY` or `AZURE_OPENAI_API_KEY` in `.env` |
| Tool fires twice | Same tool registered in `prompt.function` and `mcp.tool` | Pick one host per tool |
| 15s timeout on long calls | Teams drops the request | Send a typing indicator + reply later via `app.send(conversationId, …)` |

## 6. Manifest sanity checks

```bash
jq '.manifestVersion, .id, .bots[]?.botId, .webApplicationInfo?, .validDomains' appPackage/manifest.json
```

- `manifestVersion` ≥ `1.16` for modern features.
- `id` must equal `TEAMS_APP_ID`.
- `bots[].botId` must equal `BOT_ID` in `.env`.
- `webApplicationInfo.resource` must equal `api://<host>/<AAD client id>` for SSO.
- `validDomains` must include every host referenced by tabs or dialogs.

## 7. Network / proxy

```bash
curl -fsS "https://<host>/api/messages" -X POST -H "Content-Type: application/json" -d '{}'
```

A bare POST should return a non-200 (Teams normally signs requests). If it returns ECONNREFUSED or timeout, the tunnel or host itself is unreachable from your machine — fix that before debugging higher layers.

## 8. When all else fails

- Restart the dev server (`npm run dev`).
- Reinstall the app in Teams (uninstall + sideload again).
- `teams self-update` to pull the latest CLI.
- Search `https://github.com/microsoft/teams-sdk/issues` for the exact error string.
