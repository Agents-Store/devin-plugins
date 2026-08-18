---
name: troubleshoot
description: This skill should be used when the user hits "Infisical CLI errors", "Infisical login fails", "Infisical keyring error", "infisical project not found", "Infisical token not working", "Infisical self-hosted connection issues", "infisical run no secrets", or needs to diagnose and fix problems with the Infisical CLI.
---

# Infisical CLI Troubleshooting

Diagnostics and fixes for common Infisical CLI problems.

## Quick diagnostics

Run these first to localize the problem:

```bash
infisical --version          # CLI installed and on PATH?
infisical login status       # is there a valid session/token?
infisical vault              # which credential backend is active?
echo "$INFISICAL_API_URL"    # pointing at the right instance?
infisical secrets --env=dev  # can it actually read the project?
```

## Login & credential store

| Symptom | Cause | Fix |
|---------|-------|-----|
| `failed to store credentials` / keyring errors on Linux/WSL/headless | No system keyring available | `infisical vault set file` to use the encrypted file backend, then log in again |
| Browser never opens (SSH session, container) | No GUI to launch the browser | `infisical login -i` for interactive terminal prompts, or use machine-identity auth |
| Login succeeds but later commands say unauthenticated | Token expired or wrong profile active | `infisical login status`; re-login, or `infisical user switch` to the right profile |
| Stale/corrupt local state after switching instances | Old config cached | `infisical reset` to clear all local config, then log in fresh |

## Self-hosted & networking

| Symptom | Cause | Fix |
|---------|-------|-----|
| Commands hit US Cloud instead of your instance | `INFISICAL_API_URL` not set | `export INFISICAL_API_URL="https://your-instance"`; set it before `login` too |
| `--domain` on `login` seems ignored | Known historical quirk for some self-hosted flows | Use the `INFISICAL_API_URL` env var instead of the flag |
| 4xx from a proxied instance (Cloudflare Access, etc.) | Missing edge-auth headers | `export INFISICAL_CUSTOM_HEADERS="Access-Client-Id=… Access-Client-Secret=…"` |
| TLS / cert errors | Self-signed or internal CA | Trust the CA on the host; verify the URL scheme is `https` and reachable |

## Tokens & permissions (CI/CD)

| Symptom | Cause | Fix |
|---------|-------|-----|
| `INFISICAL_TOKEN` not picked up | Not exported into the process/container | Ensure it is `export`ed (or passed via `docker run --env INFISICAL_TOKEN=...`) |
| `project not found` / empty results under machine identity | No `.infisical.json` and no `--projectId` | Pass `--projectId=<id>` explicitly |
| `403` / scope errors | Identity lacks access to the env+path | Grant the machine identity access to the target environment and folder |
| Token rejected after a while | Access-token TTL exceeded | `infisical token renew <token>`, or re-login to mint a new one |
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
