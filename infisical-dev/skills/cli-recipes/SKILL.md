---
name: cli-recipes
description: This skill should be used when the user asks about "Infisical run", "infisical secrets", "inject secrets into a process", "Infisical export to .env", "infisical CLI commands", "manage secrets from the terminal", "Infisical folders", or "Infisical dynamic secrets lease" — the everyday Infisical CLI workflows for fetching, setting, injecting, and exporting secrets.
---

# Infisical CLI Recipes

Everyday command-line workflows. Assumes the CLI is installed, authenticated, and the project is linked (see the `setup` skill). All commands default to `--env=dev` and `--path=/` unless overridden.

## Link a project (`init`)

```bash
infisical init   # writes .infisical.json with workspaceId + env mapping
```

`.infisical.json` resolves which environment a command uses, in this precedence: `--env` flag > `gitBranchToEnvironmentMapping` (current branch; only the part after the last `/` is matched) > `defaultEnvironment` > `dev`. An optional `"domain"` field pins the Infisical instance (EU Cloud, dedicated, self-hosted) for the repository.

```json
{
  "workspaceId": "63ee5410a45f7a1ed39ba118",
  "defaultEnvironment": "dev",
  "gitBranchToEnvironmentMapping": { "main": "prod", "develop": "dev" }
}
```

## Inject secrets into a process (`run`)

`run` is the core command — it fetches secrets and injects them as environment variables into the child process. No `.env` file ever touches disk.

```bash
infisical run -- npm run dev                       # inject into a command
infisical run --env=staging -- npm start           # pick environment
infisical run --env=prod --path=/api -- node app.js # scope to a folder
infisical run --path=/common --path=/web -- npm run dev   # merge folders (the last --path wins on conflict)
infisical run --recursive -- npm run dev           # also inject every sub-folder of the path
infisical run --tags=backend,critical -- npm run dev      # filter by tag slugs
infisical run --watch -- npm run dev               # restart on secret change (dev only)
infisical run --watch --watch-interval=30 -- npm run dev  # poll every 30 s (default 10, minimum 5)
infisical run --command "npm run migrate && npm start"    # chained shell commands
```

Useful `run` flags: `--expand` (resolve `${VAR}` references in secret values, default on), `--include-imports` (default on), `--secret-overriding` (personal secrets win over shared, default on), `--recursive` (sub-folders), `--watch-interval` (seconds between `--watch` checks), `--projectId` (required under machine-identity auth without `.infisical.json`), `--project-config-dir` (point at the `.infisical.json` dir in a monorepo).

## Read & write secrets (`secrets`)

```bash
# List
infisical secrets                                  # all secrets in dev:/
infisical secrets --env=prod --path=/api           # scope by env + folder
infisical secrets --env=staging --path=/ --recursive   # include every sub-folder
infisical secrets --output=json                     # json | yaml | dotenv instead of the table (script-friendly)

# Get
infisical secrets get DATABASE_URL
infisical secrets get DATABASE_URL PORT             # multiple at once
API_KEY=$(infisical secrets get API_KEY --plain --silent)   # capture into a var
infisical secrets get API_KEY --output=json          # structured alternative to --plain

# Set
infisical secrets set STRIPE_KEY=sk_live_xxx DOMAIN=example.com
infisical secrets set TLS_KEY=@cert.pem             # load value from a file
infisical secrets set DB_PASS=secret --type=personal   # personal override (default: shared)
infisical secrets set API_KEY=abc --tag backend --tag production   # attach tags (repeatable; replaces existing tags on update)
infisical secrets set --file=./.env                 # bulk import a .env / YAML file
infisical secrets set API_KEY=abc --show-values     # the result table masks values unless asked

# Delete
infisical secrets delete STRIPE_KEY DOMAIN --type=shared   # default --type is personal: without it only your personal override is deleted
infisical secrets delete API_KEY --env=prod --path=/api --type=shared
```

### Folders

```bash
infisical secrets folders                          # list folders at /
infisical secrets folders create --path=/ --name=api
infisical secrets folders delete --path=/ --name=api
```

### Seed a teammate's .env

`generate-example-env` produces a key-only template (reads `DEFAULT:<value>` hints from secret comments):

```bash
infisical secrets generate-example-env > .example-env
```

## Export secrets to a file (`export`)

```bash
infisical export > .env                             # dotenv to stdout
infisical export --format=dotenv-export --output-file=./.env
eval "$(infisical export --format=dotenv-eval)"     # load into the current shell (values are quoted)
infisical export --format=json   --output-file=./secrets.json
infisical export --format=yaml   --output-file=./secrets.yaml
infisical export --format=csv    --output-file=./secrets.csv
infisical export --env=prod --path=/api --tags=database
infisical export --expand=false                     # leave ${VAR} references literal
```

Formats: `dotenv` (default), `dotenv-export`, `dotenv-eval`, `json`, `yaml`, `csv`. `dotenv` and `dotenv-export` do not escape quotes inside values; `dotenv-eval` quotes every value, so it is the one to load into a shell with `eval` or `source` (no format escapes secret *names*, so only do that when every name is a valid shell variable name). `--output-file` takes a file or a directory — in a directory the CLI writes `.env`, `secrets.json`, `secrets.csv` or `secrets.yaml` depending on `--format`.

For custom output, pass a Go template and omit `--format`. Templates use the Infisical Agent's template functions, such as `listSecrets "<projectId>" "<env>" "<path>"` and `getSecretByName "<projectId>" "<env>" "<path>" "<name>"`, and choose their own project, environment and folder, so every other `export` flag except `--token` is ignored:

```bash
infisical export --template=./secrets.tmpl
```

```text
{{- with listSecrets "<project-id>" "dev" "/" }}
{{- range . }}
{{ .Key }}={{ .Value }}
{{- end }}
{{- end }}
```

> Prefer `infisical run` over `export` for running apps — exporting writes plaintext secrets to disk. Export only when a tool genuinely needs a file.

## Dynamic secrets & leases (`dynamic-secrets`)

Generate short-lived, on-demand credentials (DB users, SSH keys) and manage their leases:

```bash
infisical dynamic-secrets --env=dev --path=/         # list dynamic secrets
infisical dynamic-secrets lease create db-postgres --ttl=3600 --plain   # or --output=json|yaml|dotenv
infisical dynamic-secrets lease list db-postgres
infisical dynamic-secrets lease renew  <lease-id> --ttl=3600
infisical dynamic-secrets lease delete <lease-id>    # revoke
```

## Scripting patterns

```bash
# Export a single secret into the current shell
export API_KEY=$(infisical secrets get API_KEY --plain --silent)

# Pipe all dev secrets as JSON into another tool
infisical export --format=json | jq 'keys'

# One-off command with prod secrets, no config file (machine identity)
infisical run --token="$INFISICAL_TOKEN" --projectId="$PROJECT_ID" --env=prod -- ./deploy.sh
```

## Useful global flags

| Flag | Description |
|------|-------------|
| `--env`, `-e` | Environment slug (default `dev`) |
| `--path` | Folder path (default `/`; repeatable in `run`, where the last one wins; `--recursive` includes sub-folders) |
| `--projectId` | Target project (required with machine-identity auth, no config file) |
| `--token` | Machine-identity / service token (or `INFISICAL_TOKEN`) |
| `--domain` | Infisical instance URL for EU / dedicated / self-hosted (or `INFISICAL_DOMAIN`) |
| `--profile`, `--org` | Login profile / organization for this command only (or `INFISICAL_PROFILE` / `INFISICAL_ORG`) |
| `--output`, `-o` | `json`, `yaml` or `dotenv` output on `secrets`, `secrets get`, `dynamic-secrets` (preferred over `--plain`) |
| `--plain` | Raw values only, no formatting; deprecated on the `secrets` listing, still valid on `secrets get`, `lease create` and `login` |
| `--silent` | Suppress update notices and tips |
