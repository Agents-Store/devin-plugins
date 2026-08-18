# Dify Knowledge Base — Documents & Segments endpoints

All paths relative to the base URL. Use a **Knowledge API key**:
`Authorization: Bearer dataset-XXXX`.

## Contents

- [Documents](#documents) — create (text/file), update, list, indexing-status, delete, batch status, upload-file
- [Segments (chunks)](#segments-chunks) — list, create, update, delete, child chunks
- [Document `doc_form` values](#document-doc_form-values)

---

## Documents

### POST /datasets/{dataset_id}/document/create-by-text

Create a document from raw text.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | Document name |
| `text` | string | yes | Content |
| `indexing_technique` | string | yes | `high_quality` or `economy` |
| `doc_form` | string | no | `text_model`, `hierarchical_model`, `qa_model` |
| `doc_language` | string | no | For `qa_model`, e.g. `English` |
| `process_rule` | object | yes | `{ "mode": "automatic" }` or a custom rule (see below) |

```bash
curl -X POST 'https://api.dify.ai/v1/datasets/{dataset_id}/document/create-by-text' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "FAQ",
    "text": "Q: Hours? A: 9-5 weekdays.",
    "indexing_technique": "high_quality",
    "process_rule": { "mode": "automatic" }
  }'
```

```json
{ "document": { "id": "...", "name": "FAQ", "indexing_status": "waiting", ... }, "batch": "..." }
```

**Custom `process_rule`:**

```json
{
  "mode": "custom",
  "rules": {
    "pre_processing_rules": [
      { "id": "remove_extra_spaces", "enabled": true },
      { "id": "remove_urls_emails", "enabled": false }
    ],
    "segmentation": { "separator": "\n", "max_tokens": 500 }
  }
}
```

### POST /datasets/{dataset_id}/document/create-by-file

Create a document from an uploaded file. Multipart: a `data` JSON part + the `file` part.

```bash
curl -X POST 'https://api.dify.ai/v1/datasets/{dataset_id}/document/create-by-file' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --form 'data={"indexing_technique":"high_quality","process_rule":{"mode":"automatic"}};type=text/plain' \
  --form 'file=@/path/to/doc.pdf'
```

### POST /datasets/{dataset_id}/documents/{document_id}/update-by-text

Update a document's content/name. Same body shape as create-by-text (fields optional).

### POST /datasets/{dataset_id}/documents/{document_id}/update-by-file

Replace a document's file. Multipart like create-by-file.

### GET /datasets/{dataset_id}/documents

List documents. Query: `page`, `limit`, `keyword`.

```bash
curl 'https://api.dify.ai/v1/datasets/{dataset_id}/documents?page=1&limit=20' \
  --header 'Authorization: Bearer dataset-XXXX'
```

### GET /datasets/{dataset_id}/documents/{batch}/indexing-status

Poll indexing progress using the `batch` from create.

```bash
curl 'https://api.dify.ai/v1/datasets/{dataset_id}/documents/{batch}/indexing-status' \
  --header 'Authorization: Bearer dataset-XXXX'
```

```json
{ "data": [ { "id": "...", "indexing_status": "completed",
  "completed_segments": 10, "total_segments": 10 } ] }
```

`indexing_status`: `waiting` → `parsing` → `cleaning` → `splitting` → `indexing` →
`completed` (or `error` / `paused`).

### DELETE /datasets/{dataset_id}/documents/{document_id}

Delete a document. Returns 204. Cannot delete while it is indexing (403 `document_indexing`).

### PATCH /datasets/{dataset_id}/documents/status/{action}

Batch enable/disable/archive. `{action}` ∈ `enable` / `disable` / `archive` / `un_archive`.

```bash
curl -X PATCH 'https://api.dify.ai/v1/datasets/{dataset_id}/documents/status/disable' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "document_ids": ["id1", "id2"] }'
```

### GET /datasets/{dataset_id}/documents/{document_id}/upload-file

Get info about the original uploaded file backing a document.

---

## Segments (chunks)

### GET /datasets/{dataset_id}/documents/{document_id}/segments

List chunks. Query: `keyword`, `status` (e.g. `completed`), `page`, `limit`.

```bash
curl 'https://api.dify.ai/v1/datasets/{dataset_id}/documents/{document_id}/segments' \
  --header 'Authorization: Bearer dataset-XXXX'
```

```json
{ "data": [ { "id": "...", "position": 1, "content": "...", "word_count": 3,
  "tokens": 5, "keywords": [], "enabled": true, "status": "completed" } ],
  "doc_form": "text_model" }
```

### POST /datasets/{dataset_id}/documents/{document_id}/segments

Add one or more chunks.

```bash
curl -X POST 'https://api.dify.ai/v1/datasets/{dataset_id}/documents/{document_id}/segments' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{
    "segments": [
      { "content": "Hours are 9-5 weekdays.", "answer": "", "keywords": ["hours"] }
    ]
  }'
```

For `qa_model` documents, set both `content` (question) and `answer`.

### POST /datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}

Update a chunk.

```bash
curl -X POST 'https://api.dify.ai/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "segment": { "content": "Updated content", "enabled": true, "keywords": ["hours"] } }'
```

### DELETE /datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}

Delete a chunk. Returns 204.

### Child chunks (hierarchical / parent-child mode)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `.../segments/{segment_id}/child_chunks` | GET | List child chunks |
| `.../segments/{segment_id}/child_chunks` | POST | Create a child chunk (`{ "content": "..." }`) |
| `.../segments/{segment_id}/child_chunks/{child_chunk_id}` | PATCH | Update a child chunk |
| `.../segments/{segment_id}/child_chunks/{child_chunk_id}` | DELETE | Delete a child chunk |

```bash
curl -X POST \
  'https://api.dify.ai/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "content": "child chunk text" }'
```

---

## Document `doc_form` values

| Value | Meaning |
|-------|---------|
| `text_model` | Plain text chunks (default) |
| `hierarchical_model` | Parent-child chunking (enables child chunks) |
| `qa_model` | Question/answer chunks (requires `doc_language`) |
