# postgresql-external-dev (Devin plugin)

PostgreSQL schema design for external database connections. Compatible SQL patterns for NocoDB and NocoBase — table creation, column types, relations, indexes, and anti-patterns.

## Install

Copy this directory's contents into your Devin plugin directory. The manifest (`.devin-plugin/plugin.json`) is metadata only — Devin discovers `skills/` from disk, not from a manifest pointer.

## Skills (6)

- `column-types` — This skill should be used when the user asks "what SQL type for", "which column type", "NocoDB column types", "NocoBase field types", "type compatibility", "how to store email/url/phone/json/rating", "what type for currency", "decimal vs double", or needs to choose the correct PostgreSQL type that works in both NocoDB and NocoBase.

- `create-tables` — This skill should be used when the user asks to "create a table", "design a schema", "set up a database", "create PostgreSQL tables for NocoDB", "create tables for NocoBase external DB", "what PK type to use", or needs to understand how NocoDB and NocoBase interact with the same PostgreSQL database.

- `examples` — This skill should be used when the user asks for a "full example", "complete schema", "e-commerce schema", "blog schema", "CRM schema", "content management schema", "show me a real schema", "sample database", "end-to-end example", or wants to see a complete working PostgreSQL schema with all tables, constraints, indexes, and relations that is compatible with NocoDB and NocoBase.

- `modify-schema` — This skill should be used when the user asks to "alter a table", "rename a column", "change column type", "drop a column", "drop a table", "remove a constraint", "delete a junction table", "add default value", "set NOT NULL", or needs to modify an existing PostgreSQL schema that is connected to NocoDB or NocoBase.

- `relations` — This skill should be used when the user asks to "create a relation", "add foreign key", "set up one-to-many", "many-to-many relation", "one-to-one", "self-referential", "junction table", "composite primary key", "FK constraint", "create index on FK", or needs to connect tables in a PostgreSQL database that works with NocoDB and NocoBase.

- `troubleshoot` — This skill should be used when the user asks about "incompatible types", "what to avoid", "schema checklist", "NocoDB doesn't recognize", "NocoBase can't read", "ARRAY not working", "ENUM alternative", "naming conventions", "validation checklist", or encounters issues with a PostgreSQL schema connected to NocoDB or NocoBase.


## Not carried over

- 1 agent(s) — Devin plugins do not support agents

## Source

Canonical: https://github.com/agents-store/claude-public-plugins/tree/main/plugins/postgresql-external-dev
