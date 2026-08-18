# Scenario: Bulk messaging

Broadcast the same notice to several channels, DM a list of users, and attach a file. Assumes `setup` has run.

```bash
BASE="${MATTERMOST_API_URL%/}/api/v4"
AUTH=(-H "Authorization: Bearer ${MATTERMOST_TOKEN}" -H "Content-Type: application/json")
TEAM_ID=$(curl -s "${AUTH[@]}" "${BASE}/teams/name/engineering" | jq -r .id)
NOTE=":wrench: **Maintenance tonight 22:00–23:00 UTC.** Expect brief downtime."
```

## 1. Broadcast to several channels by name

```bash
for chan in general announcements support; do
  CH=$(curl -s "${AUTH[@]}" "${BASE}/teams/${TEAM_ID}/channels/name/${chan}" | jq -r .id)
  curl -s -X POST "${AUTH[@]}" -d "{\"channel_id\":\"${CH}\",\"message\":\"${NOTE}\"}" \
    "${BASE}/posts" | jq -r '"posted to \(.channel_id)"'
  sleep 0.3   # stay under the rate limit on large fan-outs
done
```

## 2. DM a list of users

```bash
ME=$(curl -s "${AUTH[@]}" "${BASE}/users/me" | jq -r .id)
for uname in alice bob carol; do
  UID=$(curl -s "${AUTH[@]}" "${BASE}/users/username/${uname}" | jq -r .id)
  DM=$(curl -s -X POST "${AUTH[@]}" -d "[\"${ME}\",\"${UID}\"]" \
    "${BASE}/channels/direct" | jq -r .id)
  curl -s -X POST "${AUTH[@]}" -d "{\"channel_id\":\"${DM}\",\"message\":\"${NOTE}\"}" \
    "${BASE}/posts" >/dev/null && echo "DMed ${uname}"
  sleep 0.3
done
```
For one combined group message instead of separate DMs, POST a 3–8 id array to `${BASE}/channels/group`.

## 3. Broadcast with an attached file

```bash
CH=$(curl -s "${AUTH[@]}" "${BASE}/teams/${TEAM_ID}/channels/name/announcements" | jq -r .id)
FID=$(curl -s -H "Authorization: Bearer ${MATTERMOST_TOKEN}" \
  -F "channel_id=${CH}" -F "files=@/path/maintenance-plan.pdf" \
  "${BASE}/files" | jq -r '.file_infos[0].id')
curl -s -X POST "${AUTH[@]}" -d "{
  \"channel_id\":\"${CH}\",\"message\":\"Full plan attached.\",\"file_ids\":[\"${FID}\"]
}" "${BASE}/posts" | jq '{id, file_ids}'
```

## Tips

- **Rate limits**: a small `sleep` between calls avoids `429`. If you hit it, read `X-Ratelimit-Reset` and back off (see `troubleshoot`).
- **Confirm scope first**: before a broadcast, show the user the resolved channel/user list and the message, then send — broadcasts are hard to recall.
- **Prefer an incoming webhook** for repeated automated notices to a single channel (see `integrations.md`).
