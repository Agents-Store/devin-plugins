---
name: examples
description: Use when a whole OpenClaw fleet job is in view rather than a single answer — first contact with a host whose instances are unknown, a fleet where every instance lost its provider login, an upgrade whose rollback story is unclear, a new instance that has to be stood up and proven isolated — and whenever the question is what the entire sequence looks like, which command owns which step, what a run of this plugin produces end to end, or where one step's output becomes the next step's input.
---

# Examples

Four end-to-end runs on a fictional fleet. Each threads commands, skills and scripts into one
sequence and names, at every step, the observation that decides whether it worked.

Read the scenario closest to the situation, then follow the skill links for depth. These are
**shape, not data** — every name, port, path and version below is invented.

## Scenarios

| Scenario | File | Covers |
|---|---|---|
| First run on an unfamiliar host | [references/scenarios/fleet-cold-start.md](references/scenarios/fleet-cold-start.md) | discovery → config → status → deep battery → audit, without changing anything |
| The whole fleet is logged out | [references/scenarios/revive-logged-out-fleet.md](references/scenarios/revive-logged-out-fleet.md) | symptom → root cause → one owner directory → printed logins → verification across a rotation |
| Upgrade with no rollback | [references/scenarios/upgrade-with-rollback-gap.md](references/scenarios/upgrade-with-rollback-gap.md) | dist-tags → soak gate → digest pin → verified backup → post-upgrade traps → restore path |
| Clone and prove the isolation | [references/scenarios/clone-and-verify.md](references/scenarios/clone-and-verify.md) | preflight → free port → materialise → the manual half → isolation proof |

## The fictional fleet used throughout

One host, compose prefix `openclaw-`, gateways published on loopback.

| Instance | Role | Note |
|---|---|---|
| `alpha` | reference | the shape everything else is compared against |
| `beta` | canary | lowest criticality, no revenue-bearing schedule — every batch starts here |
| `gamma` | standard, `criticality: high` | carries the money schedule; its own maintenance window |
| `delta` | standard | green container, silent log — the zombie candidate |
| `legacy-one` | legacy, `manage:false` | recognisably the same product, a different deployment shape |
| `neighbour-x` | alien | matched the prefix, failed the layout markers; inventory row only |

Host paths appear as `<data-root>/<instance>` and `<compose-root>/openclaw-<instance>`; ports as
`127.0.0.1:<port>`. Container-side destinations are the ones upstream fixes and are written literally.

## The shape of every session

1. **Discover before deciding.** `fleet.py discover` first — never a remembered path, never a
   hand-written `docker exec`.
2. **Split health from liveness.** `healthcheck.py` prints both columns; the disagreement is the
   result, not a rendering detail.
3. **Name the finding.** A symptom becomes an id from the findings catalog, or it does not become a
   repair (`fleet-diagnostics`).
4. **Fetch before recommending.** Versions, flags and model ids come from a live source or the box
   (`docs-research`); no source, no recommendation.
5. **Plan, then apply.** Eight blocks, canary first, `--yes` in a later turn than the proposal.
6. **Verify with an observation that changed.** "Looks fine now" ends nothing.

## How to read a scenario

- Every step is written as **run → skill → what proves it**. The third column is the point; the first
  two are how you get there.
- Refusals are shown where they happen. A preflight that stops the run is the plugin working, and the
  scenarios keep those rows instead of routing around them.
- Where a scenario shows a value — a version, a port, a key name — treat it as a placeholder. The
  substitution rule stands everywhere: anything entering a diff must be an echo from the box.
