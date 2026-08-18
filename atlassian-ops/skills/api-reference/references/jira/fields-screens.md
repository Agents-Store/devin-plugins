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
| `GET /field/{fieldId}/context/defaultValue` · `PUT …` | Get / set the context default value. |

## Field configurations

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /fieldconfiguration` · `POST /fieldconfiguration` | List / create field configurations (which fields are required/hidden). |
| `GET /fieldconfiguration/{id}/fields` · `PUT …` | List / update behavior of fields in a configuration. |
| `GET /fieldconfigurationscheme` · `POST …` | List / create field-configuration schemes. |
| `PUT /fieldconfigurationscheme/project` | Assign a scheme to a project. |

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
