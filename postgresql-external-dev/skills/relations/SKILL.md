---
name: relations
description: >
  This skill should be used when the user asks to "create a relation", "add foreign key",
  "set up one-to-many", "many-to-many relation", "one-to-one", "self-referential",
  "junction table", "composite primary key", "FK constraint", "create index on FK",
  or needs to connect tables in a PostgreSQL database that works with NocoDB and NocoBase.
---

# Relations — FK Constraints, Indexes, and Patterns

All relations use NocoDB style: **physical FK constraints** + **indexes**. NocoBase reads existing FK constraints without conflicts.

## One-to-Many (HasMany / BelongsTo)

**Scenario**: `customers` → `orders` (one customer — many orders).

```sql
-- 1. Tables
CREATE TABLE "public"."customers" (
    "id"         serial    NOT NULL,
    "name"       text,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."orders" (
    "id"          serial    NOT NULL,
    "title"       text,
    "amount"      decimal(10, 2),
    "customer_id" int4,
    "created_at"  timestamp DEFAULT now(),
    "updated_at"  timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

-- 2. FK constraint (NocoDB style)
ALTER TABLE "public"."orders"
    ADD CONSTRAINT "fk_customers_orders"
    FOREIGN KEY ("customer_id")
    REFERENCES "public"."customers" ("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

-- 3. Index on FK
CREATE INDEX "idx_orders_customer_id" ON "public"."orders" ("customer_id");
```

> **ON DELETE NO ACTION** — NocoDB default. Deleting a parent is blocked if child records exist. Both systems correctly read this behavior.

## One-to-One

**Scenario**: `users` → `profiles` (one user — one profile).

```sql
CREATE TABLE "public"."users" (
    "id"         serial    NOT NULL,
    "username"   text,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."profiles" (
    "id"         serial    NOT NULL,
    "user_id"    int4      UNIQUE,            -- UNIQUE = One-to-One
    "bio"        text,
    "avatar_url" text,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

-- FK constraint
ALTER TABLE "public"."profiles"
    ADD CONSTRAINT "fk_users_profiles"
    FOREIGN KEY ("user_id")
    REFERENCES "public"."users" ("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

-- Index (UNIQUE already creates an implicit index, but explicit doesn't hurt)
CREATE INDEX "idx_profiles_user_id" ON "public"."profiles" ("user_id");
```

> **Key difference from One-to-Many**: `UNIQUE` on the FK column. NocoDB identifies One-to-One specifically by this constraint.

## Many-to-Many

**Scenario**: `students` ↔ `courses`.

```sql
-- 1. Main tables
CREATE TABLE "public"."students" (
    "id"         serial    NOT NULL,
    "name"       text,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."courses" (
    "id"         serial    NOT NULL,
    "title"      text,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

-- 2. Junction table (NocoDB style — composite PK, no separate id)
CREATE TABLE "public"."nc_m2m_students_courses" (
    "students_id" int4 NOT NULL,
    "courses_id"  int4 NOT NULL,
    PRIMARY KEY ("students_id", "courses_id")
);

-- 3. FK constraints (NocoDB style)
ALTER TABLE "public"."nc_m2m_students_courses"
    ADD CONSTRAINT "fk_students_courses_1"
    FOREIGN KEY ("students_id")
    REFERENCES "public"."students" ("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

ALTER TABLE "public"."nc_m2m_students_courses"
    ADD CONSTRAINT "fk_students_courses_2"
    FOREIGN KEY ("courses_id")
    REFERENCES "public"."courses" ("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

-- 4. Indexes on both FKs
CREATE INDEX "idx_m2m_students_id" ON "public"."nc_m2m_students_courses" ("students_id");
CREATE INDEX "idx_m2m_courses_id"  ON "public"."nc_m2m_students_courses" ("courses_id");
```

> **Composite PK** (`students_id`, `courses_id`) — guarantees pair uniqueness. NocoBase as external source correctly reads such tables.

## Self-Referential (Tree)

**Scenario**: `categories` with nesting.

```sql
CREATE TABLE "public"."categories" (
    "id"         serial    NOT NULL,
    "title"      text      NOT NULL,
    "parent_id"  int4,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

-- FK to self
ALTER TABLE "public"."categories"
    ADD CONSTRAINT "fk_categories_parent"
    FOREIGN KEY ("parent_id")
    REFERENCES "public"."categories" ("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

-- Index
CREATE INDEX "idx_categories_parent_id" ON "public"."categories" ("parent_id");
```

## Indexes

### When to Create

| Situation | SQL | Required? |
|-----------|-----|-----------|
| FK column | `CREATE INDEX` | Yes |
| One-to-One FK | `UNIQUE` on column + `CREATE INDEX` | Yes |
| Unique field | `UNIQUE` on column | As needed |
| Search field | `CREATE INDEX` | As needed |

### Syntax

```sql
-- Regular index
CREATE INDEX "idx_table_column" ON "public"."table_name" ("column_name");

-- Unique index
CREATE UNIQUE INDEX "uq_table_column" ON "public"."table_name" ("column_name");

-- Drop index
DROP INDEX IF EXISTS "public"."idx_table_column";
```

## One Relation Per Table Pair

Between any two tables, use exactly **one** relation type — either a direct FK (One-to-Many) or a M2M junction table, never both. Having both a FK column and a junction table between the same two tables creates duplicate link columns in the UI, because both NocoDB and NocoBase auto-detect FK constraints and junction tables independently.

If you need both a "primary" link (single value) and a "uses many" link between the same tables, model it as a single M2M junction — the "primary" is just one row in the junction.

## Relation Checklist

- **One relation type per table pair** — FK or junction, not both
- FK column type matches parent PK type (`int4` for `serial`, `int8` for `bigserial`)
- FK constraint uses `ON DELETE NO ACTION ON UPDATE NO ACTION`
- Index created on every FK column
- One-to-One has `UNIQUE` on FK column
- Junction tables use composite PK from both FK columns
- Junction tables have FK constraints on both columns
- Junction tables have indexes on both FK columns
