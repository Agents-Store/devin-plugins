---
name: knowledge-base
description: >
  This skill should be used when the user asks to work with Dify "knowledge base",
  "datasets API", "create a dataset", "upload a document to Dify", "add documents to a
  knowledge base", "segments / chunks", "retrieve from a Dify knowledge base", "test
  retrieval", or RAG ingestion. Covers the standalone Knowledge Base / Datasets API.
---

# Dify — Knowledge Base / Datasets API

A **separate API** from the app Service API, for managing knowledge bases (datasets),
documents, and chunks (segments). Used by RAG-enabled apps. Authentication is the same
Bearer pattern, but with a **Knowledge API key** (Dify → Knowledge → API), not an app key.

Base URL is the same as the Service API (`https://api.dify.ai/v1` or self-hosted
`https://{host}/v1`). For auth fundamentals see the `setup` skill.

> "Dataset" and "knowledge base" are the same object. The `dataset_id` equals the
> `knowledge_base_id` you see in app configs.

## Quick map

| Group | Endpoints | Reference |
|-------|-----------|-----------|
| Datasets | create / list / get / update / delete / **retrieve** | [references/datasets.md](references/datasets.md) |
| Documents | create (text/file) / list / get / update / delete / indexing-status / batch | [references/documents-segments.md](references/documents-segments.md) |
| Segments (chunks) | list / create / get / update / delete + child chunks | [references/documents-segments.md](references/documents-segments.md) |
| Tags / Metadata / Models | dataset tags, metadata schema, embedding models | below |

## Most common flow (ingest → index → retrieve)

```bash
# 1) Create a knowledge base
curl -X POST 'https://api.dify.ai/v1/datasets' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "name": "Product Docs", "permission": "only_me" }'
# → { "id": "<dataset_id>", ... }

# 2) Add a document by text (creates an indexing batch)
curl -X POST 'https://api.dify.ai/v1/datasets/{dataset_id}/document/create-by-text' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "FAQ",
    "text": "Q: Hours? A: 9-5 weekdays.",
    "indexing_technique": "high_quality",
    "process_rule": { "mode": "automatic" }
  }'
# → { "document": { "id": "<document_id>", ... }, "batch": "<batch>" }

# 3) Poll indexing status
curl 'https://api.dify.ai/v1/datasets/{dataset_id}/documents/{batch}/indexing-status' \
  --header 'Authorization: Bearer dataset-XXXX'

# 4) Test retrieval
curl -X POST 'https://api.dify.ai/v1/datasets/{dataset_id}/retrieve' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "query": "What are your hours?", "retrieval_model": { "top_k": 3 } }'
```

See the references for every field and the full document/segment lifecycle.

## Tags (knowledge type tags)

```bash
# List tags bound to a dataset
curl 'https://api.dify.ai/v1/datasets/{dataset_id}/tags' \
  --header 'Authorization: Bearer dataset-XXXX'
```

Workspace-level tag management lives under `/datasets/tags` (`GET` list, `POST` create,
`PATCH` rename, `DELETE` remove) plus `/datasets/tags/binding` and `/datasets/tags/unbinding`
to attach/detach tags to a dataset.

## Metadata

```bash
# List a dataset's metadata fields
curl 'https://api.dify.ai/v1/datasets/{dataset_id}/metadata' \
  --header 'Authorization: Bearer dataset-XXXX'
```

`POST /datasets/{dataset_id}/metadata` creates a field; `PATCH`/`DELETE`
`/datasets/{dataset_id}/metadata/{metadata_id}` rename/remove; `POST
/datasets/{dataset_id}/documents/metadata` assigns metadata values to documents;
`POST /datasets/{dataset_id}/metadata/built-in/{action}` toggles built-in metadata.

## Embedding models

```bash
# Text-embedding models available for indexing
curl 'https://api.dify.ai/v1/workspaces/current/models/model-types/text-embedding' \
  --header 'Authorization: Bearer dataset-XXXX'
```

## Endpoint summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/datasets` | GET / POST | List / create knowledge bases |
| `/datasets/{id}` | GET / PATCH / DELETE | Get / update / delete a knowledge base |
| `/datasets/{id}/retrieve` | POST | Test retrieval (RAG query) |
| `/datasets/{id}/document/create-by-text` | POST | Add a document from text |
| `/datasets/{id}/document/create-by-file` | POST | Add a document from a file |
| `/datasets/{id}/documents` | GET | List documents |
| `/datasets/{id}/documents/{batch}/indexing-status` | GET | Indexing progress |
| `/datasets/{id}/documents/{document_id}` | DELETE | Delete a document |
| `/datasets/{id}/documents/{document_id}/segments` | GET / POST | List / add chunks |
| `/datasets/{id}/documents/{document_id}/segments/{segment_id}` | POST / DELETE | Update / delete a chunk |
| `/datasets/{id}/tags` | GET | Tags bound to a dataset |
| `/datasets/{id}/metadata` | GET / POST | Metadata schema |

Full parameter tables and the rest of the document/segment endpoints are in the two
reference files linked above.
