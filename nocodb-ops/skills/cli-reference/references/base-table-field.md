# Workspaces, Bases, Tables, Fields -- curl Recipes (read side)

Recipes on the Meta API v3 for finding the IDs the record recipes need. Each block maps to a command of the official `nocodb.sh` script (see the parent skill's command map). The `nocodb_api METHOD /path ['body']` wrapper is defined in `../SKILL.md` -- paths are under `${NOCODB_URL}/api/v3`.

**Changing** the schema (creating tables, fields, select options, relations) is the job of the **nocodb-dev** plugin -- its `cli-reference` and `field-management` skills hold the write recipes and every field-type payload. This file stays on the read side that business users need.

## Workspaces

Listing workspaces is open on all plans; reading a single workspace needs cloud Business and above or a licensed self-hosted deployment.

```bash
nocodb_api GET /meta/workspaces                                  # → wabc1234xyz
nocodb_api GET /meta/workspaces/$WORKSPACE_ID
```

## Bases

```bash
nocodb_api GET /meta/workspaces/$WORKSPACE_ID/bases              # → pdef5678uvw
nocodb_api GET /meta/bases/$BASE_ID
```

Base members (cloud Business and above / licensed self-hosted):

```bash
nocodb_api GET "/meta/bases/$BASE_ID?include[]=members"
```

## Tables

```bash
nocodb_api GET /meta/bases/$BASE_ID/tables                       # → mghi9012rst
nocodb_api GET /meta/bases/$BASE_ID/tables/$TABLE_ID             # fields + views
```

## Fields

```bash
nocodb_api GET /meta/bases/$BASE_ID/tables/$TABLE_ID             # the `fields` array lists them  → cjkl3456opq
nocodb_api GET /meta/bases/$BASE_ID/fields/$FIELD_ID
```

Each field carries `id`, `title`, `type` (CamelCase: `SingleLineText`, `Number`, `Date`, `SingleSelect`, `LinkToAnotherRecord`, ...) and type-specific `options`. Use the exact `title` in record payloads and `where` strings, and the `id` wherever a tool asks for a field ID (`groupByRecords`, link recipes, view filters).

## Ask MCP Instead

`getTablesList`, `getTableSchema` (and `getBaseSchema` on Cloud / licensed) return the same information without an API token -- see **mcp-patterns**.
