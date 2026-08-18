# Scenario: Admin audit & health snapshot

Pull a server health, usage, and activity snapshot, then kick off a compliance export. **Requires the System Admin role.** Assumes `setup` has run.

```bash
BASE="${MATTERMOST_API_URL%/}/api/v4"
AUTH=(-H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json")
# Confirm admin rights first
curl -s "${AUTH[@]}" "${BASE}/users/me" | jq '{username, roles}'   # expect system_admin in roles
```

## 1. Server health

```bash
curl -s "${BASE}/system/ping?get_server_status=true" | jq .          # status, database, filestore
curl -s "${AUTH[@]}" "${BASE}/cluster/status" | jq .                  # HA nodes (if clustered)
```

## 2. Usage & user counts

```bash
curl -s "${AUTH[@]}" "${BASE}/users/stats" | jq .                     # total users
curl -s "${AUTH[@]}" "${BASE}/usage/posts" | jq .                     # total posts
curl -s "${AUTH[@]}" "${BASE}/usage/storage" | jq .                   # bytes of file storage
curl -s "${AUTH[@]}" "${BASE}/usage/teams" | jq .                     # team count
```

## 3. Aggregate analytics

```bash
curl -s "${AUTH[@]}" "${BASE}/analytics/old?name=standard" \
  | jq -r '.[] | "\(.name): \(.value)"'
# -> unique_user_count, team_count, channel_open_count, channel_private_count, post_count, ...
```

## 4. Channel counts per team

```bash
for tid in $(curl -s "${AUTH[@]}" "${BASE}/teams?per_page=200" | jq -r '.[].id'); do
  name=$(curl -s "${AUTH[@]}" "${BASE}/teams/${tid}" | jq -r .display_name)
  stats=$(curl -s "${AUTH[@]}" "${BASE}/teams/${tid}/stats" | jq -c '{total_member_count, active_member_count}')
  echo "${name}: ${stats}"
done
```

## 5. Recent audit records

```bash
curl -s "${AUTH[@]}" "${BASE}/audits?per_page=50" \
  | jq -r '.[] | "\(.create_at)\t\(.user_id)\t\(.action)"' | head -50
```

## 6. Start a compliance export (Enterprise)

```bash
curl -s -X POST "${AUTH[@]}" -d '{
  "desc": "Q2 review export",
  "start_at": 1714521600000,
  "end_at": 1719792000000
}' "${BASE}/compliance/reports" | jq '{id, status}'
# Poll status, then download:
# curl -s "${AUTH[@]}" "${BASE}/compliance/reports/<id>" | jq .status
# curl -s "${AUTH[@]}" "${BASE}/compliance/reports/<id>/download" -o compliance.zip
```

> Reads (stats/analytics/audits) are safe. Treat the compliance export, `PUT /config`, and any `/data_retention` write as high-impact — state what you're about to run and confirm with the user first.
