---
name: troubleshoot
description: >
  This skill should be used when the user asks about "incompatible types", "what to avoid",
  "schema checklist", "NocoDB doesn't recognize", "NocoBase can't read", "ARRAY not working",
  "ENUM alternative", "jsonb support", "UUID primary key problem", "external PostgreSQL
  missing in NocoBase", "naming conventions", "validation checklist", or encounters issues
  with a PostgreSQL schema connected to NocoDB or NocoBase.
---

# Troubleshoot — Anti-Patterns and Verification

Common issues, type support per platform, and the verification checklist for PostgreSQL schemas used as external databases for NocoDB and NocoBase.

## Type Support by Platform

Support differs per platform — a type that one platform reads cleanly may be limited on the other. The **safe default** is what to use when the schema must behave the same on both. A wider type is a choice, not a mistake: confirm it on your target NocoDB and NocoBase versions first (details and sources in `column-types` → Other PostgreSQL Types).

| Type | NocoDB | NocoBase | Safe default |
|------|--------|----------|--------------|
| `ARRAY` (`text[]`, `int4[]`, …) | No field type mapping — shown as a database-specific type | Read as `array` | `json` |
| `POINT`, `POLYGON`, `CIRCLE` | Read as a Geometry field (`PATH` is shown as a database-specific type) | Read as `point`, `polygon`, `circle` (`PATH` is `lineString`) | `json` (coordinates as `[x, y]`) |
| PostgreSQL `ENUM` | Read as SingleSelect from release 2026.04.5; editing options in the UI runs `ALTER TYPE` on your database | Not in the documented mapping table — expect an unsupported field | `text` + SingleSelect in UI |
| `jsonb` | Read as a JSON field | Read as `json` | `json` (what NocoDB creates) |
| `uuid` | Read as single-line text; as a PK it is kept as is | Read as `uuid` | `text` for ids, `serial` for the PK |
| `INHERITS` (table inheritance) | Not covered by upstream docs | Not covered by upstream docs | Regular tables + FK |

## NocoBase Does Not Offer PostgreSQL

If **PostgreSQL** is missing under Data source management → Add new, the external database plugin is not installed or not licensed. External PostgreSQL in NocoBase is the plugin `@nocobase/plugin-data-source-external-postgres`, which needs a **commercial license** (Standard edition or above; not in Community). Check, in order: the plugin is installed and enabled, the license includes it, and the current user may manage data sources. NocoBase's own system database is a different thing and does not need this plugin.

## New Column or Table Is Not Visible

The schema was changed in PostgreSQL but the platform still shows the old structure: run **Meta Sync** in NocoDB (Base Settings → Manage → External Database) and the **refresh** action on the data source in NocoBase. See `modify-schema`.

## Common Anti-Patterns

| Problem | Solution |
|---------|----------|
| Spaces in column names | Use `snake_case` |
| Reserved words (`order`, `user`) | Add suffix: `sort_order`, `app_user` |
| `DEFAULT` on `json` column | Don't set it — set default in the application |
| PK without auto-increment | Prefer `serial` or `bigserial`; a key generated elsewhere (UUID) is accepted — see below |
| `jsonb` instead of `json` | Both platforms read it; `json` stays the default — use `jsonb` when you need GIN indexes or operators |
| UUID as primary key | Accepted — NocoDB keeps an existing PK as is and NocoBase maps `uuid`; `serial` / `bigserial` stays the recommended default. With a function default (`gen_random_uuid()`) test inserts from NocoDB Grid view (open bug report) |
| Table without a primary key | NocoDB can read and add rows but not update or delete; NocoBase needs a manual **Record unique key**. Add a single-column PK |
| Missing FK constraint | Always add `ALTER TABLE ... ADD CONSTRAINT` for every relation |
| Missing index on FK column | Always `CREATE INDEX` on every FK column |
| Junction table with separate `id` | Use composite PK from both FK columns (NocoDB style) |
| `ON DELETE CASCADE` on FK | Use `ON DELETE NO ACTION` (NocoDB default) |

## Verification Checklist

Run through this checklist before connecting your database to NocoDB or NocoBase:

- [ ] PK: `serial` or `bigserial` with name `id` (or a deliberate, tested alternative such as `uuid`)
- [ ] Every table has a primary key (single-column, except junction tables); without one, NocoDB cannot update or delete rows and NocoBase needs a Record unique key
- [ ] FK columns: type matches parent PK (`int4` for `serial`, `int8` for `bigserial`)
- [ ] FK constraints: `ON DELETE NO ACTION ON UPDATE NO ACTION`
- [ ] Index on every FK column
- [ ] One-to-One: `UNIQUE` on FK column
- [ ] Junction tables: composite PK from two FKs + FK constraints + indexes
- [ ] Default types for cross-platform schemas: no `ARRAY[]`, `ENUM`, `POINT`, `POLYGON`; any that remain are deliberate and checked on both platforms
- [ ] No `INHERITS`
- [ ] JSON stored as `json` by default; `jsonb` only where indexes or operators are needed
- [ ] Select/MultiSelect stored as `text`
- [ ] Names in `snake_case`, no reserved words
- [ ] NocoBase target: the commercial external-PostgreSQL plugin is licensed and enabled
- [ ] After the last schema change: Meta Sync run in NocoDB, data source refreshed in NocoBase

## Diagnostic Queries

Run these queries to find schema issues before connecting to NocoDB or NocoBase.

```sql
-- Find tables without a serial/bigserial PK
SELECT t.table_name, c.column_name, c.data_type
FROM information_schema.tables t
JOIN information_schema.columns c ON t.table_name = c.table_name
WHERE t.table_schema = 'public'
  AND c.column_name = 'id'
  AND c.column_default NOT LIKE 'nextval%';

-- Find FK columns without indexes
SELECT tc.table_name, kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE tablename = tc.table_name
      AND indexdef LIKE '%' || kcu.column_name || '%'
  );

-- Find ENUM columns (NocoDB 2026.04.5+ reads them as SingleSelect; NocoBase
-- has no documented mapping; safe default is text)
SELECT c.table_name, c.column_name, c.udt_name
FROM information_schema.columns c
WHERE c.table_schema = 'public'
  AND c.data_type = 'USER-DEFINED'
  AND c.udt_name IN (
    SELECT t.typname FROM pg_type t
    JOIN pg_enum e ON t.oid = e.enumtypid
    GROUP BY t.typname
  );

-- Find ARRAY columns (NocoBase reads them as array; NocoDB shows a
-- database-specific type; safe default is json)
SELECT table_name, column_name, data_type, udt_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND data_type = 'ARRAY';

-- Find jsonb columns (informational — both platforms read them as JSON)
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND data_type = 'jsonb';

-- Find tables without a primary key (NocoDB: read and insert only;
-- NocoBase: needs a manual Record unique key)
SELECT n.nspname AS table_schema, c.relname AS table_name
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
  AND n.nspname = 'public'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.oid AND i.indisprimary
  );
```
