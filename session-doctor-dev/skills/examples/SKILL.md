---
name: examples
description: >
  This skill should be used when the user asks for a "full example", "sample audit",
  "example session audit", "what does the report look like", "show me a sample report",
  "example of the session doctor output", "what does a rejected token look like in the audit",
  or wants to see a complete rendered session audit before running one.
---

# Examples — Rendered Session Audits

Two complete walkthroughs of the report that the `audit` skill produces. Every value in them
is made up: hosts use `example.test` / `example.com`, tokens appear as `<token>` with a fake
8-hex fingerprint, and no real session is described.

> To audit the real session, run `/session-doctor-dev:audit` (add `full` for the raw DETAILS lines).

## Available Scenarios

| Scenario | What it shows | Reference |
|----------|---------------|-----------|
| **A clean session audit** | Nothing wrong: all tables filled, "No problems found" | [references/scenarios/clean-session.md](references/scenarios/clean-session.md) |
| **A rejected token and a failed MCP server** | A 401 on a token, a failed MCP server, and the Problems table with fixes | [references/scenarios/rejected-token-failed-mcp.md](references/scenarios/rejected-token-failed-mcp.md) |

## How to read a report

| Section | Source in the data block | Meaning |
|---------|--------------------------|---------|
| Summary table | session header | where the session runs, model and effort, context size, MCP status |
| Skills | `SKILLS INVOKED` | which skills ran, who invoked them, how they ended |
| HTTP | `HTTP REQUESTS` | every request with its method, host, path and status codes |
| Tokens | `TOKENS` | one row per token seen — variable name and fingerprint only, status from the codes received |
| Problems | findings + judgment | at most 8 rows, ordered red, yellow, low; each with evidence and a fix |

## Rules the examples follow

- A token value is never printed — the Fingerprint column is a short hash, not a prefix of the secret.
- Token status comes only from codes the session already received; the audit makes no network request.
- An empty block is written as "none", not as an empty table.
