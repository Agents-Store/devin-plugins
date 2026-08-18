---
name: column-types
description: >
  This skill should be used when the user asks "what SQL type for", "which column type",
  "NocoDB column types", "NocoBase field types", "type compatibility", "how to store
  email/url/phone/json/rating", "what type for currency", "decimal vs double", or needs
  to choose the correct PostgreSQL type that works in both NocoDB and NocoBase.
---

# Column Types — PostgreSQL ↔ NocoDB ↔ NocoBase Compatibility

Every type below is verified: NocoDB correctly creates and displays it, NocoBase correctly reads and displays it when connected as an external source.

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
| Auto-number | `int4` / `integer` | `AutoNumber` | `integer` | |

## Date and Time Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field | Notes |
|---------|----------|---------------|----------------|-------|
| Date + time | `timestamp` | `DateTime` | `datetime` / `datetimeNoTz` | **NocoDB default** — `timestamp` (no TZ) |
| Date + time + TZ | `timestamptz` | `DateTime` / `CreatedTime` | `date` / `datetimeTz` | NocoDB compatible type for DateTime |
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
| JSON data | `json` | `JSON` | `json` | **Use this one** |
| JSON with indexing | `jsonb` | `JSON` | `jsonb` | NocoDB displays as JSON. Works, but `json` is safer |

## Select Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field | Notes |
|---------|----------|---------------|----------------|-------|
| Single select | `text` | `SingleSelect` | `string` | NocoDB default for PG |
| Multi select | `text` | `MultiSelect` | `string` | NocoDB default for PG |

> NocoDB uses `text` for both SingleSelect and MultiSelect in PostgreSQL. This is compatible with NocoBase.

## Special Types

| Purpose | SQL Type | NocoDB UIType | NocoBase Field | Notes |
|---------|----------|---------------|----------------|-------|
| FK column | `character varying` | `ForeignKey` | depends on relation | NocoDB default for FK in PG |
| FK column (int) | `int4` | `ForeignKey` | `integer` | If parent PK is `serial` |
| Sort order | `numeric` | `Order` | `decimal` | NocoDB system field `nc_order` |
| Collaborator | `character varying` | `Collaborator` | `string` | |
| Geo | `text` | `GeoData` | `text` | NocoDB stores as text in PG |

To add columns using these types, see the `modify-schema` skill for ADD COLUMN, RENAME, TYPE change, and DROP operations.
