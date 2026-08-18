# CRM Schema

A customer relationship management system with companies, contacts, deals, and activities.

## Tables

```sql
CREATE TABLE "public"."companies" (
    "id"         serial    NOT NULL,
    "name"       text      NOT NULL,
    "website"    text,
    "industry"   text,
    "size"       text,
    "notes"      text,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."contacts" (
    "id"         serial            NOT NULL,
    "first_name" text              NOT NULL,
    "last_name"  text              NOT NULL,
    "email"      character varying UNIQUE,
    "phone"      character varying,
    "position"   text,
    "company_id" int4,
    "created_at" timestamp         DEFAULT now(),
    "updated_at" timestamp         DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."deal_stages" (
    "id"         serial    NOT NULL,
    "name"       text      NOT NULL,
    "sort_order" int4      DEFAULT 0,
    "created_at" timestamp DEFAULT now(),
    "updated_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."deals" (
    "id"            serial        NOT NULL,
    "title"         text          NOT NULL,
    "value"         decimal(12, 2),
    "stage_id"      int4,
    "contact_id"    int4,
    "company_id"    int4,
    "expected_close" date,
    "notes"         text,
    "created_at"    timestamp     DEFAULT now(),
    "updated_at"    timestamp     DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."activities" (
    "id"          serial    NOT NULL,
    "activity_type" text    NOT NULL,
    "subject"     text      NOT NULL,
    "description" text,
    "deal_id"     int4,
    "contact_id"  int4,
    "due_date"    timestamp,
    "is_completed" bool     DEFAULT false,
    "created_at"  timestamp DEFAULT now(),
    "updated_at"  timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

CREATE TABLE "public"."nc_m2m_deals_contacts" (
    "deal_id"    int4 NOT NULL,
    "contact_id" int4 NOT NULL,
    PRIMARY KEY ("deal_id", "contact_id")
);
```

## FK Constraints

```sql
ALTER TABLE "public"."contacts"
    ADD CONSTRAINT "fk_companies_contacts"
    FOREIGN KEY ("company_id") REFERENCES "public"."companies" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."deals"
    ADD CONSTRAINT "fk_stages_deals"
    FOREIGN KEY ("stage_id") REFERENCES "public"."deal_stages" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."deals"
    ADD CONSTRAINT "fk_contacts_deals"
    FOREIGN KEY ("contact_id") REFERENCES "public"."contacts" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."deals"
    ADD CONSTRAINT "fk_companies_deals"
    FOREIGN KEY ("company_id") REFERENCES "public"."companies" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."activities"
    ADD CONSTRAINT "fk_deals_activities"
    FOREIGN KEY ("deal_id") REFERENCES "public"."deals" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."activities"
    ADD CONSTRAINT "fk_contacts_activities"
    FOREIGN KEY ("contact_id") REFERENCES "public"."contacts" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."nc_m2m_deals_contacts"
    ADD CONSTRAINT "fk_deals_contacts_1"
    FOREIGN KEY ("deal_id") REFERENCES "public"."deals" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "public"."nc_m2m_deals_contacts"
    ADD CONSTRAINT "fk_deals_contacts_2"
    FOREIGN KEY ("contact_id") REFERENCES "public"."contacts" ("id")
    ON DELETE NO ACTION ON UPDATE NO ACTION;
```

## Indexes

```sql
CREATE INDEX "idx_contacts_company_id"      ON "public"."contacts" ("company_id");
CREATE INDEX "idx_deals_stage_id"           ON "public"."deals" ("stage_id");
CREATE INDEX "idx_deals_contact_id"         ON "public"."deals" ("contact_id");
CREATE INDEX "idx_deals_company_id"         ON "public"."deals" ("company_id");
CREATE INDEX "idx_activities_deal_id"       ON "public"."activities" ("deal_id");
CREATE INDEX "idx_activities_contact_id"    ON "public"."activities" ("contact_id");
CREATE INDEX "idx_m2m_deals_deal_id"        ON "public"."nc_m2m_deals_contacts" ("deal_id");
CREATE INDEX "idx_m2m_deals_contact_id"     ON "public"."nc_m2m_deals_contacts" ("contact_id");
```

## Relations

```
companies   → contacts       : One-to-Many
companies   → deals          : One-to-Many
contacts    → deals          : One-to-Many (primary contact)
deals       ↔ contacts       : Many-to-Many (all involved contacts)
deal_stages → deals          : One-to-Many
deals       → activities     : One-to-Many
contacts    → activities     : One-to-Many
```

## Design Notes

- `activity_type` uses `text` — configure SingleSelect values (call, email, meeting, task) in NocoDB UI
- `size` uses `text` — configure SingleSelect values (small, medium, large, enterprise) in NocoDB UI
- `industry` uses `text` — configure SingleSelect in NocoDB UI
- `deal.value` uses `decimal(12, 2)` for currency — NocoDB maps to Currency UIType
- `sort_order` on deal_stages uses `int4` for manual ordering in kanban views
- Deals have both a primary `contact_id` FK and a M2M junction for all involved contacts
