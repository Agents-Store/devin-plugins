# Config field reference

A map of the config surface by section: what a section governs, the fields worth knowing, and the
trap in each. Read it to know **where** something lives and **what it affects** — not to quote a
current value.

Three rules for using this page:

- **No defaults are printed here.** Defaults drift between versions, and a remembered default written
  into a config is indistinguishable from an intentional setting. Read the effective value with
  `config get <path>` on the instance in front of you.
- **The schema is the authority.** Field names and enums change; the strict schema means a stale name
  is an outage, not a warning. Confirm against this instance's own schema and `--help` before writing
  a key you have not seen in its current config.
- **Structure is stable, contents are not.** Sections and their responsibilities are the durable part;
  treat every enum list below as "these exist", never as "these are all of them".

Paths are written in dotted form as `config get` accepts them.

## Root

| Key | Holds |
|---|---|
| `$schema` | the only non-schema root key the strict validator accepts |
| `agents` | agent defaults and the per-agent entries (an object keyed by agent id) |
| `channels` | where conversations arrive from |
| `tools` | which tools an agent may call, and their execution limits |
| `plugins` | plugin system, allow/deny, load paths, per-plugin config |
| `skills` | bundled skill selection, extra directories, per-skill config |
| `hooks` | lifecycle hooks |
| `session` | session scoping, reset and maintenance |
| `cron` | whether the scheduler runs — the jobs live in the state store, not here |
| `gateway` | the HTTP surface: bind, port, auth, reload behaviour |
| `memory` | search provider and model, and the query limits |
| `env` | inline variables and whether shell env is imported |

## agents

| Path | Type | Governs |
|---|---|---|
| `agents.defaults.workspace` | string | agent workspace path — **unique per instance**, part of the isolation set |
| `agents.defaults.model` | string or object | the chain: a bare ref, or `{primary, fallbacks[]}` |
| `agents.defaults.models["<provider>/<model-id>"].agentRuntime.id` | string | which local runtime serves that model — the canonical place for a CLI backend |
| `agents.defaults.imageModel` | string or object | model used for image analysis |
| `agents.defaults.heartbeat` | object | `every`, `target`, `model`, `lightContext`, `isolatedSession`, `prompt` |
| `agents.defaults.compaction` | object | when and how context is compacted |
| `agents.defaults.sandbox` | object | `mode` (off / non-main / all), `scope` (session / agent / shared) |
| `agents.defaults.bootstrapMaxChars`, `…TotalMaxChars` | number | per-file and total limits on workspace files loaded at bootstrap |
| `agents.defaults.timeoutSeconds`, `maxConcurrent`, `thinkingDefault` | number/string | execution envelope (documented with the model settings) |
| `agents.defaults.userTimezone` | string | IANA zone |
| `agents.defaults.skipBootstrap` | boolean | stops the **creation** of missing bootstrap files — a defaults-only key with no per-agent form |
| `agents.entries.<id>.*` | object | per-agent overrides: `name`, `workspace`, `model`, `identity`, `sandbox`, `heartbeat`, `memory.search`, `models["<ref>"].agentRuntime` … The **object key is the stable agent id** |

Traps: a per-agent `model` **without its own** `fallbacks` is strict — it silently cancels the fleet
chain for that agent (`fleet.model.agent-override-strict`). A heartbeat pinned to a model that left the
catalogue fails on a schedule nobody watches.

**`agents.entries` is an object, not a list.** The older `agents.list[]` array is retired and
`doctor --fix` migrates it into `agents.entries`; `default` per agent is retired too (exactly one
configured agent resolves implicitly, and multi-agent calls name the agent). Per-agent heartbeat and
other overrides live under `agents.entries.<id>.*`.

**Runtime selection is not an agent-defaults key.** Which harness runs a model is policy on the model or
the provider — `agents.defaults.models["<provider>/<model-id>"].agentRuntime.id`, or
`models.providers.<provider>.agentRuntime` — and CLI adapters are registered by plugins, not configured
under `agents.defaults`. The whole-agent forms (`agents.defaults.agentRuntime`,
`agents.entries.*.agentRuntime`, the session pin and the `OPENCLAW_AGENT_RUNTIME` variable) are legacy
and **ignored**: a config that still sets one runs on something other than what it says, with no error
(`doctor --fix` removes them). The `agents.defaults.cliBackends.<runtime-id>.command` form is gone with
them.

**Keys this page used to list that could not be confirmed** against the current upstream pages:
`agents.defaults.timeFormat`, and `contextTokens` under `agents.defaults` (the documented
`contextTokens` is per model, under `models.providers.<provider>.models[]`). Do **not** write either
until `openclaw config schema` on a test instance shows the path — under a strict schema an unknown key
is an outage, not a warning.

## channels

Per channel: `enabled`, the credential as a **secret reference**, `dmPolicy`
(pairing / allowlist / open / disabled), `allowFrom[]`, a per-conversation map (`groups`, `guilds`,
…) carrying `requireMention`, its own `allowFrom` and prompt overrides, plus transport knobs
(`historyLimit`, chunk limits, streaming mode).

Traps: `open` on a production instance is an exposure finding, not a preference. Identifiers in
`allowFrom` are channel-prefixed and easy to get subtly wrong — a wrong prefix reads as "nobody is
allowed" with no error. A channel token pasted literally is `fleet.config.literal-secret`.

## tools

| Path | Governs |
|---|---|
| `tools.profile` | the preset breadth of tool access |
| `tools.allow[]`, `tools.deny[]` | explicit tool names, wildcards, and `group:` families |
| `tools.exec.*` | execution and background timeouts |
| `tools.loopDetection.*` | enable plus warning and critical thresholds |

Trap: `allow` and `deny` interact with the profile rather than replacing it; verify the effective set
with the runtime, not by reading the three keys and reasoning about them.

## plugins and skills

| Path | Governs |
|---|---|
| `plugins.enabled`, `plugins.allow[]`, `plugins.deny[]` | the plugin system and its allowlist |
| `plugins.load.paths[]` | extra load directories — **a change here needs a restart** |
| `plugins.entries.<id>.{enabled,config,env}` | per-plugin state, config (secret refs, never values) and scoped env |
| `skills.allowBundled[]` | which bundled skills are on |
| `skills.load.extraDirs[]` | extra skill directories — **the lowest load priority** |
| `skills.entries.<id>` | per-skill config |

Traps: extra directories lose to every other source, so a leftover local copy shadows the shared one
and sharing only looks done (`fleet.shared.local-shadow`). A bind mount whose ownership the runtime
distrusts is refused as a candidate with the mount present and populated
(`fleet.shared.ownership-blocked`). Installing by copying files does not register anything
(`fleet.shared.install-global-invisible`).

## session

`session.dmScope` (main / per-peer / per-channel-peer / per-account-channel-peer) · `session.mainKey` ·
`session.reset.{mode,atHour,idleMinutes}` · `session.resetTriggers[]` ·
`session.maintenance.{mode,pruneAfter,maxEntries}`.

Trap: reset hours are **local to the gateway host**. An instance whose host clock is in another zone
than the operator resets at a different real time than the one written down.

## gateway

`gateway.port` (the container-side port is fixed at 18789; the host port is a publish mapping, not
this key) · `gateway.host` · `gateway.auth.token` · `gateway.reload.mode` (`off` or `hybrid`; `hybrid` is
the default).

Traps: `hot` and `restart` are **retired** values of the reload mode — `doctor --fix` maps both to
`hybrid`, and a config still carrying one is refused rather than warned about. Reload debounce and the
in-flight deferral are no longer configurable (the old keys are removed by `doctor --fix`). Everything
under `gateway.*` needs a restart. The bearer is **all-or-nothing operator access** —
one gateway is one trust boundary, so the token is unique per instance and never appears in a
plaintext file (`fleet.security.token-reuse`). `gateway.port` is part of the isolation set: unique per
instance, together with the config path, the state directory and the workspace.

## memory

`memory.search.provider` · `memory.search.model` · `memory.search.fallback` ·
`memory.search.query.maxResults` · `memory.search.query.minScore`; per-agent overrides sit at
`agents.entries.<id>.memory.search`.

Traps: the older `memory.embedding.*` / `memorySearch` names are retired and migrated into
`memory.search` (a per-agent `memorySearch` into `agents.entries.<id>.memory.search`), `provider: "auto"`
resolves to the OpenAI adapter, and a store-path key is gone because every index lives in its agent's
database. Hybrid retrieval is **always on** — there is no switch for it, only the two query limits. An
explicit `provider: "none"` is the deliberate full-text-only mode; leaving the provider unset is **not**
that, it selects the default adapter. Index identity is derived from the provider configuration
**including the key**, so changing the provider, model or key pauses vector search until an explicit
reindex (`fleet.memory.index-identity-changed`). An explicitly configured non-local provider fails
closed rather than quietly falling back to full-text search: no errors is evidence the vector path
works, not evidence that nothing is configured.

## cron

`cron.enabled` only. The jobs themselves live in the state store and are managed through the CLI —
which is why a file full of jobs and a runtime that lists none is a migration that never ran
(`fleet.cron.migration-not-applied`), and why an upgrade can duplicate entries without the config
changing at all (`fleet.cron.duplicates-after-upgrade`).

## env

`env.vars` (inline key/value) · `env.shellEnv.enabled` (import the process environment).

Trap: inline vars are the easiest place for a literal secret to appear. Secrets arrive by reference,
delivered by the injection wrapper; the config carries names.

## Migrated keys — a retired name is a refusal

The schema is strict, so a name upstream has retired stops the gateway rather than warning. `doctor
--fix` (R4 here, planned) rewrites them; the table is the shape of what it does, not a command to run
by hand. Confirm the current mapping on the instance (`config schema`, the upstream migration table)
before writing any of them.

| Retired | Current |
|---|---|
| `agents.list` (array) | `agents.entries` (object keyed by agent id) |
| top-level `defaultModel` | `agents.defaults.model` |
| `memorySearch`, `agents.defaults.memorySearch` | `memory.search` |
| `agents.entries.*.memorySearch` | `agents.entries.*.memory.search` |
| `gateway.reload.mode` of `hot` or `restart` | `hybrid` |
| `tools.exec.security` + `tools.exec.ask` | `tools.exec.mode` |
| `tools.exec.timeoutSec` | `tools.exec.timeoutSeconds` |
| `session.idleMinutes` | `session.reset.idleMinutes` |
| `session.maintenance.pruneDays` | `session.maintenance.pruneAfter` |
| `session.resetByType.dm` | `session.resetByType.direct` |
| `cron.failureDestination` | destination fields on `cron.failureAlert` |
| whole-agent runtime keys | model- or provider-scoped `agentRuntime` (see `agents`) |

Instances older than the cut-off `versions.py` reports cannot be migrated in one step: they cross the
bridge release first (`instance-upgrade`).

## Secret references

Every credential field takes a reference object rather than a value: a source, a provider and the
**id**, which is the variable name to resolve. The value never appears in the config, in a diff, in a
plan or in a transcript.

Verification is by name: the reference ids the config uses, against the variable names actually
delivered inside the container. Names only, never values — the difference of those two sets is
`fleet.secrets.delivery-short`, the reason a feature can be silently off while the config looks right.

## Composition

- `$include` — a file or a list of files, merged at read time to a bounded depth. Composition is
  read-only: programmatic writes land in the root file and shadow the include. Edit the file that
  defines the key.
- `${UPPERCASE}` substitution — string values only, uppercase names only. A lowercase name silently
  stays literal.
