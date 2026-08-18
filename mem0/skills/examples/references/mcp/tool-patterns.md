# Mem0 MCP Tool Patterns

Exact parameter formats and expected responses for all 12 Mem0 MCP tools.

---

## add_memories

**Add new memories from messages.**

Input:
```json
{
  "messages": [
    {"role": "user", "content": "Our API uses JWT tokens with 1h expiry"},
    {"role": "assistant", "content": "Noted: JWT auth with 1 hour token expiry"}
  ],
  "user_id": "project-alpha",
  "metadata": {"category": "auth", "source": "meeting"},
  "infer": true
}
```

Minimal input:
```json
{
  "messages": [{"role": "user", "content": "PostgreSQL 16 is our database"}]
}
```

---

## get_all_memories

**List all memories with optional pagination.**

Input:
```json
{
  "user_id": "project-alpha",
  "page": 1,
  "page_size": 20
}
```

Minimal input:
```json
{}
```

---

## get_memory

**Get a specific memory by ID.**

Input:
```json
{
  "memory_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## search_memories

**Semantic search through memories.**

Input:
```json
{
  "query": "database connection settings",
  "user_id": "project-alpha",
  "threshold": 0.7,
  "top_k": 5,
  "filters": {"category": "infrastructure"}
}
```

Minimal input:
```json
{
  "query": "database settings"
}
```

---

## update_memory

**Update memory content. Data must be a string.**

Input:
```json
{
  "memory_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "data": "Updated: PostgreSQL 16 with pgvector 0.7 extension"
}
```

---

## batch_update_memories

**Update multiple memories at once (max 100).**

Input:
```json
{
  "memories": [
    {"memory_id": "id-1", "data": "Updated content for memory 1"},
    {"memory_id": "id-2", "data": "Updated content for memory 2"},
    {"memory_id": "id-3", "data": "Updated content for memory 3"}
  ]
}
```

---

## delete_memory

**Delete a single memory.**

Input:
```json
{
  "memory_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## batch_delete_memories

**Delete multiple memories at once (max 100).**

Input:
```json
{
  "memory_ids": [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "c3d4e5f6-a7b8-9012-cdef-123456789012"
  ]
}
```

---

## get_memory_history

**View change history for a memory.**

Input:
```json
{
  "memory_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## attach_files_to_memory

**Attach files to an existing memory.**

Input:
```json
{
  "memory_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "user-123",
  "files": [
    {"filename": "architecture.md", "content": "# System Architecture\n\n..."},
    {"filename": "api-spec.yaml", "content": "openapi: 3.0.0\n..."}
  ]
}
```

---

## get_memory_files

**Search attached files via vector search.**

Input:
```json
{
  "user_id": 123,
  "search_query": "authentication flow",
  "file_name": "architecture.md",
  "keywords": ["auth", "JWT", "login"],
  "limit": 5
}
```

Minimal input:
```json
{
  "user_id": 123,
  "search_query": "authentication flow"
}
```

---

## get_documentation

**Get documentation for all available tools.**

Input:
```json
{}
```
