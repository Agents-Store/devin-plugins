# Blog Schema

A blog platform with authors, posts, categories, tags, and comments.

## Tables

```sql
CREATE TABLE "public"."authors" (
    "id"         serial    NOT NULL,
    "name"       text      NOT NULL,
    "email"      character varying UNIQUE,
    "bio"        text,
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

CREATE TABLE "public"."posts" (
    "id"           serial    NOT NULL,
    "title"        text      NOT NULL,
    "slug"         text      UNIQUE,
    "body"         text,
    "status"       text      DEFAULT 'draft',
    "author_id"    int4,
    "category_id"  int4,
    "published_at" timestamp,
    "created_at"   timestamp DEFAULT now(),
    "updated_at"   timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."tags" (
    "id"         serial    NOT NULL,
    "name"       text      NOT NULL UNIQUE,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."nc_m2m_posts_tags" (
    "post_id" int4 NOT NULL,
    "tag_id"  int4 NOT NULL,
    PRIMARY KEY ("post_id", "tag_id")
);

CREATE TABLE "public"."comments" (
    "id"         serial    NOT NULL,
    "post_id"    int4      NOT NULL,
    "parent_id"  int4,
    "author_name" text,
    "body"       text      NOT NULL,
    "is_approved" bool     DEFAULT false,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);
```

## FK Constraints

```sql
ALTER TABLE "public"."categories"
    ADD CONSTRAINT "fk_categories_parent"
    FOREIGN KEY ("parent_id") REFERENCES "public"."categories" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."posts"
    ADD CONSTRAINT "fk_authors_posts"
    FOREIGN KEY ("author_id") REFERENCES "public"."authors" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."posts"
    ADD CONSTRAINT "fk_categories_posts"
    FOREIGN KEY ("category_id") REFERENCES "public"."categories" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."nc_m2m_posts_tags"
    ADD CONSTRAINT "fk_posts_tags_1"
    FOREIGN KEY ("post_id") REFERENCES "public"."posts" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."nc_m2m_posts_tags"
    ADD CONSTRAINT "fk_posts_tags_2"
    FOREIGN KEY ("tag_id") REFERENCES "public"."tags" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."comments"
    ADD CONSTRAINT "fk_posts_comments"
    FOREIGN KEY ("post_id") REFERENCES "public"."posts" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."comments"
    ADD CONSTRAINT "fk_comments_parent"
    FOREIGN KEY ("parent_id") REFERENCES "public"."comments" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;
```

## Indexes

```sql
CREATE INDEX "idx_categories_parent_id"  ON "public"."categories" ("parent_id");
CREATE INDEX "idx_posts_author_id"       ON "public"."posts" ("author_id");
CREATE INDEX "idx_posts_category_id"     ON "public"."posts" ("category_id");
CREATE INDEX "idx_m2m_post_id"           ON "public"."nc_m2m_posts_tags" ("post_id");
CREATE INDEX "idx_m2m_tag_id"            ON "public"."nc_m2m_posts_tags" ("tag_id");
CREATE INDEX "idx_comments_post_id"      ON "public"."comments" ("post_id");
CREATE INDEX "idx_comments_parent_id"    ON "public"."comments" ("parent_id");
```

## Relations

```
authors    → posts          : One-to-Many
categories → categories     : Self-referential tree
categories → posts          : One-to-Many
posts      ↔ tags           : Many-to-Many (junction: nc_m2m_posts_tags)
posts      → comments       : One-to-Many
comments   → comments       : Self-referential tree (threaded comments)
```

## Design Notes

- `status` uses `text` — configure SingleSelect values (draft, published, archived) in NocoDB UI
- `slug` has UNIQUE constraint for URL-friendly post identifiers
- Comments support threading via self-referential `parent_id`
- Categories support nesting via self-referential `parent_id`
