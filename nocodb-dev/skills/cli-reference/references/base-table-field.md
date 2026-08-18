# Bases, Tables, Fields — CLI Reference

Imported from the official NocoDB agent-skills CLI. Schema-focused.

## Workspaces (Enterprise only)

```bash
nc workspace:list                                        # → wabc1234xyz
nc workspace:get wabc1234xyz
nc workspace:create '{"title":"New Workspace"}'
nc workspace:update wabc1234xyz '{"title":"Renamed"}'
nc workspace:delete wabc1234xyz
nc workspace:members wabc1234xyz
nc workspace:members:add wabc1234xyz '{"email":"user@example.com","roles":"workspace-creator"}'
nc workspace:members:update wabc1234xyz '{"email":"user@example.com","roles":"workspace-viewer"}'
nc workspace:members:remove wabc1234xyz '{"email":"user@example.com"}'
```

## Bases

```bash
nc base:list wabc1234xyz                                 # → pdef5678uvw
nc base:get pdef5678uvw
nc base:create wabc1234xyz '{"title":"New Base"}'
nc base:update pdef5678uvw '{"title":"Renamed"}'
nc base:delete pdef5678uvw
```

Base Collaboration (Enterprise):

```bash
nc base:members pdef5678uvw
nc base:members:add pdef5678uvw '{"email":"user@example.com","roles":"base-editor"}'
nc base:members:update pdef5678uvw '{"email":"user@example.com","roles":"base-viewer"}'
nc base:members:remove pdef5678uvw '{"email":"user@example.com"}'
```

## Tables

```bash
nc table:list pdef5678uvw                                # → mghi9012rst
nc table:get pdef5678uvw mghi9012rst
nc table:create pdef5678uvw '{"title":"NewTable"}'
nc table:update pdef5678uvw mghi9012rst '{"title":"Customers"}'
nc table:delete pdef5678uvw mghi9012rst
```

Create with initial fields:

```bash
nc table:create pdef5678uvw '{
  "title": "Customers",
  "fields": [
    { "title": "Name",  "type": "SingleLineText" },
    { "title": "Email", "type": "Email" }
  ]
}'
```

Set the display field after creation:

```bash
nc table:update pdef5678uvw mghi9012rst '{"display_field_id":"cabc111"}'
```

## Fields

```bash
nc field:list pdef5678uvw mghi9012rst                                            # → cjkl3456opq
nc field:get pdef5678uvw mghi9012rst cjkl3456opq
nc field:create pdef5678uvw mghi9012rst '{"title":"Phone","type":"PhoneNumber"}'
nc field:update pdef5678uvw mghi9012rst cjkl3456opq '{"title":"Mobile"}'
nc field:delete pdef5678uvw mghi9012rst cjkl3456opq
```

### Supported Field Types

`SingleLineText`, `LongText`, `PhoneNumber`, `URL`, `Email`, `Number`, `Decimal`, `Currency`, `Percent`, `Duration`, `Date`, `DateTime`, `Time`, `Year`, `SingleSelect`, `MultiSelect`, `Rating`, `Checkbox`, `Attachment`, `JSON`, `Geometry`, `Links`, `LinkToAnotherRecord`, `Lookup`, `Rollup`, `Button`, `Formula`, `Barcode`, `QrCode`, `CreatedTime`, `LastModifiedTime`, `CreatedBy`, `LastModifiedBy`.

Per-type payloads — see `../../api-reference/references/field-types.md`.

### Common Field Tweaks

Rename:

```bash
nc field:update <baseId> <tableId> <columnId> '{"title":"NewName"}'
```

Convert type (allowed only when lossless):

```bash
nc field:update <baseId> <tableId> <columnId> '{"type":"LongText"}'
```

Add a SingleSelect option:

```bash
nc field:update <baseId> <tableId> <columnId> '{
  "colOptions": {
    "options": [
      {"title":"New"},
      {"title":"Active"},
      {"title":"Archived"}
    ]
  }
}'
```

(Existing options keep their IDs; new options appear at the end.)
