# Scenario: Reporting & export

Pull the numbers a status update needs, then take a full backup. Assumes `setup` has run.

```bash
BASE="${TAIGA_API_URL%/}/api/v1"
AUTH=(-H "Authorization: Bearer ${TAIGA_AUTH_TOKEN}")
PID=$(curl -s "${AUTH[@]}" "${BASE}/resolver?project=apollo" | jq -r .project)
```

## 1. Search across the project

```bash
curl -s "${AUTH[@]}" "${BASE}/search?project=${PID}&text=payment" \
  | jq '{userstories: (.userstories|length), tasks: (.tasks|length), issues: (.issues|length)}'
```

## 2. Targeted lists with filters

```bash
# Open issues assigned to user 15
curl -s "${AUTH[@]}" "${BASE}/issues?project=${PID}&assigned_to=15&status__is_closed=false" \
  | jq -r '.[] | "#\(.ref) [\(.severity)] \(.subject)"'

# Stories left in the current sprint (milestone 12) that aren't closed
curl -s "${AUTH[@]}" "${BASE}/userstories?project=${PID}&milestone=12&status__is_closed=false" \
  | jq -r '.[] | "#\(.ref) \(.subject)"'
```

## 3. Project & sprint statistics

```bash
curl -s "${AUTH[@]}" "${BASE}/projects/${PID}/stats"        | jq '{total_userstories, closed_points, defined_points, assigned_points}'
curl -s "${AUTH[@]}" "${BASE}/projects/${PID}/issues_stats" | jq '{total_issues, opened_issues, closed_issues}'
curl -s "${AUTH[@]}" "${BASE}/milestones/12/stats"          | jq '{total_points, completed_points, completed_userstories}'
```

## 4. Count totals using pagination headers

```bash
curl -s -D - -o /dev/null "${AUTH[@]}" "${BASE}/issues?project=${PID}" | grep -i 'x-pagination-count'
```

## 5. Full project export (backup)

```bash
DUMP=$(curl -s "${AUTH[@]}" "${BASE}/exporter/${PID}")
echo "$DUMP" | jq '{export_id, url}'
# Poll the returned url until the gzip dump is ready, then download it.
```
