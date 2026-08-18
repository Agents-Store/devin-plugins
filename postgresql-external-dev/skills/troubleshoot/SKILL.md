---
name: troubleshoot
description: >
  This skill should be used when the user asks about "incompatible types", "what to avoid",
  "schema checklist", "NocoDB doesn't recognize", "NocoBase can't read", "ARRAY not working",
  "ENUM alternative", "naming conventions", "validation checklist", or encounters issues
  with a PostgreSQL schema connected to NocoDB or NocoBase.
---

# Troubleshoot — Anti-Patterns and Verification

Common issues, incompatible types, and the verification checklist for PostgreSQL schemas used as external databases for NocoDB and NocoBase.

## Incompatible SQL Types

These PostgreSQL types are **not supported** by NocoDB. Use the replacements.

| Type | Replacement |
|------|-------------|
| `VARCHAR(255)[]`, any `ARRAY[]` | `json` |
| `POINT`, `PATH`, `POLYGON`, `CIRCLE` | `json` (coordinates as `[x, y]`) |
| PostgreSQL `ENUM` type | `text` + SingleSelect in UI |
| `INHERITS` (table inheritance) | Regular tables + FK |

## Common Anti-Patterns

| Problem | Solution |
|---------|----------|
| Spaces in column names | Use `snake_case` |
| Reserved words (`order`, `user`) | Add suffix: `sort_order`, `app_user` |
| `DEFAULT` on `json` column | Don't set it — set default in the application |
| PK without auto-increment | Always use `serial` or `bigserial` |
| `jsonb` instead of `json` | Use `json` — safer for both platforms |
| UUID as primary key | Use `serial` / `bigserial` — NocoDB expects auto-increment |
| Missing FK constraint | Always add `ALTER TABLE ... ADD CONSTRAINT` for every relation |
| Missing index on FK column | Always `CREATE INDEX` on every FK column |
| Junction table with separate `id` | Use composite PK from both FK columns (NocoDB style) |
| `ON DELETE CASCADE` on FK | Use `ON DELETE NO ACTION` (NocoDB default) |

## Verification Checklist

Run through this checklist before connecting your database to NocoDB or NocoBase:

- [ ] PK: `serial` or `bigserial` with name `id`
- [ ] FK columns: type matches parent PK (`int4` for `serial`, `int8` for `bigserial`)
- [ ] FK constraints: `ON DELETE NO ACTION ON UPDATE NO ACTION`
- [ ] Index on every FK column
- [ ] One-to-One: `UNIQUE` on FK column
- [ ] Junction tables: composite PK from two FKs + FK constraints + indexes
- [ ] No `ARRAY[]`, `ENUM`, `POINT`, `POLYGON`, `INHERITS`
- [ ] JSON stored as `json` (not `jsonb`)
- [ ] Select/MultiSelect stored as `text`
- [ ] Names in `snake_case`, no reserved words

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

-- Find ENUM columns (must be replaced with text)
SELECT c.table_name, c.column_name, c.udt_name
FROM information_schema.columns c
WHERE c.table_schema = 'public'
  AND c.data_type = 'USER-DEFINED'
  AND c.udt_name IN (
    SELECT t.typname FROM pg_type t
    JOIN pg_enum e ON t.oid = e.enumtypid
    GROUP BY t.typname
  );

-- Find ARRAY columns (must be replaced with json)
SELECT table_name, column_name, data_type, udt_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND data_type = 'ARRAY';

-- Find jsonb columns (should be replaced with json)
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND data_type = 'jsonb';
```
