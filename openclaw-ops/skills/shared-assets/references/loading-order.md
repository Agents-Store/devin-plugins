# Load order, promotion and verification

Mechanics behind the shared-assets rules. Every host path here is a placeholder — `<data-root>`,
`<shared-root>`, `<quarantine>`, `<instance>`. Read the real ones from the mount table
(`${CLAUDE_PLUGIN_ROOT}/scripts/fleet.py discover --json` → `paths.shared_skills`,
`paths.shared_plugins`), never from this page.

## The ladder

Skills resolve highest priority first. The first location that supplies a given skill name wins; the
rest are never consulted for that name.

| Rank | Location | Owned by | Typical purpose |
|---|---|---|---|
| 1 | agent workspace | the agent's own tree | per-agent override, deliberately strongest |
| 2 | project agent directory | the project | project-scoped behaviour |
| 3 | personal agent directory | the operator | one person's local variant |
| 4 | state directory | the instance | what an install writes by default |
| 5 | bundled | the image | defaults shipped with the runtime |
| 6 | extra directories + plugin-provided skills | the fleet | **shared assets land here** |

The ordering is correct as design — a local override is supposed to beat a fleet default. It is also
exactly why sharing fails quietly: rung 6 is the bottom, so anything left at rungs 1–4 wins forever.
Promotion without de-shadowing produces a fleet that reports the shared path in its config and runs
none of it.

Plugins resolve from three places: the state directory, the agent workspace, and the load-paths
list. Only the third is shareable, and the first two shadow it exactly the way rungs 1-4 shadow a
shared skill — a plugin copy left in a state tree keeps winning after the shared path is
registered. The list is read at process start, which is why a plugin change needs a restart while
a skills directory does not.

## Restart matrix

| Change | Reload enough | Restart required |
|---|---|---|
| content of an already-registered shared skill | yes, on next load | no |
| adding or removing an extra skills directory | usually yes — verify at level 3 | if level 3 still shows the old path |
| **anything under the plugins load config** | no | **yes** (`fleet.shared.plugins-load-no-restart`) |
| ownership fix on a bind mount | no | yes — the candidate is re-evaluated at load |
| new mount added to the compose file | no | recreate the container, not a restart |

A restart is R2 with an R3 precondition: an instance restarted while a referenced secret no longer
resolves comes back dead. Run the delivery precheck from the `secrets-infisical` skill before any
restart in this procedure.

## Promotion sequence

Stop points are real: each one is a place where the operator can walk away and leave the fleet in a
state that still works.

1. **Inventory.** For every instance, list the assets it carries and hash each one's content. Group as
   `asset → present on N, identical on M`.
2. **Select candidates.** `M == N`, and no instance-specific content in the body (grep the candidate
   for names, ports, host paths and key prefixes). Anything else is reported, not promoted.
   `M < N` → `fleet.shared.local-shadow` divergence, hard stop for that asset.
3. **Place.** Copy the canonical version into `<shared-root>/skills/<asset>` or
   `<shared-root>/plugins/<asset>` on the host, and set ownership to the uid the runtime expects
   (read it from the refusal message, not from memory). Nothing is registered yet, nothing changed.
   **Stop point.**
4. **Register.** Add the shared directory to the extra-directories list (skills) or the load-paths
   list (plugins), through `config-surgery` — snapshot outside the `.bak` ring, diff with deletion
   count, JSON validation, lint. **Stop point.**
5. **Restart** the instances whose plugin paths changed, canary first (`gate.canary_barrier`).
6. **De-shadow.** For each instance, move the now-redundant local copy to `<quarantine>/<instance>/`.
   Move, never delete. Re-verify at level 3 after each move.
7. **Verify** all four levels below, per instance.
8. **Record.** What was promoted, what was quarantined, what diverged and was left alone. The
   divergence list is the actual deliverable of a first run — it is the work a human has to decide.

Direction is good → changed, so the batch is **fail-fast** (`gate.batch_policy`): the first failure
stops it. A failure on the third of seven cloned instances is almost always systemic.

## De-shadowing

- Move to a quarantine path **outside every container volume**, so the move cannot be undone by a
  container recreation and cannot be read by the runtime as an asset.
- Keep the instance name in the quarantine path. Recovering "which variant did instance X run" is the
  whole reason the copy is kept.
- Never delete in the same session as the move. Deletion is a separate decision, taken after the
  fleet has run on the shared copy long enough to prove it.
- Rollback is the inverse move, one command, and it must appear verbatim in the ROLLBACK block of the
  dry-run.

## Install locks

Catalogue installs write a lock file describing what is installed.

- **Read it before installing, and back it up.** A lock that does not parse, or that lists assets that
  are not on disk, is `fleet.shared.lock-corrupt` — critical, because the next install rewrites it and
  removes everything it fails to see.
- Zero retries (`gate.RETRY_RULES["skills-install"]`, `["plugins-install"]`). A failed install is
  investigated, never repeated: the second attempt is what does the damage.
- Red line `skill-install-unread-lock` — installing before the lock has been read and backed up needs
  a typed confirmation, not `--yes`.

## Ownership refusal

The refusal names the uid it found and the uid it expected. Read both out of that line rather than
assuming a value.

- Fix on the **host** side, on the directory and its contents.
- Read-only mounts are intentional: the shared tree is authored on the host and consumed in the
  container. A write attempt from inside is a design error, not a permissions problem.
- Re-evaluation happens at load, so a restart is part of the fix — and therefore so is the delivery
  precheck.

## Capability consent

A shared asset can require a capability the instance has not approved. The runtime deliberately
refuses to approve capabilities from silent setup, from an apply flag, or from its own repair pass.

- This plugin never emits the approval flag; `ocexec.py` refuses argv containing it.
- The result of such a promotion is: the asset is in place, registered, and **inert**, plus the exact
  command a human runs to approve it.
- Reporting the promotion as complete without that line is the failure mode this rule exists to
  prevent.

## Verification, expanded

| Level | How it fails | What a pass looks like |
|---|---|---|
| 1 — list the tree from inside the container | mount missing, mounted at the wrong destination, empty tree, wrong mode | the expected asset names, read through `ocexec.py`, not from the host |
| 2 — read back the effective config | the edit went to a file the process does not read (see the state-dir fallback trap in `fleet-model/references/layout.md`) | the shared path appears in the runtime's own view of its config |
| 3 — list registered assets **with resolved paths** | registered, loaded, and resolving to a local copy | every shared asset resolves to `<shared-root>/…` on every instance |
| 4 — loaded plugins after restart | load paths changed while the process kept running | the loaded plugin set matches the config, and process start is later than the config change |

Level 3 is the contract. Levels 1, 2 and 4 can all pass on a fleet that runs entirely on shadows.
