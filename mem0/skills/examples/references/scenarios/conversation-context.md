# Scenario: Conversation Context Management

**Goal:** Use Mem0 to maintain persistent context across conversations — store user preferences, past decisions, ongoing tasks, and evolving knowledge.

---

## Step 1: Session Start — Retrieve Context

At the beginning of each conversation, retrieve relevant memories:

```
search_memories({
  query: "user preferences and recent decisions",
  user_id: "user-123",
  top_k: 10,
  threshold: 0.5
})
```

This provides context about:
- User preferences (language, style, tools)
- Recent project decisions
- Ongoing tasks and their status
- Past interactions and corrections

---

## Step 2: During Conversation — Store New Facts

As new information emerges, store it immediately:

```
add_memories({
  messages: [
    {"role": "user", "content": "I prefer concise explanations with code examples"},
    {"role": "assistant", "content": "Noted: concise style with code examples preferred"}
  ],
  user_id: "user-123",
  metadata: {"category": "preferences"},
  infer: true
})
```

Store task progress:
```
add_memories({
  messages: [
    {"role": "user", "content": "We finished the authentication module, moving to payment integration"},
    {"role": "assistant", "content": "Auth complete. Next: payment integration."}
  ],
  user_id: "user-123",
  metadata: {"category": "project-progress"},
  infer: true
})
```

---

## Step 3: Handle Corrections

When the user corrects previous information:

```
search_memories({
  query: "preferred code style",
  user_id: "user-123",
  top_k: 3
})
```

Find and update the outdated memory:
```
update_memory({
  memory_id: "<found_id>",
  data: "Prefers detailed explanations with step-by-step walkthroughs (changed from concise style)"
})
```

---

## Step 4: Cross-Session Continuity

In a new session, retrieve the full context:

```
search_memories({
  query: "current project status and what we're working on",
  user_id: "user-123",
  top_k: 5
})
```

Continue from where the previous session ended without the user repeating context.

---

## Step 5: Periodic Cleanup

Over time, some context becomes stale:

```
get_all_memories({
  user_id: "user-123",
  page: 1,
  page_size: 50
})
```

Review and clean:
```
batch_delete_memories({
  memory_ids: ["<completed_task_id>", "<outdated_preference_id>"]
})
```

Update evolving knowledge:
```
batch_update_memories({
  memories: [
    {"memory_id": "id-1", "data": "Project phase: testing (was: development)"},
    {"memory_id": "id-2", "data": "Team size: 5 (was: 3, added 2 new members)"}
  ]
})
```

---

## Step 6: Track Context Evolution

For important decisions, check how context evolved:

```
get_memory_history({ memory_id: "<key_decision_id>" })
```

This reveals:
- When preferences changed
- How project goals evolved
- Decision reversals and their timing

---

## Result

Persistent, evolving context that:
- Spans across multiple conversation sessions
- Adapts as user preferences change
- Tracks project progress over time
- Self-cleans with periodic maintenance
- Provides full history of how context evolved
