# SSO setup — Azure-side checklist

End-to-end steps to wire single sign-on into an existing Teams bot. Assumes:
- Bot already registered (`teamsAppId`, `BOT_ID`).
- `az` CLI authenticated against the target tenant.
- The bot is hosted at a stable HTTPS host (`<host>`).

## 1. Create the AAD application

```bash
az ad app create --display-name "<bot name> SSO" --sign-in-audience AzureADMyOrg
APP_ID=$(az ad app list --display-name "<bot name> SSO" --query '[0].appId' -o tsv)
echo $APP_ID
```

For multi-tenant bots use `--sign-in-audience AzureADMultipleOrgs`. The returned `appId` is the AAD client id.

## 2. Set the application ID URI

```bash
az ad app update --id $APP_ID --set identifierUris="[\"api://<host>/$APP_ID\"]"
```

This is the audience SSO tokens are issued for — must match `webApplicationInfo.resource` in the manifest exactly.

## 3. Configure the API scopes (`access_as_user`)

In the Azure Portal:

1. Azure Active Directory → App registrations → your app → **Expose an API**.
2. Add a scope: `access_as_user`, admin + user consent, status enabled.
3. **Authorized client applications** → add the Teams clients:
   - `1fec8e78-bce4-4aaf-ab1b-5451cc387264` — Teams mobile / desktop.
   - `5e3ce6c0-2b1f-4285-8d4b-75ee78787346` — Teams web.

These are the public Teams client ids; they tell AAD to skip user consent when the host has already authorised the user.

## 4. Add a client secret

```bash
SECRET=$(az ad app credential reset --id $APP_ID --display-name primary --query password -o tsv)
echo $SECRET
```

Save the secret somewhere durable — Azure does not display it again.

## 5. API permissions

For each Microsoft Graph scope your bot calls (`User.Read`, `Mail.Read`, `Calendars.ReadWrite`, …):

```bash
az ad app permission add --id $APP_ID --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions <permission-id>=Scope
```

Then grant tenant-wide admin consent:

```bash
az ad app permission admin-consent --id $APP_ID
```

`00000003-0000-0000-c000-000000000000` is the AAD app id for Microsoft Graph. The permission ids come from `az ad sp show --id 00000003-0000-0000-c000-000000000000 --query "oauth2PermissionScopes[].{name:value, id:id}"`.

## 6. Configure the OAuth connection on the bot

In the Azure Bot resource that backs your `BOT_ID` → **Configuration** → **OAuth Connection Settings** → **Add**:

| Field | Value |
|---|---|
| Name | `GRAPH_CONNECTION` (or any string — must match the bot code) |
| Service provider | Azure Active Directory v2 |
| Client id | `$APP_ID` |
| Client secret | `$SECRET` |
| Tenant id | your tenant id (or `common` for multi-tenant) |
| Scopes | `access_as_user User.Read <…other scopes…>` (space-separated) |

Save, then click **Test connection** to confirm. The first test prompts you to consent.

## 7. Update the manifest

```jsonc
// appPackage/manifest.json
{
  "webApplicationInfo": {
    "id": "<APP_ID>",
    "resource": "api://<host>/<APP_ID>"
  },
  "validDomains": ["<host>"]
}
```

Reload the app in Teams (sideload again or via Developer Portal **Preview**).

## 8. Bot code

Two handlers handle the SSO flow:

```ts
import { MessageActivity, OAuthCard, cardAttachment } from '@microsoft/teams.api';

app.on('message', async ({ send, activity, api }) => {
  const cached = await tokens.get(activity.from.id).catch(() => null);
  if (cached) return handleCommand(cached);

  await send(new MessageActivity().addAttachment(
    cardAttachment('oauth', new OAuthCard({ connectionName: 'GRAPH_CONNECTION', text: 'Sign in to continue' })),
  ));
});

app.on('signin.token-exchange', async ({ activity, api, send }) => {
  const token = await api.tokens.exchange({
    connectionName: 'GRAPH_CONNECTION',
    userTokenExchangeRequest: activity.value,
  });
  await tokens.put(activity.from.id, token.token);
  await send('Signed in. Try again.');
});

app.on('signin.verify-state', async ({ activity, api }) => {
  await api.tokens.verify({ state: activity.value.state });
});
```

`tokens` is your own KV store (Redis, Cosmos, etc.). The exchanged token can be used directly against Graph:

```ts
const events = await api.graph.withToken(userToken).me.events.list();
```

## 9. Verify

1. Sideload the updated manifest.
2. Open the bot, send any message.
3. The bot replies with an OAuth card; click **Sign in**.
4. Teams shows a brief consent prompt then collapses the card.
5. The bot replies with "Signed in. Try again." — confirms `signin.token-exchange` fired.
6. Send the original command again; the bot now executes the authenticated path.

## Common failures

| Error | Cause | Fix |
|---|---|---|
| `AADSTS50058` | User session expired | Re-send the OAuthCard |
| `AADSTS65001` | Consent missing | Run `az ad app permission admin-consent` |
| `invalid_resource` | `webApplicationInfo.resource` does not match `identifierUris` | Align both to `api://<host>/<APP_ID>` |
| `signin.token-exchange` never fires | `connectionName` mismatch | Match the OAuthCard name to the Bot Service config |
| Graph 403 | Missing scope | Add the scope to API permissions + admin-consent + add to OAuth connection scopes |
