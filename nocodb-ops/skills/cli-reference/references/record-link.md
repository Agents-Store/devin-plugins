# Records, Links, Attachments, Actions

Imported from the official NocoDB agent-skills CLI.

## Records

```bash
# List records with pagination, filtering, sorting
nc record:list pdef5678uvw mghi9012rst                              # page 1, 25 records
nc record:list pdef5678uvw mghi9012rst 2 50                         # page 2, 50 records
nc record:list pdef5678uvw mghi9012rst 1 25 "(status,eq,active)"
nc record:list pdef5678uvw mghi9012rst 1 25 "" '[{"field":"cjkl3456opq","direction":"desc"}]'
nc record:list pdef5678uvw mghi9012rst 1 25 "" "" "Name,Email" "" 2 # with fields and nestedPage

# Get single record
nc record:get pdef5678uvw mghi9012rst 31
nc record:get pdef5678uvw mghi9012rst 31 "name,email"

# Create record
nc record:create pdef5678uvw mghi9012rst '{"fields":{"name":"Alice"}}'

# Update single record
nc record:update pdef5678uvw mghi9012rst 31 '{"status":"active"}'

# Update multiple records
nc record:update-many pdef5678uvw mghi9012rst '[{"id":31,"fields":{"status":"done"}}]'

# Delete records
nc record:delete pdef5678uvw mghi9012rst 31
nc record:delete pdef5678uvw mghi9012rst '[31,32]'

# Count records
nc record:count pdef5678uvw mghi9012rst
nc record:count pdef5678uvw mghi9012rst "(status,eq,active)"
```

### record:list Parameters

```
nc record:list BASE TABLE [PAGE] [SIZE] [WHERE] [SORT] [FIELDS] [VIEW_ID] [NESTED_PAGE]
```

| Parameter | Position | Default | Description |
|-----------|----------|---------|-------------|
| BASE | 1 | required | Base name or ID |
| TABLE | 2 | required | Table name or ID |
| PAGE | 3 | 1 | Page number |
| SIZE | 4 | 25 | Records per page |
| WHERE | 5 | -- | Filter expression |
| SORT | 6 | -- | Sort expression or JSON array |
| FIELDS | 7 | -- | Comma-separated field names |
| VIEW_ID | 8 | -- | View ID to use |
| NESTED_PAGE | 9 | -- | Page for nested linked records |

Names also work — resolved to IDs automatically:
```bash
nc record:list MyBase Users
NOCODB_VERBOSE=1 nc field:list MyBase Users   # shows resolved IDs
```

## Linked Records

```bash
# List linked records
nc link:list pdef5678uvw mghi9012rst cjkl3456opq 31
nc link:list pdef5678uvw mghi9012rst cjkl3456opq 31 1 25 "(Status,eq,active)" "-CreatedAt" "Name,Email"

# Add links
nc link:add pdef5678uvw mghi9012rst cjkl3456opq 31 '[{"id":42}]'

# Remove links
nc link:remove pdef5678uvw mghi9012rst cjkl3456opq 31 '[{"id":42}]'
```

### link:list Parameters

```
nc link:list BASE TABLE LINK_FIELD RECORD_ID [PAGE] [SIZE] [WHERE] [SORT] [FIELDS]
```

## Attachments

```bash
nc attachment:upload pdef5678uvw mghi9012rst 31 cjkl3456opq ./report.pdf
```

Parameters: `BASE TABLE RECORD_ID FIELD FILEPATH`

## Button Actions

```bash
nc action:trigger pdef5678uvw mghi9012rst cjkl3456opq 31
```

Parameters: `BASE TABLE BUTTON_FIELD RECORD_ID`
