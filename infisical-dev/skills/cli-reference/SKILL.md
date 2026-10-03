---
name: cli-reference
description: This skill should be used when the user asks for "Infisical CLI reference", "all Infisical commands", "Infisical CLI flags", "Infisical environment variables", "infisical command list", or needs the full command/flag/env-var reference for the Infisical CLI.
disable-model-invocation: true
---

# Infisical CLI Reference

Complete command, flag, and environment-variable reference, checked against the CLI `--help` output of release 0.43.138 (2026-09-30) and https://infisical.com/docs/cli/reference. For task-oriented usage see the `cli-recipes`, `secret-scanning`, and `ci-cd-auth` skills.

Flags and commands that need a recent binary are tagged with the version that introduced them; run `infisical --version` and `infisical <cmd> --help` before relying on one.

## Command index

| Command | Purpose |
|---------|---------|
| `infisical login` | Authenticate (user or machine identity) |
| `infisical login status` | Report session/credential validity |
| `infisical logout` | End a login session and revoke it on the server (>= 0.43.134) |
| `infisical profile` | Named login profiles: several orgs, accounts, instances (>= 0.43.134) |
| `infisical org` | List organizations; change the one a profile uses (>= 0.43.134) |
| `infisical init` | Link the current dir to a project (`.infisical.json`) |
| `infisical run` | Inject secrets into a process as env vars |
| `infisical secrets` | List / get / set / delete secrets + folders; `agent-proxy` |
| `infisical export` | Export secrets to dotenv/json/yaml/csv/template |
| `infisical dynamic-secrets` | List dynamic secrets; manage leases |
| `infisical scan` | Scan code/git history for hardcoded secrets |
| `infisical vault` | View/switch the local credential backend |
| `infisical user` | Print a profile token, pick the default profile, change a profile's domain |
| `infisical token` | Renew a machine-identity access token |
| `infisical service-token` | Create service tokens (DEPRECATED) |
| `infisical bootstrap` | Initialize a fresh self-hosted instance |
| `infisical ssh` | Issue SSH credentials/certificates, connect, register hosts |
| `infisical agent` | Daemon that authenticates and renders secrets into files |
| `infisical cert-manager` | `cert-manager agent`: the same daemon for certificate lifecycle |
| `infisical gateway` | Gateway for private-network access (`start`, `systemd`) |
| `infisical relay` | Relay component (`start`, `systemd`) |
| `infisical proxy` | Caching proxy server for secrets (`start`) |
| `infisical pam` | Privileged access: `access`, `agentic access` |
| `infisical kmip` | KMIP server (`start`, `systemd`) |
| `infisical agent-vault` (alias `av`) | Run AI agents that hold no credentials behind a proxy (>= 0.43.132) |
| `infisical reset` | Clear all local Infisical config/credentials |

`infisical kms` is **not** a command (KMS is API/UI only).

## Global flags

Every command accepts these.

| Flag | Env var | Notes |
|------|---------|-------|
| `--domain` | `INFISICAL_DOMAIN` | Infisical instance URL (EU Cloud, dedicated, self-hosted); see "Choosing the instance" |
| `--profile` | `INFISICAL_PROFILE` | Login profile for this command only |
| `--org` | `INFISICAL_ORG` | Organization (name, slug or id) for this command only; the profile keeps its own |
| `--silent` | — | Hide update notices and tip/info messages (scripts, CI) |
| `-l`, `--log-level` | — | `trace`, `debug`, `info`, `warn`, `error`, `fatal` |
| `--log-format` | `LOG_FORMAT` | `console`, `plain`, `json` |
| `--log-destination` | `LOG_DESTINATION` | `stderr` (default) or `stdout` |
| `--telemetry` | — | Usage telemetry, on by default |

### Choosing the instance

The CLI picks the Infisical instance in this order:

1. `--domain`
2. `INFISICAL_DOMAIN` (>= 0.43.92), or the older alias listed under Environment variables when `INFISICAL_DOMAIN` is unset
3. `domain` in `.infisical.json` (>= 0.43.92; must start with `https://` or `http://`)
4. US Cloud (`https://app.infisical.com`)

`infisical login` uses that choice to pick the instance to log in to. After a user login, commands go to the instance of the profile in use, and a `--domain` / `INFISICAL_DOMAIN` that names a different instance makes the command fail. `INFISICAL_DOMAIN` is an explicit instance choice even for Infisical Cloud URLs (>= 0.43.130).

`infisical agent` ignores `--domain` (set `infisical.address` in its config file). `infisical token renew` does not use a profile, so pass `--domain` or set `INFISICAL_DOMAIN` for any instance other than US Cloud.

## login

```
infisical login [--method=<m>] [flags]
```

User logins are stored as a **profile** (see `profile`). Machine-identity logins (any method other than `user`) create no profile; they print an access token that later commands read from `--token` or `INFISICAL_TOKEN`.

| Flag | Env var | Notes |
|------|---------|-------|
| `--method` | — | `user` (default), `universal-auth`, `kubernetes`, `azure`, `gcp-id-token`, `gcp-iam`, `aws-iam`, `oidc-auth`, `jwt-auth` (the 0.43.138 `login --help` omits `jwt-auth` from this list, but its `--jwt` text and the docs name it) |
| `--client-id` / `--client-secret` | `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID` / `..._CLIENT_SECRET` | Universal Auth |
| `--machine-identity-id` | `INFISICAL_MACHINE_IDENTITY_ID` | Required for every method except `user` and `universal-auth` |
| `--service-account-token-path` | `INFISICAL_KUBERNETES_SERVICE_ACCOUNT_TOKEN_PATH` | Kubernetes |
| `--service-account-key-file-path` | `INFISICAL_GCP_IAM_SERVICE_ACCOUNT_KEY_FILE_PATH` | GCP IAM |
| `--jwt` | `INFISICAL_JWT` | `oidc-auth` / `jwt-auth` (replaces the deprecated `--oidc-jwt`) |
| `--organization-slug` | — | Scope a machine-identity session to a sub-organization it can reach (default: the org it was created in) |
| `--email` / `--password` / `--organization-id` | `INFISICAL_EMAIL` / `INFISICAL_PASSWORD` / `INFISICAL_ORGANIZATION_ID` | Direct user login, no prompts |
| `--interactive`, `-i` | — | Terminal prompts (no browser) |
| `--save-as <name>` | — | Store this user login under a profile name you choose (>= 0.43.134) |
| `--profile <name>` | `INFISICAL_PROFILE` | Sign back in to an existing profile |
| `--plain` | — | Output the raw access token only (no `-o/--output` alternative on `login`) |
| `--clear-domains` | — | Remove saved self-hosted domains from the CLI config, then exit |

`--silent` and `--domain` are global flags (see above).

`infisical login status [--json] [--token=<t>]` — exit `0` if at least one valid session, `1` otherwise.

`infisical logout [--all] [--local-only]` — revoke the profile's session on the server and delete its stored credentials (the profile itself stays; `--local-only` skips the server call; `--all` covers every profile).

## profile and org

Named login profiles (>= 0.43.134). A profile is one login: an account on one instance plus the organization it uses by default.

```
infisical profile list
infisical profile current [--plain]          # which profile applies here, and why
infisical profile create <name> [--org <o>] [--pin] [--use]   # another org, same login (>= 0.43.135; `profile new` in 0.43.134)
infisical login --save-as <name>             # another account or instance
infisical profile use <name>                 # default for this machine (user switch = same, with a picker)
eval "$(infisical profile pin <name>)"       # this terminal only (sets INFISICAL_PROFILE); unpin to undo
infisical profile bind [<name>] [<path>]     # a directory tree; stored in your CLI config, never in the repo
infisical profile unbind [<path>]
infisical profile set-org [<org>]            # same as: infisical org switch [<org>]
infisical profile rename <name> <new-name>
infisical profile delete <name> [--local-only]
infisical org list
```

A command uses the first that is set: `--profile` > `INFISICAL_PROFILE` (pin) > a bound directory > the default profile. In scripts and CI set `INFISICAL_PROFILE` or pass `--profile`; `pin` only prints an `export` line for a shell to evaluate.

## init

```
infisical init    # interactive; writes .infisical.json (workspaceId, defaultEnvironment, gitBranchToEnvironmentMapping)
```

`.infisical.json` may also hold `domain` (the instance, >= 0.43.92) and `defaultSecretPath` (read only by `secrets agent-proxy`). It is committed to git, so anyone who can edit it can redirect the CLI; the CLI prints a warning naming the host each time it uses `domain` from the file. Machine-identity logins ignore `workspaceId` — pass `--projectId` or `INFISICAL_PROJECT_ID`.

## run

```
infisical run [flags] -- <command>
infisical run [flags] --command="<chained shell>"
```

Flags: `--env`/`-e` (def `dev`), `--path` (def `/`, repeatable; **the last `--path` wins** when a secret exists in several), `--recursive` (also sub-folders of each path), `--projectId`, `--token`, `--tags`/`-t`, `--expand` (def `true`), `--include-imports` (def `true`), `--secret-overriding` (def `true`), `--watch`, `--watch-interval <sec>` (def `10`, minimum `5`), `--command`/`-c`, `--project-config-dir`.

Secrets override variables already set in the shell; `HOME`, `PATH`, `PS1`, `PS2`, `PWD`, `EDITOR`, `XAUTHORITY`, `USER`, `TERM`, `TERMINFO`, `SHELL`, `MAIL`, `XDG_*` and `LC_*` are never injected.

## secrets

```
infisical secrets [--env --path --recursive --projectId --token -t/--tags -o/--output yaml|json|dotenv --expand --include-imports --secret-overriding]
infisical secrets get <KEY...> [-o yaml|json|dotenv | --plain] [--silent]
infisical secrets set <KEY=VALUE...> [--type=shared|personal] [--file=<path>] [--tag <t>]... [--show-values] [-o ...]   # KEY=@file loads from file
infisical secrets delete <KEY...> [--type=personal|shared]   # default: personal
infisical secrets folders [get|create|delete] --path=<p> [--name=<n>] [--env <e>]
infisical secrets generate-example-env > .example-env
infisical secrets agent-proxy start|connect|run     # brokers credentials onto an AI agent's requests (>= 0.43.105)
```

`--plain` on the **listing** (`infisical secrets --plain`) is deprecated: use `-o/--output dotenv|json|yaml`. `--plain` on `secrets get` is not deprecated in 0.43.138; `-o/--output` works there too. `secrets set` hides values in its result table unless `--show-values` is passed.

`secrets agent-proxy`: `start` runs the MITM proxy (`--port` def `17322`, `--unmatched-host allow|block`); `connect --proxy <host:port> -- <agent>` launches an agent behind it; `run -- <agent>` starts an OS-sandboxed agent on this machine (`--allow-host/--allow-read/--allow-write`, `--no-sandbox` turns the sandbox off).

## export

```
infisical export [--format=dotenv|dotenv-export|dotenv-eval|json|yaml|csv] [-o|--output-file=<f>] [--template=<f>] \
                 [--env --path --projectId --tags --expand --include-imports --secret-overriding --token]
```

- `dotenv` writes `KEY='value'`, `dotenv-export` adds `export`; neither escapes quotes inside values. `dotenv-eval` (>= 0.43.98) quotes values so the output is safe for `eval "$(infisical export --format=dotenv-eval)"` or `source`. No format escapes secret *names*, so load into a shell only when every name is a valid shell variable name.
- `-o`/`--output-file` takes a file or a directory; in a directory the CLI writes `.env`, `secrets.json`, `secrets.csv` or `secrets.yaml` depending on `--format`.
- `--template=<file>` renders a Go template with the Infisical Agent's template functions (such as `listSecrets` and `getSecretByName`) and ignores every other flag except `--token`.
- `export` has no `--recursive` flag in 0.43.138 (`run` and `secrets` do).

## dynamic-secrets

```
infisical dynamic-secrets [--env --path --projectId --project-slug --token -o yaml|json|dotenv]
infisical dynamic-secrets lease create <name> [--ttl --plain|-o yaml|json|dotenv -p/--path --project-slug --kubernetes-namespace --principals]
infisical dynamic-secrets lease list   <name>
infisical dynamic-secrets lease renew  <lease-id> [--ttl]
infisical dynamic-secrets lease delete <lease-id>
```

`lease create --plain` is not deprecated in 0.43.138; `-o/--output` is the structured alternative.

## scan

```
infisical scan [-s --source] [-c --config] [-b --baseline-path] [-r --report-path]
               [-f --report-format=json|csv|sarif] [--exit-code=1] [--redact] [-v --verbose] [--no-color]
               [--confidence=low|medium|high] [--platform=github|gitlab|azuredevops|bitbucket]
               [--no-git] [--log-opts] [--max-target-megabytes] [--pipe] [--follow-symlinks]
infisical scan git-changes [--staged] [--confidence=...] [-v]
infisical scan install --pre-commit-hook
```

- `--confidence` (>= 0.43.136, default `medium`): lowest confidence reported; findings from rules that set no confidence are always reported.
- `--redact` hides secret values in **verbose output only**; a report written with `--report-path` still contains the secrets.
- Config order: `--config` > `INFISICAL_SCAN_CONFIG` > `.infisical-scan.toml` in `--source` > built-in rules. Turn the installed hook off with `git config hooks.infisical-scan false`.

## vault / user / token / reset

```
infisical vault                 # show where login credentials are stored
infisical vault set [file|auto]
infisical user switch           # pick the default profile (same as profile use)
infisical user update domain    # interactive: point a profile at another instance (clears its credentials)
infisical user get token [--plain]
infisical token renew <ua-access-token>      # needs --domain / INFISICAL_DOMAIN off US Cloud
infisical reset [--local-only]  # revoke all profile sessions, delete ~/.infisical and stored credentials
```

Vault backends: `auto` (default) is the system keyring (macOS Keychain, Windows Credential Manager, Secret Service on Linux) and falls back to `file` by itself when the keyring cannot be written; `file` keeps credentials encrypted in `~/infisical-keyring`. There is no `keychain` value. `vault set` removes every profile, the default profile and every directory binding, so log in again afterwards.

## bootstrap

```
infisical bootstrap --domain --email --password --organization
                    [--ignore-if-bootstrapped] [--output=json|k8-secret]
                    [--k8-secret-template --k8-secret-name --k8-secret-namespace]
```
Env vars: `INFISICAL_DOMAIN` (for `--domain`), `INFISICAL_ADMIN_EMAIL`, `INFISICAL_ADMIN_PASSWORD`, `INFISICAL_ADMIN_ORGANIZATION`.

## ssh

```
infisical ssh connect  [--hostname --login-user --write-host-ca-to-file --out-file-path --token]
infisical ssh add-host --projectId --hostname [--alias --configure-sshd
                       --write-user-ca-to-file --user-ca-out-file-path --write-host-cert-to-file --force --token]
infisical ssh issue-credentials --certificateTemplateId <id> [--principals --ttl --certType <type> --keyAlgorithm --keyId --outFilePath --addToAgent --token]
infisical ssh sign-key  --certificateTemplateId <id> (--publicKey <key> | --publicKeyFilePath <file>) [--principals --ttl --certType --keyId --outFilePath --token]
```

## agent and cert-manager

```
infisical agent --config agent-config.yaml           # default config path
infisical cert-manager agent --config certificate-agent-config.yaml [-v]
```

The Infisical Agent authenticates as a machine identity and renders secrets (or certificates) into files for an application, without `run`. Everything — auth method, sinks, templates, instance address (`infisical.address`) — lives in the YAML config; `INFISICAL_AGENT_CONFIG_BASE64` (base64 of the YAML) takes precedence over `--config`.

## gateway, relay, proxy, kmip

```
infisical gateway start [name] --token <t> | --enroll-method token|aws|gcp|kubernetes [--gateway-id --domain --target-relay-name --listen-address --bind]
sudo infisical gateway systemd install|uninstall <name> ...
infisical relay start --type org|instance --name <n> --host <h> --token <t> | --enroll-method token|aws [--relay-id --domain]
sudo infisical relay systemd install|uninstall <name> ...
infisical proxy start [--domain <url>] [--listen-address <host:port>] [--enable-event-subscriptions --client-id --client-secret] [--tls-enabled --tls-cert-file --tls-key-file]
infisical kmip start <server-name> --enroll-method token|aws --token <t> --domain <url> [--hostnames-or-ips --listen-address --certificate-ttl]
sudo infisical kmip systemd install|uninstall <server-name> ...
```

Deprecated: `gateway start --relay` (use `--target-relay-name`). `--domain` here is the command's own flag for the instance.

## pam

```
infisical pam access <folder/account> [--duration 1h] [--reason <text>] [--proxy] [--port N] [--target <host>] [-- <command>]
infisical pam agentic access [--account folder/account]... [--agent claude|codex|gemini|generic] [--duration] [--reason] [--no-sandbox] -- <agent command>
```

`pam access` runs as a logged-in user (no machine identity); `pam agentic access` also accepts `--token` or `--auth-method` with machine-identity flags.

## agent-vault

```
infisical agent-vault proxy [--enrollment-token <t>] [--port 17323] [--data-dir <d>]
infisical agent-vault run (--access-bundle <name> | --session-token <t>) --proxy <host:port> [--ca-fingerprint --ttl --keep-session --no-proxy] -- <agent command>
```

`run` only sets environment variables and starts the agent; unlike `secrets agent-proxy run` it does not sandbox it. Agent Vault is a different product from `secrets agent-proxy`.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `INFISICAL_TOKEN` | Machine-identity / service-token auth (auto-detected) |
| `INFISICAL_DOMAIN` | Instance URL for EU / dedicated / self-hosted (= `--domain`); preferred |
| `INFISICAL_API_URL` | Older alias of `INFISICAL_DOMAIN`, still read when `INFISICAL_DOMAIN` is unset |
| `INFISICAL_PROFILE` | Login profile to use (set by `eval "$(infisical profile pin <name>)"`) |
| `INFISICAL_ORG` | Organization for the command (= `--org`) |
| `INFISICAL_PROJECT_ID` | Project for machine-identity auth (= `--projectId`) |
| `INFISICAL_DISABLE_UPDATE_CHECK` | `true` to skip version checks (use in CI/prod) |
| `INFISICAL_CUSTOM_HEADERS` | Space-separated `name=value` extra HTTP headers (reverse-proxy auth) |
| `INFISICAL_SCAN_CONFIG` | Path to a scan TOML config |
| `INFISICAL_AGENT_CONFIG_BASE64` | Base64 agent config instead of `--config` |
| `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID` / `..._CLIENT_SECRET` | Universal Auth credentials |
| `INFISICAL_MACHINE_IDENTITY_ID` | Native cloud auth methods |
| `INFISICAL_JWT` | OIDC / JWT auth |
| `INFISICAL_EMAIL` / `INFISICAL_PASSWORD` / `INFISICAL_ORGANIZATION_ID` | Direct user login |
| `INFISICAL_ADMIN_EMAIL` / `INFISICAL_ADMIN_PASSWORD` / `INFISICAL_ADMIN_ORGANIZATION` | Bootstrap |
| `LOG_FORMAT` / `LOG_DESTINATION` | Log format and destination |

## Deprecations

- **Service tokens** (`infisical service-token create`) — use machine identities instead.
- **`--raw-value`** — replaced by `--plain`.
- **`infisical secrets --plain`** (listing) — use `-o/--output`.
- **`login --oidc-jwt`** — use `--jwt`.
- **`profile set-org --org-id`** / `org switch --org-id` — pass the organization as an argument.
- **`gateway start --relay`** — use `--target-relay-name`.
- `infisical agent` **is** a current command (the Infisical Agent daemon); `infisical kms` is not — KMS is API/UI only. Verify any other command with `infisical <cmd> --help` against your binary.
