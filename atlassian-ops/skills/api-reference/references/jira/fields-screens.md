# Jira Fields & Screens

Custom fields, their contexts/options, field configurations, and the screen layer that decides which fields appear when. Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`. Mostly admin-level configuration.

## Fields

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /field` | All fields, system + custom (`getFields`). |
| `GET /field/search` | Paginated custom field search (`getFieldsPaginated`). `?type=custom&query=&orderBy=name`. |
| `POST /field` | Create a custom field (`createCustomField`). Body `{"name","type":"com.atlassian.jira.plugin.system.customfieldtypes:textfield","searcherKey":"…"}`. |
| `PUT /field/{fieldId}` | Update a custom field's name/description (`updateCustomField`). |
| `POST /field/{id}/trash` · `POST /field/{id}/restore` · `DELETE /field/{id}` | Trash / restore / delete a custom field. |
| `GET /projects/fields` | Fields available in given projects (`getProjectFields`). |

## Custom field contexts & options

A context scopes a custom field to projects/issue types and holds its option list.

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /field/{fieldId}/context` | List contexts (`getContextsForField`). |
| `POST /field/{fieldId}/context` | Create a context (`createCustomFieldContext`). Body `{"name","projectIds":[…],"issueTypeIds":[…]}`. |
| `PUT /field/{fieldId}/context/{contextId}/project` · `…/issuetype` | Assign projects / issue types to a context. |
| `GET /field/{fieldId}/context/{contextId}/option` | List options (`getOptionsForContext`). |
| `POST /field/{fieldId}/context/{contextId}/option` | Add options (`createCustomFieldOption`). Body `{"options":[{"value":"Red"},…]}`. |
| `PUT …/option` · `PUT …/option/move` · `DELETE …/option/{optionId}` | Update / reorder / delete options. |
| `GET /field/{fieldId}/context/defaultValues` | Default values grouped by context and issue type (`getContextDefaultValues`, new in 2026): one entry per context with `isAnyIssueType: true` for the catch-all default, plus one per issue-type-specific default. |
| `PUT /field/{fieldId}/context/defaultValues` | Set per-issue-type defaults (`setContextDefaultValues`) — **early-access programme only** (CHANGE-3082); a `null` value removes the default. |
| `GET /field/{fieldId}/context/defaultValue` · `PUT …` | **Deprecated** (`getDefaultValues`, `setDefaultValues`) — use `…/defaultValues` above. Still the only way to set a default outside the EAP. |

## Field configurations (deprecated — use field schemes)

**Every `/fieldconfiguration*` and `/fieldconfigurationscheme*` operation is flagged deprecated in the spec.** Atlassian points to the **Field schemes** API (`/config/fieldschemes…`, below), which supports field-association schemes. Keep the old calls only for sites that have not moved yet.

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /fieldconfiguration` · `POST /fieldconfiguration` | *(deprecated)* List / create field configurations (which fields are required/hidden). |
| `GET /fieldconfiguration/{id}/fields` · `PUT …` | *(deprecated)* List / update behavior of fields in a configuration. |
| `GET /fieldconfigurationscheme` · `POST …` | *(deprecated)* List / create field-configuration schemes. |
| `PUT /fieldconfigurationscheme/project` | *(deprecated)* Assign a scheme to a project. |

## Field schemes (replacement)

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /config/fieldschemes` · `POST /config/fieldschemes` | List / create field schemes (`getFieldAssociationSchemes`, `createFieldAssociationScheme`). |
| `GET /config/fieldschemes/{id}` · `PUT …` · `DELETE …` | Get / update / delete one scheme. |
| `POST /config/fieldschemes/{id}/clone` | Clone a scheme (`cloneFieldAssociationScheme`). |
| `GET /config/fieldschemes/{id}/fields` | Search the fields of a scheme (`searchFieldAssociationSchemeFields`); per-field parameters at `…/fields/{fieldId}/parameters`. |
| `PUT /config/fieldschemes/fields` · `DELETE …` | Update / remove field associations across schemes; `…/fields/parameters` updates / removes per-field parameters. |
| `GET /config/fieldschemes/projects` · `PUT …` · `GET /config/fieldschemes/{id}/projects` | Which projects use which scheme; associate projects to schemes. |

## Screens, tabs & screen schemes

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /screens` · `POST /screens` | List / create screens. |
| `GET /screens/{screenId}/availableFields` | Fields not yet on the screen. |
| `GET /screens/{screenId}/tabs` · `POST …/tabs` | List / add tabs (`getAllScreenTabs`, `addScreenTab`). |
| `POST /screens/addToDefault/{fieldId}` | Add a field to the default screen (`addFieldToDefaultScreen`). |
| `GET /screenscheme` · `POST /screenscheme` | List / create screen schemes (map screens to operations). |
| `GET /issuetypescreenscheme` · `POST …` | List / create issue-type screen schemes. |
| `PUT /issuetypescreenscheme/project` | Assign an issue-type screen scheme to a project. |

## Notes
- A field only appears on create/edit/view if it's on the right **screen**, in the **screen scheme**, in the **issue-type screen scheme** assigned to the project — fix "field not showing" here.
- Custom field **type keys** are long namespaced strings; copy them from `GET /field` of an existing field of that type.
- These are powerful admin operations — confirm before deleting fields/contexts/options that may hold data.
- For exact schemas: `grep -n '"operationId": "createCustomField"' ../jira-openapi-v3.json`.
