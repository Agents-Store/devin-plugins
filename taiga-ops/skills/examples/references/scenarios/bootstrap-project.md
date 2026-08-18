# Scenario: Bootstrap a project

Stand up a new Taiga project, invite the team, and confirm the board is ready. Assumes `setup` has set `TAIGA_API_URL` and `TAIGA_AUTH_TOKEN`.

```bash
BASE="${TAIGA_API_URL%/}/api/v1"
AUTH=(-H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}" -H "Content-Type: application/json")
```

## 1. Pick a template (optional)

```bash
curl -s "${AUTH[@]}" "${BASE}/project-templates" | jq -r '.[] | "\(.id)\t\(.slug)\t\(.name)"'
# e.g. scrum -> id 1, kanban -> id 2
```

## 2. Create the project

```bash
PROJECT=$(curl -s -X POST "${AUTH[@]}" \
  -d '{"name":"Apollo","description":"Customer portal","is_private":true,"creation_template":1}' \
  "${BASE}/projects")
PID=$(echo "$PROJECT" | jq -r .id)
echo "Created project $PID ($(echo "$PROJECT" | jq -r .slug))"
```

## 3. Invite the team

Find role IDs, then bulk-invite by email.

```bash
curl -s "${AUTH[@]}" "${BASE}/roles?project=${PID}" | jq -r '.[] | "\(.id)\t\(.name)"'
# say Developer -> 12, Product Owner -> 10

curl -s -X POST "${AUTH[@]}" -d "{
  \"project\": ${PID},
  \"bulk_memberships\": [
    {\"role_id\": 12, \"username\": \"dev1@example.com\"},
    {\"role_id\": 12, \"username\": \"dev2@example.com\"},
    {\"role_id\": 10, \"username\": \"po@example.com\"}
  ]
}" "${BASE}/memberships/bulk_create" | jq 'length'
```

## 4. Tune the board (optional)

Add a status and a tag color.

```bash
curl -s -X POST "${AUTH[@]}" \
  -d "{\"project\":${PID},\"name\":\"Blocked\",\"color\":\"#e44057\"}" \
  "${BASE}/userstory-statuses" | jq '{id,name}'

curl -s -X POST "${AUTH[@]}" \
  -d '{"tag":"urgent","color":"#ff0000"}' \
  "${BASE}/projects/${PID}/create_tag" >/dev/null
```

## 5. Confirm

```bash
curl -s "${AUTH[@]}" "${BASE}/projects/${PID}/stats" | jq '{total_memberships, total_milestones, total_userstories: .total_userstories}'
```

The project is ready for backlog and sprint planning (see `sprint-planning.md`).
