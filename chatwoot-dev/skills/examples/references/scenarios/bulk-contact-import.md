# Scenario: Bulk import contacts with custom attributes

Goal: create many contacts through the Application API, tag them with custom attributes, and
search them back — handling pagination correctly. Uses `api-reference` (Contacts) and the
pagination rules in `pagination-errors.md`.

## 1. Create contacts from a CSV

```bash
# contacts.csv: name,email,phone,plan
tail -n +2 contacts.csv | while IFS=, read -r name email phone plan; do
  curl -s -X POST \
    -H "api_access_token: ${CHATWOOT_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg n "$name" --arg e "$email" --arg p "$phone" --arg pl "$plan" \
          '{name:$n, email:$e, phone_number:$p, custom_attributes:{plan:$pl}}')" \
    "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/contacts" \
    | jq -r '.payload.contact.id // .id'
  sleep 0.2   # be gentle; back off on 429
done
```

`custom_attributes` keys must already exist as contact custom-attribute definitions
(create them via the `custom_attribute_definitions` endpoint — see `application-api.md`).

## 2. Page through all contacts

```bash
page=1
while :; do
  resp=$(curl -s -H "api_access_token: ${CHATWOOT_API_KEY}" \
    "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/contacts?page=${page}")
  count=$(echo "$resp" | jq '.payload | length')
  [ "$count" -eq 0 ] && break
  echo "$resp" | jq -r '.payload[] | "\(.id)\t\(.name)\t\(.email)"'
  page=$((page+1))
done
```

## 3. Search and filter

```bash
# Quick text search
curl -s -H "api_access_token: ${CHATWOOT_API_KEY}" \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/contacts/search?q=jane@example.com" | jq '.payload[].id'

# Structured filter (POST body with attribute/operator/values) — see contacts filter endpoint
curl -s -X POST \
  -H "api_access_token: ${CHATWOOT_API_KEY}" -H "Content-Type: application/json" \
  -d '{"payload":[{"attribute_key":"plan","filter_operator":"equal_to","values":["pro"],"query_operator":null,"custom_attribute_type":"contact_attribute"}]}' \
  "${CHATWOOT_BASE_URL}/api/v1/accounts/${CHATWOOT_ACCOUNT_ID}/contacts/filter" | jq '.payload | length'
```

## Notes

- Check the exact create/response shape in `openapi/application_swagger.json` (the create
  response nests the contact under `payload.contact`).
- For large imports, add exponential backoff on `429` rather than a fixed `sleep`.
