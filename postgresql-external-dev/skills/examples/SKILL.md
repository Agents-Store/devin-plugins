---
name: examples
description: >
  This skill should be used when the user asks for a "full example", "complete schema",
  "e-commerce schema", "blog schema", "CRM schema", "content management schema",
  "show me a real schema", "sample database", "end-to-end example", or wants to see
  a complete working PostgreSQL schema with all tables, constraints, indexes, and relations
  that is compatible with NocoDB and NocoBase.
---

# Examples — Complete Schema Walkthroughs

Full working examples of PostgreSQL schemas designed for external database connections to NocoDB and NocoBase.

> See also: [Compatible Platforms](references/compatible-platforms.md) for the list of supported low-code/no-code platforms.

## Available Scenarios

| Scenario | Tables | Relations | Reference |
|----------|--------|-----------|-----------|
| **E-Commerce** (below) | 8 tables | All 4 types | This file |
| **Blog** | 6 tables | 1:M, M:M, Self-ref | [references/scenarios/blog.md](references/scenarios/blog.md) |
| **CRM** | 6 tables | 1:M, M:M | [references/scenarios/crm.md](references/scenarios/crm.md) |
| **Content Management** | 6 tables | 1:M, M:M, Self-ref | [references/scenarios/content-management.md](references/scenarios/content-management.md) |

## E-Commerce Schema

A complete online store schema with 7 tables covering all relation types.

### Tables

```sql
CREATE TABLE "public"."users" (
    "id"         serial    NOT NULL,
    "username"   text,
    "email"      character varying UNIQUE,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."profiles" (
    "id"         serial    NOT NULL,
    "user_id"    int4      UNIQUE,
    "first_name" text,
    "last_name"  text,
    "bio"        text,
    "birth_date" date,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."categories" (
    "id"         serial    NOT NULL,
    "title"      text      NOT NULL,
    "parent_id"  int4,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."products" (
    "id"          serial    NOT NULL,
    "title"       text      NOT NULL,
    "description" text,
    "price"       decimal(10, 2),
    "quantity"    int4      DEFAULT 0,
    "is_active"   bool      DEFAULT true,
    "rating"      smallint  DEFAULT 0,
    "metadata"    json,
    "category_id" int4,
    "created_at"  timestamp DEFAULT now(),
    "updated_at"  timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."tags" (
    "id"         serial    NOT NULL,
    "name"       text      NOT NULL UNIQUE,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."nc_m2m_products_tags" (
    "product_id" int4 NOT NULL,
    "tag_id"     int4 NOT NULL,
    PRIMARY KEY ("product_id", "tag_id")
);

CREATE TABLE "public"."orders" (
    "id"         serial    NOT NULL,
    "user_id"    int4,
    "status"     text      DEFAULT 'pending',
    "total"      decimal(12, 2),
    "notes"      text,
    "ordered_at" timestamp DEFAULT now(),
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."order_items" (
    "id"         serial    NOT NULL,
    "order_id"   int4      NOT NULL,
    "product_id" int4      NOT NULL,
    "quantity"   int4      NOT NULL DEFAULT 1,
    "unit_price" decimal(10, 2) NOT NULL,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);
```

### FK Constraints

```sql
ALTER TABLE "public"."profiles"
    ADD CONSTRAINT "fk_users_profiles"
    FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."categories"
    ADD CONSTRAINT "fk_categories_parent"
    FOREIGN KEY ("parent_id") REFERENCES "public"."categories" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."products"
    ADD CONSTRAINT "fk_categories_products"
    FOREIGN KEY ("category_id") REFERENCES "public"."categories" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."nc_m2m_products_tags"
    ADD CONSTRAINT "fk_products_tags_1"
    FOREIGN KEY ("product_id") REFERENCES "public"."products" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."nc_m2m_products_tags"
    ADD CONSTRAINT "fk_products_tags_2"
    FOREIGN KEY ("tag_id") REFERENCES "public"."tags" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."orders"
    ADD CONSTRAINT "fk_users_orders"
    FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."order_items"
    ADD CONSTRAINT "fk_orders_items"
    FOREIGN KEY ("order_id") REFERENCES "public"."orders" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."order_items"
    ADD CONSTRAINT "fk_products_items"
    FOREIGN KEY ("product_id") REFERENCES "public"."products" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;
```

### Indexes

```sql
CREATE INDEX "idx_profiles_user_id"       ON "public"."profiles" ("user_id");
CREATE INDEX "idx_categories_parent_id"   ON "public"."categories" ("parent_id");
CREATE INDEX "idx_products_category_id"   ON "public"."products" ("category_id");
CREATE INDEX "idx_m2m_product_id"         ON "public"."nc_m2m_products_tags" ("product_id");
CREATE INDEX "idx_m2m_tag_id"             ON "public"."nc_m2m_products_tags" ("tag_id");
CREATE INDEX "idx_orders_user_id"         ON "public"."orders" ("user_id");
CREATE INDEX "idx_order_items_order_id"   ON "public"."order_items" ("order_id");
CREATE INDEX "idx_order_items_product_id" ON "public"."order_items" ("product_id");
```

### Relation Summary

```
users     → profiles       : One-to-One   (UNIQUE FK)
users     → orders         : One-to-Many
categories → categories    : Self-ref tree
categories → products      : One-to-Many
products  ↔ tags           : Many-to-Many (junction: nc_m2m_products_tags)
orders    → order_items    : One-to-Many
products  → order_items    : One-to-Many
```

This example demonstrates all four relation types:
- **One-to-One**: users → profiles (UNIQUE on `user_id`)
- **One-to-Many**: users → orders, categories → products, orders → order_items
- **Many-to-Many**: products ↔ tags (via `nc_m2m_products_tags` junction table with composite PK)
- **Self-referential**: categories → categories (via `parent_id`)
