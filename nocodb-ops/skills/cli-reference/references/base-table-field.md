# Workspaces, Bases, Tables, Fields

Imported from the official NocoDB agent-skills CLI.

## Workspaces

**Note:** Workspace APIs and Workspace Collaboration APIs are available only with self-hosted **Enterprise** plans and cloud-hosted **Enterprise** plans.

```bash
nc workspace:list                                                               # → wabc1234xyz
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
nc base:list wabc1234xyz                                                        # → pdef5678uvw
nc base:get pdef5678uvw
nc base:create wabc1234xyz '{"title":"New Base"}'
nc base:update pdef5678uvw '{"title":"Renamed"}'
nc base:delete pdef5678uvw
```

**Base Collaboration (Enterprise plans only)**

```bash
nc base:members pdef5678uvw
nc base:members:add pdef5678uvw '{"email":"user@example.com","roles":"base-editor"}'
nc base:members:update pdef5678uvw '{"email":"user@example.com","roles":"base-viewer"}'
nc base:members:remove pdef5678uvw '{"email":"user@example.com"}'
```

## Tables

```bash
nc table:list pdef5678uvw                                                       # → mghi9012rst
nc table:get pdef5678uvw mghi9012rst
nc table:create pdef5678uvw '{"title":"NewTable"}'
nc table:update pdef5678uvw mghi9012rst '{"title":"Customers"}'
nc table:delete pdef5678uvw mghi9012rst
```

## Fields

```bash
nc field:list pdef5678uvw mghi9012rst                                           # → cjkl3456opq
nc field:get pdef5678uvw mghi9012rst cjkl3456opq
nc field:create pdef5678uvw mghi9012rst '{"title":"Phone","type":"PhoneNumber"}'
nc field:update pdef5678uvw mghi9012rst cjkl3456opq '{"title":"Mobile"}'
nc field:delete pdef5678uvw mghi9012rst cjkl3456opq
```

## Field Types

Supported field types for `field:create`:

SingleLineText, LongText, Number, Decimal, Currency, Percent, Email, URL, PhoneNumber, Date, DateTime, Time, SingleSelect, MultiSelect, Checkbox, Rating, Attachment, Links, User, JSON
