---
name: troubleshoot
description: Use this skill when the user is debugging a Microsoft Teams bot built on Teams SDK 2.1 — "bot did not reply", "All incoming requests will be rejected", 401/403 from or to Teams, sideload and install errors, SSO sign-in failures, Adaptive Card or dialog problems, streaming and AI issues, manifest checks. Triggers on "Teams bot not responding", "No credentials configured", "Teams 401", "Teams 403", "sideload error", "Teams app manifest invalid", "teams app doctor".
---

# Troubleshooting Teams apps

Walk the sections in order — most problems end in the first three. Two tools do most of the work: `teams app doctor <teamsAppId>` (bot registration, Entra app, manifest, SSO) and `teams status` (login, Developer Portal access, sideloading policy). The official guide `teams-sdk-teams-dev` → `references/troubleshooting.md` covers CLI errors, sideloading blocked by the tenant, "this app cannot be found", AAD replication delays and bot migration; this skill covers what happens in your code.

For an app that sits inside an existing server (a frequent cause of "no reply"), see `references/integrate-existing-server.md`.

## 1. The bot does not reply

| Symptom | Likely cause | Fix |
|---|---|---|
| Server logs `No credentials configured … All incoming requests will be rejected` | `CLIENT_ID`/`CLIENT_SECRET`/`TENANT_ID` missing, and no local opt-in | Set the credentials (`teams app create --env .env`); for Playground testing only, `DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS=true` (`agents-playground`) |
| A message is sent in Teams, the server log shows nothing | The endpoint is wrong, or the tunnel is down | `teams app get <id> --json appId,endpoint`; `teams app update <id> --endpoint "https://<host>/api/messages"`; restart the tunnel |
| The server logs an inbound `401` | The token does not validate: wrong `TENANT_ID`, a rotated secret, a wrong cloud | Compare the environment with the app (`teams app doctor`); set `CLOUD` for sovereign tenants |
| The activity arrives, `send` throws | Credentials wrong for outbound calls, or the user uninstalled the app | Check the error text; reinstall |
| The handler runs, nothing appears | It returned before `send`, or a route name matched another handler first | Add `log.info` lines; check route order and `next()` |
| Replies arrive late or never for long work | The handler runs longer than Teams waits | Stream, or acknowledge and follow up with `app.send` (`messaging`) |

First check where the request dies: `curl -i https://<host>/api/messages`. Any answer — even `401` or `404` — means the tunnel and host work; a timeout or `502` means they do not. A `502` through Dev Tunnels usually means the tunnel's port protocol does not match the app (recreate the port with `--protocol http`).

## 2. Install and sideload

| Symptom | Likely cause | Fix |
|---|---|---|
| "Custom apps are blocked" or a permission error | Tenant or user policy forbids custom apps | `teams status` shows both policies; ask the admin to allow custom app upload |
| "This app cannot be found" | The app was created in a different tenant than the one you install in | Sign in to Teams with the tenant the CLI used (`teams status`) |
| Fails right after creation, works a few minutes later | Registration propagation | Wait one or two minutes |
| "Manifest validation failed" | Schema mismatch, missing icon, invalid `validDomains` | `teams app manifest download <id> manifest.json`, check against the schema, `teams app manifest upload` |
| The app installs, a tab or dialog is blank | The host is missing from `validDomains` | `teams app manifest update <id> --set-json validDomains='["<host>"]'` |

## 3. Authentication

| Symptom | Likely cause | Fix |
|---|---|---|
| `AUTH_REQUIRED` or `AUTH_TOKEN_FAILED` from the CLI | Not signed in or an expired token | `teams login`, then `teams status` |
| `graph.signIn(ctx)` returns undefined and the user sees no card | The bot is Teams-managed, or the connection name is wrong | Migrate the bot to Azure; match the flow name to the Azure connection |
| Sign-in loops, a six-digit code appears | The signing-in identity differs from the Teams user | Sign in with the same account; this is expected for cross-tenant setups |
| `signin/failure` with `resourcematchfailed` | The OAuth card's resource does not match the Entra application id URI | Align `webApplicationInfo.resource`, the app's "Expose an API" URI and the connection's token exchange URL; `teams app doctor` checks them |
| `installedappnotfound` | The bot is not installed for the user or chat | Install it |
| Graph `403` | Missing delegated or application permission, or no consent | Add the permission, grant consent, add the scope to the connection (`graph-integration`) |

`graph.onSignInFailure(ctx, failure)` receives the failure code (`authentication`). SSO needs the Teams desktop and web clients pre-authorised on the Entra app; `teams app doctor` reports whether they are.

## 4. Cards, dialogs, extensions

| Symptom | Likely cause | Fix |
|---|---|---|
| A card button does nothing | No `card.action.<action>` route for the name in `SubmitData`, or the handler returned nothing | Add the handler and return a response (`adaptive-cards`) |
| Input values missing | The input has no id, or `withAssociatedInputs('auto')` is missing | Set both |
| A card is blank in Teams | An element newer than the client supports | Lower the schema version or the element |
| A dialog never opens | `OpenDialogData` is on an `ExecuteAction` | Use a `SubmitAction` (`dialogs`) |
| An action command's form never opens | `fetchTask: true` without a `message.ext.open` handler | Add it (`message-extensions`) |
| Link unfurling does nothing | The domain is not in `messageHandlers` and `validDomains` | Add it |

## 5. AI and streaming

| Symptom | Likely cause | Fix |
|---|---|---|
| Streaming shows nothing in a channel | Streaming is 1:1 only | Gate on `conversationType === 'personal'` and `send` the text |
| A streamed answer stops mid-way | The two-minute window closed | Hand off to message updates (`messaging`) |
| `401` from the model API | Wrong key, endpoint or deployment for the client | Check `OPENAI_API_KEY` or the `AZURE_OPENAI_*` variables (`ai-agents`) |
| A tool fires twice | The same tool is registered locally and through MCP | Keep one |

## 6. Manifest sanity checks

```bash
teams app manifest download <teamsAppId> manifest.json
jq '{manifestVersion, id, bots: [.bots[]?.botId], webApplicationInfo, validDomains}' manifest.json
```

- `bots[].botId` equals the bot's `CLIENT_ID`.
- `validDomains` includes every host used by tabs, dialogs, link handlers and the endpoint.
- `webApplicationInfo.resource` equals the Entra application id URI for SSO (`api://botid-<client-id>`).

## 7. When all else fails

- Restart the dev server and the tunnel, and re-run `teams app doctor <teamsAppId>`.
- Raise logging: `LOG_LEVEL=debug`.
- Test the handler without Teams in the Agents Playground (`agents-playground`).
- `teams self-update`, then retry.
- Search the issues of `microsoft/teams.ts` and `microsoft/teams-sdk` for the exact error text.
