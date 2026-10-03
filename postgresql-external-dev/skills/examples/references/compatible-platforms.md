# Compatible Low-Code / No-Code Platforms

This plugin produces PostgreSQL schemas that work with the following platforms when the database is connected as an external data source. The patterns in the skills are conservative **defaults**; the wider type support listed below comes from upstream documentation and source code, and was checked against them in October 2026 (NocoBase docs, NocoDB `develop` and release 2026.09.1) — it was not run against a live database. Re-check on your target versions before relying on a non-default type.

## NocoDB

- **Role**: Connects PostgreSQL as an external data source. It can also create and alter tables itself, but **Allow Schema Edit is off by default** for external sources and NocoDB itself advises against enabling it. When it is off, change the schema with SQL and then run **Meta Sync**
- **Connection**: PostgreSQL as main or external database; NocoDB recommends PostgreSQL 14 or later
- **PK convention**: `serial` (`int4` + auto-increment) by default for tables it creates. For an existing external table the primary key is kept as is — NocoDB does not add an `id` column
- **FK handling**: Creates physical FK constraints with `ON DELETE NO ACTION`
- **Junction tables**: Composite PK (no separate `id` column)
- **Timestamps**: `timestamp` (without timezone) by default
- **Column types**: Creates `text` for SingleSelect/MultiSelect and `json` for JSON fields. Reading an existing schema, it maps `json`/`jsonb` to a JSON field and, since release 2026.04.5, a native PostgreSQL `ENUM` to SingleSelect
- **Rows without a primary key**: can be read and added, but not updated or deleted
- **Deleting rows**: external sources have no Base Trash — a deleted row is gone

## NocoBase

- **Role**: Connects as an **external data source** — reads schema only, never changes the external structure
- **License**: the PostgreSQL connector is the plugin `@nocobase/plugin-data-source-external-postgres`, which **requires a commercial license**. It is available from the **Standard** edition upward and is **not part of Community**. Without it, the PostgreSQL type does not appear under Data source management → Add new
- **Connection**: PostgreSQL 9.5 or later (the documented minimum; that release is long out of upstream support)
- **Sync behavior**: after any schema change made outside NocoBase, run the **refresh** action on the data source so it re-reads the structure
- **Primary keys**: `serial`, `bigserial`, `uuid` and `varchar` keys are all mapped. A table without a primary key, a composite-primary-key table or a view needs a **Record unique key** set by hand in the collection settings, otherwise blocks may not create or edit records correctly
- **FK reading**: Reads existing FK constraints without conflicts. The only field type you can add inside NocoBase is a relation field, which is not a real column
- **Junction tables**: Reads composite PK tables as-is (set a Record unique key if you need to edit them)
- **Column mapping**: maps PostgreSQL types to a NocoBase *Field type* — see the table in `column-types`. Unsupported types are listed separately and need development support

## Compatibility Summary

| Feature | NocoDB | NocoBase |
|---------|--------|----------|
| Creates tables | Only with Allow Schema Edit (off by default) | No (read-only) |
| Modifies schema | Only with Allow Schema Edit | No |
| Needs a paid license for external PostgreSQL | No separate plugin for the external source; check your NocoDB edition/plan | **Yes** — commercial plugin, Standard edition or above |
| Re-read schema after DDL | Meta Sync | Refresh the data source |
| Reads FK constraints | Yes | Yes |
| Reads composite PK | Yes | Yes (set Record unique key to edit) |
| Reads `serial` PK | Yes | Yes |
| Reads `bigserial` PK | Yes | Yes |
| Reads `uuid` PK | Yes — existing PK is kept as is (UUID with a DB-function default has an open insert bug, see `create-tables`) | Yes — `uuid` field type |
| Reads `timestamp` | Yes | Yes — `date` |
| Reads `timestamptz` | Yes | Yes — `date` (the docs list one `TIMESTAMP` row) |
| Reads `json` | Yes — JSON field | Yes — `json` |
| Reads `jsonb` | Yes — JSON field | Yes — `json` |
| Reads `ARRAY` | Not mapped to a field type (shown as a database-specific type) | Yes — `array` |
| Reads native `ENUM` | Yes, since 2026.04.5 — SingleSelect | Not in the documented mapping table — treat as unsupported |
| Reads `POINT` / `POLYGON` / `CIRCLE` | Maps to a Geometry field (`PATH` is shown as a database-specific type) | Yes — `point`, `polygon`, `circle` (`PATH` is `lineString`) |
| Table without PK | Read and insert only | Needs a manual Record unique key |

"Safe default" in the skills means: the type both platforms handle in every row above without a caveat. A wider type is not forbidden — it needs a check on your target versions.

## PostgreSQL Versions

| Version | Upstream status (checked 2026-10-02) |
|---------|--------------------------------------|
| 18 | Supported (18.6) |
| 17, 16, 15 | Supported |
| 14 | Supported until 2026-11-12 |
| 13 and older | End of life (13 ended 2025-11-13) |

Use a supported major version. NocoDB recommends 14 or later; the NocoBase external connector documents 9.5 or later as its minimum.

## NocoDB Custom Sync — read-only mirrors

Instead of connecting NocoDB directly to a production database, **Custom Sync** (release 2026.06.1, Business plan and above) mirrors chosen PostgreSQL or MySQL tables into NocoDB as read-only synced tables, refreshed manually or on a schedule, with full or incremental runs. Use it when business users need a friendly view of production data and nothing should be written back. The schema rules in this plugin still apply to the source tables; the mirror is a separate, NocoDB-managed copy.

## Other external databases

NocoDB can also connect Microsoft SQL Server and Oracle Database as external sources (Enterprise add-ons), and NocoBase has external connectors for MySQL, MariaDB, MSSQL, Oracle and others. The patterns in this plugin are PostgreSQL-specific.

## Sources

- NocoBase documentation: Data sources → External databases (license table, plugin names, field type mapping, Record unique key, refresh)
- NocoDB documentation: Primary Key, Connect to a Data Source, Sync with Data Source, release notes 2026.04.5 and 2026.06.1
- NocoDB source: `PgUi.ts` (type mapping on introspection), `ColumnsService` (native enum handling), `BaseModelSqlv2.ts` (soft delete applies to NocoDB-managed sources only)
- PostgreSQL versioning policy

## Future Platforms

This section will be updated as compatibility is verified with additional platforms.

<!-- Add new platforms here as they are tested -->
