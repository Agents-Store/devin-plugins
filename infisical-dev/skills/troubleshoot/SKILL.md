---
name: troubleshoot
description: This skill should be used when the user hits "Infisical CLI errors", "Infisical login fails", "Infisical keyring error", "infisical project not found", "Infisical token not working", "Infisical self-hosted connection issues", "infisical run no secrets", or needs to diagnose and fix problems with the Infisical CLI.
---

# Infisical CLI Troubleshooting

Diagnostics and fixes for common Infisical CLI problems.

## Quick diagnostics

Run these first to localize the problem:

```bash
infisical --version          # CLI installed and on PATH? (profiles need >= 0.43.134)
infisical login status       # is there a valid session/token?
infisical profile current    # which login profile applies here, and why
infisical vault              # which credential backend is active?
echo "$INFISICAL_DOMAIN"     # pointing at the right instance? (an older API-URL variable still counts, see cli-reference)
infisical secrets --env=dev  # can it actually read the project?
```

## Login & credential store

| Symptom | Cause | Fix |
|---------|-------|-----|
| `failed to store credentials` / keyring errors on Linux/WSL/headless | No system keyring available | `infisical vault set file` to use the encrypted file backend, then log in again (`vault set` drops every stored profile; the backends are only `file` and `auto`) |
| Browser never opens (SSH session, container) | No GUI to launch the browser | `infisical login -i` for interactive terminal prompts, or use machine-identity auth |
| Login succeeds but later commands say unauthenticated | Token expired or wrong profile active | `infisical login status` and `infisical profile current`; re-login with `infisical login --profile <name>`, or `infisical profile use <name>` (`infisical user switch` picks the default from a list) |
| Commands run against the wrong organization | The profile's default organization, or a pinned/bound profile | `infisical profile current` shows which profile applies and why; override for one command with `--profile <name>` or `--org <org>`; change the default with `infisical profile set-org <org>` |
| Stale/corrupt local state after switching instances | Old config cached | `infisical reset` revokes every profile's session on the server and deletes `~/.infisical` plus stored credentials (add `--local-only` to skip the server call), then log in fresh |

## Install & upgrade

| Symptom | Cause | Fix |
|---------|-------|-----|
| `apt-get update` fails, or yum/apk warns about the Infisical repo, since 2026-09-16 | The machine still uses the Cloudsmith package repository, which stopped serving the CLI | Remove the old source and re-run the `artifacts-cli.infisical.com` setup script (see the `setup` skill, or https://infisical.com/docs/cli/cloudsmith-migration) |
| `unknown command "profile"` / `"logout"` / `"org"`, `unknown flag: --profile` | CLI older than 0.43.134 | Upgrade the CLI; check with `infisical --version` |
| `unknown flag: --confidence` on `infisical scan` | CLI older than 0.43.136 | Upgrade the CLI |

## Self-hosted & networking

| Symptom | Cause | Fix |
|---------|-------|-----|
| Commands hit US Cloud instead of your instance | No domain set | `export INFISICAL_DOMAIN="https://your-instance"`, pass `--domain` on the command, or set `domain` in `.infisical.json`; order is flag, env var, file, then US Cloud |
| Command fails because the domain differs from your login | `--domain` / `INFISICAL_DOMAIN` names another instance than the logged-in profile | Unset the override, or keep the second instance as its own profile: `infisical login --save-as <name> --domain=<url>`, then `--profile <name>` |
| Command goes to an unexpected host | `domain` in a committed `.infisical.json` (the CLI prints a warning naming the host) | Check the file before trusting the repository; override with `--domain` |
| `infisical token renew` hits the wrong instance | `token renew` does not use a login profile | Pass `--domain` or set `INFISICAL_DOMAIN` |
| 4xx from a proxied instance (Cloudflare Access, etc.) | Missing edge-auth headers | `export INFISICAL_CUSTOM_HEADERS="Access-Client-Id=… Access-Client-Secret=…"` |
| TLS / cert errors | Self-signed or internal CA | Trust the CA on the host; verify the URL scheme is `https` and reachable |

## Tokens & permissions (CI/CD)

| Symptom | Cause | Fix |
|---------|-------|-----|
| `INFISICAL_TOKEN` not picked up | Not exported into the process/container | Ensure it is `export`ed (or passed via `docker run --env INFISICAL_TOKEN=...`) |
| `project not found` / empty results under machine identity | No `.infisical.json` and no `--projectId` | Pass `--projectId=<id>` explicitly |
| `403` / scope errors | Identity lacks access to the env+path | Grant the machine identity access to the target environment and folder |
| Token rejected after a while | Access-token TTL exceeded | `infisical token renew <token>` (add `--domain` off US Cloud), or re-login to mint a new one |
| Captured token contains extra output | Missing `--plain`/`--silent` on login | `export INFISICAL_TOKEN=$(infisical login ... --silent --plain)` |

## Secrets not appearing

| Symptom | Cause | Fix |
|---------|-------|-----|
| `infisical run` injects nothing | Wrong env or path | Check `--env` and `--path`; confirm with `infisical secrets --env=<e> --path=<p>` |
| Branch maps to an unexpected environment | `gitBranchToEnvironmentMapping` in `.infisical.json` | Override with `--env`, or fix the mapping |
| Imported secrets missing | Imports disabled | Ensure `--include-imports=true` (default) |
| `${VAR}` references appear literally | Expansion disabled | Use `--expand=true` (default); only disable it intentionally |
| A personal value unexpectedly overrides shared | `--secret-overriding` on by default | Set `--secret-overriding=false` to force shared values |

## Production hygiene

```bash
export INFISICAL_DISABLE_UPDATE_CHECK=true   # skip version checks in CI/prod
# pin the CLI to a specific version via your package manager for reproducible builds
```

## When to escalate

- Consistent 5xx from the API → server-side issue; check the Infisical server/self-hosted logs
- A machine identity that should have access keeps getting 403 → review the identity's project role and the env/path scope in the Infisical UI
- Scan false positives that allowlisting can't suppress → refine `.infisical-scan.toml` rules (see the `secret-scanning` skill)
