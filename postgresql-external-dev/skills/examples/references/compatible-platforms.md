# Compatible Low-Code / No-Code Platforms

This plugin produces PostgreSQL schemas that are verified to work with the following platforms when the database is connected as an external data source.

## NocoDB

- **Role**: Primary system — manages schema directly
- **Connection**: PostgreSQL as main or external database
- **PK convention**: `serial` (`int4` + auto-increment) by default
- **FK handling**: Creates physical FK constraints with `ON DELETE NO ACTION`
- **Junction tables**: Composite PK (no separate `id` column)
- **Timestamps**: `timestamp` (without timezone) by default
- **Column types**: Uses `text` for SingleSelect/MultiSelect in PostgreSQL (not `enum`)

## NocoBase

- **Role**: Connects as **external data source** — reads schema only
- **Connection**: PostgreSQL as external data source
- **Sync behavior**: Does **not** modify external DB structure
- **PK reading**: Reads any PK type (`serial`, `bigserial`)
- **FK reading**: Reads existing FK constraints without conflicts
- **Junction tables**: Reads composite PK tables as-is
- **Column mapping**: Maps PostgreSQL types to internal field types (string, integer, datetime, etc.)

## Compatibility Summary

| Feature | NocoDB | NocoBase |
|---------|--------|----------|
| Creates tables | Yes | No (read-only) |
| Modifies schema | Yes | No |
| Reads FK constraints | Yes | Yes |
| Reads composite PK | Yes | Yes |
| Reads `serial` PK | Yes | Yes |
| Reads `bigserial` PK | Yes | Yes |
| Reads `timestamp` | Yes | Yes |
| Reads `timestamptz` | Yes | Yes |
| Reads `json` | Yes | Yes |

## Future Platforms

This section will be updated as compatibility is verified with additional platforms.

<!-- Add new platforms here as they are tested -->
