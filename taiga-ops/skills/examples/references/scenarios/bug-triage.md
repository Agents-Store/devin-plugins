# Scenario: Bug triage

File an issue with the right classifiers, assign and document it, then resolve. Assumes `setup` has run.

```bash
BASE="${TAIGA_API_URL%/}/api/v1"
AUTH=(-H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json")
PID=$(curl -s "${AUTH[@]}" "${BASE}/resolver?project=apollo" | jq -r .project)
```

## 1. Discover this project's classifier IDs

```bash
curl -s "${AUTH[@]}" "${BASE}/issues/filters_data?project=${PID}" \
  | jq '{statuses: [.statuses[]|{id,name}], types: [.types[]|{id,name}], priorities: [.priorities[]|{id,name}], severities: [.severities[]|{id,name}]}'
```

## 2. Create the issue

```bash
ISSUE=$(curl -s -X POST "${AUTH[@]}" -d "{
  \"project\": ${PID},
  \"subject\": \"Checkout returns 500 on retry\",
  \"description\": \"Repro: submit payment, click retry -> 500.\",
  \"type\": 1, \"severity\": 5, \"priority\": 4
}" "${BASE}/issues")
IID=$(echo "$ISSUE" | jq -r .id)
echo "Filed issue #$(echo "$ISSUE" | jq -r .ref) (id ${IID})"
```

## 3. Assign, comment, attach (all need the current version)

```bash
get_ver () { curl -s "${AUTH[@]}" "${BASE}/issues/${IID}" | jq -r .version; }

# Assign to user 15
curl -s -X PATCH "${AUTH[@]}" -d "{\"assigned_to\":15,\"version\":$(get_ver)}" "${BASE}/issues/${IID}" >/dev/null
# Comment
curl -s -X PATCH "${AUTH[@]}" -d "{\"comment\":\"Reproduced on staging. Looks like a double-charge guard.\",\"version\":$(get_ver)}" "${BASE}/issues/${IID}" >/dev/null
# Attach a screenshot (multipart — no JSON Content-Type here)
curl -s -X POST -H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" \
  -F "project=${PID}" -F "object_id=${IID}" -F "attached_file=@./checkout-500.png" \
  "${BASE}/issues/attachments" | jq '{id, name}'
```

## 4. Resolve

```bash
CLOSED=$(curl -s "${AUTH[@]}" "${BASE}/issue-statuses?project=${PID}" | jq -r '.[]|select(.is_closed)|.id' | head -1)
curl -s -X PATCH "${AUTH[@]}" -d "{\"status\":${CLOSED},\"version\":$(get_ver)}" "${BASE}/issues/${IID}" | jq '{id, status, is_closed}'
```

## 5. Read the trail

```bash
curl -s "${AUTH[@]}" "${BASE}/history/issue/${IID}" | jq -r '.[] | select(.comment!="") | .comment'
```
