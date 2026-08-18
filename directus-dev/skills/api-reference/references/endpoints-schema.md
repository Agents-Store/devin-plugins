# Schema API — Detailed Reference

## Collections

| Method | Path | Description |
|--------|------|-------------|
| GET | `/collections` | List all collections |
| POST | `/collections` | Create collection |
| GET | `/collections/{collection}` | Get collection info |
| PATCH | `/collections/{collection}` | Update collection |
| DELETE | `/collections/{collection}` | Delete collection |

### Create Collection

```bash
curl -X POST "${DIRECTUS_URL}/collections" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "articles",
    "schema": {},
    "meta": {
      "icon": "article",
      "note": "Blog articles",
      "singleton": false
    },
    "fields": [
      {
        "field": "title",
        "type": "string",
        "meta": { "interface": "input" },
        "schema": { "is_nullable": false }
      },
      {
        "field": "content",
        "type": "text",
        "meta": { "interface": "input-rich-text-md" }
      }
    ]
  }'
```

## Fields

| Method | Path | Description |
|--------|------|-------------|
| GET | `/fields` | List all fields (all collections) |
| GET | `/fields/{collection}` | List fields for collection |
| POST | `/fields/{collection}` | Create field |
| GET | `/fields/{collection}/{field}` | Get field info |
| PATCH | `/fields/{collection}/{field}` | Update field |
| DELETE | `/fields/{collection}/{field}` | Delete field |

### Create Field

```bash
curl -X POST "${DIRECTUS_URL}/fields/articles" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "field": "published_date",
    "type": "datetime",
    "meta": {
      "interface": "datetime",
      "display": "datetime",
      "width": "half"
    },
    "schema": {
      "is_nullable": true
    }
  }'
```

## Relations

| Method | Path | Description |
|--------|------|-------------|
| GET | `/relations` | List all relations |
| POST | `/relations` | Create relation |
| GET | `/relations/{collection}/{field}` | Get relation |
| PATCH | `/relations/{collection}/{field}` | Update relation |
| DELETE | `/relations/{collection}/{field}` | Delete relation |

### Create M2O Relation

```bash
curl -X POST "${DIRECTUS_URL}/relations" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "articles",
    "field": "author",
    "related_collection": "authors",
    "schema": { "on_delete": "SET NULL" },
    "meta": { "one_field": "articles" }
  }'
```

## Schema Migration

### Snapshot (Export)

```bash
# Get current schema as JSON
curl -s "${DIRECTUS_URL}/schema/snapshot" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" | jq . > snapshot.json
```

### Diff (Compare)

```bash
# Compare snapshot against current state
curl -s -X POST "${DIRECTUS_URL}/schema/diff" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @snapshot.json | jq . > diff.json
```

### Apply (Migrate)

```bash
# Apply diff to update schema
curl -s -X POST "${DIRECTUS_URL}/schema/apply" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @diff.json
```

### CI/CD Migration Workflow

```bash
#!/bin/bash
# Export from staging
curl -s "${STAGING_URL}/schema/snapshot" \
  -H "Authorization: Bearer ${STAGING_TOKEN}" > snapshot.json

# Generate diff against production
DIFF=$(curl -s -X POST "${PROD_URL}/schema/diff" \
  -H "Authorization: Bearer ${PROD_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @snapshot.json)

# Check if there are changes
if [ "$(echo $DIFF | jq '.data')" != "null" ]; then
  echo "Applying schema changes..."
  echo "$DIFF" | jq '.data' | curl -s -X POST "${PROD_URL}/schema/apply" \
    -H "Authorization: Bearer ${PROD_TOKEN}" \
    -H "Content-Type: application/json" \
    -d @-
  echo "Schema migration complete."
else
  echo "No schema changes to apply."
fi
```

## Extensions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/extensions` | List installed extensions |
| PATCH | `/extensions/{bundle}/{extension}` | Enable/disable extension |
