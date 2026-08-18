# dify-dev (Devin plugin)

Dify API dev plugin for Agents Store. Complete coverage of the Dify App Service API (chat, completion, workflows, conversations, files, audio, annotations) and the Knowledge Base / Datasets API — auth, endpoints, streaming events, curl examples, and troubleshooting.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (9)

- `annotations` — This skill should be used when the user asks to "list/create/update/delete Dify annotations", "call /apps/annotations", "set up Dify annotation reply", "enable annotation reply", "disable annotation reply", or "check annotation reply status". Covers the annotation (curated Q&A) subsystem.

- `chat-completion` — This skill should be used when the user asks to "send a chat message to Dify", "call /chat-messages", "use the Dify completion API", "/completion-messages", "stream a Dify chat response", "stop Dify generation", "get suggested questions", or "submit message feedback / like a message". Covers conversational (chat/agent/ chatflow) and stateless (completion) message sending.

- `conversations` — This skill should be used when the user asks to "list Dify conversations", "get conversation history", "list messages in a Dify conversation", "rename a Dify conversation", "delete a conversation", or "get/update Dify conversation variables". Covers chat-history management for chat/agent/chatflow apps.

- `examples` — This skill should be used when the user asks for a "full Dify example", "end-to-end Dify integration", "how do I build a chatbot with Dify", "complete workflow example", "Dify RAG example", or wants a working, copy-paste walkthrough that strings multiple Dify API calls together.

- `files-audio` — This skill should be used when the user asks to "upload a file to Dify", "call /files/upload", "send an image to a Dify app", "transcribe audio with Dify", "/audio-to-text", "Dify text to speech", or "/text-to-audio". Covers file upload for multimodal input and the speech endpoints.

- `knowledge-base` — This skill should be used when the user asks to work with Dify "knowledge base", "datasets API", "create a dataset", "upload a document to Dify", "add documents to a knowledge base", "segments / chunks", "retrieve from a Dify knowledge base", "test retrieval", or RAG ingestion. Covers the standalone Knowledge Base / Datasets API.

- `setup` — This skill should be used when the user asks how to "connect to the Dify API", "authenticate with Dify", "get a Dify API key", "what is the Dify base URL", "blocking vs streaming in Dify", "the Dify user field", "send files to a Dify app", or needs the app metadata endpoints (/info, /parameters, /meta, /site). Foundation for every other Dify API call.

- `troubleshoot` — This skill should be used when a Dify API call fails or behaves unexpectedly — "Dify 401 / 404 / 429 error", "Dify conversation not found", "Dify blocking timeout", "Dify rate limit", "why is my Dify conversation empty", "Dify user mismatch", or "Dify file upload not working". Error codes, limits, and common pitfalls.

- `workflows` — This skill should be used when the user asks to "run a Dify workflow", "call /workflows/run", "execute a Dify workflow app via API", "get a workflow run result", "list Dify workflow logs", "stop a Dify workflow task", or work with Chatflow/Workflow node events. Covers Workflow-type apps (no conversation wrapper).


## Not carried over

- 1 agent(s) — Devin plugins do not support agents
- 3 command(s) — Devin plugins do not support commands

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/dify-dev
