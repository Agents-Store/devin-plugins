---
name: n8n-cli-recipes
description: n8n CLI commands for self-hosted instances. Use when executing workflows from command line, exporting/importing workflows and credentials, managing licenses, resetting user accounts, running security audits via CLI, or managing community nodes. Also use when asking about "n8n CLI", "command line", "n8n execute", "export workflow".
---

# n8n CLI Recipes

n8n has two command-line tools; do not mix them up.

| | **Server CLI** (`n8n <command>`) | **n8n CLI** (`n8n-cli`, package `@n8n/cli`) |
|---|---|---|
| Runs | on the machine that hosts n8n | from any machine with network access |
| Authenticates with | direct database access (bypasses access control) | an API key (respects the key's scopes) |
| Needs n8n running | no, for most commands | yes |
| Best for | backups, migrations, license, emergency resets | scripts, remote management, AI agents |

Everything below, up to the `@n8n/cli` section at the end, is the **Server CLI**.

## Running CLI Commands

How you invoke CLI commands depends on your installation method.

### npm / Global Install

```bash
n8n <command>
```

> **n8n 3.0 (scheduled for October 2026) no longer supports installs run with `npm` or `npx n8n` — self-hosted n8n will require Docker.** Plan the move before upgrading; for new setups use the Docker forms below.

### Docker

```bash
docker exec -u node -it <container-name> n8n <command>
```

Replace `<container-name>` with your n8n container name (e.g., `n8n`, `n8n-main`).

### Docker Compose

```bash
docker compose exec -u node n8n n8n <command>
```

---

## Workflow Execution

Execute a workflow directly from the command line without needing a trigger.

```bash
# Execute workflow by ID
n8n execute --id <WORKFLOW_ID>
```

This runs the workflow once synchronously and outputs the result to stdout. Useful for:
- Testing workflows without a trigger
- Cron-based execution via system crontab
- CI/CD pipeline integration

---

## Workflow Status Management

In n8n 2.x a workflow is *published* or *unpublished* (it was "active" / "inactive" in 1.x). The CLI changes that state directly in the database.

```bash
# Publish the current draft of one workflow
n8n publish:workflow --id=<ID>

# Publish a specific historical version
n8n publish:workflow --id=<ID> --versionId=<VERSION_ID>

# Unpublish one workflow
n8n unpublish:workflow --id=<ID>

# Unpublish ALL workflows
n8n unpublish:workflow --all
```

- `publish:workflow` has **no `--all`** on purpose: it stops accidental bulk publishing in production. Publish workflows one ID at a time.
- `unpublish:workflow` takes either `--id` or `--all`, never both.
- The old `update:workflow` command is **deprecated since n8n 2.0 and will be removed**. Do not use it in new scripts.

**Important:** These commands operate on the database. If n8n is running, the change only takes effect after you **restart n8n**.

---

## Export

### Export Workflows

```bash
# Export all workflows to stdout (JSON)
n8n export:workflow --all

# Export a single workflow to a file
n8n export:workflow --id=<ID> --output=workflow.json

# Export all workflows as separate files in a directory
n8n export:workflow --all --separate --output=backups/workflows/

# Export with backup flag (shorthand for --all --pretty --separate)
n8n export:workflow --backup --output=backups/latest/

# Pretty-print the JSON output
n8n export:workflow --all --pretty

# Export the published version instead of the current draft
n8n export:workflow --id=<ID> --published --output=published.json
n8n export:workflow --all --published --output=workflows.json     # unpublished workflows are skipped

# Export one historical version
n8n export:workflow --id=<ID> --version=<VERSION_ID> --output=workflow-v1.json
```

Exports now carry a `versionMetadata` property (the version's historical name and description); import preserves it in the workflow history.

### Export Credentials

```bash
# Export all credentials (encrypted)
n8n export:credentials --all

# Export a single credential
n8n export:credentials --id=<ID> --output=credential.json

# Export all credentials DECRYPTED (plaintext secrets)
n8n export:credentials --all --decrypted --output=decrypted-creds.json

# Export as separate files
n8n export:credentials --all --separate --output=backups/credentials/
```

### Export Entities (Full Database Export)

```bash
# Export entire n8n database (workflows, credentials, tags, variables, etc.)
n8n export:entities --outputDir=./outputs

# Include execution history and data tables
n8n export:entities --outputDir=./outputs --includeExecutionHistoryDataTables=true
```

### Export Flags Reference

| Flag | Description |
|------|-------------|
| `--all` | Export all items of this type |
| `--id=<ID>` | Export a single item by ID |
| `--output=<path>` | Output file or directory path |
| `--backup` | Shorthand for `--all --pretty --separate`; combine with `--output=<directory>`. Exports workflows and credentials only — not a complete instance backup |
| `--published` | Export the published version instead of the draft (workflows only; with `--all`, unpublished workflows are skipped; not with `--version`) |
| `--version=<ID>` | Export one historical version (workflows only; not with `--all` or `--published`) |
| `--pretty` | Pretty-print JSON output |
| `--separate` | Write each item as a separate file |
| `--decrypted` | Export credentials with decrypted (plaintext) secret values |

> **Security Warning:** The `--decrypted` flag exports sensitive credential data in **plaintext**. Never commit decrypted exports to version control. Store them securely and delete after use.

---

## Import

### Import Workflows

```bash
# Import workflow(s) from a single file
n8n import:workflow --input=workflow.json

# Import multiple workflows from separate files in a directory
n8n import:workflow --separate --input=backups/workflows/

# Import into a specific project
n8n import:workflow --input=workflow.json --projectId=<PROJECT_ID>

# Import and assign to a specific user
n8n import:workflow --input=workflow.json --userId=<USER_ID>

# Keep each file's `active` flag instead of unpublishing everything (multi-main / queue mode only)
n8n import:workflow --separate --input=backups/workflows/ --activeState=fromJson
```

**`import:workflow` unpublishes every imported workflow** by default (`--activeState=false`). After a restore, publish the workflows you need one by one. Imported workflows keep their exported IDs and **overwrite** workflows with the same ID — change or delete the IDs first if that is not what you want. Known issue: on a single-main instance the cron triggers of a previously active workflow keep running until n8n restarts.

### Import Credentials

```bash
# Import credential(s) from a file
n8n import:credentials --input=credentials.json

# Import from separate files
n8n import:credentials --separate --input=backups/credentials/
```

### Import Entities (Full Database Import)

```bash
# Import full database export
n8n import:entities --inputDir=./outputs

# Import and truncate existing tables first
n8n import:entities --inputDir=./outputs --truncateTables=true
```

### Import Flags Reference

| Flag | Description |
|------|-------------|
| `--input=<path>` | Input file or directory path |
| `--separate` | Read from separate files in a directory |
| `--projectId=<ID>` | Import into a specific project |
| `--userId=<ID>` | Assign imported items to a specific user (not with `--projectId`) |
| `--activeState=<false\|fromJson>` | `false` (default) unpublishes imported workflows; `fromJson` keeps each file's `active` field (multi-main / queue mode only) |
| `--skipMigrationChecks` | Skip database migration version checks during import |
| `--truncateTables` | Clear existing data before importing (entities only) |

---

## Backup and Restore Pattern

### Full Backup

```bash
# Create timestamped backup directory
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Export workflows
n8n export:workflow --all --pretty --output="$BACKUP_DIR/workflows.json"

# Export credentials (encrypted)
n8n export:credentials --all --output="$BACKUP_DIR/credentials.json"

echo "Backup saved to $BACKUP_DIR"
```

### Full Restore

```bash
# Import credentials first (workflows may reference them)
n8n import:credentials --input="$BACKUP_DIR/credentials.json"

# Import workflows (they arrive unpublished)
n8n import:workflow --input="$BACKUP_DIR/workflows.json"

# Publish the ones that should run, one ID at a time, then restart n8n if it was running
n8n publish:workflow --id=<ID>
```

### Migrate Between Instances

```bash
# On source instance: export decrypted
n8n export:credentials --all --decrypted --output=creds-decrypted.json
n8n export:workflow --all --output=workflows.json

# Copy files to target instance, then import
n8n import:credentials --input=creds-decrypted.json
n8n import:workflow --input=workflows.json      # imported workflows are unpublished

# Clean up decrypted file
rm creds-decrypted.json
```

---

## License Management

```bash
# Show current license information
n8n license:info

# Clear/remove the current license (revert to community edition)
n8n license:clear
```

---

## User Management

```bash
# Reset ALL user accounts (removes owner setup, all users)
# Use when locked out of the instance
n8n user-management:reset

# Disable MFA (two-factor) for a specific user
n8n mfa:disable --email=user@example.com

# Reset LDAP configuration
n8n ldap:reset
```

**Warning:** `user-management:reset` is destructive. It removes all users and resets the instance to the initial setup state. Only use when you cannot access the instance through normal means.

---

## Community Nodes

Manage community-installed nodes from CLI.

```bash
# Uninstall a community node package
n8n community-node --uninstall --package <PACKAGE_NAME>

# Uninstall a community credential type
n8n community-node --uninstall --credential <CREDENTIAL_TYPE> --userId <USER_ID>
```

Example:

```bash
# Remove the n8n-nodes-google-sheets community package
n8n community-node --uninstall --package n8n-nodes-google-sheets
```

---

## Security Audit

Run a security audit of your n8n instance from the command line.

```bash
n8n audit
```

This checks for:
- Credentials with overly broad access
- Nodes using potentially dangerous operations
- Database security configuration
- Filesystem access risks
- Instance configuration issues

---

## Environment Variables for CLI

The CLI respects the same environment variables as the n8n server:

| Variable | Purpose |
|----------|---------|
| `N8N_HOST` | Host to bind to |
| `N8N_PORT` | Port to listen on |
| `N8N_PROTOCOL` | `http` or `https` |
| `DB_TYPE` | Database type (`sqlite` or `postgresdb`; MySQL/MariaDB support was removed in n8n 2.0) |
| `DB_POSTGRESDB_HOST` | PostgreSQL host |
| `DB_POSTGRESDB_DATABASE` | PostgreSQL database name |
| `N8N_ENCRYPTION_KEY` | Encryption key for credentials (critical for import/export) |
| `EXECUTIONS_DATA_SAVE_ON_ERROR` | Save execution data on error |
| `EXECUTIONS_DATA_SAVE_ON_SUCCESS` | Save execution data on success |

**Critical:** When importing credentials between instances, both instances must use the same `N8N_ENCRYPTION_KEY`, or you must use `--decrypted` export and re-encrypt on import.

---

## Common Recipes

### Nightly Backup Cron Job

```bash
# crontab entry: run at 2 AM daily
0 2 * * * docker exec -u node n8n n8n export:workflow --all --output=/backups/workflows-$(date +\%Y\%m\%d).json 2>&1 | logger -t n8n-backup
```

### Unpublish All Workflows Before Maintenance

```bash
# Record what is published first, so you know what to bring back
n8n export:workflow --all --published --output=published-before-maintenance.json

n8n unpublish:workflow --all
# Restart n8n to apply the change, then ... perform maintenance ...

# There is no "publish all": publish each workflow again by ID
n8n publish:workflow --id=<ID>
# Restart n8n to apply the change
```

### Test Workflow from CI/CD

```bash
# Execute and capture output
OUTPUT=$(docker exec -u node n8n n8n execute --id 42 2>&1)
if echo "$OUTPUT" | grep -q "ERROR"; then
  echo "Workflow execution failed"
  exit 1
fi
```

---

## `@n8n/cli` — the remote API client

A lightweight client over the Public API. It runs anywhere with network access and respects the API key's scopes. Current release at the time of writing: 0.20.0 (`npm view @n8n/cli version`).

```bash
# Zero install
npx @n8n/cli workflow list

# Or install globally
npm install -g @n8n/cli

# Connect (saved to ~/.n8n-cli/config.json, mode 0600) ...
n8n-cli config set-url https://<n8n-host>
n8n-cli config set-api-key "$N8N_API_KEY"
# ... or use environment variables N8N_URL and N8N_API_KEY, or the --url / --api-key flags
```

Topics: `workflow` (list, get, create, update, delete, activate, deactivate, tags, transfer), `execution`, `credential`, `project`, `tag`, `variable`, `data-table`, `user`, `source-control`, `audit`, `login` / `logout`. Output via `--format=table|json|id-only`. `n8n-cli skill install --global` installs a skill that teaches Claude Code the client.

Use it for remote reads and scripted changes; use the Server CLI for anything that must bypass access control (backups, license, resets) — and remember the two have different `activate` / `publish` vocabularies, so check `n8n-cli workflow --help` on the version you installed.
