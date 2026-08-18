---
name: create-tables
description: >
  This skill should be used when the user asks to "create a table", "design a schema",
  "set up a database", "create PostgreSQL tables for NocoDB", "create tables for NocoBase
  external DB", "what PK type to use", or needs to understand how NocoDB and NocoBase
  interact with the same PostgreSQL database.
---

# Create Tables — PostgreSQL External Database

How to create PostgreSQL tables that work correctly when connected as an external data source to NocoDB and NocoBase.

## System Roles

| Aspect | NocoDB | NocoBase |
|--------|--------|----------|
| Role | Primary system, manages schema | Connects as **external data source**, reads schema only |
| Sync | Yes — creates/modifies tables and columns | **No** — does not modify external DB structure |
| FK constraints | Creates physical FK for external DB | Reads existing FK, no conflicts |
| Junction tables | Composite PK (no separate `id`) | Reads as-is |

**What this means:**
- **Table structure and relations** → NocoDB style (composite PK, physical FK constraints)
- **Column types** → intersection of both systems (so both UIs display data correctly)
- **PK type** → `serial` / `int4` (NocoDB default for PostgreSQL), NocoBase reads any PK

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

> Both `serial` and `bigserial` are compatible with both systems. NocoDB uses `serial` by default but supports `bigserial`. NocoBase reads both.

## PK Conventions

- Always use `serial` or `bigserial` with name `id`
- Never use UUID or text-based primary keys — NocoDB expects auto-increment integers
- FK columns must match the parent PK type (`int4` for `serial`, `int8` for `bigserial`)

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
│  FORBIDDEN: ARRAY[], ENUM, POINT, POLYGON,         │
│             PATH, CIRCLE, INHERITS, jsonb           │
└────────────────────────────────────────────────────┘
```

For the full column type compatibility table, see the `column-types` skill.
