---
name: modify-schema
description: >
  This skill should be used when the user asks to "alter a table", "rename a column",
  "change column type", "drop a column", "drop a table", "remove a constraint",
  "delete a junction table", "add default value", "set NOT NULL", "sync schema",
  "meta sync", "refresh data source", "NocoDB doesn't show the new column", or needs to
  modify an existing PostgreSQL schema that is connected to NocoDB or NocoBase.
---

# Modify Schema — ALTER TABLE & DROP Operations

How to safely modify PostgreSQL tables that are connected as external data sources to NocoDB and NocoBase.

## After Every Schema Change: Sync the Platforms

Both platforms keep their own copy of the schema metadata. A change made with SQL is invisible to them until you sync — run the sync after **every** DDL statement or batch (add, rename, retype, drop, new FK, new index):

| Platform | How to sync |
|----------|-------------|
| NocoDB | **Meta Sync** — Base Settings → Manage → External Database → pick the data source → *Meta Sync* tab → *Reload* (optional) to refresh the state, review the *Sync State* column, then *Sync Now* |
| NocoBase | **Refresh** — Data source management → the external data source → run the refresh action, which re-reads collections and fields. NocoBase never changes the external schema itself |

- NocoDB lists the detected changes in the *Sync State* column before you apply them — read it, especially after a rename or drop
- Do the SQL first, then the sync, then check the table in each UI. If NocoDB can change the schema itself (*Allow Schema Edit*, off by default for external sources), prefer one owner for DDL, not both
- A column you rename or retype in SQL is not updated in the platform's field settings until the sync has run

## Add Columns

```sql
-- Text
ALTER TABLE "public"."products" ADD "title" text;

-- Number
ALTER TABLE "public"."products" ADD "quantity" bigint;

-- Decimal
ALTER TABLE "public"."products" ADD "price" decimal(10, 2);

-- Percent
ALTER TABLE "public"."products" ADD "discount" double precision;

-- Rating
ALTER TABLE "public"."products" ADD "rating" smallint DEFAULT 0;

-- Boolean
ALTER TABLE "public"."products" ADD "is_active" bool DEFAULT false;

-- DateTime
ALTER TABLE "public"."products" ADD "published_at" timestamp;

-- DateTime with TZ
ALTER TABLE "public"."products" ADD "event_at" timestamptz;

-- Date only
ALTER TABLE "public"."products" ADD "birth_date" date;

-- Time only
ALTER TABLE "public"."products" ADD "start_time" time;

-- JSON (default)
ALTER TABLE "public"."products" ADD "metadata" json;

-- JSON with GIN indexes / operators (accepted by both platforms, see column-types)
-- ALTER TABLE "public"."products" ADD "attributes" jsonb;

-- FK column (type must match parent PK)
ALTER TABLE "public"."products" ADD "category_id" int4;
```

## Rename Column

```sql
ALTER TABLE "public"."products" RENAME COLUMN "old_name" TO "new_name";
```

## Change Column Type

```sql
ALTER TABLE "public"."products" ALTER COLUMN "price" DROP DEFAULT;
ALTER TABLE "public"."products" ALTER COLUMN "price" TYPE decimal(12, 4)
    USING "price"::decimal(12, 4);
```

## Set / Remove DEFAULT

```sql
-- Set default
ALTER TABLE "public"."products" ALTER COLUMN "status" SET DEFAULT 'draft';

-- Remove default
ALTER TABLE "public"."products" ALTER COLUMN "status" DROP DEFAULT;
```

## Set / Remove NOT NULL

```sql
-- Set NOT NULL
ALTER TABLE "public"."products" ALTER COLUMN "title" SET NOT NULL;

-- Remove NOT NULL
ALTER TABLE "public"."products" ALTER COLUMN "title" DROP NOT NULL;
```

## Before You Drop Anything

`DROP COLUMN` and `DROP TABLE` cannot be undone, and neither platform can restore what PostgreSQL no longer has:

- Ask the user to confirm the exact object before running the statement
- Take a backup first, e.g. `pg_dump --table=public.products --format=custom "$DATABASE_URL" > products_backup.dump`
- NocoDB's Base Trash does not cover rows of an external data source — rows deleted through NocoDB are gone for good, and a dropped column or table is gone from PostgreSQL itself
- After the drop, run the sync (see above) so the platforms stop showing the removed object

## Drop Column

```sql
ALTER TABLE "public"."products" DROP COLUMN "obsolete_field";
```

## Drop Table

```sql
DROP TABLE IF EXISTS "public"."table_name";
```

## Drop FK Constraint

Destructive (see Before You Drop Anything). When removing a relation, drop the constraint first, then the FK column:

```sql
-- 1. Drop FK constraint
ALTER TABLE "public"."child_table" DROP CONSTRAINT "fk_name";

-- 2. Drop FK column
ALTER TABLE "public"."child_table" DROP COLUMN "parent_id";
```

## Drop Junction Table (Many-to-Many)

Destructive (see Before You Drop Anything). For M2M relations, drop FK constraints before the table:

```sql
-- 1. Drop FK constraints
ALTER TABLE "public"."nc_m2m_a_b" DROP CONSTRAINT "fk_name_1";
ALTER TABLE "public"."nc_m2m_a_b" DROP CONSTRAINT "fk_name_2";

-- 2. Drop table
DROP TABLE IF EXISTS "public"."nc_m2m_a_b";
```

## Drop Index

```sql
DROP INDEX IF EXISTS "public"."idx_table_column";
```

## Safe Modification Order

When making complex schema changes:

1. Back up and get confirmation before anything destructive
2. Drop dependent FK constraints first
3. Modify or drop columns
4. Add new columns
5. Add new FK constraints
6. Add indexes on new FK columns
7. Run Meta Sync in NocoDB and refresh the data source in NocoBase
