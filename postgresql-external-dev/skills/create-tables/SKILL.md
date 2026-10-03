---
name: create-tables
description: >
  This skill should be used when the user asks to "create a table", "design a schema",
  "set up a database", "create PostgreSQL tables for NocoDB", "create tables for NocoBase
  external DB", "what PK type to use", "UUID primary key", "table without a primary key",
  "does NocoBase need a license", or needs to understand how NocoDB and NocoBase interact
  with the same PostgreSQL database.
---

# Create Tables — PostgreSQL External Database

How to create PostgreSQL tables that work correctly when connected as an external data source to NocoDB and NocoBase.

## System Roles

| Aspect | NocoDB | NocoBase |
|--------|--------|----------|
| Role | Connects the database; can manage schema only if **Allow Schema Edit** is on (off by default for external sources) | Connects as **external data source**, reads schema only |
| License | No separate plugin for the external PostgreSQL source; check your NocoDB edition/plan | **Commercial license required** — plugin `@nocobase/plugin-data-source-external-postgres`, Standard edition or above, not in Community |
| Sync | Yes — creates/modifies tables and columns when schema edit is on; otherwise **Meta Sync** reads your SQL changes | **No** — does not modify external DB structure; **refresh** the data source after SQL changes |
| FK constraints | Creates physical FK for external DB | Reads existing FK, no conflicts |
| Junction tables | Composite PK (no separate `id`) | Reads as-is; set a Record unique key to edit them |

**What this means:**
- **Table structure and relations** → NocoDB style (composite PK, physical FK constraints)
- **Column types** → default to the intersection of both systems (so both UIs display data correctly); wider types are accepted with caveats — see `column-types`
- **PK type** → `serial` / `int4` is the recommended default (NocoDB's own default for PostgreSQL); both platforms also read other key types — see PK Conventions
- **Schema changes** → made with SQL, then synced: Meta Sync in NocoDB, refresh in NocoBase — see `modify-schema`

## Base Table Template

```sql
CREATE TABLE "public"."products" (
    "id"         serial       NOT NULL,
    "title"      text,
    "created_at" timestamp    DEFAULT now(),
    "updated_at" timestamp    DEFAULT now(),
    PRIMARY KEY ("id")
);
```

> NocoDB default for PostgreSQL: PK = `serial` (`int4` + auto-increment), timestamps = `timestamp`. NocoBase as external source correctly reads `serial` PK.

## BIGSERIAL Variant (for large IDs)

```sql
CREATE TABLE "public"."products" (
    "id"         bigserial    NOT NULL,
    "title"      text,
    "created_at" timestamp    DEFAULT now(),
    "updated_at" timestamp    DEFAULT now(),
    PRIMARY KEY ("id")
);
```

> Both `serial` and `bigserial` are compatible with both systems. NocoDB uses `serial` by default but supports `bigserial`. NocoBase reads both (`serial` becomes `integer`, `bigserial` becomes `bigInt`).

## PK Conventions

- **Recommended default**: `serial` or `bigserial` with name `id`
- FK columns must match the parent PK type (`int4` for `serial`, `int8` for `bigserial`, `uuid` for `uuid`)
- Other key types are **accepted, not forbidden**. NocoDB keeps the existing primary key of a connected external table as is (it does not add an `id` column) and can itself create tables with a string key; NocoBase maps `uuid` and `varchar` columns. Use one when the database already has it or another system generates the key — and check it on your target versions
- Caveat for a PK whose default is a database function (for example a `uuid` key with `gen_random_uuid()`): NocoDB has an open bug report where adding a row in Grid view shows `Record 'null' not found` although the row is created (Form view works). Test insert paths before committing to such a key

### Tables without a unique key

- **NocoDB**: a table with no primary key can be read and new rows can be added, but rows cannot be updated or deleted
- **NocoBase**: a table without a primary key, a composite-primary-key table and a view all need a **Record unique key** set by hand in the collection settings (a primary key or another unique field). Without it, blocks may not be created correctly or may not be able to view and edit records
- To make a table fully editable on both platforms, give it a single-column primary key. Junction tables stay composite (NocoDB style) — set the Record unique key in NocoBase only if you need to edit their rows there

## Timestamp Conventions

- Use `timestamp` (without timezone) — NocoDB default
- Use `timestamptz` if timezone matters — both systems support it
- Always add `DEFAULT now()` for `created_at` and `updated_at`

## Quick Reference

```
┌────────────────────────────────────────────────────┐
│  TABLE STRUCTURE (NocoDB + NocoBase compatible)     │
├────────────────────────────────────────────────────┤
│  PK:        serial / bigserial, column name "id"   │
│  FK:        int4 / int8 + CONSTRAINT + INDEX       │
│  Timestamps: timestamp DEFAULT now()               │
├────────────────────────────────────────────────────┤
│  RELATION STRUCTURE (NocoDB style):                │
│  • FK constraint ON DELETE/UPDATE NO ACTION        │
│  • INDEX on every FK                               │
│  • One-to-One = UNIQUE on FK                       │
│  • M2M junction = composite PK                     │
├────────────────────────────────────────────────────┤
│  SAFE DEFAULTS: json, text for selects,            │
│    no ARRAY / ENUM / geometric types, no INHERITS  │
│  ACCEPTED WITH CAVEATS: jsonb, uuid, ARRAY, ENUM,  │
│    geometric types (see column-types)              │
└────────────────────────────────────────────────────┘
```

For the full column type compatibility table, see the `column-types` skill.
