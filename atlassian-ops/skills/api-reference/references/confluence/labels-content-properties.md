# Confluence Labels, Content Properties & Governance

Labels, key/value content properties, and the governance surface (classification, data policies, redactions, admin key, app properties). Base `${ATLASSIAN_SITE_URL%/}/wiki/api/v2`.

## Labels

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /labels` | List labels by id/prefix (`getLabels`). `?label-id=&prefix=&sort=name`. |
| `GET /pages/{id}/labels` · `GET /blogposts/{id}/labels` · `GET /attachments/{id}/labels` · `GET /custom-content/{id}/labels` | Labels on a piece of content. |
| `GET /spaces/{id}/labels` · `GET /spaces/{id}/content/labels` | Labels on a space / on all content in a space. |
| `GET /labels/{id}/pages` · `/blogposts` · `/attachments` | Content carrying a given label. |

> **Adding/removing** a label is not in v2 — use the v1 endpoint `POST ${ATLASSIAN_SITE_URL%/}/wiki/rest/api/content/{id}/label` with body `[{"prefix":"global","name":"release-1-2"}]`, and `DELETE …/label/{name}` to remove.

## Content properties (key/value on any content)

The same five-call pattern repeats for each content type (`pages`, `blogposts`, `attachments`, `custom-content`, `comments`, `databases`, `folders`, `embeds`, `whiteboards`):

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /pages/{page-id}/properties` | List properties (`getPageContentProperties`). |
| `POST /pages/{page-id}/properties` | Create (`createPageProperty`). Body `{"key":"…","value":<any JSON>}`. |
| `GET /pages/{page-id}/properties/{property-id}` | Get one (`getPageContentPropertiesById`). |
| `PUT /pages/{page-id}/properties/{property-id}` | Update (`updatePagePropertyById`) — body carries a `version.number` bump. |
| `DELETE /pages/{page-id}/properties/{property-id}` | Delete (`deletePagePropertyById`). |

Swap `pages` for `blogposts`, `attachments`, `custom-content`, `comments`, `databases`, `folders`, `embeds`, `whiteboards` to address the matching operationIds (e.g. `getBlogpostContentProperties`).

## Classification levels (Data Classification, Premium/Enterprise)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /classification-levels` | All classification levels on the site (`getClassificationLevels`). |
| `GET/PUT /pages/{id}/classification-level` | Get / set a page's level (`getPageClassificationLevel`, `putPageClassificationLevel`). |
| `POST /pages/{id}/classification-level/reset` | Reset to the space default. |
| `GET/PUT/DELETE /spaces/{id}/classification-level/default` | Manage a space's default level. |

(Same get/put/reset trio exists for `blogposts`, `databases`, `whiteboards`.)

## Governance & admin

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /data-policies/metadata` · `GET /data-policies/spaces` | Data-residency policy info (`getDataPolicyMetadata`, `getDataPolicySpaces`). |
| `POST /pages/{id}/redact` · `POST /blogposts/{id}/redact` | Redact content (`postRedactPage`). |
| `GET/POST/DELETE /admin-key` | Read / enable / disable the org Admin Key (`getAdminKey`, `enableAdminKey`). |
| `GET/PUT/DELETE /app/properties/{propertyKey}` | Forge app property store (`getForgeAppProperty`). |

## Notes
- **Label add/remove and attachment upload live on the Confluence v1 REST API** (`/wiki/rest/api/...`) — v2 only reads labels. State that rather than hunting for a v2 write.
- Content properties take **arbitrary JSON** in `value`; updates need a `version.number` bump just like pages.
- Classification, data policies, and redactions are gated by plan/site config — expect `403`/`404` if not enabled.
- For exact schemas: `grep -n '"operationId": "getLabels"' ../confluence-openapi-v2.json`.
