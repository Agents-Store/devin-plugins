# Bot infrastructure setup

Register a bot identity so Teams can authenticate inbound activities and your code can talk back. Two paths — pick one.

## Path A: Teams-managed bot (recommended)

The Teams Developer Portal hands you an identity and rotates secrets for you. Simplest for new apps.

```bash
teams app create my-bot
```

Capture the output and write `.env`:

```
TEAMS_APP_ID=...   # the Teams-side app id
BOT_ID=...         # the bot client id
BOT_PASSWORD=...   # the bot secret
```

If you missed the output:

```bash
teams app list --json | jq '.[] | select(.name=="my-bot")'
teams app get <teamsAppId> --json
```

The secret is only shown on creation. Rotate via:

```bash
teams app credentials rotate <teamsAppId>
```

## Path B: Custom AAD app

When you need to share the same AAD app with another workload (Graph batch jobs, a web app), register a Bot Channel Registration backed by your own AAD app.

```bash
APP_ID=$(az ad app create --display-name "my-bot" --sign-in-audience AzureADMyOrg --query appId -o tsv)
SECRET=$(az ad app credential reset --id $APP_ID --display-name primary --query password -o tsv)

az bot create --resource-group <rg> --name my-bot \
  --kind registration \
  --appid $APP_ID --password $SECRET \
  --endpoint "https://<host>/api/messages"

# Connect the bot to the Teams channel
az bot msteams create --resource-group <rg> --name my-bot
```

Then register the app in the Teams Developer Portal pointing at the same `BOT_ID = $APP_ID`.

`.env`:

```
BOT_ID=$APP_ID
BOT_PASSWORD=$SECRET
TEAMS_APP_ID=<id-from-developer-portal>
```

## Initial endpoint

Whichever path, set the endpoint to your current host:

```bash
teams app update <teamsAppId> --endpoint "https://<host>/api/messages"
```

For local dev, `<host>` is a devtunnel/ngrok host; for production, a stable DNS name.

## Verify

```bash
teams app get <teamsAppId> --json | jq '{id, name, bots, endpoint}'
```

Confirm `bots[0].botId` matches `BOT_ID` in `.env`. Start the bot (`npm run dev`), sideload the manifest in Teams, and send a message — the activity should hit your handler.

## Bot identity types

| Type | Use when |
|---|---|
| `MultiTenant` | App is shared across tenants / on AppSource |
| `SingleTenant` | App is internal to one tenant |
| `UserAssignedMSI` | Azure-hosted bot using a managed identity (no secret) |
| `Teams-managed` | New apps where you do not own the AAD registration |

`MultiTenant` is the default for new Teams-managed bots. Switch via the Developer Portal **Configurations** tab if needed.

## Secret rotation

- Rotate annually at minimum.
- For Path A: `teams app credentials rotate <teamsAppId>`. Update `.env` and redeploy.
- For Path B: `az ad app credential reset --id $APP_ID --display-name <new-name>` — Azure keeps the previous secret valid for a grace period; redeploy with the new one, then `az ad app credential delete` the old one.
