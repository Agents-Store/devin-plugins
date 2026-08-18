# Scenario: Issue lifecycle (create → comment → transition → Done)

Drive one issue through its workflow. Assumes `setup` ran.

```bash
JIRA="${ATLASSIAN_SITE_URL%/}/rest/api/3"
AUTH=(-u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json")
JSON=(-H "Content-Type: application/json")
PROJ="PROJ"
```

## 1. Create the issue

```bash
KEY=$(curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/issue" -d "{
  \"fields\": {
    \"project\": {\"key\": \"${PROJ}\"},
    \"issuetype\": {\"name\": \"Bug\"},
    \"summary\": \"Login times out after 30s\",
    \"description\": {\"type\":\"doc\",\"version\":1,\"content\":[
      {\"type\":\"paragraph\",\"content\":[{\"type\":\"text\",\"text\":\"Intermittent on prod since the 2.1 deploy.\"}]}]}
  }
}" | jq -r '.key')
echo "Created ${KEY}"
```

## 2. Add a comment (ADF)

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/issue/${KEY}/comment" -d '{
  "body": {"type":"doc","version":1,"content":[
    {"type":"paragraph","content":[{"type":"text","text":"Reproduced locally — root cause is a stale connection pool."}]}]}
}' | jq '{id, created}'
```

## 3. Discover available transitions

```bash
curl -s "${AUTH[@]}" "${JIRA}/issue/${KEY}/transitions" \
  | jq -r '.transitions[] | "\(.id)  \(.name)  -> \(.to.name)"'
```

## 4. Move to "In Progress", then "Done"

```bash
move_to () {
  local name="$1"
  local tid
  tid=$(curl -s "${AUTH[@]}" "${JIRA}/issue/${KEY}/transitions" \
    | jq -r --arg n "$name" '.transitions[] | select(.name==$n) | .id')
  if [ -z "$tid" ] || [ "$tid" = "null" ]; then
    echo "No transition named '$name' from the current status"; return 1
  fi
  curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/issue/${KEY}/transitions" \
    -d "{\"transition\":{\"id\":\"${tid}\"}}"
  echo "→ ${name}"
}
move_to "In Progress"
move_to "Done"
```

## 5. Confirm final state

```bash
curl -s "${AUTH[@]}" "${JIRA}/issue/${KEY}?fields=summary,status,resolution" \
  | jq '{key: .key, status: .fields.status.name, resolution: .fields.resolution.name}'
```

## Result

A bug created with an ADF description, an ADF comment, and walked through its real workflow transitions to `Done`. Transition names depend on the project's workflow — always read them from step 3 rather than assuming `In Progress`/`Done` exist.
