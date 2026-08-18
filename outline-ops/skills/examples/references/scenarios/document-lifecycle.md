# Scenario: Document lifecycle

Take one document through its whole life: draft → edit → move → archive → restore → trash → restore. Assumes `setup` has run.

```bash
OUT="${OUTLINE_API_URL%/}"
H_AUTH="Authorization: Bearer ${OUTLINE_API_KEY}"
JSON="Content-Type: application/json"
ACC="Accept: application/json"
```

## 1. Create a draft

```bash
DOC_ID=$(curl -s -X POST "${OUT}/documents.create" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"title\":\"Release Notes\",\"text\":\"# Release Notes\\n\\nDraft.\",\"collectionId\":\"${COLLECTION_ID}\"}" \
  | jq -r '.data.id')
```
No `publish` → it stays a draft, visible only to you.

## 2. Edit — append, then a surgical patch

```bash
# Append a section without resending the whole body
curl -s -X POST "${OUT}/documents.update" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${DOC_ID}\",\"text\":\"\\n## v1.2\\n- Fixed login\",\"editMode\":\"append\"}" >/dev/null

# Replace one phrase in place
curl -s -X POST "${OUT}/documents.update" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${DOC_ID}\",\"editMode\":\"patch\",\"findText\":\"Draft.\",\"text\":\"Published notes.\"}" >/dev/null
```
`editMode` options: `append`, `prepend`, `replace` (default), `patch` (needs `findText`). (→ `documents.md`)

## 3. Publish

```bash
curl -s -X POST "${OUT}/documents.update" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${DOC_ID}\",\"publish\":true}" | jq '.data | {id, title, publishedAt}'
```

## 4. Move to another collection

```bash
curl -s -X POST "${OUT}/documents.move" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${DOC_ID}\",\"collectionId\":\"${OTHER_COLLECTION_ID}\"}" | jq '.data.documents[0].id'
```

## 5. Archive, then restore

```bash
curl -s -X POST "${OUT}/documents.archive" -H "$H_AUTH" -H "$JSON" -H "$ACC" -d "{\"id\":\"${DOC_ID}\"}" >/dev/null
curl -s -X POST "${OUT}/documents.restore" -H "$H_AUTH" -H "$JSON" -H "$ACC" -d "{\"id\":\"${DOC_ID}\"}" | jq '.data | {id, archivedAt}'
```
Archived docs are hidden but still searchable and appear in `documents.archived`.

## 6. Trash, then restore from trash

```bash
# Moves to trash (recoverable ~30 days). Confirm with the user before deleting.
curl -s -X POST "${OUT}/documents.delete" -H "$H_AUTH" -H "$JSON" -H "$ACC" -d "{\"id\":\"${DOC_ID}\"}" >/dev/null
# Find it in trash and restore
curl -s -X POST "${OUT}/documents.deleted" -H "$H_AUTH" -H "$JSON" -H "$ACC" -d '{"limit":25}' | jq -r '.data[] | select(.id=="'"${DOC_ID}"'") | .title'
curl -s -X POST "${OUT}/documents.restore" -H "$H_AUTH" -H "$JSON" -H "$ACC" -d "{\"id\":\"${DOC_ID}\"}" | jq '.data | {id, deletedAt}'
```
To destroy immediately instead, `documents.delete {"id","permanent":true}` — irreversible, confirm first.

## 7. (optional) Inspect history

```bash
curl -s -X POST "${OUT}/revisions.list" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"documentId\":\"${DOC_ID}\",\"limit\":10}" | jq '.data[] | {id, createdAt}'
```
Restore to a past revision with `documents.restore {"id","revisionId"}`. (→ `revisions-templates-events.md`)
