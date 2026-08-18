# Scenario 1 — Define a collection and write a record (REST API)

Goal: create a `posts` collection with two fields, insert one record, list with a filter, and verify via the CLI.

## Prerequisites

- A bearer token (API Key path is fine — see `auth` skill).
- Shell environment:

  ```bash
  export NB_URL="https://app.example.com"
  export TOKEN="<your-bearer-token>"
  H='Authorization: Bearer '"${TOKEN}"
  J='Content-Type: application/json'
  ```

## 1. Create the collection

```bash
curl -X POST -H "$H" -H "$J" -d '{
  "name": "posts",
  "title": "Posts",
  "fields": [
    {
      "type": "string",
      "name": "title",
      "uiSchema": { "type": "string", "x-component": "Input", "title": "Title" }
    },
    {
      "type": "text",
      "name": "body",
      "uiSchema": { "type": "string", "x-component": "Input.TextArea", "title": "Body" }
    }
  ]
}' "${NB_URL}/api/collections:create"
```

Expected: `{"data": { "name": "posts", … }}` with HTTP 200.

## 2. Insert a record

```bash
curl -X POST -H "$H" -H "$J" \
     -d '{"title":"hello","body":"first post"}' \
     "${NB_URL}/api/posts:create"
```

Capture the returned `data.id` — call it `${POST_ID}`.

## 3. List with a filter

URL-encoded filter for `title` containing `hello`:

```bash
FILTER='%7B%22title%22%3A%7B%22%24includes%22%3A%22hello%22%7D%7D'
curl -H "$H" "${NB_URL}/api/posts:list?filter=${FILTER}&page=1&pageSize=20"
```

Expected: a `data` array containing the record from step 2 and a `meta` object with `count: 1`.

## 4. Get the record by primary key

```bash
curl -H "$H" "${NB_URL}/api/posts:get?filterByTk=${POST_ID}"
```

## 5. Verify from the CLI

```bash
nb api collections list | grep -E '\bposts\b'
```

Should print the `posts` row. If the schema doesn't show up, run `nb api app:clearCache` then retry — schema reads are cached.

## 6. Clean up

```bash
# Delete the record
curl -X POST -H "$H" \
     "${NB_URL}/api/posts:destroy?filterByTk=${POST_ID}"

# Drop the collection
curl -X POST -H "$H" -H "$J" \
     -d '{"name":"posts"}' \
     "${NB_URL}/api/collections:destroy"
```

## When to deviate

- If you also need relations, fields under `nocobase-data-modeling` cover hasMany/belongsToMany payloads.
- For seeded sample data at scale, prefer a `nb migration import` over hundreds of `:create` calls — see `nocobase-publish-manage`.
- If the collection already exists, switch to `:update` with `filterByTk: "<name>"` against `/api/collections:update`.
