---
name: file-management
description: File management — attach files to memories and search file content via vector search. This skill should be used when the user asks to upload documents, attach files, or search within attached files.
---

# File Management

Attach files to memories and search file content using vector search.

## Available Tools

| Tool | Purpose | Required Params |
|------|---------|----------------|
| attach_files_to_memory | Attach files to a memory | memory_id, user_id, files[] |
| get_memory_files | Vector search in files | user_id, search_query |

## Attaching Files

Tool: `attach_files_to_memory`

```
attach_files_to_memory({
  memory_id: "abc-123",
  user_id: "user-456",
  files: [
    { "filename": "architecture.md", "content": "..." },
    { "filename": "api-spec.yaml", "content": "..." }
  ]
})
```

### Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| memory_id | string | Yes | Target memory to attach to |
| user_id | string | Yes | File owner identifier |
| files | array | Yes | Array of file objects |

### File Object Format
```
{
  "filename": "document-name.ext",
  "content": "file content as string"
}
```

## Searching Files

Tool: `get_memory_files`

```
get_memory_files({
  user_id: 123,
  search_query: "authentication flow diagram",
  file_name: "architecture.md",
  keywords: ["auth", "login", "JWT"],
  limit: 5
})
```

### Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | int | Yes | File owner identifier |
| search_query | string | Yes | Semantic search within file content |
| file_name | string | No | Filter by specific filename |
| user_file_name | string | No | Filter by user-facing filename |
| keywords | string[] | No | Additional keyword filters |
| limit | int | No | Max results (default 5) |

## Common Workflows

### Build Document Knowledge Base
```
1. add_memories(messages about project) -> get memory_id
2. attach_files_to_memory(memory_id, user_id, [design_doc, api_spec])
3. get_memory_files(user_id, "key topic") -> verify searchable
```

### Search Across All Documents
```
get_memory_files({
  user_id: 123,
  search_query: "error handling patterns",
  limit: 10
})
```

### Search in Specific Document
```
get_memory_files({
  user_id: 123,
  search_query: "rate limiting",
  file_name: "api-guidelines.md"
})
```

### Keyword + Semantic Search
```
get_memory_files({
  user_id: 123,
  search_query: "how to handle retries",
  keywords: ["retry", "backoff", "resilience"]
})
```

## Best Practices

1. **Always provide user_id** — required for all file operations
2. **Verify memory exists** before attaching — `get_memory(memory_id)` first
3. **Use descriptive filenames** — helps with filtering later
4. **Semantic queries work best** — use natural language, not just keywords
5. **Combine keyword + semantic** — keywords filter, semantic search ranks
6. **Chunk large documents** — split into topic-specific memories for better precision
7. **Organize by memory** — attach related files to the same memory for grouping

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| File not found | Invalid memory_id | Verify memory exists first |
| Empty results | Wrong user_id | Check user_id matches the one used in attach |
| No matches | Too specific query | Broaden search query or remove file_name filter |
| Missing user_id | Omitted required param | Always include user_id for file operations |
