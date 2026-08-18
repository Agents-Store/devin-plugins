---
name: cli-reference
description: This skill should be used when the user asks for "Infisical CLI reference", "all Infisical commands", "Infisical CLI flags", "Infisical environment variables", "infisical command list", or needs the full command/flag/env-var reference for the Infisical CLI.
disable-model-invocation: true
---

# Infisical CLI Reference

Complete command, flag, and environment-variable reference. For task-oriented usage see the `cli-recipes`, `secret-scanning`, and `ci-cd-auth` skills. Full docs: https://infisical.com/docs/cli/overview

## Command index

| Command | Purpose |
|---------|---------|
| `infisical login` | Authenticate (user or machine identity) |
| `infisical login status` | Report session/credential validity |
| `infisical init` | Link the current dir to a project (`.infisical.json`) |
| `infisical run` | Inject secrets into a process as env vars |
| `infisical secrets` | List / get / set / delete secrets + folders |
| `infisical export` | Export secrets to dotenv/json/yaml/csv/template |
| `infisical dynamic-secrets` | List dynamic secrets; manage leases |
| `infisical scan` | Scan code/git history for hardcoded secrets |
| `infisical vault` | View/switch the local credential backend |
| `infisical user` | Switch profiles, change domain, print token |
| `infisical token` | Renew a machine-identity access token |
| `infisical service-token` | Create service tokens (DEPRECATED) |
| `infisical bootstrap` | Initialize a fresh self-hosted instance |
| `infisical ssh` | Issue/connect short-lived SSH access |
| `infisical reset` | Clear all local Infisical config/credentials |

## login

```
infisical login [--method=<m>] [flags]
```

| Flag | Env var | Notes |
|------|---------|-------|
| `--method` | — | `user` (default), `universal-auth`, `kubernetes`, `azure`, `gcp-id-token`, `gcp-iam`, `aws-iam`, `oidc-auth`, `jwt-auth` |
| `--client-id` / `--client-secret` | `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID` / `..._CLIENT_SECRET` | Universal Auth |
| `--machine-identity-id` | `INFISICAL_MACHINE_IDENTITY_ID` | Native cloud methods |
| `--service-account-token-path` | `INFISICAL_KUBERNETES_SERVICE_ACCOUNT_TOKEN_PATH` | Kubernetes |
| `--service-account-key-file-path` | `INFISICAL_GCP_IAM_SERVICE_ACCOUNT_KEY_FILE_PATH` | GCP IAM |
| `--jwt` | `INFISICAL_JWT` | OIDC / JWT auth |
| `--email` / `--password` / `--organization-id` | `INFISICAL_EMAIL` / `INFISICAL_PASSWORD` / `INFISICAL_ORGANIZATION_ID` | Direct user login |
| `--interactive`, `-i` | — | Terminal prompts (no browser) |
| `--plain` | — | Output the raw JWT only |
| `--silent` | — | Suppress update notices |
| `--domain` | `INFISICAL_API_URL` | Self-hosted / EU API URL |

`infisical login status [--json] [--token=<t>]` — exit `0` if ≥1 valid session, `1` otherwise.

## init

```
infisical init    # interactive; writes .infisical.json (workspaceId, defaultEnvironment, gitBranchToEnvironmentMapping)
```

## run

```
infisical run [flags] -- <command>
infisical run [flags] --command="<chained shell>"
```

Flags: `--env`/`-e` (def `dev`), `--path` (def `/`, repeatable), `--projectId`, `--token`, `--tags`, `--expand` (def `true`), `--include-imports` (def `true`), `--secret-overriding` (def `true`), `--watch`, `--command`, `--project-config-dir`, `--domain`.

## secrets

```
infisical secrets [--env --path --projectId --token --plain --expand --include-imports]
infisical secrets get <KEY...> [--plain --silent]
infisical secrets set <KEY=VALUE...> [--type=shared|personal] [--file=<path>]   # KEY=@file loads from file
infisical secrets delete <KEY...>
infisical secrets folders [get|create|delete] --path=<p> [--name=<n>]
infisical secrets generate-example-env > .example-env
```

## export

```
infisical export [--format=dotenv|dotenv-export|json|yaml|csv] [--output-file=<f>] [--template=<f>] \
                 [--env --path --projectId --tags --expand --include-imports --secret-overriding --token]
```

## dynamic-secrets

```
infisical dynamic-secrets [--env --path --projectId --project-slug --token]
infisical dynamic-secrets lease create <name> [--ttl --plain --kubernetes-namespace --principals]
infisical dynamic-secrets lease list   <name>
infisical dynamic-secrets lease renew  <lease-id> [--ttl]
infisical dynamic-secrets lease delete <lease-id>
```

## scan

```
infisical scan [-s --source] [-c --config] [-b --baseline-path] [-r --report-path]
               [-f --report-format=json|csv|sarif] [--exit-code=1] [--redact] [-v --verbose]
               [--no-git] [--log-opts] [--max-target-megabytes] [--pipe] [--follow-symlinks]
infisical scan git-changes [--staged] [-v]
infisical scan install --pre-commit-hook
```

## vault / user / token / reset

```
infisical vault                 # show backend
infisical vault set <auto|file|keychain>
infisical user switch           # switch logged-in profiles
infisical user update domain    # change a profile's API URL
infisical user get token [--plain]
infisical token renew <ua-access-token>
infisical reset                 # clear all local config/credentials
```

## bootstrap

```
infisical bootstrap --domain --email --password --organization
                    [--ignore-if-bootstrapped] [--output=k8-secret]
                    [--k8-secret-template --k8-secret-name --k8-secret-namespace]
```
Env vars: `INFISICAL_ADMIN_EMAIL`, `INFISICAL_ADMIN_PASSWORD`, `INFISICAL_ADMIN_ORGANIZATION`.

## ssh

```
infisical ssh connect  [--hostname --login-user --write-host-ca-to-file --out-file-path --token]
infisical ssh add-host --projectId --hostname [--alias --configure-sshd
                       --write-user-ca-to-file --user-ca-out-file-path --write-host-cert-to-file --force --token]
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `INFISICAL_TOKEN` | Machine-identity / service-token auth (auto-detected) |
| `INFISICAL_API_URL` | Backend URL for self-hosted / EU (= `--domain`) |
| `INFISICAL_DISABLE_UPDATE_CHECK` | `true` to skip version checks (use in CI/prod) |
| `INFISICAL_CUSTOM_HEADERS` | Space-separated `name=value` extra HTTP headers (reverse-proxy auth) |
| `INFISICAL_SCAN_CONFIG` | Path to a scan TOML config |
| `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID` / `..._CLIENT_SECRET` | Universal Auth credentials |
| `INFISICAL_MACHINE_IDENTITY_ID` | Native cloud auth methods |
| `INFISICAL_JWT` | OIDC / JWT auth |
| `INFISICAL_EMAIL` / `INFISICAL_PASSWORD` / `INFISICAL_ORGANIZATION_ID` | Direct user login |
| `INFISICAL_ADMIN_EMAIL` / `INFISICAL_ADMIN_PASSWORD` / `INFISICAL_ADMIN_ORGANIZATION` | Bootstrap |

## Deprecations

- **Service tokens** (`infisical service-token create`) — use machine identities instead.
- **`--raw-value`** — replaced by `--plain`.
- `infisical kms` and `infisical agent` are **not** current CLI commands (KMS is API/UI only). Verify with `infisical <cmd> --help` against your binary before relying on them.
