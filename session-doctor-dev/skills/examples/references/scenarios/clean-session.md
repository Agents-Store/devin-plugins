# Scenario: a clean session audit

A short working session in a project directory. The developer asked for one change, ran the
tests, and every request succeeded. The audit finds nothing to fix.

## Command

```
/session-doctor-dev:audit
```

## Rendered report

## Session audit — 🟢 clean: no problems found in this session

| | |
|---|---|
| Where | /work/example-app · git main, 0 uncommitted · alone |
| Session | 3f9a1c2e · Claude Code 2.x · cli · mode default · 24 min |
| Main model | sonnet @ medium ← settings; default effort · settings: sonnet |
| Subagents | 1: Explore ×1 → haiku @ default (asked haiku) ← agent definition |
| Context | instructions 2 (≈1.8k tokens) · skills 6, 0 without description · plugins 2 · agents 3 · hooks 1 |
| MCP | 2 connected · 0 failed · 0 need auth |
| Env | 14 names: 9 shell, 5 settings · auth: subscription login |

### Skills
| Skill | Invoked by | × | Outcome |
|---|---|---|---|
| audit | user | 1 | ok |
| examples | model | 1 | ok |

### HTTP
| Source | Method | Host · path | × | Codes |
|---|---|---|---|---|
| mcp | CALL | docs · search | 6 | ok×6 |
| curl | GET | api.example.test · /v1/health | 2 | 200×2 |

### Tokens
| Kind | Variable | Fingerprint | Codes | Status |
|---|---|---|---|---|
| bearer | $EXAMPLE_API_TOKEN | a1b2c3d4 | 200×2 | accepted |

### Problems
No problems found

### Next step
Nothing to fix — keep the session focused on one task and `/clear` before starting an unrelated one.

## What to notice

- The summary verdict is green and the Problems section says "No problems found" in one line.
- The Tokens row shows the variable **name** and an 8-hex fingerprint — never the value.
- Status "accepted" comes from the 200 codes in the row, not from a check made by the audit.
- Tokens come only from Bash `curl`/`wget` commands: the token above rode on the 2 curl calls, so
  its codes are `200×2`. The 6 MCP calls appear in HTTP (source `mcp`, method `CALL`, the server
  and tool in the target column) but never count toward a token.

## Variant: first turn of a session

On the very first turn the transcript does not exist yet. The data block reports
`TRANSCRIPT_MISSING`; the report then fills Skills, subagent types and MCP status from the
assistant's own context, marks those cells "from context", and does not list it as a problem.
