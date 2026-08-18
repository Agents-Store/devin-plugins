---
name: credential-tag-management
description: Credentials and tags management. This skill should be used when the user asks to create or manage credentials, list service connections, organize workflows with tags, or configure authentication.
---

# Credential & Tag Management

This skill covers managing n8n credentials (service integrations) and tags (workflow organization).

## Available Tools

| Tool | Description |
|------|-------------|
| `list_credentials` | List all credentials |
| `create_credential` | Create a new credential |
| `delete_credential` | Delete a credential |
| `list_tags` | List all tags |
| `create_tag` | Create a new tag |
| `update_tag` | Update a tag |
| `delete_tag` | Delete a tag |

## Credentials

### List Credentials
```
Tool: list_credentials
Input: {}

Returns: Array of { id, name, type, createdAt, updatedAt }
```

### Create Credential
```
Tool: create_credential
Input: {
  "name": "My API Key",
  "type": "httpHeaderAuth",
  "data": {
    "name": "Authorization",
    "value": "Bearer sk-..."
  }
}
```

### Common Credential Types

| Type | Use Case | Key Fields |
|------|----------|------------|
| httpHeaderAuth | API key in header | name, value |
| httpBasicAuth | Basic auth | user, password |
| httpQueryAuth | API key in query | name, value |
| oAuth2Api | OAuth 2.0 | clientId, clientSecret, accessTokenUrl, authUrl, scope |
| noOp | No auth needed | — |

### Credential Patterns

#### API Key in Header
```
Tool: create_credential
Input: {
  "name": "OpenAI API",
  "type": "httpHeaderAuth",
  "data": {
    "name": "Authorization",
    "value": "Bearer sk-..."
  }
}
```

#### Basic Auth
```
Tool: create_credential
Input: {
  "name": "Jenkins",
  "type": "httpBasicAuth",
  "data": {
    "user": "admin",
    "password": "token123"
  }
}
```

#### API Key in Query Parameter
```
Tool: create_credential
Input: {
  "name": "Weather API",
  "type": "httpQueryAuth",
  "data": {
    "name": "api_key",
    "value": "abc123"
  }
}
```

#### OAuth 2.0
```
Tool: create_credential
Input: {
  "name": "Google Sheets",
  "type": "oAuth2Api",
  "data": {
    "clientId": "xxx.apps.googleusercontent.com",
    "clientSecret": "xxx",
    "accessTokenUrl": "https://oauth2.googleapis.com/token",
    "authUrl": "https://accounts.google.com/o/oauth2/v2/auth",
    "scope": "https://www.googleapis.com/auth/spreadsheets"
  }
}
```

**OAuth2 workflow:**
1. Create credential with clientId, clientSecret, URLs
2. User authorizes via authUrl (generates auth code)
3. n8n exchanges code for access token automatically
4. Token is refreshed automatically when expired

### Delete Credential
```
Tool: delete_credential
Input: { "credential_id": "cred_abc123" }
```

## Tags

### List Tags
```
Tool: list_tags
Input: {}

Returns: Array of { id, name, createdAt }
```

### Create Tag
```
Tool: create_tag
Input: { "name": "production" }
```

### Update Tag
```
Tool: update_tag
Input: {
  "tag_id": "tag_abc123",
  "name": "production-v2"
}
```

### Delete Tag
```
Tool: delete_tag
Input: { "tag_id": "tag_abc123" }
```

## Common Workflows

### Set Up API Integration
```
1. list_credentials() -> Check if credential already exists
2. create_credential(name, type, data) -> Create credential
3. Reference credential in workflow nodes by name
```

### Organize Workflows with Tags
```
1. list_tags() -> See existing tags
2. create_tag("production") -> Create organizational tag
3. create_tag("staging") -> Create environment tag
4. Apply tags when creating/updating workflows
```

## Best Practices

1. **Name credentials descriptively** — "Slack Production Bot" not "API Key 1"
2. **Don't duplicate credentials** — check `list_credentials` before creating
3. **Use environment-based tags** — "production", "staging", "development"
4. **Use functional tags** — "data-sync", "notifications", "reporting"
5. **Clean up unused credentials** — delete when no longer needed
