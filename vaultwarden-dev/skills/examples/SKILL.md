---
name: examples
description: This skill should be used when the user asks "how do I onboard/offboard someone in Vaultwarden", "show a Vaultwarden CI pipeline example", "back up and upgrade Vaultwarden", or wants an end-to-end walkthrough combining the admin panel, client API and bw CLI.
---

# Vaultwarden Scenario Walkthroughs

End-to-end flows that combine the surfaces described in the other skills. Each scenario lists the surface used per step, the exact commands, and the checks between steps. Pick the closest scenario, read it, and adapt ids and names.

| Scenario | When | File |
|---|---|---|
| Onboard an employee | new person needs an account, org membership and collection access | [references/scenarios/onboard-member.md](references/scenarios/onboard-member.md) |
| Offboard an employee | someone leaves; cut access and rotate what they could see | [references/scenarios/offboard-member.md](references/scenarios/offboard-member.md) |
| Secrets in CI / scripts | a pipeline or cron job needs passwords from the vault | [references/scenarios/ci-secrets.md](references/scenarios/ci-secrets.md) |
| Backup and upgrade the server | routine upgrade without breaking clients | [references/scenarios/backup-and-upgrade.md](references/scenarios/backup-and-upgrade.md) |

Conventions in all scenarios:

- `VW_URL=https://vault.example.com`, ids as `<org-uuid>`, `<member-id>`, `<user-uuid>`, `<item-id>`.
- Secrets are entered by the user with `read -r -s` and passed through variables (`vaultwarden-dev:secret-hygiene`).
- Every destructive step is preceded by a read of the target and an explicit confirmation from the user.

Which surface does what: the routing table in [setup § 1](../setup/SKILL.md).
