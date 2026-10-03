# API Keys, OAuth & Data Attributes

Personal API keys, OAuth client applications, a user's authorized OAuth grants, and custom document metadata fields. Every endpoint is `POST ${OUTLINE_API_URL%/}/<method>` with a JSON body and the Bearer header.

## API keys

Personal API keys (`ol_api_…`) used as the Bearer token. The UI lives under **Settings → API & Apps**; the same management is available through the API.

| Method | Purpose & key fields |
|--------|----------------------|
| `apiKeys.create` | Mint a key for the current user. `{"name"(required, ≤255),"expiresAt"?(ISO date-time),"scope"?(string[])}` → `{id, name, scope, last4, value, expiresAt, …}`. **The full `value` is returned only in this response and can never be retrieved again** — capture it straight into the secret store / env var and do not print or log it. |
| `apiKeys.list` | List the current user's keys (an **admin** sees all users' keys; `userId` narrows to one user, admin only). Pagination + sorting + `{"userId"?,"query"?(name filter)}`. The secret `value` is never included. |
| `apiKeys.delete` | Permanently revoke a key; every later request with it returns `401`. `{"id"}`. **Confirm first** — and do not revoke the key you are currently using. |

- `scope` narrows a key: global `read` / `write`, namespaced (`documents:read`, `collections:write`), a single endpoint (`documents.info`) or a wildcard (`documents.*`, `users.*`). Omit `scope` for a full-access key. Outline v1.10.1 validates key scopes at the model layer, so a scoped key that used to work may start returning `403` — re-check it after a server upgrade.
- Give each key an identifiable `name` (one per integration) and a sensible `expiresAt` so keys can be rotated and traced; rotate by `apiKeys.create` → switch the integration → `apiKeys.delete` the old one.

## OAuth clients

An OAuth client is an application that can authenticate users and call the API on their behalf.

| Method | Purpose & key fields |
|--------|----------------------|
| `oauthClients.info` | Retrieve a client. One of `{"id"}` or `{"clientId"}` (the public identifier). |
| `oauthClients.list` | List clients accessible to the user (own + published). Pagination. |
| `oauthClients.create` | `{"name"(required),"redirectUris"(required, string[]),"description"?,"developerName"?,"developerUrl"?,"avatarUrl"?,"published"?}`. |
| `oauthClients.update` | `{"id"}` + any of the create fields. |
| `oauthClients.rotate_secret` | Generate a new client secret; the old one is invalidated immediately. `{"id"}`. Update your app with the new secret right away. |
| `oauthClients.delete` | Permanently delete the client and revoke its tokens. `{"id"}`. **Confirm first.** |

## OAuth authentications

These represent third-party applications the current user has authorized to access their account.

| Method | Purpose & key fields |
|--------|----------------------|
| `oauthAuthentications.list` | List the user's OAuth authentications. Pagination. |
| `oauthAuthentications.delete` | Revoke an application's access. `{"oauthClientId"(required),"scope"?(string[])}`. |

## Data attributes (Business / Enterprise)

Custom structured metadata fields (e.g. Status, Priority) that can be attached to documents. **Business/Enterprise feature; only admins can create/update/delete.** `dataType` is one of `string`, `number`, `boolean`, `list`.

| Method | Purpose & key fields |
|--------|----------------------|
| `dataAttributes.info` | Retrieve one. `{"id"}`. |
| `dataAttributes.list` | List all. Pagination + sorting. |
| `dataAttributes.create` | `{"name"(required),"dataType"(required),"description"?,"options"?(for `list`: `{options:[{value,color}]}` + optional `icon`),"pinned"?}`. |
| `dataAttributes.update` | `{"id","name"(required)}` + `{"description"?,"options"?,"pinned"?}`. **`dataType` cannot be changed** after creation. |
| `dataAttributes.delete` | `{"id"}`. |

To set attribute values on a document, pass `dataAttributes:[{"dataAttributeId","value"}]` to `documents.create` / `documents.update` (→ `documents.md`).

## Notes

- Treat `apiKeys.delete` like `oauthClients.delete`: anything still using the key stops working.
- Treat `oauthClients.rotate_secret` and `oauthClients.delete` as high-impact — they break any integration using the old secret/client.
- `dataAttributes.*` and `documents.answerQuestion` are the gated (Business/Enterprise) parts of the API; on lower plans they return `403`/`402`-style errors.
- For exact schemas, search `operationId: apiKeys…` / `oauthClients…` / `oauthAuthentications…` / `dataAttributes…` in `outline-openapi.yml`.
