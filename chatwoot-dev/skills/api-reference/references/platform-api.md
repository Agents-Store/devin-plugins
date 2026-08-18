# Chatwoot Platform API

Installation-level super-admin API for multi-account provisioning. Auth: `api_access_token` header with the **platform app** token. Base: `${CHATWOOT_BASE_URL}/platform/api/v1`.

Authoritative schemas: `openapi/platform_swagger.json` (8 paths, 17 operations). Grep it for request bodies, query params, and response shapes.

```bash
jq -r '.paths | keys[]' openapi/platform_swagger.json
```

## Account Users

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| DELETE | `/accounts/{account_id}/account_users` | `delete-an-account-user` | Delete an Account User |
| GET | `/accounts/{account_id}/account_users` | `list-all-account-users` | List all Account Users |
| POST | `/accounts/{account_id}/account_users` | `create-an-account-user` | Create an Account User |

## Accounts

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| POST | `/accounts` | `create-an-account` | Create an Account |
| DELETE | `/accounts/{account_id}` | `delete-an-account` | Delete an Account |
| GET | `/accounts/{account_id}` | `get-details-of-an-account` | Get an account details |
| PATCH | `/accounts/{account_id}` | `update-an-account` | Update an account |

## AgentBots

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/agent_bots` | `list-all-agent-bots` | List all AgentBots |
| POST | `/agent_bots` | `create-an-agent-bot` | Create an Agent Bot |
| DELETE | `/agent_bots/{id}` | `delete-an-agent-bot` | Delete an AgentBot |
| GET | `/agent_bots/{id}` | `get-details-of-a-single-agent-bot` | Get an agent bot details |
| PATCH | `/agent_bots/{id}` | `update-an-agent-bot` | Update an agent bot |

## Users

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| POST | `/users` | `create-a-user` | Create a User |
| DELETE | `/users/{id}` | `delete-a-user` | Delete a User |
| GET | `/users/{id}` | `get-details-of-a-user` | Get an user details |
| PATCH | `/users/{id}` | `update-a-user` | Update a user |
| GET | `/users/{id}/login` | `get-sso-url-of-a-user` | Get User SSO Link |
