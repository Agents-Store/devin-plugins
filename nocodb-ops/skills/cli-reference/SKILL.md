---
name: cli-reference
description: |
  NocoDB CLI commands and nc command reference from the official NocoDB agent-skills package. Use when:
  - "NocoDB CLI commands"
  - "nc command reference"
  - "NocoDB agent-skills"
  - "what CLI commands are available"
  - "how to use nc command"
disable-model-invocation: true
---

# NocoDB CLI

CLI for NocoDB API. Imported from the official `nocodb/agent-skills` package.

## Platform Support

- **Linux / macOS**: `scripts/nocodb.sh` (Bash, requires `curl` and `jq`)

## Plan Requirements

**FREE PLANS:** Base, Table, Field, Record, Link, Attachment APIs, Filter, Sorts APIs

**ENTERPRISE (self-hosted OR cloud-hosted):** Workspace, Workspace Collaboration APIs, Base Collaboration APIs, View, Script, Team, API Token APIs

## Setup

```bash
export NOCODB_API_TOKEN="your-api-token"
export NOCODB_URL="https://app.nocodb.com"   # optional, this is default
export NOCODB_VERBOSE=1                       # optional, shows resolved IDs
```

Get your API token: NocoDB → Team & Settings → API Tokens → Add New Token.

## Installation

```bash
npx skills add nocodb/agent-skills
```

Or as a Claude Code plugin:

```bash
/plugin marketplace add nocodb/agent-skills
```

## Argument Order

Commands follow a hierarchical pattern. Arguments are always in this order:

```
WORKSPACE → BASE → TABLE → VIEW/FIELD → RECORD
```

Use **names** (human-readable) or **IDs** (faster, from NocoDB).

**ID Prefixes:** `w`=workspace, `p`=base, `m`=table, `c`=column, `vw`=view

Examples:
- Name: `nc record:list MyBase Users`
- ID: `nc record:list pdef5678uvw mghi9012rst`

Set `NOCODB_VERBOSE=1` to see resolved IDs:
```bash
NOCODB_VERBOSE=1 nc field:list MyBase Users
# → base: MyBase → pdef5678uvw
# → table: Users → mghi9012rst
```

## Quick Reference

```bash
# Workspace APIs (Enterprise only)
nc workspace:list                          # → wabc1234xyz

# Free plan APIs
nc base:list wabc1234xyz                   # → pdef5678uvw
nc table:list pdef5678uvw                  # → mghi9012rst
nc field:list pdef5678uvw mghi9012rst      # → cjkl3456opq
nc record:list pdef5678uvw mghi9012rst
nc record:get pdef5678uvw mghi9012rst 31
nc filter:list pdef5678uvw mghi9012rst vwmno7890abc

# View APIs (Enterprise only)
nc view:list pdef5678uvw mghi9012rst       # → vwmno7890abc

# Filter syntax help
nc where:help
```

## Full Command Reference

See `references/` for detailed command documentation:

- **base-table-field.md** — Workspaces, bases, tables, and field commands
- **record-link.md** — Record CRUD, linked records, attachments, button actions
- **view-filter-sort.md** — Views, filters, sorts, scripts, teams, tokens (enterprise)
- **filter-syntax.md** — Complete where filter syntax for CLI and MCP queries
