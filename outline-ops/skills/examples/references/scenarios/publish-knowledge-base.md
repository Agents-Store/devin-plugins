# Scenario: Publish a knowledge base

Stand up a new collection, fill it with nested documents, publish, share the homepage publicly, and star it. Assumes `setup` has run.

```bash
OUT="${OUTLINE_API_URL%/}"
H_AUTH="Authorization: Bearer ${OUTLINE_API_KEY}"
JSON="Content-Type: application/json"
ACC="Accept: application/json"
```

## 1. Create the collection

```bash
COLLECTION_ID=$(curl -s -X POST "${OUT}/collections.create" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d '{"name":"Employee Handbook","description":"Everything new hires need.","permission":"read","color":"#4E5C6E","icon":"book"}' \
  | jq -r '.data.id')
echo "collection: $COLLECTION_ID"
```
`permission:"read"` lets all members read by default; omit `permission` for a private collection. (→ `collections.md`)

## 2. Create the homepage (published)

```bash
HOME_ID=$(curl -s -X POST "${OUT}/documents.create" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"title\":\"Welcome\",\"text\":\"# Welcome to Acme\\n\\nStart here.\",\"collectionId\":\"${COLLECTION_ID}\",\"publish\":true}" \
  | jq -r '.data.id')
echo "home: $HOME_ID"
```

## 3. Create child documents under the homepage

```bash
for T in "Benefits" "Time Off" "IT Setup"; do
  curl -s -X POST "${OUT}/documents.create" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
    -d "{\"title\":\"${T}\",\"text\":\"# ${T}\\n\\nTODO\",\"collectionId\":\"${COLLECTION_ID}\",\"parentDocumentId\":\"${HOME_ID}\",\"publish\":true}" \
    | jq -r '.data | "created \(.title) → \(.id)"'
done
```
`parentDocumentId` nests them under Welcome. View the resulting tree with `collections.documents {"id":"…"}`.

## 4. Share the homepage publicly

```bash
SHARE_ID=$(curl -s -X POST "${OUT}/shares.create" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"documentId\":\"${HOME_ID}\"}" | jq -r '.data.id')
curl -s -X POST "${OUT}/shares.update" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"id\":\"${SHARE_ID}\",\"published\":true}" | jq '.data | {url, published}'
```
Shares start unpublished; publishing makes the link accessible without login. Revoke later with `shares.revoke`. (→ `sharing-access.md`)

## 5. Star the collection for quick access

```bash
curl -s -X POST "${OUT}/stars.create" -H "$H_AUTH" -H "$JSON" -H "$ACC" \
  -d "{\"collectionId\":\"${COLLECTION_ID}\"}" | jq '.data | {id}'
```

**Result:** a published Handbook collection with a homepage + three child docs, a public link to the homepage, and the collection starred in the sidebar.
