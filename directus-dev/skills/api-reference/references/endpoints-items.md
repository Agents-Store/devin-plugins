# Items API — Detailed Reference

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/items/{collection}` | List items |
| POST | `/items/{collection}` | Create item(s) |
| PATCH | `/items/{collection}` | Batch update items |
| DELETE | `/items/{collection}` | Batch delete items |
| GET | `/items/{collection}/{id}` | Get single item |
| PATCH | `/items/{collection}/{id}` | Update single item |
| DELETE | `/items/{collection}/{id}` | Delete single item |

## Filtering (URL syntax)

### Basic Filter

```bash
curl "${DIRECTUS_URL}/items/posts?filter[status][_eq]=published" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

### Multiple Filters (AND)

```bash
curl "${DIRECTUS_URL}/items/posts?filter[status][_eq]=published&filter[date_created][_gte]=2024-01-01" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

### OR Filter

```bash
curl "${DIRECTUS_URL}/items/posts" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -G \
  --data-urlencode 'filter={"_or":[{"status":{"_eq":"published"}},{"featured":{"_eq":true}}]}'
```

### Relational Filter

```bash
curl "${DIRECTUS_URL}/items/posts?filter[author][name][_eq]=John" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

## Deep Queries (URL syntax)

```bash
curl "${DIRECTUS_URL}/items/posts?fields=title,comments.text&deep[comments][_limit]=5&deep[comments][_sort]=-date_created" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

## Aggregation

### Count All

```bash
curl "${DIRECTUS_URL}/items/orders?aggregate[count]=*" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

### Sum with GroupBy

```bash
curl "${DIRECTUS_URL}/items/orders?aggregate[sum]=total&aggregate[count]=*&groupBy[]=status" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}"
```

## Batch Operations

### Create Multiple

```bash
curl -X POST "${DIRECTUS_URL}/items/posts" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '[
    {"title": "Post 1", "status": "draft"},
    {"title": "Post 2", "status": "draft"}
  ]'
```

### Update Multiple by IDs

```bash
curl -X PATCH "${DIRECTUS_URL}/items/posts" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "keys": ["uuid-1", "uuid-2"],
    "data": {"status": "published"}
  }'
```

### Delete Multiple

```bash
curl -X DELETE "${DIRECTUS_URL}/items/posts" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '["uuid-1", "uuid-2"]'
```

## Export

```bash
# Export as CSV
curl "${DIRECTUS_URL}/utils/export/posts?fields=id,title,status" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -o posts.csv

# Export as JSON
curl "${DIRECTUS_URL}/items/posts?export=json&limit=-1" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -o posts.json
```

## Import

```bash
curl -X POST "${DIRECTUS_URL}/utils/import/posts" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -F "file=@data.csv"
```

## Files Upload

```bash
# Upload file
curl -X POST "${DIRECTUS_URL}/files" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -F "title=My Image" \
  -F "file=@image.jpg"

# Import from URL
curl -X POST "${DIRECTUS_URL}/files/import" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg", "data": {"title": "Imported Image"}}'
```

## Assets (File Content)

```bash
# Get original file
curl "${DIRECTUS_URL}/assets/{file-id}" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" -o file.jpg

# With transformations
curl "${DIRECTUS_URL}/assets/{file-id}?width=300&height=200&fit=cover&quality=80" \
  -H "Authorization: Bearer ${DIRECTUS_TOKEN}" -o thumb.jpg
```

### Transform Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `width` | number | Target width (px) |
| `height` | number | Target height (px) |
| `fit` | cover, contain, inside, outside | Resize fit mode |
| `quality` | 1-100 | JPEG/WebP quality |
| `format` | jpg, png, webp, avif | Output format |
| `withoutEnlargement` | true | Don't upscale |
