# Fleet config

One file, owned by the operator, living **outside** this repository at mode 0600. It is a frozen
snapshot of autodetection plus the handful of decisions autodetection cannot make. The schema is
`${CLAUDE_PLUGIN_ROOT}/scripts/lib/fleet.schema.json`; a filled-in sample on a fictional fleet is
`fleet.example.json`.

## Resolution ladder

First hit wins. `fleet.py --config PATH` bypasses the ladder entirely.

| Order | Path | Typical use |
|---|---|---|
| 1 | `$OPENCLAW_OPS_CONFIG` | one-off targeting, tests, fixtures |
| 2 | `./.openclaw-ops.json` | a working directory that belongs to one fleet |
| 3 | `~/.config/openclaw-ops/fleet.json` | a single operator on a shared host |
| 4 | `/etc/openclaw-ops/fleet.json` | the host-wide answer |

The file mode is checked. Group- or world-writable is **fatal**, not a warning: a config anyone can
edit decides which instances are mutable.

Missing config is a legitimate state, not an error. Discovery still enumerates the fleet from Docker;
what stops working is everything that needs a decision — roles, canary, managed flags, policy. Read
commands say so and continue; mutations refuse.

## Who fills each field

| Field | Origin | Notes |
|---|---|---|
| `version` | fixed | `1` is the only accepted value |
| `project_prefix` | **detected**, confirmed by a human | the prefix that selects this fleet. Instance name = project name minus the prefix. Wrong prefix = an empty or over-wide fleet, so `/init` shows what it matched before writing |
| `host_fingerprint` | **detected** | see below |
| `host_label` | human | free text, shown in reports, never matched on |
| `generated_at` | written by `/init` | last write timestamp |
| `compose_root`, `data_root` | **detected** | recorded so a *stopped* instance is still locatable. Never used in place of the live mount table for a running one |
| `gateway_service` | **detected** per instance | this value is only the fallback used when the project has no container to inspect |
| `reference` | **human only** | which instance is the baseline and clone source. Nothing on the host says "this one is the truth" |
| `policy.*` | **human only** | see the policy table |
| `instances.<name>.manage` | **human only** | `false` keeps the instance in the inventory and refuses every mutation on it |
| `instances.<name>.role` | **human only** | `reference` · `canary` · `standard` · `legacy` · `neighbour` |
| `instances.<name>.criticality` | **human only** | `low` · `normal` · `high`; orders waves and forces a separate window for the top tier |
| `instances.<name>.aliases` | human | extra names the selector accepts |
| `instances.<name>.secrets` | mixed | delivery mechanism, identity file path, project id, environment, expected key count — **names and ids only, never values** |
| `instances.<name>.notes` | human | carried into reports; the place to record why an instance is unmanaged |

`expected_key_count` is worth filling in: an instance receiving a handful of keys while its siblings
receive a full set is the signature of a wrong project id or a broken machine identity, and a count
makes that a one-line check instead of an investigation.

## Policy

| Key | Default | What the decision is |
|---|---|---|
| `update_channel` | `stable` | which release channel the fleet follows. Resolved through package-registry dist-tags — never through semver ordering or release dates |
| `soak_days` | `14` | how long a version must have been promoted before this fleet accepts it. A correction release on the same line resets the clock |
| `canary` | — | the instance that takes any multi-instance mutation first. Must be the least critical one and must not be the reference |
| `stale_log_hours` | `24` | how long a running, health-green instance may be silent before it is called a zombie |
| `batch_max` | `3` | hard cap on instances touched by one batch, canary included |
| `snapshot_dir` | — | where this plugin writes its own pre-mutation snapshots, outside the CLI's own `.bak` ring |
| `lock_dir` | the `locks` sibling of `snapshot_dir` | where the fleet-wide front lock lives. Host-local: it serialises credential work **across** instances, which the runtime's own per-state-dir lock cannot |
| `snapshot_keep` | `20` | how many snapshots to keep per file |
| `loopback_only` | `true` | assert every published gateway port binds to loopback; a non-loopback publish becomes a security finding |

Two cross-field rules the validator enforces: exactly one `reference` and at most one `canary`, and
they must not be the same instance; a `legacy` role cannot carry `manage: true`.

`snapshot_dir` exists because the CLI's own backup ring is short and rotating. Four automated edits in
a row evict the last-known-good file a human deliberately kept. The ring is the human's safety net;
this plugin keeps its own.

## host_fingerprint and read-only mode

`host_fingerprint` is `sha256(<machine-id>)[0:16]`. On load, the plugin recomputes it and compares.

- **Match** — normal operation.
- **Mismatch** — the plugin enters read-only mode and says why. Every mutation is refused, reads
  continue. The config describes a different machine, so every recorded path, port, role and managed
  flag in it is a guess about this one. A confident guess applied to the wrong host is precisely the
  incident this field exists to prevent.
- **Absent from the file** — allowed (some hosts have no machine id) and reported. Absence weakens the
  guarantee; it does not fake it.

Recovery from a mismatch is a decision, not a flag: either you are on the wrong host — go to the right
one — or the host genuinely changed identity, in which case re-run `/openclaw-ops:init` and review the
detected fleet before writing. There is no "ignore fingerprint" switch, because that switch would be
used exactly when it should not be.

## Commands

| Command | Does |
|---|---|
| `fleet.py config --show` | print the resolved config plus which rung of the ladder it came from |
| `fleet.py config --validate` | schema and cross-field rules; exit 2 when invalid |
| `fleet.py config --diff` | what the live host has that the file does not, and the reverse: `added` / `removed` / `changed` |
| `fleet.py config --init [--out PATH] [--force] [--detect-only] [--reference N] [--canary N] [--host-label S] [--update-channel C] [--soak-days N] [--stale-log-hours H]` | write a config from detection plus the decisions passed in. The three policy flags are the wizard's policy answers; omitting one keeps its schema default (`stable` / 14 / 24) |

`--diff` is the maintenance loop. A fleet grows an instance, or one is retired, and the file silently
stops describing reality; the difference is exactly the set of objects nobody has decided about yet.

## Init came back with nothing usable

`/openclaw-ops:init` diagnoses an empty or unusable detection instead of retrying it. The shape of the
answer is always **what I saw → the hypothesis → exactly one action for the operator**: never two
actions in one message, and never a second detection run hoping for a different result.

| Seen | Hypothesis | The one action |
|---|---|---|
| docker answers, zero compose projects | no compose workload here — wrong machine | run init from a shell on the host that serves the gateways |
| projects exist, none match the prefix | right host, different naming | re-run with `--prefix <their-prefix>` |
| projects match, every one `alien` | right host, a deployment class this plugin does not model | collect `fleet.py discover --json`; leave them unmanaged |
| config loads, `host_fingerprint` differs | it describes another machine, so everything stays read-only | re-run init with `--force` here, or point `$OPENCLAW_OPS_CONFIG` at this host's file |

`alien` and `legacy` rows are still listed. Nothing detected is hidden — an unmanaged row is a decision
the operator has not made yet, not an object the plugin pretends not to see.
