---
name: secret-scanning
description: This skill should be used when the user asks to "scan for secrets", "Infisical scan", "find leaked secrets in git", "set up a pre-commit secret scan", "infisical scan git-changes", "scan repo for API keys", "add a secret-scanning baseline", or "ignore a false-positive secret" — using the Infisical CLI to detect and prevent committed secrets.
---

# Infisical Secret Scanning

Use `infisical scan` to detect hardcoded secrets in code, directories, and full git history (140+ secret types), and to block leaks at commit time. This is local, offline-capable, and does not require login.

## Scan a repository

```bash
infisical scan                       # scan entire git history (default)
infisical scan --verbose             # show each finding
infisical scan --no-git              # treat the target as a plain directory
infisical scan --source=./services   # scan a specific path
infisical scan --log-opts="--all commitA..commitB"   # restrict to a commit range
```

`scan` exits non-zero (default `1`) when leaks are found — that exit code is what makes it useful in CI.

## Scan only uncommitted / staged changes

Fast checks for local workflows and hooks:

```bash
infisical scan git-changes               # unstaged working-tree diff
infisical scan git-changes --staged --verbose   # staged changes (use in pre-commit)
```

## Install the pre-commit hook

Block secrets before they ever land in a commit:

```bash
infisical scan install --pre-commit-hook
```

For Husky or another hook manager, add this line to the hook script instead:

```bash
infisical scan git-changes --staged --verbose
```

Temporarily disable the hook (e.g. an intentional test fixture):

```bash
git config --bool hooks.infisical-scan false
```

## Reports

```bash
infisical scan --report-path=leaks.json                  # write findings to a file
infisical scan --report-format=sarif --report-path=leaks.sarif   # json | csv | sarif
infisical scan --redact                                  # hide secret values in output
```

## Baselines — ignore known/legacy findings

Capture the current findings as a baseline, then future scans report only **new** leaks:

```bash
infisical scan --report-path=baseline.json
infisical scan --baseline-path=baseline.json --report-path=new-findings.json
```

## Allowlisting individual findings

Inline ignore on a single line:

```js
const testKey = "sk_test_abc123";  // infisical-scan:ignore
```

Or list fingerprints in a `.infisicalignore` file at the repo root, one per line, format `commit:file:rule-id:line`:

```
bea0ff6e05a4de73a5db625d4ae181a015b50855:frontend/utils/login.js:stripe-access-token:147
```

## Custom rules (`.infisical-scan.toml`)

Config is resolved in this order: `--config` flag > `INFISICAL_SCAN_CONFIG` env var > `.infisical-scan.toml` in the source > built-in defaults.

```toml
[extend]
useDefault = true            # keep Infisical's default ruleset, then add your own

[[rules]]
id          = "acme-internal-token"
description = "ACME internal service token"
regex       = '''acme_(prod|stg)_[0-9a-f]{32}'''
keywords    = ["acme_"]       # pre-filter to speed scanning
entropy     = 3.5             # minimum Shannon entropy
tags        = ["api", "token"]

[rules.allowlist]
paths   = ['''go\.mod''', '''_test\.go$''']
regexes = ['''EXAMPLE_[A-Z]+''']

# A top-level [allowlist] applies globally and overrides per-rule allowlists.
[allowlist]
commits = ["abc123"]
paths   = ['''(.*?)(jpg|png|gif)$''']
```

## CI usage

```bash
# Fail the pipeline on any leak in the diff being merged
infisical scan git-changes --staged --verbose --report-format=sarif --report-path=scan.sarif
```

## Useful flags

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--source` | `-s` | `.` | Path to scan |
| `--config` | `-c` | auto | TOML rules config |
| `--report-path` | `-r` | — | Write findings to a file |
| `--report-format` | `-f` | `json` | `json`, `csv`, `sarif` |
| `--baseline-path` | `-b` | — | Ignore findings already in the baseline |
| `--exit-code` | — | `1` | Exit code when leaks are found |
| `--redact` | — | off | Hide secret values in output |
| `--no-git` | — | off | Scan as a plain directory |
| `--log-opts` | — | — | Pass-through `git log` args for a commit range |
| `--verbose` | `-v` | off | Detailed per-finding output |
