# Jira Plans & Teams (Advanced Roadmaps)

Advanced Roadmaps "Plans" (Jira Premium) and the teams attached to them. Base `${ATLASSIAN_SITE_URL%/}/rest/api/3`.

## Plans

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /plans/plan` | List plans (`getPlans`), paginated with a cursor. |
| `POST /plans/plan` | Create a plan (`createPlan`). Body includes `name`, `issueSources` (board/project/filter), `scheduling`, `permissions`. |
| `GET /plans/plan/{planId}` | Get a plan (`getPlan`). |
| `PUT /plans/plan/{planId}` | Update a plan (`updatePlan`) — JSON Patch style operations. |
| `PUT /plans/plan/{planId}/archive` · `/trash` | Archive / trash a plan. **Confirm first.** |
| `POST /plans/plan/{planId}/duplicate` | Duplicate a plan (`duplicatePlan`). Body `{"name":"…"}`. |

## Teams in a plan

| Method | Purpose & key fields |
|--------|----------------------|
| `GET /plans/plan/{planId}/team` | List teams in a plan (`getTeams`). |
| `POST /plans/plan/{planId}/team/atlassian` | Add an existing Atlassian team to the plan (`addAtlassianTeam`). |
| `GET/PUT/DELETE /plans/plan/{planId}/team/atlassian/{atlassianTeamId}` | Get / update / remove an Atlassian team in the plan. |
| `POST /plans/plan/{planId}/team/planonly` | Create a plan-only team (`createPlanOnlyTeam`). Body `{"name","memberAccountIds":[…],"capacity"?,"issueSourceId"?}`. |
| `GET/PUT/DELETE /plans/plan/{planId}/team/planonly/{planOnlyTeamId}` | Get / update / delete a plan-only team. |

## Notes
- **Premium-only** — these endpoints require Advanced Roadmaps; on Standard they return `403`/`404`.
- **Plans ≠ Scrum boards/sprints.** Boards, sprints, and the backlog are in the separate **Jira Software Agile REST API** at `${ATLASSIAN_SITE_URL%/}/rest/agile/1.0/…` (`/board`, `/sprint`, `/backlog`) — *not* in this platform spec. If a user needs sprint operations, that's the API to call.
- `updatePlan` uses operation lists rather than a flat body — grep the spec for the exact shape.
- For exact schemas: `grep -n '"operationId": "createPlan"' ../jira-openapi-v3.json`.
