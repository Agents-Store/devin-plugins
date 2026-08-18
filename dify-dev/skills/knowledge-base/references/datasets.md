# Dify Knowledge Base — Datasets endpoints

All paths are relative to the base URL (`https://api.dify.ai/v1` or self-hosted). Use a
**Knowledge API key**: `Authorization: Bearer dataset-XXXX`.

## Contents

- [POST /datasets](#post-datasets--create-a-knowledge-base) — create
- [GET /datasets](#get-datasets--list-knowledge-bases) — list
- [GET /datasets/{id}](#get-datasetsdataset_id--get-details) — get
- [PATCH /datasets/{id}](#patch-datasetsdataset_id--update) — update
- [DELETE /datasets/{id}](#delete-datasetsdataset_id--delete) — delete
- [POST /datasets/{id}/retrieve](#post-datasetsdataset_idretrieve--test-retrieval) — retrieve (RAG)
- [Permission values](#permission-values) · [Indexing techniques](#indexing-techniques)

## POST /datasets — create a knowledge base

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | Knowledge base name |
| `description` | string | no | Description |
| `permission` | string | no | `only_me` (default), `all_team_members`, `partial_members` |
| `indexing_technique` | string | no | `high_quality` or `economy` |
| `provider` | string | no | `vendor` (default) or `external` |

```bash
curl -X POST 'https://api.dify.ai/v1/datasets' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "name": "Product Docs", "description": "Public docs", "permission": "only_me" }'
```

```json
{
  "id": "...", "name": "Product Docs", "description": "Public docs",
  "permission": "only_me", "indexing_technique": null,
  "document_count": 0, "word_count": 0, "created_at": 1700000000
}
```

## GET /datasets — list knowledge bases

```bash
curl 'https://api.dify.ai/v1/datasets?page=1&limit=20' \
  --header 'Authorization: Bearer dataset-XXXX'
```

Query params: `page`, `limit` (max 100), `keyword`. Returns
`{ "data": [...], "has_more", "limit", "total", "page" }`.

## GET /datasets/{dataset_id} — get details

```bash
curl 'https://api.dify.ai/v1/datasets/{dataset_id}' \
  --header 'Authorization: Bearer dataset-XXXX'
```

Returns the dataset with `embedding_model`, `embedding_model_provider`, counts, and
`retrieval_model_dict`.

## PATCH /datasets/{dataset_id} — update

```bash
curl -X PATCH 'https://api.dify.ai/v1/datasets/{dataset_id}' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{ "name": "Renamed", "indexing_technique": "high_quality", "permission": "all_team_members" }'
```

## DELETE /datasets/{dataset_id} — delete

```bash
curl -X DELETE 'https://api.dify.ai/v1/datasets/{dataset_id}' \
  --header 'Authorization: Bearer dataset-XXXX'
```

Returns 204 No Content. Deletes the knowledge base and all its documents.

## POST /datasets/{dataset_id}/retrieve — test retrieval

The core RAG query. Returns scored chunks.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `query` | string | yes | Search query |
| `retrieval_model` | object | no | Override retrieval config |
| `external_retrieval_model` | object | no | For external knowledge |

`retrieval_model` fields: `search_method` (`semantic_search` / `full_text_search` /
`hybrid_search` / `keyword_search`), `reranking_enable` (bool), `reranking_model`
(`{ reranking_provider_name, reranking_model_name }`), `top_k` (int), `score_threshold_enabled`
(bool), `score_threshold` (0–1).

```bash
curl -X POST 'https://api.dify.ai/v1/datasets/{dataset_id}/retrieve' \
  --header 'Authorization: Bearer dataset-XXXX' \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "What are your hours?",
    "retrieval_model": {
      "search_method": "hybrid_search",
      "top_k": 3,
      "score_threshold_enabled": true,
      "score_threshold": 0.5
    }
  }'
```

```json
{
  "query": { "content": "What are your hours?" },
  "records": [
    {
      "segment": { "id": "...", "document_id": "...", "content": "9-5 weekdays", "word_count": 3 },
      "score": 0.92
    }
  ]
}
```

## Permission values

| Value | Meaning |
|-------|---------|
| `only_me` | Creator only |
| `all_team_members` | Everyone in the workspace |
| `partial_members` | Specific members (set in UI) |

## Indexing techniques

| Value | Trade-off |
|-------|-----------|
| `high_quality` | Embedding-based; better accuracy; needs an embedding model; costs tokens |
| `economy` | Keyword index; faster/cheaper; lower accuracy |
