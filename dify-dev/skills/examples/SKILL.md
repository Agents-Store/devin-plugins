---
name: examples
description: >
  This skill should be used when the user asks for a "full Dify example", "end-to-end
  Dify integration", "how do I build a chatbot with Dify", "complete workflow example",
  "Dify RAG example", or wants a working, copy-paste walkthrough that strings multiple
  Dify API calls together.
---

# Dify API — End-to-End Examples

Complete, runnable **curl** walkthroughs that combine multiple endpoints. Replace
`https://api.dify.ai/v1` with your self-hosted base URL and the `app-XXXX` / `dataset-XXXX`
keys with your own. For per-endpoint detail, follow the linked skills.

| Scenario | What it shows | Reference |
|----------|---------------|-----------|
| **Chatbot integration** | Discover the app, start a conversation, continue it, stream, then list history | [references/scenarios/chatbot-integration.md](references/scenarios/chatbot-integration.md) |
| **Run a workflow** | Inspect inputs, run blocking & streaming, fetch the run detail, list logs | [references/scenarios/run-workflow.md](references/scenarios/run-workflow.md) |
| **Knowledge base RAG** | Create a KB, ingest a document, wait for indexing, test retrieval | [references/scenarios/knowledge-base-rag.md](references/scenarios/knowledge-base-rag.md) |

## Picking a scenario

- Building a chat/agent UI on top of a Dify app → **Chatbot integration**.
- Calling a Dify Workflow app as a backend function → **Run a workflow**.
- Populating or querying a Dify knowledge base programmatically → **Knowledge base RAG**.

Each scenario is self-contained and notes which skill covers each step in depth
(`setup`, `chat-completion`, `workflows`, `conversations`, `knowledge-base`).
