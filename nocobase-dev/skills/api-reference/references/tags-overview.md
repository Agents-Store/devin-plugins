# OpenAPI tag overview

Every tag from `references/openapi/nocobase.json`, with a one-line summary and the matching specialist skill in this plugin.

| Tag | Ops | What it does | Specialist skill |
|---|---:|---|---|
| `flowSurfaces` | 46 | Atomic and declarative FlowModel surface orchestration — pages, blocks, popups, tabs, layout, linkage, blueprints, templates. Used by the UI builder. | `nocobase-ui-builder` |
| `$collection` | 10 | CRUD on a user-defined data table (`{collectionName}:list/get/create/update/destroy/move`). | `nocobase-data-modeling`, `nocobase-data-analysis` |
| `$collection.$manyToManyAssociation` | 10 | Many-to-many relation actions (`list/get/create/update/destroy/move/set/add/remove/toggle`). | `nocobase-data-modeling` |
| `$collection.$oneToManyAssociation` | 9 | One-to-many relation actions. | `nocobase-data-modeling` |
| `$collection.$manyToOneAssociation` | 6 | Many-to-one relation actions. | `nocobase-data-modeling` |
| `$collection.$oneToOneAssociation` | 6 | One-to-one relation actions. | `nocobase-data-modeling` |
| `collections` | 9 | Collection metadata CRUD + bulk field updates. | `nocobase-data-modeling` |
| `collections.fields` | 6 | Field modelling under a collection — scalar, relation, ordering. | `nocobase-data-modeling` |
| `collectionCategories` | 6 | Group collections into categories. | `nocobase-data-modeling` |
| `fields` | 1 | High-level field-application entry. | `nocobase-data-modeling` |
| `dbViews` | 3 | Inspect database views for view-backed collections. | `nocobase-data-modeling` |
| `pm` | 9 | Plugin manager — list, enable, disable, install, remove, upgrade. | `nocobase-plugin-manage` |
| `app` | 5 | Application lifecycle and runtime metadata — `getInfo`, `getLang`, `getPlugins`, `restart`, `clearCache`. | `nocobase-env-manage` |
| `applications` | 4 | Multi-app instance admin (sub-applications). | `nocobase-env-manage` |
| `roles` | 9 | Roles CRUD, default role, system role mode, data permission application. | `nocobase-acl-manage` |
| `roles.users` | 3 | Add/list/remove users on a role. | `nocobase-acl-manage` |
| `users.roles` | 3 | Add/list/remove roles on a user. | `nocobase-acl-manage` |
| `roles.dataSourceResources` | 3 | Per-role data-source resource permissions. | `nocobase-acl-manage` |
| `roles.dataSourcesCollections` | 1 | List a role's collection access in a data source. | `nocobase-acl-manage` |
| `roles.desktopRoutes` | 4 | Per-role desktop menu visibility. | `nocobase-acl-manage` |
| `dataSources` | 1 | List enabled data sources. | `nocobase-data-modeling` |
| `dataSources.roles` | 2 | Per-role policy on a data source. | `nocobase-acl-manage` |
| `dataSources.rolesResourcesScopes` | 5 | Scopes that constrain a role's resource access. | `nocobase-acl-manage` |
| `rolesResourcesScopes` | 2 | Resource-scope CRUD (legacy). | `nocobase-acl-manage` |
| `desktopRoutes` | 1 | Desktop route inspection. | `nocobase-acl-manage` |
| `availableActions` | 1 | List available actions usable in role policy. | `nocobase-acl-manage` |
| `users` | 5 | User CRUD. | `nocobase-acl-manage` |
| `apiKeys` | 3 | API key CRUD (the API Keys plugin). | `auth` |
| `Auth`, `Authenticator`, `Basic auth`, `OIDC`, `SAML`, `Push` | ~13 | Authenticator configuration and sign-in endpoints. | `auth` |
| `verifications`, `verifications_providers` | 9 | MFA / verification challenges. | `auth` |
| `workflows` | 8 | Workflow CRUD, version sync, manual run. | `nocobase-workflow-manage` |
| `workflows.nodes` | 1 | Create node in workflow (association). | `nocobase-workflow-manage` |
| `flow_nodes` | 7 | Update, delete, move, duplicate, test a node. | `nocobase-workflow-manage` |
| `executions` | 4 | Execution list, get, cancel, delete. | `nocobase-workflow-manage` |
| `jobs` | 3 | Node job list, get, resume. | `nocobase-workflow-manage` |
| `userWorkflowTasks` | 1 | Current-user workflow task queue. | `nocobase-workflow-manage` |
| `uiSchemas` | 9 | Lower-level UI schema CRUD (used internally by `flowSurfaces`). | `nocobase-ui-builder` |
| `themeConfig` | 4 | Theme configuration. | `nocobase-utils` |
| `storages` | 5 | File storages (local, s3, …). | `nocobase-utils` |
| `localization`, `localizationTexts`, `localizationTranslations` | 4 | i18n translations. | `nocobase-utils` |
| `map-configuration` | 2 | Map provider settings. | `nocobase-utils` |
| `chinaRegions` | 1 | Bundled China regions reference data. | `nocobase-utils` |
| `swagger` | 1 | Swagger doc serving. | `nocobase-utils` |

The 19 tags listed in `tags[]` at the top of the spec are the curated headline groups; the table above includes every tag actually attached to operations.
