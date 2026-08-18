# Chatwoot Application API

Account-scoped agent/admin API. Auth: `api_access_token` header (user access token). Base: `${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}`.

Authoritative schemas: `openapi/application_swagger.json` (69 paths, 112 operations). Grep it for request bodies, query params, and response shapes.

```bash
jq -r '.paths | keys[]' openapi/application_swagger.json
```

## Account

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/` | `get-account-details` | Get account details |
| PATCH | `/` | `update-account` | Update account |

## Account AgentBots

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/agent_bots` | `list-all-account-agent-bots` | List all AgentBots |
| POST | `/agent_bots` | `create-an-account-agent-bot` | Create an Agent Bot |
| DELETE | `/agent_bots/{id}` | `delete-an-account-agent-bot` | Delete an AgentBot |
| GET | `/agent_bots/{id}` | `get-details-of-a-single-account-agent-bot` | Get an agent bot details |
| PATCH | `/agent_bots/{id}` | `update-an-account-agent-bot` | Update an agent bot |

## Agents

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/agents` | `get-account-agents` | List Agents in Account |
| POST | `/agents` | `add-new-agent-to-account` | Add a New Agent |
| DELETE | `/agents/{id}` | `delete-agent-from-account` | Remove an Agent from Account |
| PATCH | `/agents/{id}` | `update-agent-in-account` | Update Agent in Account |

## Audit Logs

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/audit_logs` | `get-account-audit-logs` | List Audit Logs in Account |

## Automation Rule

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/automation_rules` | `get-account-automation-rule` | List all automation rules in an account |
| POST | `/automation_rules` | `add-new-automation-rule-to-account` | Add a new automation rule |
| DELETE | `/automation_rules/{id}` | `delete-automation-rule-from-account` | Remove a automation rule from account |
| GET | `/automation_rules/{id}` | `get-details-of-a-single-automation-rule` | Get a automation rule details |
| PATCH | `/automation_rules/{id}` | `update-automation-rule-in-account` | Update automation rule in Account |

## Canned Responses

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/canned_responses` | `get-account-canned-response` | List all Canned Responses in an Account |
| POST | `/canned_responses` | `add-new-canned-response-to-account` | Add a New Canned Response |
| DELETE | `/canned_responses/{id}` | `delete-canned-response-from-account` | Remove a Canned Response from Account |
| PATCH | `/canned_responses/{id}` | `update-canned-response-in-account` | Update Canned Response in Account |

## Contact Labels

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/contacts/{id}/labels` | `list-all-labels-of-a-contact` | List Labels |
| POST | `/contacts/{id}/labels` | `contact-add-labels` | Add Labels |

## Contacts

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| POST | `/actions/contact_merge` | `contactMerge` | Merge Contacts |
| GET | `/contacts` | `contactList` | List Contacts |
| POST | `/contacts` | `contactCreate` | Create Contact |
| POST | `/contacts/filter` | `contactFilter` | Contact Filter |
| GET | `/contacts/search` | `contactSearch` | Search Contacts |
| DELETE | `/contacts/{id}` | `contactDelete` | Delete Contact |
| GET | `/contacts/{id}` | `contactDetails` | Show Contact |
| PUT | `/contacts/{id}` | `contactUpdate` | Update Contact |
| POST | `/contacts/{id}/contact_inboxes` | `contactInboxCreation` | Create contact inbox |
| GET | `/contacts/{id}/contactable_inboxes` | `contactableInboxesGet` | Get Contactable Inboxes |
| GET | `/contacts/{id}/conversations` | `contactConversations` | Contact Conversations |

## Conversation Assignments

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| POST | `/conversations/{conversation_id}/assignments` | `assign-a-conversation` | Assign Conversation |

## Conversations

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/conversations` | `conversationList` | Conversations List |
| POST | `/conversations` | `newConversation` | Create New Conversation |
| POST | `/conversations/filter` | `conversationFilter` | Conversations Filter |
| GET | `/conversations/meta` | `conversationListMeta` | Get Conversation Counts |
| GET | `/conversations/{conversation_id}` | `get-details-of-a-conversation` | Conversation Details |
| PATCH | `/conversations/{conversation_id}` | `update-conversation` | Update Conversation |
| POST | `/conversations/{conversation_id}/custom_attributes` | `update-custom-attributes-of-a-conversation` | Update Custom Attributes |
| GET | `/conversations/{conversation_id}/labels` | `list-all-labels-of-a-conversation` | List Labels |
| POST | `/conversations/{conversation_id}/labels` | `conversation-add-labels` | Add Labels |
| GET | `/conversations/{conversation_id}/reporting_events` | `get-conversation-reporting-events` | Conversation Reporting Events |
| POST | `/conversations/{conversation_id}/toggle_priority` | `toggle-priority-of-a-conversation` | Toggle Priority |
| POST | `/conversations/{conversation_id}/toggle_status` | `toggle-status-of-a-conversation` | Toggle Status |
| POST | `/conversations/{conversation_id}/toggle_typing_status` | `toggle-typing-status-of-a-conversation` | Toggle Typing Status |

## Custom Attributes

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/custom_attribute_definitions` | `get-account-custom-attribute` | List all custom attributes in an account |
| POST | `/custom_attribute_definitions` | `add-new-custom-attribute-to-account` | Add a new custom attribute |
| DELETE | `/custom_attribute_definitions/{id}` | `delete-custom-attribute-from-account` | Remove a custom attribute from account |
| GET | `/custom_attribute_definitions/{id}` | `get-details-of-a-single-custom-attribute` | Get a custom attribute details |
| PATCH | `/custom_attribute_definitions/{id}` | `update-custom-attribute-in-account` | Update custom attribute in Account |

## Custom Filters

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/custom_filters` | `list-all-filters` | List all custom filters |
| POST | `/custom_filters` | `create-a-custom-filter` | Create a custom filter |
| DELETE | `/custom_filters/{custom_filter_id}` | `delete-a-custom-filter` | Delete a custom filter |
| GET | `/custom_filters/{custom_filter_id}` | `get-details-of-a-single-custom-filter` | Get a custom filter details |
| PATCH | `/custom_filters/{custom_filter_id}` | `update-a-custom-filter` | Update a custom filter |

## Help Center

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/portals` | `get-portal` | List all portals in an account |
| POST | `/portals` | `add-new-portal-to-account` | Add a new portal |
| PATCH | `/portals/{id}` | `update-portal-to-account` | Update a portal |
| POST | `/portals/{id}/articles` | `add-new-article-to-account` | Add a new article |
| POST | `/portals/{id}/categories` | `add-new-category-to-account` | Add a new category |

## Inboxes

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| DELETE | `/inbox_members` | `delete-agent-in-inbox` | Remove an Agent from Inbox |
| PATCH | `/inbox_members` | `update-agents-in-inbox` | Update Agents in Inbox |
| POST | `/inbox_members` | `add-new-agent-to-inbox` | Add a New Agent |
| GET | `/inbox_members/{inbox_id}` | `get-inbox-members` | List Agents in Inbox |
| GET | `/inboxes` | `listAllInboxes` | List all inboxes |
| POST | `/inboxes` | `inboxCreation` | Create an inbox |
| GET | `/inboxes/{id}` | `GetInbox` | Get an inbox |
| PATCH | `/inboxes/{id}` | `updateInbox` | Update Inbox |
| GET | `/inboxes/{id}/agent_bot` | `getInboxAgentBot` | Show Inbox Agent Bot |
| POST | `/inboxes/{id}/set_agent_bot` | `updateAgentBot` | Add or remove agent bot |

## Integrations

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/integrations/apps` | `get-details-of-all-integrations` | List all the Integrations |
| POST | `/integrations/hooks` | `create-an-integration-hook` | Create an integration hook |
| DELETE | `/integrations/hooks/{hook_id}` | `delete-an-integration-hook` | Delete an Integration Hook |
| PATCH | `/integrations/hooks/{hook_id}` | `update-an-integrations-hook` | Update an Integration Hook |

## Labels

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/labels` | `list-all-labels` | List all labels |
| POST | `/labels` | `create-a-label` | Create a label |
| DELETE | `/labels/{id}` | `delete-a-label` | Delete a label |
| GET | `/labels/{id}` | `get-details-of-a-single-label` | Get a label |
| PATCH | `/labels/{id}` | `update-a-label` | Update a label |

## Messages

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/conversations/{conversation_id}/messages` | `list-all-messages` | Get messages |
| POST | `/conversations/{conversation_id}/messages` | `create-a-new-message-in-a-conversation` | Create New Message |
| DELETE | `/conversations/{conversation_id}/messages/{message_id}` | `delete-a-message` | Delete a message |

## Profile

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/api/v1/profile` | `fetchProfile` | Fetch user profile |
| PUT | `/api/v1/profile` | `updateProfile` | Update user profile |

## Reports

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/reporting_events` | `get-account-reporting-events` | Account Reporting Events |
| GET | `/api/v2/accounts/{account_id}/reports` | `list-all-conversation-statistics` | Get Account reports |
| GET | `/api/v2/accounts/{account_id}/reports/conversations` | `get-account-conversation-metrics` | Account Conversation Metrics |
| GET | `/api/v2/accounts/{account_id}/reports/conversations/` | `get-agent-conversation-metrics` | Agent Conversation Metrics |
| GET | `/api/v2/accounts/{account_id}/reports/first_response_time_distribution` | `get-first-response-time-distribution` | Get first response time distribution by channel |
| GET | `/api/v2/accounts/{account_id}/reports/inbox_label_matrix` | `get-inbox-label-matrix` | Get inbox-label matrix report |
| GET | `/api/v2/accounts/{account_id}/reports/outgoing_messages_count` | `get-outgoing-messages-count` | Get outgoing messages count grouped by entity |
| GET | `/api/v2/accounts/{account_id}/reports/summary` | `list-all-conversation-statistics-summary` | Get Account reports summary |
| GET | `/api/v2/accounts/{account_id}/summary_reports/agent` | `get-agent-summary-report` | Get conversation statistics grouped by agent |
| GET | `/api/v2/accounts/{account_id}/summary_reports/channel` | `get-channel-summary-report` | Get conversation statistics grouped by channel type |
| GET | `/api/v2/accounts/{account_id}/summary_reports/inbox` | `get-inbox-summary-report` | Get conversation statistics grouped by inbox |
| GET | `/api/v2/accounts/{account_id}/summary_reports/team` | `get-team-summary-report` | Get conversation statistics grouped by team |

## Teams

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/teams` | `list-all-teams` | List all teams |
| POST | `/teams` | `create-a-team` | Create a team |
| DELETE | `/teams/{team_id}` | `delete-a-team` | Delete a team |
| GET | `/teams/{team_id}` | `get-details-of-a-single-team` | Get a team details |
| PATCH | `/teams/{team_id}` | `update-a-team` | Update a team |
| DELETE | `/teams/{team_id}/team_members` | `delete-agent-in-team` | Remove an Agent from Team |
| GET | `/teams/{team_id}/team_members` | `get-team-members` | List Agents in Team |
| PATCH | `/teams/{team_id}/team_members` | `update-agents-in-team` | Update Agents in Team |
| POST | `/teams/{team_id}/team_members` | `add-new-agent-to-team` | Add a New Agent |

## Webhooks

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/webhooks` | `list-all-webhooks` | List all webhooks |
| POST | `/webhooks` | `create-a-webhook` | Add a webhook |
| DELETE | `/webhooks/{webhook_id}` | `delete-a-webhook` | Delete a webhook |
| PATCH | `/webhooks/{webhook_id}` | `update-a-webhook` | Update a webhook object |
