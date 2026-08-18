# infisical-dev (Devin plugin)

Infisical CLI dev plugin for Agents Store. Complete command-line coverage for secrets management — install & auth, infisical run/secrets/export, dynamic secrets, secret scanning with pre-commit hooks, machine-identity CI/CD auth, self-hosted, and troubleshooting.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (6)

- `ci-cd-auth` — This skill should be used when the user asks to "use Infisical in CI/CD", "Infisical machine identity", "infisical login universal-auth", "authenticate Infisical without a browser", "Infisical in Docker", "inject secrets in a pipeline", "Infisical Kubernetes/AWS/GCP/Azure auth", or "bootstrap a self-hosted Infisical" — non-interactive Infisical CLI authentication and secret injection for automation.
- `cli-recipes` — This skill should be used when the user asks about "Infisical run", "infisical secrets", "inject secrets into a process", "Infisical export to .env", "infisical CLI commands", "manage secrets from the terminal", "Infisical folders", or "Infisical dynamic secrets lease" — the everyday Infisical CLI workflows for fetching, setting, injecting, and exporting secrets.
- `cli-reference` — This skill should be used when the user asks for "Infisical CLI reference", "all Infisical commands", "Infisical CLI flags", "Infisical environment variables", "infisical command list", or needs the full command/flag/env-var reference for the Infisical CLI.
- `secret-scanning` — This skill should be used when the user asks to "scan for secrets", "Infisical scan", "find leaked secrets in git", "set up a pre-commit secret scan", "infisical scan git-changes", "scan repo for API keys", "add a secret-scanning baseline", or "ignore a false-positive secret" — using the Infisical CLI to detect and prevent committed secrets.
- `setup` — This skill should be used when the user asks to "install Infisical CLI", "set up Infisical CLI", "log in to Infisical", "authenticate Infisical CLI", "verify Infisical is working", "is Infisical CLI working", "point Infisical at self-hosted", or needs to get the Infisical CLI installed, authenticated, and confirmed operational.
- `troubleshoot` — This skill should be used when the user hits "Infisical CLI errors", "Infisical login fails", "Infisical keyring error", "infisical project not found", "Infisical token not working", "Infisical self-hosted connection issues", "infisical run no secrets", or needs to diagnose and fix problems with the Infisical CLI.

## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/infisical-dev
