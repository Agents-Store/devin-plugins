# Scenario: Search & report

Find content, then build a small usage report: search, list by collection, view counts, insights, and the audit log. Assumes `setup` has run.

```bash
OUT="${OUTLINE_API_URL%/}"
H_AUTH="Authorization: Bearer ${OUTLINE_API_KEY}"
JSON="Content-Type: application/json"
ACC="Accept: application/json"
```

## 1. Full-text search with snippets

```bash
curl -s -X POST "${OUT}/documents.search" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d '{"query":"onboarding","limit":5,"sort":"relevance","direction":"DESC"}' \
  | jq -r '.data[] | "\(.ranking | .*1000 | floor) — \(.document.title): \(.context)"'
```
Returns `data[]` of `{context, ranking, document}`. Use `documents.search_titles` for a faster title-only match. (→ `documents.md`)

## 2. Most-recently-updated documents in a collection

```bash
curl -s -X POST "${OUT}/documents.list" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"collectionId\":\"${COLLECTION_ID}\",\"sort\":\"updatedAt\",\"direction\":\"DESC\",\"limit\":10}" \
  | jq -r '.data[] | "\(.updatedAt[0:10])  \(.title)"'
```

## 3. View counts for a document

```bash
curl -s -X POST "${OUT}/views.list" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"documentId\":\"${DOC_ID}\"}" \
  | jq -r '.data[] | "\(.user.name): \(.count) views (last \(.lastViewedAt[0:10]))"'
```
(→ `comments-stars-views.md`)

## 4. Activity insights for a document (Business/Enterprise)

```bash
curl -s -X POST "${OUT}/documents.insights" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${DOC_ID}\"}" \
  | jq -r '.data[] | "\(.date) views=\(.viewCount) editors=\(.editorCount) comments=\(.commentCount)"'
```
Defaults to the last 30 days; insights must be enabled on the document. (→ `documents.md`)

## 5. Audit log — who created documents this period

```bash
curl -s -X POST "${OUT}/events.list" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d '{"name":"documents.create","auditLog":true,"limit":50,"sort":"createdAt","direction":"DESC"}' \
  | jq -r '.data[] | "\(.createdAt[0:19])  \(.actor.name)  \(.data.title // .documentId)"'
```
Filter by `actorId` for one user's activity, or `collectionId`/`documentId` to scope to an object. (→ `revisions-templates-events.md`)

## 6. Paginate a large report

```bash
OFFSET=0
while :; do
  PAGE=$(curl -s -X POST "${OUT}/documents.list" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
    -d "{\"limit\":100,\"offset\":${OFFSET}}")
  echo "$PAGE" | jq -r '.data[] | .title'
  COUNT=$(echo "$PAGE" | jq '.data | length')
  [ "$COUNT" -lt 100 ] && break
  OFFSET=$((OFFSET+100))
done
```
Or follow `pagination.nextPath` from each response.
