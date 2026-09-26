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
| `agents` | agent defaults and the per-agent list |
| `channels` | where conversations arrive from |
| `tools` | which tools an agent may call, and their execution limits |
| `plugins` | plugin system, allow/deny, load paths, per-plugin config |
| `skills` | bundled skill selection, extra directories, per-skill config |
| `hooks` | lifecycle hooks |
| `session` | session scoping, reset and maintenance |
| `cron` | whether the scheduler runs — the jobs live in the state store, not here |
| `gateway` | the HTTP surface: bind, port, auth, reload behaviour |
| `memory` | embedding provider and search mode |
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
| `agents.defaults.timeoutSeconds`, `maxConcurrent`, `contextTokens`, `thinkingDefault` | number/string | execution envelope |
| `agents.defaults.userTimezone`, `timeFormat` | string | IANA zone, clock format |
| `agents.defaults.cliBackends.<runtime-id>.command` | string | explicit binary path when the runtime is not resolvable on PATH |
| `agents.list[]` | array | per-agent `id`, `default`, `name`, `workspace`, `model`, `identity`, `sandbox` |

Traps: a per-agent `model` **without its own** `fallbacks` is strict — it silently cancels the fleet
chain for that agent (`fleet.model.agent-override-strict`). A heartbeat pinned to a model that left the
catalogue fails on a schedule nobody watches. `agent.skipBootstrap` (singular, at root) is a different
key from anything under `agents.defaults`.

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
this key) · `gateway.host` · `gateway.auth.token` · `gateway.reload.mode` (hot / restart / hybrid /
off).

Traps: everything under `gateway.*` needs a restart. The bearer is **all-or-nothing operator access** —
one gateway is one trust boundary, so the token is unique per instance and never appears in a
plaintext file (`fleet.security.token-reuse`). `gateway.port` is part of the isolation set: unique per
instance, together with the config path, the state directory and the workspace.

## memory

`memory.embedding.provider` · `memory.embedding.model` · `memory.search.hybrid`.

Traps: index identity is derived from the provider configuration **including the key**, so changing
any of the three — key included — pauses vector search until an explicit reindex
(`fleet.memory.index-identity-changed`). An explicitly configured non-local provider fails closed
rather than quietly falling back to full-text search: no errors is evidence the vector path works,
not evidence that nothing is configured.

## cron

`cron.enabled` only. The jobs themselves live in the state store and are managed through the CLI —
which is why a file full of jobs and a runtime that lists none is a migration that never ran
(`fleet.cron.migration-not-applied`), and why an upgrade can duplicate entries without the config
changing at all (`fleet.cron.duplicates-after-upgrade`).

## env

`env.vars` (inline key/value) · `env.shellEnv.enabled` (import the process environment).

Trap: inline vars are the easiest place for a literal secret to appear. Secrets arrive by reference,
delivered by the injection wrapper; the config carries names.

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
