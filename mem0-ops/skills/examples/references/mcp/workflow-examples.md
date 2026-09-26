# Mem0 Workflow Examples

Multi-step workflows combining multiple Mem0 tools for common scenarios.

---

## Workflow 1: Build a Knowledge Base from Scratch

**Goal:** Store project knowledge and make it searchable.

```
Step 1: Add core project facts
  add_memories({
    messages: [
      {"role": "user", "content": "Project Alpha uses React 19, Node.js 22, PostgreSQL 16"},
      {"role": "user", "content": "Deployment is on AWS ECS with Fargate"},
      {"role": "user", "content": "CI/CD pipeline runs on GitHub Actions"}
    ],
    user_id: "project-alpha",
    metadata: {"category": "tech-stack"}
  })

Step 2: Add architecture decisions
  add_memories({
    messages: [
      {"role": "user", "content": "We chose microservices over monolith for independent scaling"},
      {"role": "user", "content": "Event-driven communication via Amazon SQS between services"}
    ],
    user_id: "project-alpha",
    metadata: {"category": "architecture-decisions"}
  })

Step 3: Attach design documents
  attach_files_to_memory({
    memory_id: "<id from step 1>",
    user_id: "project-alpha",
    files: [{"filename": "system-design.md", "content": "..."}]
  })

Step 4: Verify retrieval
  search_memories({
    query: "what database does the project use",
    user_id: "project-alpha"
  })
  -> Should return PostgreSQL 16 memory

Step 5: Search documents
  get_memory_files({
    user_id: "project-alpha",
    search_query: "scaling strategy"
  })
  -> Should return relevant sections from system-design.md
```

---

## Workflow 2: Context-Aware Conversation

**Goal:** Use memories to maintain context across sessions.

```
Step 1: Retrieve context at session start
  search_memories({
    query: "user preferences and past decisions",
    user_id: "user-123",
    top_k: 10
  })

Step 2: Store new facts during conversation
  add_memories({
    messages: [
      {"role": "user", "content": "I prefer dark mode and vim keybindings"},
      {"role": "assistant", "content": "Updated preferences: dark mode, vim keys"}
    ],
    user_id: "user-123",
    metadata: {"category": "preferences"}
  })

Step 3: Update corrections
  search_memories({
    query: "editor preferences",
    user_id: "user-123"
  })
  -> Find the memory to correct

  update_memory({
    memory_id: "<found_id>",
    data: "Prefers dark mode, switched from vim to Neovim keybindings"
  })

Step 4: Verify update
  get_memory_history({ memory_id: "<found_id>" })
  -> Shows original -> updated values
```

---

## Workflow 3: Knowledge Audit and Cleanup

**Goal:** Review, update, and clean stale memories.

```
Step 1: List all memories
  get_all_memories({
    user_id: "project-alpha",
    page: 1,
    page_size: 50
  })

Step 2: Identify stale entries
  Review each memory for relevance.
  Collect IDs of outdated memories.

Step 3: Update outdated but still relevant
  batch_update_memories({
    memories: [
      {"memory_id": "id-1", "data": "Corrected: now using Node.js 22 (was 20)"},
      {"memory_id": "id-2", "data": "Updated: migrated from MySQL to PostgreSQL"}
    ]
  })

Step 4: Delete obsolete memories
  batch_delete_memories({
    memory_ids: ["id-3", "id-4", "id-5"]
  })

Step 5: Verify cleanup
  get_all_memories({
    user_id: "project-alpha",
    page: 1,
    page_size: 50
  })
  -> Should show only current, relevant memories
```

---

## Workflow 4: Memory Update with History Verification

**Goal:** Update a memory and verify the change was recorded.

```
Step 1: Find the target memory
  search_memories({
    query: "API rate limit configuration",
    user_id: "project-alpha",
    top_k: 3
  })

Step 2: Review current state
  get_memory({ memory_id: "<best_match_id>" })

Step 3: Update
  update_memory({
    memory_id: "<best_match_id>",
    data: "API rate limit increased from 100 to 500 req/min for authenticated users"
  })

Step 4: Verify in history
  get_memory_history({ memory_id: "<best_match_id>" })
  -> Should show the before/after change with timestamp
```

---

## Workflow 5: Multi-Agent Knowledge Sharing

**Goal:** Different agents share knowledge through memories.

```
Step 1: Agent A stores findings
  add_memories({
    messages: [{"role": "assistant", "content": "Found 3 critical vulnerabilities in auth module"}],
    agent_id: "security-scanner",
    app_id: "code-review",
    metadata: {"severity": "critical", "module": "auth"}
  })

Step 2: Agent B retrieves context
  search_memories({
    query: "security issues in authentication",
    app_id: "code-review",
    top_k: 5
  })

Step 3: Agent B adds its analysis
  add_memories({
    messages: [{"role": "assistant", "content": "Remediation plan: patch JWT validation, add CSRF tokens, update dependencies"}],
    agent_id: "remediation-planner",
    app_id: "code-review",
    metadata: {"severity": "critical", "module": "auth", "type": "remediation"}
  })
```
