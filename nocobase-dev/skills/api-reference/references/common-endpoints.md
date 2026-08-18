# Common endpoint recipes

Copy-paste recipes for the highest-traffic operations. Replace `${NB_URL}` with your host and `${TOKEN}` with the bearer token from the `auth` skill. All examples assume `Content-Type: application/json` for `POST` payloads.

```bash
H='Authorization: Bearer '"${TOKEN}"
J='Content-Type: application/json'
```

## 1. App lifecycle

```bash
# Health / metadata
curl -H "$H" "${NB_URL}/api/app:getInfo"

# Force restart (admin-level, useful after schema migration)
curl -X POST -H "$H" "${NB_URL}/api/app:restart"

# Clear server cache
curl -X POST -H "$H" "${NB_URL}/api/app:clearCache"
```

## 2. Plugin manager

```bash
# List all plugins
curl -H "$H" "${NB_URL}/api/pm:list"

# Enable / disable
curl -X POST -H "$H" -H "$J" \
     -d '{"name":"api-keys"}' \
     "${NB_URL}/api/pm:enable"

curl -X POST -H "$H" -H "$J" \
     -d '{"name":"api-keys"}' \
     "${NB_URL}/api/pm:disable"
```

## 3. Collection schema

```bash
# Create a collection with two fields
curl -X POST -H "$H" -H "$J" -d '{
  "name": "posts",
  "title": "Posts",
  "fields": [
    { "type": "string", "name": "title", "uiSchema": { "title": "Title" } },
    { "type": "text",   "name": "body",  "uiSchema": { "title": "Body"  } }
  ]
}' "${NB_URL}/api/collections:create"

# List collections
curl -H "$H" "${NB_URL}/api/collections:list?pageSize=200"
```

## 4. Records — CRUD on a user-defined collection

```bash
# Create
curl -X POST -H "$H" -H "$J" \
     -d '{"title":"hello","body":"first post"}' \
     "${NB_URL}/api/posts:create"

# List with filter + relation eager-load
curl -H "$H" "${NB_URL}/api/posts:list?\
filter=%7B%22title%22%3A%7B%22%24includes%22%3A%22hello%22%7D%7D&\
appends=author&page=1&pageSize=20"

# Get one by primary key
curl -H "$H" "${NB_URL}/api/posts:get?filterByTk=42"

# Update
curl -X POST -H "$H" -H "$J" \
     -d '{"title":"hello, edited"}' \
     "${NB_URL}/api/posts:update?filterByTk=42"

# Delete
curl -X POST -H "$H" \
     "${NB_URL}/api/posts:destroy?filterByTk=42"
```

## 5. Relations

```bash
# Eager-load author and tags
curl -H "$H" "${NB_URL}/api/posts:list?appends=author&appends=tags"

# Add tags to post 42 (m2m)
curl -X POST -H "$H" -H "$J" \
     -d '{"values":[1,2,3]}' \
     "${NB_URL}/api/posts/42/tags:add"

# Replace tag set on post 42
curl -X POST -H "$H" -H "$J" \
     -d '{"values":[5,6]}' \
     "${NB_URL}/api/posts/42/tags:set"
```

## 6. Workflows

```bash
# List
curl -H "$H" "${NB_URL}/api/workflows:list"

# Manually trigger a workflow (key or id)
curl -X POST -H "$H" -H "$J" \
     -d '{"data": {"orderId": 100}}' \
     "${NB_URL}/api/workflows:trigger?filterByTk=order-fulfilment"

# Recent executions
curl -H "$H" "${NB_URL}/api/executions:list?pageSize=50&sort=-createdAt"

# Cancel a stuck execution
curl -X POST -H "$H" \
     "${NB_URL}/api/executions:cancel?filterByTk=12345"
```

## 7. ACL — roles and membership

```bash
# Roles
curl -H "$H" "${NB_URL}/api/roles:list"

# Attach a role to a user
curl -X POST -H "$H" -H "$J" \
     -d '{"values":[{"name":"editor"}]}' \
     "${NB_URL}/api/users/7/roles:add"

# Set the default role
curl -X POST -H "$H" -H "$J" \
     -d '{"name":"member"}' \
     "${NB_URL}/api/roles:setDefaultRole"
```

## 8. API keys

```bash
# Create a key (requires the API Keys plugin enabled)
curl -X POST -H "$H" -H "$J" \
     -d '{"name":"agent-bot","role":"member"}' \
     "${NB_URL}/api/apiKeys:create"

# List
curl -H "$H" "${NB_URL}/api/apiKeys:list"

# Revoke
curl -X POST -H "$H" \
     "${NB_URL}/api/apiKeys:destroy?filterByTk=3"
```

## 9. UI schemas (low-level, used by ui-builder)

```bash
# Read a UI schema by uid
curl -H "$H" "${NB_URL}/api/uiSchemas:getJsonSchema/<uid>"

# Patch
curl -X POST -H "$H" -H "$J" \
     -d '{"x-component-props":{"title":"New title"}}' \
     "${NB_URL}/api/uiSchemas:patch/<uid>"
```

For pages, blocks, popups, tabs, and linkage rules prefer the `flowSurfaces` resource — the `nocobase-ui-builder` skill has the full playbook.

## 10. Filter language quick reference

```jsonc
{
  "$and": [
    { "title":     { "$includes":  "hello" } },
    { "createdAt": { "$gte":       "2026-01-01" } },
    { "status":    { "$in":        ["draft","review"] } }
  ]
}
```

URL-encode and pass as `?filter=…`. Operators: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$notIn`, `$includes`, `$notIncludes`, `$startsWith`, `$endsWith`, `$null`, `$notNull`, `$between`, `$and`, `$or`. Full grammar lives in `nocobase-data-modeling`.
