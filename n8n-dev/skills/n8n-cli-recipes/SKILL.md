---
name: n8n-cli-recipes
description: n8n CLI commands for self-hosted instances. Use when executing workflows from command line, exporting/importing workflows and credentials, managing licenses, resetting user accounts, running security audits via CLI, or managing community nodes. Also use when asking about "n8n CLI", "command line", "n8n execute", "export workflow".
---

# n8n CLI Recipes

## Running CLI Commands

How you invoke CLI commands depends on your installation method.

### npm / Global Install

```bash
n8n <command>
```

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

Activate or deactivate workflows from CLI. Changes the `active` flag in the database.

```bash
# Deactivate a specific workflow
n8n update:workflow --id=<ID> --active=false

# Activate a specific workflow
n8n update:workflow --id=<ID> --active=true

# Deactivate ALL workflows
n8n update:workflow --all --active=false

# Activate ALL workflows
n8n update:workflow --all --active=true
```

**Important:** After changing workflow status via CLI, you must **restart n8n** for the changes to take effect. The running n8n process caches workflow active states.

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

# Export with backup flag (includes metadata)
n8n export:workflow --backup --output=backups/latest/

# Pretty-print the JSON output
n8n export:workflow --all --pretty
```

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
| `--backup` | Include additional metadata for backup purposes |
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
```

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
| `--userId=<ID>` | Assign imported items to a specific user |
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

# Import workflows
n8n import:workflow --input="$BACKUP_DIR/workflows.json"
```

### Migrate Between Instances

```bash
# On source instance: export decrypted
n8n export:credentials --all --decrypted --output=creds-decrypted.json
n8n export:workflow --all --output=workflows.json

# Copy files to target instance, then import
n8n import:credentials --input=creds-decrypted.json
n8n import:workflow --input=workflows.json

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
| `DB_TYPE` | Database type (`sqlite`, `postgresdb`, `mysqldb`) |
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

### Deactivate All Workflows Before Maintenance

```bash
n8n update:workflow --all --active=false
# ... perform maintenance ...
n8n update:workflow --all --active=true
# Restart n8n to apply changes
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
