# Scenario: Onboard a team

Create a team, add channels, bring in existing users, email-invite new ones, and post a welcome. Assumes `setup` has run.

```bash
BASE="${MATTERMOST_API_URL%/}/api/v4"
AUTH=(-H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json")
```

## 1. Create the team

```bash
TEAM=$(curl -s -X POST "${AUTH[@]}" -d '{
  "name": "launch",
  "display_name": "Product Launch",
  "type": "O"
}' "${BASE}/teams")
TEAM_ID=$(echo "$TEAM" | jq -r .id)
echo "team: ${TEAM_ID}"
```
`type` is `O` (open — anyone can join) or `I` (invite-only). `name` is the URL slug (lowercase, no spaces).

## 2. Create channels in the team

```bash
for ch in "announcements:Announcements:O" "support:Support:O" "war-room:War Room:P"; do
  IFS=: read -r name disp type <<< "$ch"
  curl -s -X POST "${AUTH[@]}" -d "{
    \"team_id\":\"${TEAM_ID}\",\"name\":\"${name}\",\"display_name\":\"${disp}\",\"type\":\"${type}\"
  }" "${BASE}/channels" | jq -r '"created #\(.name) (\(.type))"'
done
```

## 3. Add existing users to the team

```bash
for uname in alice bob carol; do
  UID=$(curl -s "${AUTH[@]}" "${BASE}/users/username/${uname}" | jq -r .id)
  curl -s -X POST "${AUTH[@]}" -d "{\"team_id\":\"${TEAM_ID}\",\"user_id\":\"${UID}\"}" \
    "${BASE}/teams/${TEAM_ID}/members" | jq -r '"added \(.user_id)"'
done
```

## 4. Email-invite new people

```bash
curl -s -X POST "${AUTH[@]}" \
  -d '["dave@example.com","erin@example.com"]' \
  "${BASE}/teams/${TEAM_ID}/invite/email" | jq .
```

## 5. Add a user to a specific channel and make them channel admin

```bash
CH_ID=$(curl -s "${AUTH[@]}" "${BASE}/teams/${TEAM_ID}/channels/name/war-room" | jq -r .id)
UID=$(curl -s "${AUTH[@]}" "${BASE}/users/username/alice" | jq -r .id)
curl -s -X POST "${AUTH[@]}" -d "{\"user_id\":\"${UID}\"}" "${BASE}/channels/${CH_ID}/members" >/dev/null
curl -s -X PUT "${AUTH[@]}" -d '{"roles":"channel_user channel_admin"}' \
  "${BASE}/channels/${CH_ID}/members/${UID}/roles" | jq .
```

## 6. Post a welcome message

```bash
ANN=$(curl -s "${AUTH[@]}" "${BASE}/teams/${TEAM_ID}/channels/name/announcements" | jq -r .id)
curl -s -X POST "${AUTH[@]}" -d "{
  \"channel_id\":\"${ANN}\",
  \"message\":\":tada: Welcome to **Product Launch**! Use #support for questions.\"
}" "${BASE}/posts" | jq '{id, message}'
```
