# Scenario: Plan an Epic with child Stories

Create an Epic, add Stories under it, and report on the epic's children. Assumes `setup` ran. Adjust the project key `PROJ` and summaries.

```bash
JIRA="${ATLASSIAN_SITE_URL%/}/rest/api/3"
AUTH=(-u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json")
JSON=(-H "Content-Type: application/json")
PROJ="PROJ"
```

## 1. Create the Epic

```bash
EPIC_KEY=$(curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/issue" -d "{
  \"fields\": {
    \"project\": {\"key\": \"${PROJ}\"},
    \"issuetype\": {\"name\": \"Epic\"},
    \"summary\": \"Checkout revamp\",
    \"description\": {\"type\":\"doc\",\"version\":1,\"content\":[
      {\"type\":\"paragraph\",\"content\":[{\"type\":\"text\",\"text\":\"Rebuild the checkout flow for Q3.\"}]}]}
  }
}" | jq -r '.key')
echo "Epic: ${EPIC_KEY}"
```

> If `Epic` isn't a valid type in your project, check `GET /issue/createmeta/${PROJ}/issuetypes`.

## 2. Create Stories linked to the Epic

Team-managed and company-managed projects differ in how a child links to its epic. The portable way is the **parent** field:

```bash
for S in "Cart page redesign" "Payment provider integration" "Order confirmation email"; do
  curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/issue" -d "{
    \"fields\": {
      \"project\": {\"key\": \"${PROJ}\"},
      \"issuetype\": {\"name\": \"Story\"},
      \"summary\": \"${S}\",
      \"parent\": {\"key\": \"${EPIC_KEY}\"}
    }
  }" | jq -r '"  created \(.key)  (\(.fields.summary // "'"$S"'"))"'
done
```

> If `parent` is rejected on a company-managed project, the epic link is a custom field instead (often `Epic Link`, id like `customfield_10014`). Find it with `GET /issue/createmeta/${PROJ}/issuetypes/<storyTypeId>` and set `{"customfield_10014":"${EPIC_KEY}"}`.

## 3. Report on the Epic's children

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/search/jql" -d "{
  \"jql\": \"parent = ${EPIC_KEY} ORDER BY created ASC\",
  \"fields\": [\"summary\",\"status\",\"assignee\"],
  \"maxResults\": 100
}" | jq -r '.issues[] | "\(.key)  [\(.fields.status.name)]  \(.fields.summary)"'
```

## Result

An Epic with three Stories beneath it, plus a status table of its children — the backbone of a sprint-ready backlog. Next: estimate, assign (`PUT /issue/{key}/assignee`), or pull into a sprint (Agile API `/rest/agile/1.0/sprint/{id}/issue`).
