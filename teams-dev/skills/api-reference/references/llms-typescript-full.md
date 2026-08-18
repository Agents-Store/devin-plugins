# Offline pointer — `llms_typescript_full.txt`

Microsoft publishes an LLM-optimised, single-file reference for the TypeScript SDK at:

`https://microsoft.github.io/teams-sdk/llms_docs/llms_typescript_full.txt`

That file is the authoritative source for:

- The full list of `@microsoft/teams.*` packages and their public exports.
- Method signatures and option shapes for `App`, `ChatPrompt`, `OpenAIChatModel`, `McpPlugin`, `A2AClientPlugin`, `AdaptiveCard` builders, message-extension types, dialog envelopes, and the activity types.
- Streaming semantics, function-calling shape, and sovereign-cloud constants.
- CLI flags for `teams project new`, `teams app create/list/get/update`, `teams self-update`.

## When to fetch

- The handler signature in the SDK changes and the local skills look stale.
- You need an exhaustive enum (e.g. all Adaptive Card element types).
- You hit a TypeScript error referencing a type the skill files do not mention.

## How to consult

Run a one-off WebFetch in the parent session:

```text
WebFetch:
  url: https://microsoft.github.io/teams-sdk/llms_docs/llms_typescript_full.txt
  prompt: "Find the signature of <method or option>. Quote verbatim."
```

The file is plain text and a single fetch normally returns the section you need. Treat the returned content as authoritative and patch local skill files when it diverges from what they say — record the change in `LEARNINGS.md`.

## Cached snapshot

This plugin intentionally does not commit a cached copy of the upstream file — it changes faster than the plugin release cadence, and a stale snapshot is worse than no snapshot. Fetch on demand.
