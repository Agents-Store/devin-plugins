# Post-clone checklist

The script stops at the boundary of things it must not touch. Everything below is what stands between
"the files exist" and "the instance is a working member of the fleet". Work top to bottom: each step
assumes the one above it.

Legend: **why manual** — the reason automation stops here. **verify** — the observation that changes
between done and not done. **if skipped** — how the omission shows up, usually much later.

## 1. Machine identity and project access

- **Do**: create the identity the new instance authenticates with, grant it read access to the same
  secret project and environment the source uses, and place its file with owner-only permissions.
- **Why manual**: it mints credentials. This plugin never handles secret values, and an identity file
  written by automation is an identity nobody audited.
- **Verify**: the injection wrapper starts and delivers keys — `run-with-infisical printenv` piped to a
  name-only filter, never printed as values.
- **If skipped**: the container starts with almost no keys and behaves like a zombie: green health,
  no work. This is `fleet.secrets.identity-broken`.

## 2. Per-instance secrets

- **Do**: create the values the source's config references, under the same names.
- **Why manual**: values.
- **Verify**: delivered key **names** and **count** match the source. Record the count in the fleet
  config as `secrets.expected_key_count` so the comparison is one line next time.
- **If skipped**: a feature is silently off with a config that reads correctly
  (`fleet.secrets.delivery-short`). A count far below the siblings' means the wrong project id, not a
  missing feature (`fleet.secrets.wrong-project`).

## 3. Provider logins

- **Do**: register each backend on the new instance and log in from the credential **owner**
  directory. The plugin prints login lines; a human runs them.
- **Why manual**: a login is interactive, its callback is local to the process that started it, and a
  repeated attempt burns a single-use refresh token — retry budget zero (`gate.RETRY_RULES`).
- **Verify**: the credential check exits 0 on the clone, and — this is the part people forget — still
  exits 0 on every other instance an hour later. A login that logged out a sibling is a failure that
  reports success.
- **If skipped**: every request falls down the chain into cooldowns, or fails outright; scheduled jobs
  fail as a group (`fleet.cron.all-failing`).

## 4. Model chain

- **Do**: apply the chain at **all three levels** — defaults, per-agent overrides, per-schedule pins.
  Model ids are pinned, and every id must be an echo from this instance's own catalogue.
- **Why manual**: it is a policy decision, and the ids are version- and account-specific.
- **Verify**: the catalogue lists every id in the config; the chain resolves; fallback and cooldown
  events stay near zero over the first full day. A fleet that formally has a chain and actually lives
  on its reserve looks identical to a healthy one until the bill arrives
  (`fleet.model.fallback-burn`).
- **If skipped**: a per-agent primary with no fallbacks of its own is **strict** and silently cancels
  the fleet chain for that agent (`fleet.model.agent-override-strict`).

## 5. Skills and plugins

- **Do**: point the clone at the shared trees rather than copying assets into it, align ownership on
  the bind mount, and restart after touching plugin load paths.
- **Why manual**: which assets a new instance should load is a decision; and the global install path
  copies files without registering them, so it produces invisible assets
  (`fleet.shared.install-global-invisible`).
- **Verify**: list the shared trees **from inside the container**; then confirm each loaded asset
  resolves to the shared path. Extra directories are the **lowest** load priority, so any local copy
  left behind wins silently (`fleet.shared.local-shadow`).
- **If skipped**: the clone runs with a different asset set than its siblings and diverges from the day
  it starts.

## 6. Embedding key and memory

- **Do**: give the instance **its own** embedding key, delivered by reference, and index once it is
  live.
- **Why manual**: it is a value, and it is a cost decision.
- **Verify**: an embedding call succeeds; the index timestamp advances.
- **If skipped**: vector search fails closed — which is the intended behaviour and looks like silence
  rather than an error. Subscription OAuth covers chat completions and does **not** satisfy embedding
  requests (`fleet.memory.embeddings-unauthorized`).

## 7. Fleet config entry

- **Do**: add the instance with `manage`, `role`, `criticality`, any aliases, and a note saying what it
  is for. A clone made to be a canary is only the canary once `policy.canary` names it.
- **Why manual**: role and criticality are judgements nothing on the host can make.
- **Verify**: `fleet.py config --diff` reports nothing under `added` or `changed`.
- **If skipped**: the instance is unmanaged. It appears in inventory, and every mutation on it is
  refused — which surfaces during the first incident on it.

## 8. Bring up and verify before work

- **Do**: `up`, then the health battery, then hand it work — in that order.
- **Verify**: HEALTH and LIVENESS agree; the log moves; the first scheduled run completes; the security
  layer-two checks pass on it, especially loopback publication.
- **If skipped**: the clone joins the fleet carrying findings, and the next fleet-wide report cannot
  distinguish a new problem from an unfinished setup.

## Isolation re-check

Run after step 8, not before: some of these only become observable once the instance has started.

| Assertion | How |
|---|---|
| no shared paths beyond the intended ones | mount tables of clone and source side by side |
| the source's name appears nowhere in the clone's compose file or config | search the rendered files |
| config path, state dir, workspace and published port are unique | the preflight, re-run against the live instance |
| the source is untouched | its config mtime, restart count and port match the values recorded before the clone |
| credential ownership is unambiguous | exactly one directory can write the chain; anything else mounts it read-only |

## Definition of done

The clone is done when: the health battery is clean, delivered key names match the source, the
credential check is clean on the clone **and** on every sibling, the chain resolves with fallback
events near zero, loaded assets resolve to the shared paths, `config --diff` is clean, and the source's
recorded state is unchanged. Anything less is a clone that exists, not a clone that works.
