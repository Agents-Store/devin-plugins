# Views, Filters, Sorts, Enterprise Features

Imported from the official NocoDB agent-skills CLI.

## Views

**Note:** View APIs are available only on self-hosted and cloud-hosted **Enterprise** plans.

```bash
nc view:list pdef5678uvw mghi9012rst                                            # → vwmno7890abc
nc view:get pdef5678uvw mghi9012rst vwmno7890abc
nc view:create pdef5678uvw mghi9012rst '{"title":"Active Users","type":"grid"}'
nc view:update pdef5678uvw mghi9012rst vwmno7890abc '{"title":"Renamed"}'
nc view:delete pdef5678uvw mghi9012rst vwmno7890abc
```

View types: grid, gallery, kanban, calendar, form

## Filters (View-level)

```bash
nc filter:list pdef5678uvw mghi9012rst vwmno7890abc
nc filter:create pdef5678uvw mghi9012rst vwmno7890abc '{"field_id":"cjkl3456opq","operator":"eq","value":"active"}'
nc filter:replace pdef5678uvw mghi9012rst vwmno7890abc '...'
nc filter:update pdef5678uvw FILTER_ID '{"operator":"neq","value":"archived"}'
nc filter:delete pdef5678uvw FILTER_ID
```

### filter:create JSON Format

```json
{
  "field_id": "cjkl3456opq",
  "operator": "eq",
  "value": "active"
}
```

Operators: eq, neq, gt, lt, gte, lte, like, nlike, is, isnot, empty, notempty, null, notnull

For grouped filters, use `group_operator` with nested `filters` array.

## Sorts (View-level)

```bash
nc sort:list pdef5678uvw mghi9012rst vwmno7890abc
nc sort:create pdef5678uvw mghi9012rst vwmno7890abc '{"field_id":"cjkl3456opq","direction":"desc"}'
nc sort:update pdef5678uvw SORT_ID '{"direction":"asc"}'
nc sort:delete pdef5678uvw SORT_ID
```

### sort:create JSON Format

```json
{
  "field_id": "cjkl3456opq",
  "direction": "desc"
}
```

Direction: `asc` (default) or `desc`.

## Scripts (Enterprise only)

```bash
nc script:list pdef5678uvw
nc script:get pdef5678uvw SCRIPT_ID
nc script:create pdef5678uvw '{"title":"My Script"}'
nc script:update pdef5678uvw SCRIPT_ID '{"title":"Updated"}'
nc script:delete pdef5678uvw SCRIPT_ID
```

## Teams (Enterprise only)

```bash
nc team:list wabc1234xyz
nc team:get wabc1234xyz TEAM_ID
nc team:create wabc1234xyz '{"title":"Engineering"}'
nc team:update wabc1234xyz TEAM_ID '{"title":"Updated"}'
nc team:delete wabc1234xyz TEAM_ID
nc team:members:add wabc1234xyz TEAM_ID '{"email":"user@example.com"}'
nc team:members:update wabc1234xyz TEAM_ID '{"email":"user@example.com"}'
nc team:members:remove wabc1234xyz TEAM_ID '{"email":"user@example.com"}'
```

## API Tokens (Enterprise only)

```bash
nc token:list
nc token:create '{"title":"CI Token"}'
nc token:delete tkn1a2b3c4d5e6f7g
```
