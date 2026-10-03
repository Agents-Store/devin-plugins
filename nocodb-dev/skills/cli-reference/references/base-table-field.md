# Bases, Tables, Fields — curl Recipes

Schema-focused recipes on the Meta API v3. Each block maps to a command of the official `nocodb.sh` script (see the parent skill's command map). The `nocodb_api METHOD /path ['body']` wrapper is defined in `../SKILL.md` — paths are under `${NOCODB_URL}/api/v3`.

## Workspaces (plan-dependent)

```bash
nocodb_api GET    /meta/workspaces                                  # → wabc1234xyz
nocodb_api GET    /meta/workspaces/$WORKSPACE_ID
nocodb_api POST   /meta/workspaces '{"title":"New Workspace"}'
nocodb_api PATCH  /meta/workspaces/$WORKSPACE_ID '{"title":"Renamed"}'
nocodb_api DELETE /meta/workspaces/$WORKSPACE_ID
nocodb_api GET    "/meta/workspaces/$WORKSPACE_ID?include[]=members"
nocodb_api POST   /meta/workspaces/$WORKSPACE_ID/members '[{"email":"user@example.com","workspace_role":"workspace-level-creator"}]'
nocodb_api PATCH  /meta/workspaces/$WORKSPACE_ID/members '[{"user_id":"<userId>","workspace_role":"workspace-level-viewer"}]'
nocodb_api DELETE /meta/workspaces/$WORKSPACE_ID/members '[{"user_id":"<userId>"}]'
```

Member bodies are arrays; a new member is identified by `user_id` or `email` (not both), updates and deletes by `user_id`. `workspace_role`: `workspace-level-owner`, `-creator`, `-editor`, `-viewer`, `-commenter`, `-no-access`.

Listing and creating workspaces is open on all plans; reading, updating and deleting a specific workspace needs cloud Business and above or a licensed self-hosted deployment.

## Bases

```bash
nocodb_api GET    /meta/workspaces/$WORKSPACE_ID/bases              # → pdef5678uvw
nocodb_api GET    /meta/bases/$BASE_ID
nocodb_api POST   /meta/workspaces/$WORKSPACE_ID/bases '{"title":"New Base"}'
nocodb_api PATCH  /meta/bases/$BASE_ID '{"title":"Renamed"}'
nocodb_api DELETE /meta/bases/$BASE_ID
```

Base collaboration (cloud Business and above / licensed self-hosted):

```bash
nocodb_api GET    "/meta/bases/$BASE_ID?include[]=members"
nocodb_api POST   /meta/bases/$BASE_ID/members   '[{"email":"user@example.com","base_role":"editor"}]'
nocodb_api PATCH  /meta/bases/$BASE_ID/members   '[{"user_id":"<userId>","base_role":"viewer"}]'
nocodb_api DELETE /meta/bases/$BASE_ID/members   '[{"user_id":"<userId>"}]'
```

Bodies are arrays. `base_role`: `owner`, `creator`, `editor`, `viewer`, `commenter`, `no-access`; invites use `user_id` or `email` (not both), updates and deletes use `user_id`.

## Tables

```bash
nocodb_api GET    /meta/bases/$BASE_ID/tables                       # → mghi9012rst
nocodb_api GET    /meta/bases/$BASE_ID/tables/$TABLE_ID             # fields + views
nocodb_api POST   /meta/bases/$BASE_ID/tables '{"title":"NewTable"}'
nocodb_api PATCH  /meta/bases/$BASE_ID/tables/$TABLE_ID '{"title":"Customers"}'
nocodb_api DELETE /meta/bases/$BASE_ID/tables/$TABLE_ID
```

Create with initial fields:

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables '{
  "title": "Customers",
  "fields": [
    { "title": "Name",  "type": "SingleLineText" },
    { "title": "Email", "type": "Email" }
  ]
}'
```

Set the display field after creation:

```bash
nocodb_api PATCH /meta/bases/$BASE_ID/tables/$TABLE_ID '{"display_field_id":"cabc111"}'
```

## Fields

```bash
nocodb_api GET    /meta/bases/$BASE_ID/tables/$TABLE_ID             # the `fields` array lists them        → cjkl3456opq
nocodb_api GET    /meta/bases/$BASE_ID/fields/$FIELD_ID
nocodb_api POST   /meta/bases/$BASE_ID/tables/$TABLE_ID/fields '{"title":"Phone","type":"PhoneNumber"}'
nocodb_api PATCH  /meta/bases/$BASE_ID/fields/$FIELD_ID '{"title":"Mobile"}'
nocodb_api DELETE /meta/bases/$BASE_ID/fields/$FIELD_ID
```

### Supported Field Types

`SingleLineText`, `LongText`, `PhoneNumber`, `URL`, `Email`, `Number`, `Decimal`, `Currency`, `Percent`, `Duration`, `Date`, `DateTime`, `Time`, `Year`, `SingleSelect`, `MultiSelect`, `Rating`, `Checkbox`, `Attachment`, `JSON`, `Geometry`, `Links`, `LinkToAnotherRecord`, `Lookup`, `Rollup`, `Button`, `Formula`, `Barcode`, `QrCode`, `User`, `AutoNumber`, `CreatedTime`, `LastModifiedTime`, `CreatedBy`, `LastModifiedBy`.

Per-type payloads — see `../../api-reference/references/field-types.md`. Type-specific settings go inside `options`.

### Common Field Tweaks

Rename:

```bash
nocodb_api PATCH /meta/bases/$BASE_ID/fields/$FIELD_ID '{"title":"NewName"}'
```

Convert type (allowed only when lossless):

```bash
nocodb_api PATCH /meta/bases/$BASE_ID/fields/$FIELD_ID '{"type":"LongText"}'
```

Add select choices (existing choices keep their place; titles that already exist are skipped):

```bash
nocodb_api POST /meta/bases/$BASE_ID/fields/$FIELD_ID/options '{
  "choices": [ {"title":"Blocked","color":"#fee2d5"} ]
}'
```

Remove select choices by title (clears them from existing records; at least one choice must remain):

```bash
nocodb_api DELETE /meta/bases/$BASE_ID/fields/$FIELD_ID/options '{ "choices": [ {"title":"Archived"} ] }'
```
