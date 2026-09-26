---
name: shared-assets
description: Use when skills or plugins are shared across OpenClaw instances on one host — shared trees mounted but empty, the same skill copied into every instance, a shared copy edited with no change in behaviour, an installed asset that never appears in the registered list, a plugin change that did nothing, a load candidate refused over ownership, a suspect install lock, or any request to deduplicate, promote, register, verify or roll out shared skills and plugins.
---

# Shared skills and plugins

Sharing is file layout plus configuration. Nothing else registers an asset. Every failure in this
area is silent — mounted, present, and not used — so verification is not optional here.

## Where a runtime looks

Two independent mechanisms, one per asset kind. Confirm the exact config keys against this instance's
own documentation before editing: spellings drift between versions and the runtime is the authority
on itself (skill `docs-research`).

| Kind | Registered by | Takes effect |
|---|---|---|
| skills | `skills.load.extraDirs[]` — the extra-directories list | on the next load |
| plugins | `plugins.load.paths[]` — the load-paths list | **only after a gateway restart** |

**The isolation rule decides what may be shared.** Startup enforces unique ownership of the state
directory, so an extension directory *inside* `state_dir` can never be shared — two instances pointed
at one state tree is a refusal, not a warning. A directory *outside* every state tree, mounted
read-only into each container and named in the load paths, is the supported way. That split is the
whole design: `state_dir` stays private, the shared tree is a separate mount.

## Load order, and the trap in it

Highest priority first: workspace → project agent → personal agent → state directory → bundled →
**extra directories and plugin-provided skills, lowest**.

The shared tree is registered at the bottom. A per-instance copy left anywhere above it therefore
**shadows** the shared one: the fleet looks shared while each instance still runs its old private
copy, and editing the canonical version changes nothing. That reads as "sharing is broken" and is
really "sharing was never reached" — `fleet.shared.local-shadow`.

**Promotion is not finished until the shadows are gone.** Remove a shadow by *moving* it to a
quarantine path, never by deleting: the move is reversible in one command, and that copy is the only
evidence of what the instance was actually running.

## Divergence stops the automation

Promote a skill only when its content is identical on every instance that has it
(`fleet.shared.duplicate-skill`: present on N, identical on all N). **If a local copy differs from the
shared one, stop and report the difference.** Automation does not get to decide whose version is
right — an instance may depend on its variant, and the divergence itself is what a human needs to
see. Same rule for instance-specific content: a name, a port, a key prefix or a host path in the body
disqualifies a candidate from the shared tree.

## Install policy

- **The global install path is never used.** It copies files and does not register them, so the asset
  sits on disk invisible to the runtime — the most convincing kind of non-fix
  (`fleet.shared.install-global-invisible`).
- Shared assets are managed by **file layout plus config**, and by nothing else.
- **Back up the install lock before any catalogue install, and read it.** A corrupted lock makes the
  next install remove the other assets: `fleet.shared.lock-corrupt`, red line
  `skill-install-unread-lock`, and `gate.RETRY_RULES` allows **zero** retries on `skills-install` and
  `plugins-install`. One failure stops the batch and the lock gets read.

## Ownership on the bind mount

A candidate whose directory owner does not match the uid the runtime expects is refused as a
suspicious candidate: the mount is there, the files are there, one line lands in the log, and the
feature is off (`fleet.shared.ownership-blocked`). Align ownership **on the host side** — a change
made inside the container lands outside a mount and dies with it (red line
`in-container-write-outside-mount`).

## Capability consent is never automated

Non-interactive or silent setup cannot approve new capabilities, and neither an apply flag nor the
runtime's own repair pass approves them. That is deliberate upstream design; automating it would
destroy the mechanism. **The approval flag is printed for a human to run and never passed by this
plugin** — `ocexec.py` refuses any argv containing it (`gate.BANNED_ARGS`). A promotion that needs a
new capability therefore has a two-part result: what was promoted, and the exact line the operator
must run (`fleet.security.capability-consent-pending`).

## Verification: four levels, four failure classes

Each level catches what the others cannot; skipping one leaves that class silently open.

| # | Check | Catches |
|---|---|---|
| 1 | list the shared tree **from inside the container** | mount absent, wrong mode, or empty tree (`fleet.shared.empty-mount`) |
| 2 | read the effective config back from the runtime | the edit landed in a file the process does not read |
| 3 | list registered assets **and the path each one resolved from** | registered but shadowed — the path is the whole answer (`fleet.shared.local-shadow`) |
| 4 | after a restart, compare loaded plugins with the config change time | load paths changed without a restart (`fleet.shared.plugins-load-no-restart`) |

Level 3 is the one usually skipped, and it is the only one that separates "shared" from "looks
shared".

## Common mistakes

- Counting files on the host instead of listing from inside the container. A host path proves nothing
  about what the process sees.
- Deleting a local copy instead of moving it, destroying the only record of what ran.
- Promoting a skill that is not identical everywhere, or one carrying instance-specific content.
- Editing plugin load paths and reporting success without a restart.
- Reaching for the global install path because it is one command.
- Restarting to "make it pick up" before checking which path an asset loaded from — the restart hides
  the shadow instead of finding it.
- Aligning ownership inside the container.

Procedure, deduplication and rollout: `/openclaw-ops:shared-sync`. Load-order mechanics, the promotion
sequence, the restart matrix and the expanded verification: `references/loading-order.md`.
