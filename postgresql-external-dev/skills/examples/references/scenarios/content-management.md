# Content Management Schema

A content management system with pages, media library, menus, and translations.

## Tables

```sql
CREATE TABLE "public"."pages" (
    "id"         serial    NOT NULL,
    "title"      text      NOT NULL,
    "slug"       text      UNIQUE,
    "body"       text,
    "status"     text      DEFAULT 'draft',
    "parent_id"  int4,
    "sort_order" int4      DEFAULT 0,
    "metadata"   json,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."media" (
    "id"         serial    NOT NULL,
    "filename"   text      NOT NULL,
    "mime_type"  text,
    "file_size"  int4,
    "alt_text"   text,
    "url"        text,
    "metadata"   json,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."nc_m2m_pages_media" (
    "page_id"  int4 NOT NULL,
    "media_id" int4 NOT NULL,
    PRIMARY KEY ("page_id", "media_id")
);

CREATE TABLE "public"."menus" (
    "id"         serial    NOT NULL,
    "name"       text      NOT NULL,
    "location"   text,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."menu_items" (
    "id"         serial    NOT NULL,
    "menu_id"    int4      NOT NULL,
    "page_id"    int4,
    "label"      text      NOT NULL,
    "url"        text,
    "parent_id"  int4,
    "sort_order" int4      DEFAULT 0,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."translations" (
    "id"         serial    NOT NULL,
    "page_id"    int4      NOT NULL,
    "locale"     text      NOT NULL,
    "title"      text,
    "body"       text,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);
```

## FK Constraints

```sql
ALTER TABLE "public"."pages"
    ADD CONSTRAINT "fk_pages_parent"
    FOREIGN KEY ("parent_id") REFERENCES "public"."pages" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."nc_m2m_pages_media"
    ADD CONSTRAINT "fk_pages_media_1"
    FOREIGN KEY ("page_id") REFERENCES "public"."pages" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."nc_m2m_pages_media"
    ADD CONSTRAINT "fk_pages_media_2"
    FOREIGN KEY ("media_id") REFERENCES "public"."media" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."menu_items"
    ADD CONSTRAINT "fk_menus_items"
    FOREIGN KEY ("menu_id") REFERENCES "public"."menus" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."menu_items"
    ADD CONSTRAINT "fk_pages_menu_items"
    FOREIGN KEY ("page_id") REFERENCES "public"."pages" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."menu_items"
    ADD CONSTRAINT "fk_menu_items_parent"
    FOREIGN KEY ("parent_id") REFERENCES "public"."menu_items" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."translations"
    ADD CONSTRAINT "fk_pages_translations"
    FOREIGN KEY ("page_id") REFERENCES "public"."pages" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;
```

## Indexes

```sql
CREATE INDEX "idx_pages_parent_id"           ON "public"."pages" ("parent_id");
CREATE INDEX "idx_m2m_pages_page_id"         ON "public"."nc_m2m_pages_media" ("page_id");
CREATE INDEX "idx_m2m_pages_media_id"        ON "public"."nc_m2m_pages_media" ("media_id");
CREATE INDEX "idx_menu_items_menu_id"        ON "public"."menu_items" ("menu_id");
CREATE INDEX "idx_menu_items_page_id"        ON "public"."menu_items" ("page_id");
CREATE INDEX "idx_menu_items_parent_id"      ON "public"."menu_items" ("parent_id");
CREATE INDEX "idx_translations_page_id"      ON "public"."translations" ("page_id");
```

## Relations

```
pages       → pages          : Self-referential tree (nested pages)
pages       ↔ media          : Many-to-Many (junction: nc_m2m_pages_media)
pages       → translations   : One-to-Many (one translation per locale)
menus       → menu_items     : One-to-Many
menu_items  → pages          : One-to-Many (link to page)
menu_items  → menu_items     : Self-referential tree (nested menu)
```

## Design Notes

- `status` uses `text` — configure SingleSelect values (draft, published, archived) in NocoDB UI
- `location` uses `text` — configure SingleSelect values (header, footer, sidebar) in NocoDB UI
- `locale` uses `text` — configure SingleSelect values (en, uk, ru, de) in NocoDB UI
- `metadata` uses `json` for flexible page settings (SEO fields, layout options)
- Pages support nesting via self-referential `parent_id` for hierarchical site structure
- Menu items support nesting via self-referential `parent_id` for dropdown menus
- `sort_order` uses `int4` for manual ordering in NocoDB grid/kanban views
- Translations are per-page, per-locale — add UNIQUE constraint on `(page_id, locale)` if needed:

```sql
CREATE UNIQUE INDEX "uq_translations_page_locale"
    ON "public"."translations" ("page_id", "locale");
```
