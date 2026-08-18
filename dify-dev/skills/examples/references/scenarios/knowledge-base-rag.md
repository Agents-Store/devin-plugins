# Scenario: Knowledge base RAG pipeline

Create a knowledge base, ingest a document, wait for indexing, and test retrieval — entirely
via the Knowledge Base / Datasets API. Uses a **Knowledge API key** (`dataset-…`), not an
app key.

```bash
BASE=https://api.dify.ai/v1          # or https://your-host/v1
KEY=dataset-XXXXXXXXXXXXXXXXXXXX     # Knowledge → API key
```

## 1. Create a knowledge base (knowledge-base skill)

```bash
curl -X POST "$BASE/datasets" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data '{ "name": "Product Docs", "permission": "only_me" }'
# → { "id": "<DSID>", ... }
```

## 2. Ingest a document by text

```bash
DSID=<dataset_id-from-step-1>

curl -X POST "$BASE/datasets/$DSID/document/create-by-text" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "FAQ",
    "text": "Our support hours are 9am to 5pm on weekdays. We are closed on holidays.",
    "indexing_technique": "high_quality",
    "process_rule": { "mode": "automatic" }
  }'
# → { "document": { "id": "<DOCID>", ... }, "batch": "<BATCH>" }
```

To ingest a file instead:

```bash
curl -X POST "$BASE/datasets/$DSID/document/create-by-file" \
  --header "Authorization: Bearer $KEY" \
  --form 'data={"indexing_technique":"high_quality","process_rule":{"mode":"automatic"}};type=text/plain' \
  --form 'file=@/path/to/handbook.pdf'
```

## 3. Wait for indexing to complete

```bash
BATCH=<batch-from-step-2>

curl "$BASE/datasets/$DSID/documents/$BATCH/indexing-status" \
  --header "Authorization: Bearer $KEY"
# poll until data[].indexing_status == "completed"
```

## 4. Test retrieval

```bash
curl -X POST "$BASE/datasets/$DSID/retrieve" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "What are your support hours?",
    "retrieval_model": {
      "search_method": "hybrid_search",
      "top_k": 3,
      "score_threshold_enabled": true,
      "score_threshold": 0.4
    }
  }'
# → { "records": [ { "segment": { "content": "..." }, "score": 0.9 } ] }
```

## 5. (Optional) Inspect / edit chunks

```bash
DOCID=<document_id>

# List chunks
curl "$BASE/datasets/$DSID/documents/$DOCID/segments" \
  --header "Authorization: Bearer $KEY"

# Add a chunk
curl -X POST "$BASE/datasets/$DSID/documents/$DOCID/segments" \
  --header "Authorization: Bearer $KEY" \
  --header 'Content-Type: application/json' \
  --data '{ "segments": [ { "content": "Holiday schedule: closed Dec 25.", "keywords": ["holiday"] } ] }'
```

## Notes

- Use the **dataset** key here; app keys return 401/403.
- `high_quality` indexing needs an embedding model configured in the workspace.
- Don't delete a document while it's indexing — wait for `completed` (else 403
  `document_indexing`).
- Once the knowledge base is attached to an app in Dify Studio, the app's `/chat-messages`
  responses will include `retriever_resources` citations in `message_end`.
