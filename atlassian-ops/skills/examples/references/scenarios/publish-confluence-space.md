# Scenario: Publish a Confluence space

Stand up a space, add a parent page and a child, update the parent (with the version bump), label it, and list the result. Assumes `setup` ran.

```bash
CONF="${ATLASSIAN_SITE_URL%/}/wiki/api/v2"
AUTH=(-u "${ATLASSIAN_EMAIL}:${ATLASSIAN_API_TOKEN}" -H "Accept: application/json")
JSON=(-H "Content-Type: application/json")
```

## 1. Create the space (or reuse an existing key)

```bash
SPACE_ID=$(curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${CONF}/spaces" \
  -d '{"key":"HANDBOOK","name":"Team Handbook"}' | jq -r '.id')
# If it already exists, resolve the id instead:
# SPACE_ID=$(curl -s "${AUTH[@]}" "${CONF}/spaces?keys=HANDBOOK" | jq -r '.results[0].id')
echo "Space id: ${SPACE_ID}"
```

## 2. Create a parent page

```bash
PARENT_ID=$(curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${CONF}/pages" -d "{
  \"spaceId\": \"${SPACE_ID}\",
  \"status\": \"current\",
  \"title\": \"Welcome\",
  \"body\": {\"representation\": \"storage\", \"value\": \"<h1>Welcome</h1><p>Start here.</p>\"}
}" | jq -r '.id')
echo "Parent page: ${PARENT_ID}"
```

## 3. Create a child page under it

```bash
CHILD_ID=$(curl -s "${AUTH[@]}" "${JSON[@]}" -X POST "${CONF}/pages" -d "{
  \"spaceId\": \"${SPACE_ID}\",
  \"status\": \"current\",
  \"title\": \"Engineering Onboarding\",
  \"parentId\": \"${PARENT_ID}\",
  \"body\": {\"representation\": \"storage\", \"value\": \"<p>Day-one setup steps.</p>\"}
}" | jq -r '.id')
echo "Child page: ${CHILD_ID}"
```

## 4. Update the parent (read version → write version+1)

```bash
VER=$(curl -s "${AUTH[@]}" "${CONF}/pages/${PARENT_ID}?body-format=storage" | jq -r '.version.number')
curl -s "${AUTH[@]}" "${JSON[@]}" -X PUT "${CONF}/pages/${PARENT_ID}" -d "{
  \"id\": \"${PARENT_ID}\",
  \"status\": \"current\",
  \"title\": \"Welcome\",
  \"version\": {\"number\": $((VER+1)), \"message\": \"Add onboarding link\"},
  \"body\": {\"representation\": \"storage\", \"value\": \"<h1>Welcome</h1><p>See <strong>Engineering Onboarding</strong> to get started.</p>\"}
}" | jq '{id, version: .version.number}'
```

## 5. Label the parent (v1 endpoint — labels aren't writable in v2)

```bash
curl -s "${AUTH[@]}" "${JSON[@]}" -X POST \
  "${ATLASSIAN_SITE_URL%/}/wiki/rest/api/content/${PARENT_ID}/label" \
  -d '[{"prefix":"global","name":"handbook"}]' >/dev/null
curl -s "${AUTH[@]}" "${CONF}/pages/${PARENT_ID}/labels" | jq '.results[].name'
```

## 6. List the space's pages

```bash
curl -s "${AUTH[@]}" "${CONF}/pages?space-id=${SPACE_ID}&sort=-modified-date" \
  | jq -r '.results[] | "\(.id)  \(.title)"'
```

## Result

A space with a parent page, a nested child, a versioned edit, and a label — the skeleton of a knowledge base. Note the **read-then-write version bump** in step 4: that's the single most common Confluence update mistake.
