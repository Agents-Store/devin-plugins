---
name: security-audit
description: Workspace prompt security audit checklist — checks for hardcoded secrets, prompt injection risks, data leakage, missing safety rules, PII exposure, and overly broad standing orders. Use this skill whenever auditing workspace security, checking for vulnerabilities, reviewing prompt safety, or as part of any workspace optimization. Even if the user doesn't explicitly ask for security, include these checks when doing a full workspace review, optimization, or pre-deployment audit.
---

# Workspace Prompt Security Audit

Security audit checklist for OpenClaw workspace files. Every workspace optimization or audit should include these checks to ensure the agent operates securely.

## Audit Categories

### 1. Hardcoded Secrets Detection

Scan ALL workspace files for inline secrets:

```bash
# Check workspace .md files for potential secrets
grep -rn -E '(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|xox[bprs]-[a-zA-Z0-9-]+|[0-9]+:[A-Za-z0-9_-]{35,})' ./workspace/ 2>/dev/null

# Check for generic API key patterns
grep -rn -i -E '(api[_-]?key|token|secret|password)\s*[:=]\s*["\x27][A-Za-z0-9_\-]{10,}' ./workspace/ 2>/dev/null
```

**Severity**: CRITICAL — secrets in workspace files are loaded into every LLM prompt.

**Fix**: Move secrets to environment variables. Never put API keys, tokens, or passwords in workspace .md files.

### 2. openclaw.json Secret Handling

Check that `openclaw.json` uses SecretRef pattern instead of inline secrets:

**Correct** (SecretRef pattern):
```json
{
  "source": "env",
  "provider": "default",
  "id": "OPENAI_API_KEY"
}
```

**Incorrect** (inline secret):
```json
{
  "botToken": "7123456789:AAF_actual_token_here"
}
```

```bash
# Detect potential inline secrets in openclaw.json
grep -E '"[A-Za-z0-9_:.-]{20,}"' ./openclaw.json 2>/dev/null | grep -vi '"source"\|"provider"\|"id"\|"model"\|"profile"\|"mode"\|"workspace"'
```

**Known false positive**: `openclaw doctor` may show:
```
Error: channels.telegram.botToken: unresolved SecretRef "env:default:TELEGRAM_BOT_TOKEN"
```
This is safe to ignore — it appears when running doctor outside gateway runtime.

**If inline secrets found**: Warn the user that this is a security risk. Recommend migrating to SecretRef pattern via `.env` file.

### 3. Prompt Injection Vectors

Check for workspace content that could enable prompt injection:

| Risk | What to look for | Where |
|------|------------------|-------|
| User-controllable system prompts | Dynamic content in AGENTS.md/SOUL.md that references user input without sanitization | AGENTS.md, SOUL.md |
| Unrestricted tool execution | No limits on tool usage, missing deny rules | TOOLS.md, openclaw.json |
| Memory injection | MEMORY.md content loaded into prompts without validation | MEMORY.md |
| Standing order scope creep | Orders with overly broad authority or no approval gates | docs/standing-orders/ |

**Checks**:
- Does AGENTS.md reference external URLs or user-provided content that gets injected into prompts?
- Are there standing orders that can execute without approval?
- Can the agent modify its own SOUL.md or AGENTS.md without user confirmation?

### 4. Data Exfiltration Rules

Verify the workspace has rules preventing data leakage:

**Check AGENTS.md for**:
- [ ] "Don't exfiltrate private data" or equivalent red line
- [ ] "Ask before taking external actions (sending messages, API calls)"
- [ ] "Never share MEMORY.md content in group chats"
- [ ] "Don't dump directories or secrets into chat"

**Check SOUL.md for**:
- [ ] Boundaries section exists
- [ ] "Private things stay private" or equivalent
- [ ] "Don't speak as the user in groups"

**If missing**: Flag as HIGH severity. Recommend adding explicit red lines.

### 5. MEMORY.md Group Chat Isolation

Verify MEMORY.md is never loaded in group chats:

```bash
# Check AGENTS.md for memory group isolation rule
grep -i "memory.*group\|group.*memory\|MEMORY.md.*main.*session\|never.*group" ./workspace/AGENTS.md 2>/dev/null
```

MEMORY.md should only load in main private sessions — loading it in group chats risks leaking private user data to shared contexts. If this rule is missing from AGENTS.md, flag it.

### 6. PII in Workspace Files

Check for unnecessary personally identifiable information:

```bash
# Check for email addresses
grep -rn -E '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' ./workspace/ 2>/dev/null

# Check for phone numbers
grep -rn -E '\+?[0-9]{10,15}' ./workspace/ 2>/dev/null

# Check for potential credit card numbers
grep -rn -E '[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}' ./workspace/ 2>/dev/null
```

**USER.md exception**: PII in USER.md is expected (names, Telegram IDs, timezones). Flag only if it contains sensitive data like SSNs, credit cards, or passwords.

### 7. Standing Orders Authority Review

For each file in `docs/standing-orders/`:

| Check | Pass criteria |
|-------|--------------|
| Scope defined | Has explicit "Authority" section listing what agent CAN do |
| Approval gates | Has "Approval" section with human sign-off requirements |
| Escalation rules | Has "Escalation" section for edge cases |
| "What NOT to do" | Has explicit prohibitions |
| External actions | Any action visible to others requires approval (first 30 days minimum) |
| Financial thresholds | Transactions above defined limits require approval |

**If standing orders lack approval gates**: Flag as HIGH severity.

### 8. Tool Access Controls

Check `openclaw.json` tools configuration:

```bash
# Check tools profile and permissions
jq '.tools' ./openclaw.json 2>/dev/null
```

| Check | Why |
|-------|-----|
| `profile` is not `"full"` without justification | Full profile gives agent maximum tool access |
| `deny` list exists for dangerous tools | Prevents accidental destructive operations |
| `loopDetection.enabled` is true for production | Prevents runaway tool loops |
| `exec.timeoutSec` is reasonable (< 3600) | Prevents long-running unattended processes |

## Security Report Template

```markdown
# Workspace Security Audit Report

## Summary
- Overall risk level: [LOW / MEDIUM / HIGH / CRITICAL]
- Issues found: [N critical, N high, N medium, N low]

## Findings

### CRITICAL
- [ ] [Finding description + file + line]

### HIGH
- [ ] [Finding description + file + line]

### MEDIUM
- [ ] [Finding description + file + line]

### LOW
- [ ] [Finding description + file + line]

## Recommendations
1. [Specific fix with code/content suggestion]
2. [Another fix]
```

## Advisory vs Hard Enforcement

Red lines in AGENTS.md and boundaries in SOUL.md are **prompting-level guardrails** — they guide the agent's behavior but are advisory only. A sufficiently creative prompt or edge case can bypass them.

For **hard enforcement**, use openclaw.json configuration:
- `tools.deny` — block specific tools entirely (agent cannot call them regardless of instructions)
- `sandbox.mode` — restrict file system and network access
- `dmPolicy: "allowlist"` — only allow messages from approved users
- `tools.profile` — limit available tool categories

Both layers are important: advisory guardrails handle the common case with nuance, while hard enforcement prevents catastrophic failures.

## Best Practices

1. Run security audit before deploying any workspace changes. Also available via CLI: `openclaw security audit` (with `--deep` for live probing, `--fix` to tighten defaults)
2. Never put secrets in workspace files — use environment variables
3. Always have explicit red lines in AGENTS.md (advisory guardrails)
4. Always have boundaries in SOUL.md (advisory guardrails)
5. Use `tools.deny` and `sandbox.mode` in openclaw.json for hard enforcement
6. Review standing orders quarterly for scope creep
7. Enable `loopDetection` in production
8. Use `allowlist` dmPolicy instead of `open` for production agents
9. Keep MEMORY.md isolated from group chats
