---
name: column-types
description: >
  This skill should be used when the user asks "what SQL type for", "which column type",
  "NocoDB column types", "NocoBase field types", "type compatibility", "how to store
  email/url/phone/json/rating", "what type for currency", "decimal vs double", "jsonb",
  "uuid column", "ARRAY column", "PostgreSQL enum", or needs to choose the correct
  PostgreSQL type that works in both NocoDB and NocoBase.
---

# Column Types — PostgreSQL ↔ NocoDB ↔ NocoBase Compatibility

The tables below list the **safe default** type for each purpose: NocoDB creates and displays it, and NocoBase reads it when connected as an external source. The NocoBase column shows the *Field type* NocoBase assigns, taken from its external-database documentation. Wider types (`jsonb`, `uuid`, `ARRAY`, native `ENUM`, geometric) are covered in "Other PostgreSQL Types" below. Neither the defaults nor the wider types were run against a live database for this plugin; check on your target versions.

## Text Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field | Notes |
|---------|----------|---------------|----------------|-------|
| Short text | `text` | `SingleLineText` | `string` / `text` | NocoDB default for PG |
| Long text | `text` | `LongText` | `text` | Same SQL type, UIType configured in NocoDB |
| Email | `character varying` | `Email` | `string` | NocoDB default for Email in PG |
| URL | `text` | `URL` | `string` / `text` | |
| Phone | `character varying` | `PhoneNumber` | `string` | |
| Attachment | `text` | `Attachment` | `text` | JSON string inside |

## Numeric Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field | Notes |
|---------|----------|---------------|----------------|-------|
| Integer | `int4` / `integer` | `Number` | `integer` | |
| Large integer | `bigint` / `int8` | `Number` | `bigInt` | NocoDB default for Number in PG |
| Decimal | `decimal` | `Decimal` / `Currency` / `Duration` | `decimal` | Specify precision/scale: `decimal(10,2)` |
| Percent | `double precision` | `Percent` | `double` | |
| Rating | `smallint` / `int2` | `Rating` | `integer` | NocoDB default for Rating in PG |
| Auto-number | `int8` / `bigint` | `AutoNumber` | `bigInt` | NocoDB creates `int8` with auto-increment (`serial` types are accepted too) |

## Date and Time Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field | Notes |
|---------|----------|---------------|----------------|-------|
| Date + time | `timestamp` | `DateTime` | `date` | **NocoDB default** — `timestamp` (no TZ) |
| Date + time + TZ | `timestamptz` | `DateTime` / `CreatedTime` | `date` | NocoBase docs list one `TIMESTAMP` row; confirm `timestamptz` on your version |
| Date only | `date` | `Date` | `dateOnly` | |
| Time only | `time` | `Time` | `time` | |
| Year | `int4` | `Year` | `integer` | NocoDB stores Year as int |

> **Choosing**: if timezone matters — use `timestamptz`. If not — `timestamp`. Both work in both systems. NocoDB creates `timestamp` (no TZ) by default.

## Boolean Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field |
|---------|----------|---------------|----------------|
| Yes/No | `bool` | `Checkbox` | `boolean` |

## JSON Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field | Notes |
|---------|----------|---------------|----------------|-------|
| JSON data | `json` | `JSON` | `json` | **Default** — this is what NocoDB creates for a JSON field |
| JSON with indexing/operators | `jsonb` | `JSON` | `json` | Accepted by both platforms (see the note below). Pick it when you need GIN indexes or `@>` operators |

> Both platforms read JSON columns of either kind. The NocoBase docs map `JSON, JSONB` to the `json` field type (there is no separate `jsonb` field type); NocoDB maps `json` and `jsonb` to its JSON field. Confirm on your target versions before relying on `jsonb` operators through the UI.

## Select Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field | Notes |
|---------|----------|---------------|----------------|-------|
| Single select | `text` | `SingleSelect` | `string` | NocoDB default for PG |
| Multi select | `text` | `MultiSelect` | `string` | NocoDB default for PG |

> NocoDB uses `text` for both SingleSelect and MultiSelect in PostgreSQL. This is compatible with NocoBase. A native PostgreSQL `ENUM` is a different case — see below.

## Special Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field | Notes |
|---------|----------|---------------|----------------|-------|
| FK column | `character varying` | `ForeignKey` | depends on relation | NocoDB default for FK in PG |
| FK column (int) | `int4` | `ForeignKey` | `integer` | If parent PK is `serial` |
| Sort order | `numeric` | `Order` | `decimal` | NocoDB system field `nc_order` |
| Collaborator | `character varying` | `Collaborator` | `string` | |
| Geo | `text` | `GeoData` | `text` | NocoDB stores as text in PG |

## Other PostgreSQL Types

None of these is forbidden — each is read by at least one platform, and the support is **per platform**. The last column is the **safe default**: use the wider type when you need it and have checked it on your target NocoDB and NocoBase versions.

| PostgreSQL type | NocoDB | NocoBase (Field type) | Safe default |
|-----------------|--------|-----------------------|--------------|
| `uuid` column or PK | An existing `uuid` column is read as a single-line text field and an existing PK is kept as is. NocoDB's own UUID field creates `uuid` with a `gen_random_uuid()` default | `uuid` | `serial`/`bigserial` for the PK; `text` for other ids |
| `ARRAY` (e.g. `text[]`) | No field type mapping — shown as a database-specific type, with no array or select editor | `array` (multiple select, checkbox group) | `json`, or a junction table when the items are real entities |
| Native `ENUM` | Read as SingleSelect from release 2026.04.5. Editing options in the NocoDB UI runs `ALTER TYPE` on your database: add and rename in place, remove by rebuilding the type | **Not in the documented mapping table** — expect it under unsupported field types | `text` + SingleSelect |
| `POINT`, `POLYGON`, `CIRCLE` | Read as a Geometry field | `point`, `polygon`, `circle` | `json` with coordinates, or two `double precision` columns |
| `PATH` | Shown as a database-specific type | `lineString` | `json` |
| `INHERITS` (table inheritance) | Not covered by upstream docs | Not covered by upstream docs | Regular tables + FK |

The NocoBase column comes from its external-database documentation (field type mapping). The NocoDB column comes from reading `PgUi.ts` and the column service on the `develop` branch, October 2026. Types NocoBase does not map (`RANGE`, `BIT`, `GEOMETRY`) appear as unsupported fields there.

To add columns using these types, see the `modify-schema` skill for ADD COLUMN, RENAME, TYPE change, and DROP operations.
