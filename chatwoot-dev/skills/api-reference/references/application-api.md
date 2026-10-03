# Chatwoot Application API

Account-scoped agent/admin API. Auth: `api-access-token` header (user access token; upstream's OpenAPI spells it `api_access_token`, see `pagination-errors.md` → Authentication for why to send the hyphen form). Base: `${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}`.

Authoritative schemas: `openapi/application_swagger.json` (75 paths, 124 operations). Grep it for request bodies, query params, and response shapes.

Spec source: `chatwoot/chatwoot` `develop` at commit `843385f` (2026-10-02), `swagger/tag_groups/application_swagger.json`. The latest release, v4.18.0, ships 122 operations; the two extra ones (`GET /portals/{id}`, `POST /conversations/{id}/update_last_seen`) exist only on `develop` until the next release. Match the operation to your instance version before relying on it.

```bash
jq -r '.paths | keys[]' openapi/application_swagger.json
```

## Recent additions (since the 112-operation snapshot of v4.15)

| In spec since | Method | Path | Operation | What it is for |
|-------|--------|------|-----------|----------------|
| v4.16.0 | GET, PATCH | `/branded_email_layout` | `getAccountBrandedEmailLayout`, `updateAccountBrandedEmailLayout` | Account-wide Liquid HTML layout used as the fallback for branded email replies |
| v4.17.0 | GET | `/inboxes/{id}/message_templates` | `listWhatsappMessageTemplates` | List the cached message templates of a WhatsApp Cloud API or Twilio WhatsApp inbox |
| v4.17.0 | POST | `/conversations/{conversation_id}/destroy_custom_attributes` | `destroy-custom-attributes-of-a-conversation` | Remove custom attribute keys from a conversation |
| v4.17.1 | PATCH | `/conversations/{conversation_id}/messages/{message_id}` | `update-message-status` | Report `sent` / `delivered` / `read` / `failed` for a message in an API channel inbox |
| v4.18.0 | GET, POST | `/campaigns` | `list-campaigns`, `create-campaign` | List and create campaigns |
| v4.18.0 | GET, PATCH, DELETE | `/campaigns/{id}` | `get-campaign`, `update-campaign`, `delete-campaign` | Read, change or remove one campaign |
| `develop` only | GET | `/portals/{id}` | `get-details-of-a-single-portal` | Details of one Help Center portal |
| `develop` only | POST | `/conversations/{conversation_id}/update_last_seen` | `conversationUpdateLastSeen` | Mark a conversation as seen so the unread bubble clears in the agent UI |

The "In spec since" column was derived by diffing the upstream swagger at each release tag (v4.15.0 to v4.18.0) against `develop`.

### Campaigns

`/campaigns` needs an **account administrator** token and API access enabled for the account (`401` if the user is not an administrator, `403` if API access is off). The list is an unpaginated array. Channel support: Website (ongoing campaign), Twilio SMS / SMS and WhatsApp Cloud (one-off campaign). Chatwoot derives `campaign_type` (`ongoing` or `one_off`) and `campaign_status` (`active`, `processing`, `completed`) from the inbox; you do not send them.

Body is always wrapped as `{"campaign": {...}}`. Field rules, straight from the spec (`campaign_fields`):

| Field | Applies to | Rule |
|-------|-----------|------|
| `title`, `inbox_id`, `message` | all | required on create |
| `description`, `sender_id` | all | optional; `sender_id` is a user id in this account |
| `audience` | SMS, WhatsApp | `[{"type":"Label","id":<label id>}]`, at least one label; contacts with **any** selected label receive the campaign. Omit on update to keep the existing audience |
| `scheduled_at` | SMS, WhatsApp | ISO 8601 timestamp with timezone; defaults to now when omitted, so the next scheduler run sends it. Responses return Unix seconds |
| `template_params` | WhatsApp | `{"name","language","processed_params":{...}}`, template must exist in the inbox's `message_templates` |
| `trigger_rules`, `trigger_only_during_business_hours`, `enabled` | Website | `trigger_rules.url` required; `enabled` does **not** cancel a scheduled one-off campaign |

Completed campaigns cannot be updated. A successful create response does not confirm delivery.

```bash
# Schedule an SMS campaign for every contact labelled with label 5 (sends to real customers - confirm first)
curl -s -X POST \
  -H "api-access-token: ${CHATWOOT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"campaign":{"title":"January announcement","inbox_id":12,
       "message":"Our January offers are here!",
       "scheduled_at":"2027-01-15T10:00:00Z",
       "audience":[{"type":"Label","id":5}]}}' \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/campaigns" | jq .

# Read back status and timing
curl -s -H "api-access-token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/campaigns/42" \
  | jq '{id, title, campaign_status, campaign_type, scheduled_at, started_at, completed_at}'
```

### WhatsApp message templates

`GET /inboxes/{id}/message_templates` returns `{"payload": [...], "meta": {"last_sync_attempt_at": ...}}` for a WhatsApp Cloud API or Twilio WhatsApp inbox. The templates are the locally **cached** copy, so `meta.last_sync_attempt_at` tells you how stale they are. Filter with `?name=<exact template name>`. Errors: `404` unknown inbox, `403` no access, `422` the inbox is not a WhatsApp inbox. Each template is a free-form object (`additionalProperties: true` in the spec) - inspect a real response before coding against its fields.

```bash
curl -s -H "api-access-token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/inboxes/15/message_templates?name=order_shipped" \
  | jq '{synced: .meta.last_sync_attempt_at, templates: .payload}'
```

To send one, post a message to the conversation with `template_params` (`name`, `category`, `language`, `processed_params`; schema `conversation_message_create_payload` in the spec). For a campaign, put the same name and language into `campaign.template_params`.

### Smaller additions

- `PATCH .../messages/{message_id}` body `{"status":"sent|delivered|read|failed","external_error":"..."}`: **API channel inboxes only** (`403` otherwise). A message already `read` cannot move back to `delivered`; `external_error` is stored only when `status` is `failed`.
- `POST .../conversations/{id}/destroy_custom_attributes` body `{"custom_attributes":["order_id"]}` returns the remaining custom attributes.
- `PATCH /branded_email_layout` body `{"branded_email_layout":"<html>...{{ content_for_layout }}...</html>"}` (max 262,144 characters); `null` or blank removes the account override.

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

## Campaigns

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/campaigns` | `list-campaigns` | List campaigns |
| POST | `/campaigns` | `create-campaign` | Create a campaign |
| DELETE | `/campaigns/{id}` | `delete-campaign` | Delete a campaign |
| GET | `/campaigns/{id}` | `get-campaign` | Get a campaign |
| PATCH | `/campaigns/{id}` | `update-campaign` | Update a campaign |

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
| POST | `/conversations/{conversation_id}/destroy_custom_attributes` | `destroy-custom-attributes-of-a-conversation` | Destroy Custom Attributes |
| GET | `/conversations/{conversation_id}/labels` | `list-all-labels-of-a-conversation` | List Labels |
| POST | `/conversations/{conversation_id}/labels` | `conversation-add-labels` | Add Labels |
| GET | `/conversations/{conversation_id}/reporting_events` | `get-conversation-reporting-events` | Conversation Reporting Events |
| POST | `/conversations/{conversation_id}/toggle_priority` | `toggle-priority-of-a-conversation` | Toggle Priority |
| POST | `/conversations/{conversation_id}/toggle_status` | `toggle-status-of-a-conversation` | Toggle Status |
| POST | `/conversations/{conversation_id}/toggle_typing_status` | `toggle-typing-status-of-a-conversation` | Toggle Typing Status |
| POST | `/conversations/{conversation_id}/update_last_seen` | `conversationUpdateLastSeen` | Update Last Seen |

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
| GET | `/portals/{id}` | `get-details-of-a-single-portal` | Get a portal details |
| PATCH | `/portals/{id}` | `update-portal-to-account` | Update a portal |
| POST | `/portals/{id}/articles` | `add-new-article-to-account` | Add a new article |
| POST | `/portals/{id}/categories` | `add-new-category-to-account` | Add a new category |

## Inboxes

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| GET | `/branded_email_layout` | `getAccountBrandedEmailLayout` | Get account branded email layout |
| PATCH | `/branded_email_layout` | `updateAccountBrandedEmailLayout` | Update account branded email layout |
| DELETE | `/inbox_members` | `delete-agent-in-inbox` | Remove an Agent from Inbox |
| PATCH | `/inbox_members` | `update-agents-in-inbox` | Update Agents in Inbox |
| POST | `/inbox_members` | `add-new-agent-to-inbox` | Add a New Agent |
| GET | `/inbox_members/{inbox_id}` | `get-inbox-members` | List Agents in Inbox |
| GET | `/inboxes` | `listAllInboxes` | List all inboxes |
| POST | `/inboxes` | `inboxCreation` | Create an inbox |
| GET | `/inboxes/{id}` | `GetInbox` | Get an inbox |
| PATCH | `/inboxes/{id}` | `updateInbox` | Update Inbox |
| GET | `/inboxes/{id}/agent_bot` | `getInboxAgentBot` | Show Inbox Agent Bot |
| GET | `/inboxes/{id}/message_templates` | `listWhatsappMessageTemplates` | List WhatsApp message templates |
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
| PATCH | `/conversations/{conversation_id}/messages/{message_id}` | `update-message-status` | Update message status |

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
