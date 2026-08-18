# Scenario: Release notes in Confluence from Jira

Cross-product workflow: query the issues shipped in a fix version from Jira, then publish a formatted release-notes page in Confluence. Assumes `setup` ran.

```bash
JIRA="${ATLASSIAN_SITE_URL%/}/rest/api/3"
CONF="${ATLASSIAN_SITE_URL%/}/wiki/api/v2"
AUTH=(-u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json")
JSON=(-H "Content-Type: application/json")
PROJ="PROJ"
VERSION="1.2.0"
SPACE_KEY="HANDBOOK"
```

## 1. Pull the done issues for the fix version (Jira)

```bash
ISSUES_JSON=$(curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${JIRA}/search/jql" -d "{
  \"jql\": \"project = ${PROJ} AND fixVersion = \\\"${VERSION}\\\" AND statusCategory = Done ORDER BY issuetype, key\",
  \"fields\": [\"summary\",\"issuetype\",\"key\"],
  \"maxResults\": 200
}")
echo "$ISSUES_JSON" | jq -r '.issues | length | "Done issues: \(.)"'
```

## 2. Build a Confluence storage-format body from the results

```bash
SITE="${ATLASSIAN_SITE_URL%/}"
ROWS=$(echo "$ISSUES_JSON" | jq -r --arg site "$SITE" '
  .issues[]
  | "<li><a href=\"\($site)/browse/\(.key)\">\(.key)</a> — \(.fields.summary) <em>(\(.fields.issuetype.name))</em></li>"' )
BODY="<h1>Release Notes — ${VERSION}</h1><p>Shipped issues:</p><ul>${ROWS}</ul>"
```

## 3. Resolve the space id and create the page (Confluence)

```bash
SPACE_ID=$(curl -s "${AUTH[@]}" "${CONF}/spaces?keys=${SPACE_KEY}" | jq -r '.results[0].id')
# jq -Rs safely JSON-encodes the HTML body string
BODY_JSON=$(printf '%s' "$BODY" | jq -Rs '.')
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${CONF}/pages" -d "{
  \"spaceId\": \"${SPACE_ID}\",
  \"status\": \"current\",
  \"title\": \"Release Notes ${VERSION}\",
  \"body\": {\"representation\": \"storage\", \"value\": ${BODY_JSON}}
}" | jq '{id, title, url: ._links.webui}'
```

## Result

A Confluence "Release Notes 1.2.0" page whose body is generated from a live Jira JQL query — one token, two products. Re-run with a new `VERSION` each release; to update an existing page instead of creating a new one, switch step 3 to the read-version → `PUT /pages/{id}` flow (see `publish-confluence-space.md`).
