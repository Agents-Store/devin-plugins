---
name: examples
description: This skill should be used when the user wants a worked end-to-end Mattermost example or walkthrough — "show me a full Mattermost workflow", "example of onboarding a team in Mattermost", "how do I broadcast a message to several channels via the API", "end-to-end channel management example", or wants to see several Mattermost API calls chained together for a real scenario.
---

# Mattermost Worked Examples

End-to-end scenarios that chain real Mattermost REST calls. Each scenario lives in `references/scenarios/`. They assume the `setup` skill has run (so `MATTERMOST_API_URL` and `MATTERMOST_TOKEN` are set) and reuse the conventions from `common-operations` (resolve names → IDs, patch don't replace, confirm destructive actions).

## Scenarios

| Scenario | File | What it demonstrates |
|----------|------|----------------------|
| Onboard a team | `references/scenarios/onboard-team.md` | Create a team → create channels → add existing users & email-invite new ones → post a welcome |
| Channel management | `references/scenarios/channel-management.md` | Set header/purpose → convert privacy → move members → archive & restore |
| Bulk messaging | `references/scenarios/bulk-messaging.md` | Broadcast to many channels → DM a list of users → attach a file |
| Admin audit | `references/scenarios/admin-audit.md` | Server ping → user/team/channel stats → analytics → start a compliance export |

## How to use

Pick the scenario closest to the user's goal, open its file, and adapt the names/IDs (team, channel, user) to the live instance. When an exact endpoint or field is unclear, open the matching `api-reference` `references/*.md` file. When a call fails, switch to `troubleshoot`.

<example>
User: "Walk me through standing up a new team in Mattermost and adding my people."
→ Open `references/scenarios/onboard-team.md` and run it, substituting the team name, channels, and member emails.
</example>

<example>
User: "I need to post the same maintenance notice to five channels."
→ Open `references/scenarios/bulk-messaging.md`; resolve the channel ids, then loop the `POST /posts` call.
</example>

<example>
User: "Give me an admin health-and-usage snapshot of our server."
→ Open `references/scenarios/admin-audit.md`; it chains ping, stats, and analytics into one report.
</example>
