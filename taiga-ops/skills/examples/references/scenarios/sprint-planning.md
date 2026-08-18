# Scenario: Sprint planning

Create a sprint, fill it with stories, break stories into tasks, and read progress. Assumes `setup` has run.

```bash
BASE="${TAIGA_API_URL%/}/api/v1"
AUTH=(-H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json")
PID=$(curl -s "${AUTH[@]}" "${BASE}/resolver?project=apollo" | jq -r .project)
```

## 1. Create the sprint

```bash
SPRINT=$(curl -s -X POST "${AUTH[@]}" -d "{
  \"project\": ${PID},
  \"name\": \"Sprint 4\",
  \"estimated_start\": \"2026-06-01\",
  \"estimated_finish\": \"2026-06-14\"
}" "${BASE}/milestones")
MID=$(echo "$SPRINT" | jq -r .id)
```

## 2. Create stories straight into the sprint

```bash
for S in "Reset password flow" "Email verification" "Account lockout"; do
  curl -s -X POST "${AUTH[@]}" \
    -d "{\"project\":${PID},\"subject\":\"$S\",\"milestone\":${MID}}" \
    "${BASE}/userstories" | jq -r '.ref as $r | .subject as $s | "#\($r) \($s)"'
done
```

Already-existing backlog stories can be moved in bulk instead:

```bash
curl -s -X POST "${AUTH[@]}" -d "{
  \"project_id\": ${PID}, \"milestone_id\": ${MID},
  \"bulk_stories\": [{\"us_id\": 1234, \"order\": 1}, {\"us_id\": 1235, \"order\": 2}]
}" "${BASE}/userstories/bulk_update_milestone" | jq 'length'
```

## 3. Break a story into tasks

```bash
curl -s -X POST "${AUTH[@]}" -d "{
  \"project_id\": ${PID}, \"us_id\": 1234, \"milestone_id\": ${MID},
  \"bulk_tasks\": \"Design schema\nWrite migration\nAdd tests\"
}" "${BASE}/tasks/bulk_create" | jq -r '.[] | "#\(.ref) \(.subject)"'
```

## 4. Estimate a story (set points)

```bash
curl -s "${AUTH[@]}" "${BASE}/points?project=${PID}" | jq -r '.[] | "\(.id)\t\(.name)"'   # role->point map keys
US=$(curl -s "${AUTH[@]}" "${BASE}/userstories/1234")
VER=$(echo "$US" | jq -r .version)
# points is a map of {roleId: pointId}
curl -s -X PATCH "${AUTH[@]}" \
  -d "{\"points\": {\"12\": 5}, \"version\": ${VER}}" \
  "${BASE}/userstories/1234" | jq '{id, total_points}'
```

## 5. Track progress

```bash
curl -s "${AUTH[@]}" "${BASE}/milestones/${MID}/stats" | jq '{
  total_points, completed_points, total_userstories: .total_userstories, completed_userstories
}'
```
