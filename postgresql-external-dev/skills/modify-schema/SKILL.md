---
name: modify-schema
description: >
  This skill should be used when the user asks to "alter a table", "rename a column",
  "change column type", "drop a column", "drop a table", "remove a constraint",
  "delete a junction table", "add default value", "set NOT NULL", or needs to modify
  an existing PostgreSQL schema that is connected to NocoDB or NocoBase.
---

# Modify Schema — ALTER TABLE & DROP Operations

How to safely modify PostgreSQL tables that are connected as external data sources to NocoDB and NocoBase.

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

-- JSON
ALTER TABLE "public"."products" ADD "metadata" json;

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

## Drop Column

```sql
ALTER TABLE "public"."products" DROP COLUMN "obsolete_field";
```

## Drop Table

```sql
DROP TABLE IF EXISTS "public"."table_name";
```

## Drop FK Constraint

When removing a relation, drop the constraint first, then the FK column:

```sql
-- 1. Drop FK constraint
ALTER TABLE "public"."child_table" DROP CONSTRAINT "fk_name";

-- 2. Drop FK column
ALTER TABLE "public"."child_table" DROP COLUMN "parent_id";
```

## Drop Junction Table (Many-to-Many)

For M2M relations, drop FK constraints before the table:

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

1. Drop dependent FK constraints first
2. Modify or drop columns
3. Add new columns
4. Add new FK constraints
5. Add indexes on new FK columns
