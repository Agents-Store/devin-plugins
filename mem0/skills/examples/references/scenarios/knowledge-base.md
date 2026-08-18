# Scenario: Building a Project Knowledge Base

**Goal:** Store project decisions, architecture choices, team preferences, and documentation as a searchable knowledge base in Mem0.

---

## Step 1: Define Knowledge Categories

Plan what types of knowledge to store:

| Category | Examples |
|----------|---------|
| tech-stack | Languages, frameworks, databases, tools |
| architecture | Design decisions, patterns, trade-offs |
| processes | CI/CD, deployment, review workflows |
| team | Preferences, conventions, coding standards |
| decisions | ADRs (Architecture Decision Records) |

---

## Step 2: Add Core Project Facts

```
add_memories({
  messages: [
    {"role": "user", "content": "Project uses React 19 frontend with TypeScript 5.4"},
    {"role": "user", "content": "Backend is Node.js 22 with Express 5"},
    {"role": "user", "content": "Database is PostgreSQL 16 with pgvector for embeddings"}
  ],
  user_id: "project-alpha",
  metadata: {"category": "tech-stack"},
  infer: true
})
```

---

## Step 3: Add Architecture Decisions

```
add_memories({
  messages: [
    {"role": "user", "content": "ADR-001: Chose microservices for independent scaling of API and worker services"},
    {"role": "user", "content": "ADR-002: Event-driven via SQS over synchronous HTTP for inter-service communication"},
    {"role": "user", "content": "ADR-003: Feature flags via LaunchDarkly for gradual rollouts"}
  ],
  user_id: "project-alpha",
  metadata: {"category": "architecture"},
  infer: false
})
```

Note: `infer: false` for ADRs — store exact text to preserve precise wording.

---

## Step 4: Attach Design Documents

```
attach_files_to_memory({
  memory_id: "<architecture_memory_id>",
  user_id: "project-alpha",
  files: [
    {"filename": "system-design.md", "content": "# System Architecture\n\n## Overview\nMicroservices architecture with 4 core services..."},
    {"filename": "database-schema.sql", "content": "CREATE TABLE users (\n  id UUID PRIMARY KEY,\n  ..."}
  ]
})
```

---

## Step 5: Verify Retrieval

Test key queries to ensure knowledge is searchable:

```
search_memories({ query: "what database do we use", user_id: "project-alpha" })
-> Should return PostgreSQL 16 memory

search_memories({ query: "why microservices", user_id: "project-alpha" })
-> Should return ADR-001

get_memory_files({ user_id: "project-alpha", search_query: "database schema for users" })
-> Should return relevant section from database-schema.sql
```

---

## Step 6: Ongoing Maintenance

### When decisions change:
```
search_memories({ query: "feature flags", user_id: "project-alpha" })
update_memory({ memory_id: "<found_id>", data: "ADR-003 Updated: Migrated from LaunchDarkly to custom feature flag service" })
```

### When knowledge becomes obsolete:
```
get_all_memories({ user_id: "project-alpha" })
batch_delete_memories({ memory_ids: ["<obsolete_id_1>", "<obsolete_id_2>"] })
```

### Track what changed:
```
get_memory_history({ memory_id: "<adr_memory_id>" })
-> See full timeline of decision changes
```

---

## Result

A searchable project knowledge base where:
- Technical decisions are stored with precise wording
- Design documents are vector-searchable
- Knowledge stays current through regular maintenance
- Changes are tracked via history
