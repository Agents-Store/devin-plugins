# Scenario: a session with a rejected token and a failed MCP server

A longer session. A curl call kept answering 401, one MCP server failed to connect, and the
assistant retried it unchanged. The audit turns this into a Problems
table with a concrete fix per row.

## Command

```
/session-doctor-dev:audit
```

## Rendered report

## Session audit — 🔴 broken: the API token is rejected (401) and the `tracker` MCP server failed to connect

| | |
|---|---|
| Where | /work/example-app · git feature/export, 7 uncommitted · 1 other live session |
| Session | 8d41b7f0 · Claude Code 2.x · cli · mode default · 2 h 10 min |
| Main model | <!-- example-only -->opus<!-- /example-only --> @ high ← `--model` flag; settings effort · settings: sonnet |
| Subagents | 3: general-purpose ×3 → sonnet @ default (asked default) ← `CLAUDE_CODE_SUBAGENT_MODEL` |
| Context | instructions 4 (≈9.4k tokens) · skills 11, 2 without description · plugins 3 · agents 5 · hooks 2 |
| MCP | 2 connected · 1 failed: tracker · 1 need auth: crm |
| Env | 21 names: 12 shell, 6 settings, 3 project · auth: API key |

### Skills
| Skill | Invoked by | × | Outcome |
|---|---|---|---|
| audit | user | 1 | ok |
| export-report | model | 2 | ok |

### HTTP
| Source | Method | Host · path | × | Codes |
|---|---|---|---|---|
| curl | GET | api.example.test · /v1/reports | 5 | 401×5 |
| curl | POST | api.example.test · /v1/exports | 2 | 401×2 |
| mcp | CALL | docs · search | 9 | ok×9 |
| mcp-connect | | tracker | 1 | AUTH_HEADER_REJECTED |

### Tokens
| Kind | Variable | Fingerprint | Codes | Status |
|---|---|---|---|---|
| bearer | $EXAMPLE_API_TOKEN | a1b2c3d4 | 401×7 | rejected |

### Problems
| # | | Problem | Evidence | Fix |
|---|---|---|---|---|
| 1 | 🔴 | 1 API token refused by the server in this session | bearer $EXAMPLE_API_TOKEN fp a1b2c3d4 -> 401×7 @ api.example.test | Renew or replace the token and update where it is stored (settings env, `.env`, vault) |
| 2 | 🔴 | MCP server `tracker` failed to start | AUTH_HEADER_REJECTED: the server refused the Authorization header | Run `claude mcp list` or `/mcp` to see the error and fix the server config |
| 3 | 🟡 | The same request was retried unchanged after a 401 | 5 identical GET /v1/reports calls returned 401 | Stop after the first 401 and fix the token before retrying (judgment) |
| 4 | ⚪ | MCP servers waiting for authentication | 1: crm | Authenticate the ones you need in `/mcp`; disconnect the rest |

### Next step
Replace the rejected `EXAMPLE_API_TOKEN` — it blocks every curl call to api.example.test.

## What to notice

- The token Status is **rejected** only because its codes include 401; the audit never tested
  the token itself. The Tokens table lists only tokens used in Bash `curl`/`wget` commands, so
  an MCP server's credential never appears there.
- A failed MCP connection is one HTTP row per (server, error code): source `mcp-connect`, empty
  method, the server name as the target, count 1, and the server's error code as the code.
- Rows 1-2 and 4 come from the data block's findings. Row 4 is low (⚪) because only 1 server
  waits for authentication; it becomes medium (🟡) at 5 or more. Row 3 is a step-2 judgment and
  is marked "(judgment)".
- The summary counts (for example, skills without a description) stay in the summary table and
  never become Problems rows.
- The model name in the Main model cell is only an illustration.
