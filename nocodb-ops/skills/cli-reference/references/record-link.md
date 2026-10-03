# Records, Links, Attachments, Actions -- curl Recipes

Recipes on the Data API v3. Each block maps to a command of the official `nocodb.sh` script (see the parent skill's command map). The `nocodb_api METHOD /path ['body']` wrapper is defined in `../SKILL.md` -- paths are under `${NOCODB_URL}/api/v3`. The MCP equivalents (`queryRecords`, `createRecords`, `linkRecords`, ...) are described in **mcp-patterns**.

## Records

```bash
# List — query parameters: where, sort, fields, page, pageSize, viewId, nestedPage
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/records"                                  # first page
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/records?page=2&pageSize=50"
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/records?where=(status,eq,active)"
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/records?sort=%5B%7B%22field%22%3A%22Name%22%2C%22direction%22%3A%22desc%22%7D%5D"
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/records?fields=Name,Email&viewId=$VIEW_ID"

# Get one record
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/records/31"
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/records/31?fields=Name,Email"

# Create — body is an array of {fields}
nocodb_api POST /data/$BASE_ID/$TABLE_ID/records '[{"fields":{"Name":"Alice"}}]'

# Update — body is an array of {id, fields}; only the fields you send change
nocodb_api PATCH /data/$BASE_ID/$TABLE_ID/records '[{"id":31,"fields":{"Status":"done"}}]'

# Upsert — insert-or-update on 1-3 business-key fields (REST: at most 10 records per call)
nocodb_api POST /data/$BASE_ID/$TABLE_ID/records/upsert \
  '{"fieldsToMergeOn":["Email"],"records":[{"fields":{"Email":"alice@example.com","Status":"active"}}]}'

# Delete — body is an array of {id}
nocodb_api DELETE /data/$BASE_ID/$TABLE_ID/records '[{"id":31},{"id":32}]'

# Count
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/count"
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/count?where=(status,eq,active)"
```

Notes:

- `sort` is a JSON array of `{"field","direction"}` objects (`asc` | `desc`) -- or a single such object -- and must be URL-encoded. If `viewId` is also given, `sort` takes precedence over the view's sorting.
- `where` uses the string grammar in `filter-syntax.md` and is applied on top of the view's filters when `viewId` is given. URL-encode spaces, `~` and quotes (`curl --data-urlencode` with `-G` does it for you).
- Field names in `where` are case-sensitive; dates need a sub-operator (`exactDate`) and ranges are two bounds.
- Page size limits on the REST API depend on the deployment -- read `next` in the response and follow it instead of computing offsets; `next` is `null` on the last page.
- The MCP record tools are stricter than REST: **at most 100 records per write call**. For scripts, keep to the same ceiling.

```bash
# Safer than hand-encoding: let curl encode the query parameters
curl -sS -G -H "xc-token: ${NOCODB_TOKEN}" \
  --data-urlencode 'where=(Due Date,gte,exactDate,2026-06-01)~and(Status,neq,Done)' \
  --data-urlencode 'sort=[{"field":"Due Date","direction":"asc"}]' \
  --data-urlencode 'pageSize=50' \
  "${NOCODB_URL}/api/v3/data/$BASE_ID/$TABLE_ID/records"
```

### Query parameters of the list endpoint

| Parameter | Default | Description |
|-----------|---------|-------------|
| `where` | -- | Filter expression (`filter-syntax.md`) |
| `sort` | -- | JSON array of `{field, direction}` |
| `fields` | all | Comma-separated field names, or a JSON array |
| `page` | 1 | Page number |
| `pageSize` | deployment default | Records per page |
| `viewId` | -- | Apply a view's filters, sorts and field visibility |
| `nestedPage` | 1 | Page of nested linked-record data |
| `linksAsLtar` | -- | `true`: `Links` fields return linked records instead of a count |

## Linked Records

```bash
# List linked records of one row through a link field (query: fields, sort, where, page, pageSize)
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/links/$LINK_FIELD_ID/31"
nocodb_api GET "/data/$BASE_ID/$TABLE_ID/links/$LINK_FIELD_ID/31?pageSize=25&sort=%5B%7B%22field%22%3A%22CreatedAt%22%2C%22direction%22%3A%22desc%22%7D%5D"

# Add links — one object or an array of {id}; existing links are kept
nocodb_api POST   /data/$BASE_ID/$TABLE_ID/links/$LINK_FIELD_ID/31 '[{"id":"42"}]'

# Remove links
nocodb_api DELETE /data/$BASE_ID/$TABLE_ID/links/$LINK_FIELD_ID/31 '[{"id":"42"}]'
```

The link body accepts up to 1000 entries on REST. The MCP tools `linkRecords` / `unlinkRecords` take at most 100 records with at most 100 links each.

## Attachments

```bash
# Upload a file into an Attachment cell — body is JSON with base64 content
nocodb_api POST /data/$BASE_ID/$TABLE_ID/records/31/fields/$ATTACHMENT_FIELD_ID/upload "$(jq -n \
  --arg name "report.pdf" --arg type "application/pdf" --arg data "$(base64 -w0 ./report.pdf)" \
  '{filename:$name, contentType:$type, file:$data}')"
```

Body keys: `filename`, `contentType`, `file` (base64). On macOS use `base64 -i ./report.pdf` instead of `base64 -w0`. To read an attachment back through MCP use `readAttachment`.

## Button Actions

```bash
# Trigger a Button field for up to 25 rows at once
nocodb_api POST /data/$BASE_ID/$TABLE_ID/actions/$BUTTON_FIELD_ID '{"rowIds":["31","32"]}'
```

Body: `rowIds` (1-25 record IDs) and an optional `"preview": true` for a dry run.
