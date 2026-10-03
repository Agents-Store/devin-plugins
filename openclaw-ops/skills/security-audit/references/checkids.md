# Check ids, families, and what each layer can prove

Read this before quoting any id, severity or fix hint. Every value on this page is a *shape*: the ids
themselves, their messages and their hints come from the live run, never from here and never from
memory.

## The finding record

The audit and the lint share one finding shape. Consumers of this plugin depend on all six fields
surviving intact.

| Field | Meaning | How it is used here |
|---|---|---|
| `checkId` | stable id of the check that fired | the join key for reports, deltas and repair lines. Never rewritten, never translated |
| `severity` | the runtime's own grading | ordering input, not the final order — see the triage tiers in `SKILL.md` |
| `message` | what is wrong | quoted verbatim into the report |
| `path` | the location involved — a config path in current builds, a filesystem path in older ones | shown as recorded; a path inside a container is not a host path |
| `ocPath` | the config pointer the finding refers to (older builds; current ones may fold it into `path`) | what `config-surgery` edits; the pointer, not a guessed key name |
| `fixHint` | what upstream suggests | a **suggestion in this version's vocabulary**. Confirm the flag exists in this instance's `--help` before running it |

Three spellings of "how bad" exist, and none is translated by hand: the lint grades `info` /
`warning` / `error`, the security audit `info` / `warn` / `critical`, and the post-upgrade probes name
the field `level`, not `severity`. `ocjson.worst_severity` reads both field names; the battery maps
them into the plugin's own four-name vocabulary through one table.

### Exit contracts — only where upstream documents them

Asserted in `ocjson.EXIT_CONTRACTS`. Every row below is a documented contract; a command that is not
in the list carries only the ordinary "0 succeeded" meaning, and its payload is the answer.

| Command | 0 | 1 | 2 |
|---|---|---|---|
| `doctor --lint` | no finding at or above `--severity-min` | at least one finding at or above it | **the command failed before its checks completed** — a failure, not "warnings only" |
| `doctor --post-upgrade` | no `level: "error"` finding | at least one `level: "error"` finding | not part of the contract — an ordinary failure |
| `secrets audit --check` | clean | plaintext, shadowed references or residues | unresolved references or a store validation failure |
| `models status --check` | healthy | expired or missing credentials, an incompatible route, an unavailable runtime, or **indeterminate readiness** | expiring |

- **The lint threshold is the caller's.** The same instance exits 0 or 1 depending on `--severity-min`
  (`info`, `warning`, `error`), and upstream states no default. Pin it — this plugin always passes
  `--severity-min info` — or the exit code means different things on different builds. `--severity-min`
  controls both what prints and the exit threshold, so a run at `error` can print nothing and exit 0
  while `warning` findings exist.
- **`--all` widens the selection, not the threshold.** The default lint run leaves out deep, historical
  and opt-in checks; `doctor --lint --all` is the complete inventory (the audit posture), and
  `--only <id>` / `--skip <id>` select by the path-shaped check id. `checksRun` and `checksSkipped` in
  the document prove a focused gate ran what you meant.
- **Plain `doctor` is not a read.** Without `--lint` or `--json`, ordinary `doctor` — including
  `doctor --non-interactive`, which suppresses prompts and not writes — can copy legacy config and
  migrate state. `--fix` and its alias `--repair` apply repairs, and `--yes` accepts defaults and
  **enters repair maintenance** (the managed gateway is stopped and restarted around it). The door
  classifies plain `doctor` as an R2, and `--fix`, `--repair` and `--yes` as R4; the read postures are
  `--lint` and bare `--json` (both on the door's read list), and upstream states that both reject
  `--repair`, `--fix`, `--force`, `--yes` and `--generate-gateway-token` ("Run doctor", options
  table) — if one is passed anyway, the door still classifies the line by that flag.
- **Bare `doctor --json` is advisory.** It exits 0 once it has produced a report, even when `ok` is
  false — read `ok` and `findings`. Only explicit `--lint` is the threshold-based gate. A lint run
  that fails before producing a report exits 2 and prints one error finding under
  `core/doctor/lint-inspection`; that finding is the detail, and the run is **not** a pass.
- **`doctor --post-upgrade --json`** is `{probesRun, findings}` with a `level` per finding. Version drift
  between an official plugin and the upgraded CLI is a warning and never changes the exit code — read
  the findings, not only the code.
- **`security audit` has no contract here, deliberately.** Upstream documents its severities
  (`critical` / `warn` / `info`) and its document (`{summary, findings, suppressedFindings}`) but no
  exit-code table. Until the owner confirms one on a test instance, read the payload and take the exit
  code as "0 succeeded" only; do not rebuild the old 0 / 1 / 2 reading.

## Families the runtime owns

Ids are namespaced by prefix. Knowing the scope of a family tells you whether an id you are looking at
can even exist, and where its evidence lives.

| Prefix | Scope | Typical evidence | What it cannot see |
|---|---|---|---|
| `core/doctor/*` | a core health check of the runtime itself (`core/doctor/<check>`): config, state, gateway, auth profiles, plugin load | the check's own inspection of config and state | how the instance is exposed or what the host lets others read |
| `<plugin>/*` | a check a plugin registers (`<plugin>/<check>`); some are opt-in and appear only with `--all` or `--only` | that plugin's own state | anything outside the plugin |
| `fs.*` | files and directories the runtime owns: state tree, config, credential material | modes, owners, unexpected files | anything outside the paths this process knows about |
| `gateway.*` | the HTTP surface and its auth: bearer configuration, exposure of gateway features | the gateway's own configuration | how the port is published or routed on the host |
| `tools.exec.*` | what agents are permitted to execute | tool policy in the config | what the host would allow if the policy were wrong |
| `plugins.*` | loaded extensions, their origins and trust | plugin load paths and registration | the contents of a shared tree it was never pointed at |
| `security.exposure.*` | settings that widen the surface | config-level exposure switches | the network the container is actually attached to |

Current ids are path-shaped (`core/doctor/<check>`, `<plugin>/<check>`) and older ones are dotted
prefixes; both are the runtime's, and both are carried through unchanged.

**Rule: verbatim pass-through.** A composed id in one of those families is worse than no id — it looks
authoritative, joins against nothing, and quietly poisons every stored report that reuses the key.

**Rule: `fleet.*` is ours**, and exists only for what the families above structurally cannot check.
Each of them is defined in `fleet-diagnostics/references/findings-catalog.md` with severity, detection,
fix, verification and risk class.

## What `--fix` covers, and what it never covers

- It repairs the narrow subset of checks that declare an automatic repair. Everything else stays.
- It does **not** approve capabilities. Neither does the general confirmation flag. That is deliberate
  upstream design: consent is the one thing automation is not allowed to grant. Print the consent line
  for a human (`fleet.security.capability-consent-pending`).
- It does not touch the host: no firewall rules, no port publication, no ownership of a bind mount, no
  token rotation. What it does change is file modes: it tightens permissions on the state tree, the
  config and its includes, the credential files, the per-agent database and legacy session artefacts.
- It is R4 in this plugin. A repair that rewrites files the operator did not enumerate needs an
  eight-block plan, a snapshot outside the CLI's own backup ring, and a typed confirmation.

## Layer-two procedures

Each check below is R0 to detect. The fix class is the one recorded against the finding id.

### Publication and reachability

1. `fleet.py discover --json` gives `port.host_ip`, `port.host_port`, `port.loopback` per instance.
   `loopback` false while `policy.loopback_only` is true is the finding.
2. Confirm by **reaching for it from another machine**, not by reading rules. Published container ports
   bypass the ordinary input chain, so the rules that protect every other service on the host are not
   in the path. The container-aware chain is the one that applies.
3. A `down` instance still owns its publication in its compose file. Absence of a listening socket is
   not absence of exposure — it is exposure that starts with the next `up`.

### Operator token

1. Resolve the token **inside** the container, fingerprint it there, and let only the fingerprint out.
2. Identical fingerprints on two instances is `fleet.security.token-reuse`: two gateways, one boundary,
   and any holder of that token operates both.
3. Rotation is R4 (`gateway-token-rotation`): every scraper, monitor and internal caller that holds the
   old value is enumerated first, or the rotation is an outage with extra steps.

### Plaintext values at rest

1. Scan by **class**, not by value: name pattern plus key-class prefixes (`redact.classify_key`),
   reporting `{path, name, class, fingerprint, size bucket}`.
2. Fingerprint parity against the delivered value decides the verdict: parity means the file is
   redundant, no parity means it is load-bearing and deleting it stops the instance.
3. Neutralise a redundant file by moving it to quarantine **outside** the container's volumes. Then
   rotate — the value has been readable by everyone with host access for as long as the file existed.

### Permissions

- Credential and identity trees: owner only. A group-writable identity file means anyone in that group
  can mint the fleet's secrets.
- The plugin's own fleet config is checked the same way, and group- or world-writable is fatal rather
  than a warning: that file decides which instances are mutable.

### Metrics and other side doors

- Metrics require the bearer. Because the bearer is all-or-nothing operator access, a scraper
  configured with it is an operator; scrape from inside the container and export only the numbers.
- A chat or completion endpoint is never a health check. Each such call creates a full agent session:
  it costs money, writes history, and can be the very thing that is broken.

## Reporting a security finding

```
<severity>  <checkId>  <instance>
  evidence: <what was observed, values as fingerprints and presence>
  source:   <live audit run | layer-two check | quoted documentation URL>
  repair:   /openclaw-ops:repair <instance> --issue <finding-id>
```

A finding with no source line does not get acted on. For anything the built-in audit did not produce,
the source is a documentation citation fetched through the `docs-research` skill — no citation, no
action.
