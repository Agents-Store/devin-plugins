# Findings catalog

A contract, not a document. Four consumers read it, and each depends on a different column staying
stable.

| Consumer | Reads |
|---|---|
| `fleet-diagnostics` | symptom → id, plus the description under it |
| `report.py` | `sev`, for ordering and for the fleet rollup |
| `/openclaw-ops:repair --issue <id>` | the id, its fix, its risk class, its verification |
| the auditor agent | the whole row, to emit a ready-to-run repair line under each finding |

## Rules

- **Ids are stable.** A renamed id breaks stored reports and repair lines already pasted into
  tickets. Add ids, deprecate ids, never repurpose one.
- **Upstream ids pass through verbatim.** Checks emitted by the runtime's own lint and security audit
  carry their own `checkId` — families `fs.*`, `gateway.*`, `tools.exec.*`, `plugins.*`,
  `security.exposure.*` — with a message and a fix hint. Use what the live `--json` returned. Never
  compose an id in one of those families from memory.
- **`fleet.*` is ours**, and only for what upstream does not check: the zombie, wrapper drift, empty
  shared trees, the token-sink signature, skills shadowed by local copies, schedules duplicated by an
  upgrade, secret delivery falling short of what the config references.
- **One row is one repairable thing.** If the fix would branch on which of two causes it is, that is
  two findings.
- **No id, no repair.** A symptom that is not in this file cannot go through `/openclaw-ops:repair`.
  Add it first, together with the documentation citation the fix rests on.
- **One id space.** Every id `healthcheck.py` emits has a row here, spelled exactly the same way;
  the battery does not carry a private vocabulary that the report and `/repair` cannot resolve.
  The inclusion is mechanical, so check it rather than trusting it:

  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/catalog-check.py"
  ```
- **`risk` is the class of the fix**, from `gate.RISK_CLASSES`. Detection is always R0.
- **`verify` is a command whose result differs before and after.** "Looks fine now" is not a
  verification.

Severity — one vocabulary, four names, used by everything in this plugin:

`critical` (the instance is not doing its job, or a secret has left its boundary) → `high` (a
subsystem is dead, or a change does not do what it appears to) → `warn` (degradation, drift, growth) →
`info` (an inventory statement that needs a decision, not a repair).

`healthcheck.py` emits exactly these four, the `sev` column below states them, `report.py` orders and
filters by them (`--severity-min info|warn|high|critical`), and the auditor agent reports in that
order. There is no fifth spelling: a severity outside the four aborts the report with a named schema
error rather than quietly disappearing from it. Exit codes follow the same split — `5` means at least
one `critical` or `high` finding, `6` means `warn` findings only.

Every check below runs through `${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py <instance> --json -- <args>` or `fleet.py`. Command spellings
are intent: confirm them against this instance's own `--help` before quoting one, because they drift
between versions.

## Inventory and layout

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.inventory.alien` | info | `layout_profile` returns `alien`: the project matched the prefix but failed the marker set | none automatic — decide: adopt it into the config, or mark it `manage:false` with a note | the object appears in `discover --table` with a decision recorded in the config | R0 |
| `fleet.inventory.unmanaged` | info | present on the host, absent from `instances` in the config | add an entry with `manage`, `role`, `criticality` | `fleet.py config --diff` shows nothing under `added` | R0 |
| `fleet.inventory.not-deployed` | warn | named in the config, no compose project on the host (`ok:false`, "not deployed") | deploy it, or remove the entry | the record resolves with `ok:true`, or the diff is clean | R0 |
| `fleet.inventory.host-mismatch` | critical | recomputed `host_fingerprint` differs from the file | stop. Move to the right host, or re-run `/openclaw-ops:init` after reviewing detection | the plugin no longer reports read-only mode | R0 |
| `fleet.inventory.legacy-layout` | warn | profile `legacy`: recognisably OpenClaw, missing template markers | none here. Record it as a migration project; every mutation stays refused | the entry carries `role: legacy` and `manage:false` | R0 |
| `fleet.inventory.state-dir-fallback` | high | the running process's state dir differs from the one the compose file names — the resolver silently falls back to a legacy directory when the configured one is absent | restore the intended state dir in the compose file, then recreate | the process reports the intended state dir, and the config you edit is the one it reads | R2 |
| `fleet.inventory.discovery-failed` | high | the sweep could not describe the object at all: the record comes back carrying an error instead of a shape, so every other check on it is unavailable rather than clean | read the error first — an unreachable container runtime, a project mid-recreate, or a permission problem. Nothing else on this instance is trustworthy until it resolves | the record resolves with `ok:true` and carries a container id | R0 |
| `fleet.inventory.extra-mount` | warn | a mount whose destination matches no known role (`paths.extra[]`) | explain it in the instance `notes`, or remove it | `paths.extra` is empty, or every entry is documented | R2 |

## Container, endpoints and the health rollup

The lowest layer of the battery, and the one a self-report cannot cover: a container that is not
there, an endpoint that does not answer, a rollup that says `ok:false`. The three endpoints answer
three different questions and are not interchangeable — the liveness endpoint proves only that the
HTTP server is up, the startup endpoint adds "startup finished" and deliberately ignores channel
health, and only the readiness endpoint means the channels passed a deep check, and only **with a
bearer token**.

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.container.absent` | critical | the compose project resolves and no gateway container exists under it | recreate the service through compose. Never hand-start a container beside it: it comes up without the mounts, so it reads a different state directory than the one being audited | a container exists for the project and reaches running | R2 |
| `fleet.container.down` | critical | the container exists and its state is not `running` | read the exit code and the **first** failed start before touching it. Zero restart attempts before the cause is named (`gate.RETRY_RULES`) — a restart during a crash loop overwrites the log holding the cause | the container runs and stays up across a full healthcheck interval | R2 after the cause is known |
| `fleet.container.unhealthy` | warn | the container runs and its own healthcheck reports unhealthy | read what the healthcheck command returns. An unhealthy verdict over a gateway that answers its endpoints is usually a misconfigured probe, not a dead gateway — fix whichever of the two is actually wrong | the container health returns healthy and the endpoints agree | R2 |
| `fleet.probe.unreachable` | warn | the probe battery could not be executed inside the container at all | usually the container is not running or exec is refused. Resolve that first; until then HEALTH rests on the CLI reads alone and the report says so | the battery returns a client name and a status per endpoint | R0 |
| `fleet.probe.no-http-client` | info | no HTTP client exists inside the container, so the endpoint probes were skipped | none required. Either accept CLI-only evidence for this instance, or add a client to the image if endpoint evidence has to be comparable across the fleet | the battery reports which client it used | R0 |
| `fleet.probe.healthz-fail` | critical | the liveness endpoint does not answer 200: the HTTP server itself is not serving | treat as a down gateway, not as a probe problem — read the startup log | the endpoint answers 200 | R2 after the cause is known |
| `fleet.probe.startupz-fail` | high | the startup endpoint does not answer 200: startup has not finished. It ignores channel health, so this is about the process, not the channels | read the startup log for the step it is stuck on; a gateway stopped by its own startup repair is `fleet.upgrade.gateway-stopped`, not this | the endpoint answers 200 and stays there | R2 |
| `fleet.probe.readyz-fail` | high | the readiness endpoint answers non-200 **with** a bearer, so the body carries the list of channels that failed the deep check | act on the named channels. An unauthenticated negative is a different finding (`fleet.liveness.health-vs-ready`) because it names nothing | readiness answers 200 with an empty failure list | R2 |
| `fleet.probe.token-absent` | info | no gateway bearer token was found in the container environment under any known name, so the authenticated readiness probe was skipped | point the battery at the variable holding the token, or add it to the container environment. The value is read inside the container and only the variable NAME is ever printed | the report names the token variable and the authenticated readiness probe ran | R0 |
| `fleet.health.not-ok` | high | the health rollup reports `ok:false` while the delivery queues are clear, so the negative comes from a subsystem rather than from backlog | read the rollup's own detail for the failing subsystem and follow that family's row | the rollup reports `ok:true` | depends on the underlying finding |

## Liveness

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.liveness.zombie` | critical | container running and health green, log age above `policy.stale_log_hours`, and at least one corroborating signal: empty config, short secret delivery, no schedule fired | triage before repair — the zombie is a symptom of one of the auth, secret or config findings. Fix that one; do not restart to "wake it up" | log advances, a schedule fires, session count moves | depends on the underlying finding |
| `fleet.liveness.health-vs-ready` | warn | the healthcheck and the readiness endpoint disagree, or readiness returns a bare negative | query readiness **with the bearer** to get the reason list, then act on the reason | readiness returns a positive with an empty reason list | R0 to detect |
| `fleet.liveness.queue-backlog` | high | rollup reports healthy while a delivery queue keeps growing | drain or fix the channel behind the queue | queue depth returns to its baseline and stays there across two samples | R2 |
| `fleet.liveness.crash-loop` | critical | restart count above the threshold with health unhealthy | read the **first** failed start, not the latest. Zero restart attempts before that (`gate.RETRY_RULES`) | the container reaches running and stays there for a full healthcheck interval | R2 after the cause is known |
| `fleet.liveness.evidence-conflict` | warn | the log has not moved past the stale threshold while the index was written inside the idle window: the two outside observers disagree about whether this instance works | do not average them. Find out which subsystem is still moving and which stopped — one moving subsystem must never vouch for a gateway that stopped serving | both observers agree, or the report states which one is authoritative here and why | R0 |
| `fleet.liveness.log-unreadable` | warn | the gateway log carries no readable timestamp, so LIVENESS rests on the index write time alone | restore timestamped logging. Until then every age on this instance is weaker evidence, and the zombie test loses its primary witness | the log yields a parseable timestamp and LIVENESS names the log as its evidence | R2 |
| `fleet.liveness.orphan-activity` | warn | the gateway is down and its log moved recently: something else is still writing under this instance's name | find the writer before recreating anything — a second process on the same state directory corrupts it | only the intended process writes there | R0 |
| `fleet.liveness.quiet` | info | healthy and idle past the idle threshold | none. Expected on an instance with no schedules; it is recorded so that "quiet" is a stated decision rather than an unnoticed slide toward stale | the instance carries a note saying it has no scheduled work, or a schedule starts firing | R0 |

## Config

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.config.empty` | critical | `signals.config_present` false, or `config_bytes` below the sanity floor, on a running instance | restore from the plugin snapshot or the reference baseline, never by hand-writing a new one | config parses, lint is clean, the instance resumes work | R2 |
| `fleet.config.literal-secret` | critical | a value in the config matches a key class instead of being a secret reference | replace with a reference by name, deliver the value through the secret store, then **rotate** it — it has been on disk | the config holds no value-shaped strings; the feature still works | R3 |
| `fleet.config.deletions` | high | a proposed edit removes lines: the CHANGE block's deletion count is non-zero | do not apply. Explain each deletion, or rewrite the edit as additive | the plan's deletion count is zero, or every deletion is justified in the plan | R2 |
| `fleet.config.legacy-model-ref` | warn | models referenced in the old combined runtime-and-model form | rewrite as a provider reference plus a runtime override; the legacy form still works, so this is not urgent | the config carries provider references, the chain still resolves | R2 |
| `fleet.config.model-id-unverified` | high | a model id in the config that this instance's model catalogue does not list | pin an id that the catalogue actually returns. Every model id entering a diff must be an echo from the box | the id appears in the catalogue; the chain resolves | R2 |
| `fleet.config.bak-ring-pressure` | warn | the CLI's own backup ring is at capacity, so the next automated edit evicts the oldest entry | take a plugin snapshot outside the ring before editing, and say in the plan which ring entry will be evicted | a snapshot exists in `policy.snapshot_dir` with its fingerprint recorded | R0 |

## Provider auth

The whole family shares one retry rule: **zero attempts**. A repeated login or refresh burns a
single-use token and logs out another consumer. Detection reads expiry and fingerprints from stored
profiles; it never triggers a refresh to "see if it works".

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.auth.token-sink` | critical | one account identifier fingerprint appearing across several separate credential directories: several copies of one account, each rotating a single-use refresh token and invalidating the others | give the chain exactly one owner: one host directory mounted into every container as the credential directory, mount the **directory** not the file. Log in once, from the owner directory, and register the backend on each instance | one fingerprint, one directory, credential check clean on every instance across two rotation cycles | R2 (compose change) — the login itself is printed for a human, never run by the plugin |
| `fleet.auth.emptied` | critical | the credential block exists, its token strings are empty and the expiry is zero — the sink after it fired | one login from the owner directory | structure-only read shows non-empty tokens and a real expiry | R1 |
| `fleet.auth.expired` | critical | credential check exits 1 **and its document names an expired or missing credential**. A CLI-backed route (claude-cli, codex) exits 1 with every flagged route `indeterminate` — that is `fleet.auth.check-inconclusive`, not this | log in again from the owner directory; meanwhile demote the dead entry so every request stops paying the retry-and-cooldown ladder | check exits 0 | R1 |
| `fleet.auth.expiring` | high | credential check exits 2, or expiry is inside the warning window | one touch refresh, from the owner directory, under a fleet-level front lock — the runtime's own lock is local to one state directory | expiry moves forward; no other consumer got logged out | R1 |
| `fleet.auth.shadowed` | high | a static-token profile exists for a provider whose chain intends the CLI backend — the embedded path wins and billing moves to metered tokens with no config change | remove the shadowing profile | the provider resolves through the CLI backend; metered usage returns to its baseline | R2 |
| `fleet.auth.orphan-runtime` | high | the config names a CLI backend whose binary is not resolvable inside the container | mount the binary, or change the runtime; the gateway must resolve it on PATH | `command -v` finds it inside the container and the chain resolves | R2 |
| `fleet.auth.check-inconclusive` | warn | the credential check exits a code the exit-code table does not map, so neither "valid" nor "expired" was established | read the command's own output. Do **not** trigger a login or a refresh to find out — the whole family is zero-attempt, and a probing refresh burns a single-use token | the check exits a mapped code | R0 |
| `fleet.auth.dead-profile` | warn | a profile that can no longer authenticate is still in the rotation, costing a retry and a cooldown on every request | remove it. Rotation runs through every profile of a provider **before** moving to the next model | first-attempt success rate returns to normal; cooldown events drop | R2 |
| `fleet.auth.account-drift` | warn | the account identifier fingerprint changed between two snapshots | find out who logged in with a different account before changing anything | the fingerprint matches the intended account | R0 |
| `fleet.auth.owner-ambiguous` | high | more than one process can refresh the same chain: several credential directories writable by different instances, no declared owner | declare and enforce one owner; the others re-read | only one path can write; the others are read-only mounts | R2 |
| `fleet.auth.oauth-copied` | high | an OAuth profile appears identical on two instances — someone copied a profile file | remove the copy and log in properly. API-key and static-token entries are portable; OAuth entries are not | each instance has its own profile, or shares one owner directory by mount, not by copy | R2 |

## Model chain

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.model.primary-overwritten` | critical | after an upgrade the primary reference changed and the runtime override is gone; symptom arrives later as an expired-session error | restore the reference and its runtime override from the pre-upgrade snapshot | the config carries the runtime override; requests resolve to the intended backend | R2 |
| `fleet.model.agent-override-strict` | high | an agent carries its own primary and no fallbacks of its own, which makes it strict and silently cancels the fleet chain for that agent | give the agent fallbacks, or remove the override | all three levels — default, per agent, per schedule — agree with the intended chain | R2 |
| `fleet.model.cron-pinned-dead` | high | a schedule payload pins a model the catalogue no longer lists | repin to a catalogued id, or drop the pin so it inherits | the schedule runs to completion | R2 |
| `fleet.model.fallback-burn` | high | fallback and cooldown events over 24h are far from zero: the chain is formally applied and the fleet actually lives on its reserve | fix the primary — this is a symptom of an auth finding, not a chain finding | fallback events return near zero over a full day | depends on the underlying finding |
| `fleet.model.disabled-until` | high | a provider carries a long disabled-until marker, the signature of billing failures | fix billing, then clear or wait out the backoff | the marker is gone and the provider answers | R2 |
| `fleet.model.chain-unpinned` | warn | the chain follows a moving alias instead of a pinned model id | pin ids that the catalogue returns; an automatic move to a new model on production is a surprise in price and behaviour | ids in the config match ids in the catalogue exactly | R2 |

## Memory and embeddings

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.memory.embeddings-unauthorized` | critical | every embedding call fails authorization — typically a session credential presented where an API key is required; subscription OAuth covers chat completions and does not satisfy embedding requests | give the instance its own embedding API key through the secret store, reference it by name in the config, then **fully restart** the gateway | an embedding call succeeds; indexing resumes | R3 (key change forces a reindex) |
| `fleet.memory.index-identity-changed` | high | vector search paused with an index-identity warning after a provider, model or chunking change — including a key change | reindex explicitly, one instance at a time, outside peak hours | search returns vector hits again; the warning is gone | R3 |
| `fleet.memory.index-clock-skew` | warn | the last index timestamp is in the future relative to this host's clock | fix the clock on whichever side is wrong. A skew of this size makes every age in the report — log age, index age, finding age, the stale gate — unreliable, so treat it as blocking for age-based conclusions | timestamps are in the past and the two clocks agree | R2 |
| `fleet.memory.stale-index` | warn | last index timestamp far behind current activity | reindex after fixing the cause; a reindex over a broken provider just fails slower | index timestamp tracks activity | R3 |
| `fleet.memory.search-stuck-fallback` | high | search stays degraded after the provider was fixed: it is stuck on the fallback model, and only a full restart clears it | full restart, not a reload | quality returns and stays after the restart | R2 |
| `fleet.memory.db-growth` | warn | the state database grows without bound: chunk and embedding-cache tables have neither retention nor LRU, and embeddings are stored as text | operator retention procedure, **explicitly not supported upstream**: back up, stop the gateway, delete old rows from the embedding **cache** only, compact, start, smoke test. Never touch the index itself | database shrinks, search still returns hits after the smoke test | R3 |
| `fleet.memory.fail-closed-silent` | info | an explicitly configured non-local provider fails closed rather than falling back to full-text — no error is not the same as no problem | none. This is intended behaviour; treat the absence of errors as evidence the vector path really works | vector hits appear in results | R0 |

## Schedules

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.cron.duplicates-after-upgrade` | critical | entries group by name and schedule with more than one member; copies are enabled, fire two or three times per tick, and have lost their agent binding | in each group keep the entry with a non-empty agent binding and disable the rest. Extra care where a schedule moves money | one entry per group, each with a binding; one fire per tick | R2 with a backup |
| `fleet.cron.orphaned-agent` | warn | timers carry no agent binding, with no duplicate group to explain it — a timer whose `sessionTarget` is `isolated` has no binding by construction and is not counted | rebind each entry to its agent. An unbound schedule fires and resolves to nothing, which looks like a working timer from every angle except its output | every entry carries a binding, and a fire produces its output | R2 |
| `fleet.cron.night-stall` | high | timers stall for hours on a nightly cadence and then catch up; the process stays active and green the whole time | no upstream fix. Keep the history — expected versus actual fire time per job — and alert on drift. This is only visible to an outside observer with memory | drift stays inside the threshold across several nights | R0 |
| `fleet.cron.timer-dead-after-timeouts` | high | one timer stopped firing permanently after a run of timeouts | recreate the entry | it fires on the next tick | R2 |
| `fleet.cron.all-failing` | critical | every job on the instance fails | not a scheduling problem: check the model chain and credentials first | jobs complete once the chain is fixed | depends on the underlying finding |
| `fleet.cron.migration-not-applied` | high | jobs exist in the file and the runtime lists none — the migration into the store never ran | run the migration, then verify the count on both sides | file count equals runtime count | R2 |
| `fleet.cron.money-job-unguarded` | high | a revenue-bearing schedule on an instance with `criticality: high` sits in the same maintenance window as everything else | give it its own window; never batch it with the fleet | the schedule is excluded from batch targets | R0 |

## Secrets delivery

Nothing in this family ever prints a value. Presence, fingerprint, size bucket, expiry and key name
answer every question; that is a hard rule, not a preference.

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.secrets.delivery-short` | critical | required reference names minus delivered key names is non-empty — the feature is silently dead | fix delivery (identity, project, environment), never by pasting the value into the config | the difference is empty; the feature works | R2 |
| `fleet.secrets.wrong-project` | critical | delivered key count far below `secrets.expected_key_count` and below sibling instances | point the identity at the right project and environment | the count matches siblings and the expected value | R2 |
| `fleet.secrets.identity-broken` | critical | the injection wrapper cannot mint a token; the container starts with almost no keys | repair the identity file — one per instance, mode 0600, owned by root | delivery returns the full key set | R2 |
| `fleet.secrets.plaintext-env` | high | plaintext key-shaped values in a file inside the state tree | classify first: fingerprint parity with the store makes it **redundant**; no parity makes it **load-bearing** and deleting it takes the instance down. Neutralise a redundant one by moving it to quarantine outside the container's volumes — never `rm` | the instance keeps working with the file moved away, and delivery still supplies every referenced key | R3, red line `delete-plaintext-env` |
| `fleet.secrets.leaked-in-backup` | critical | a backup or identity copy contains a token- or client-shaped value | **rotate** it. Deleting the file does not un-leak the value | the old fingerprint no longer authenticates; the new one is delivered everywhere it is needed | R4 |
| `fleet.secrets.identity-file-mode` | high | the identity file is readable or writable beyond root | tighten to 0600, owner root | the mode check passes | R2 |
| `fleet.secrets.shared-store-plaintext` | info | store values are not encrypted at rest; anyone with host access reads them | none technically. Record it in the trust-boundary section of the audit so it is a decision, not a surprise | the audit report states it explicitly | R0 |

## Shared skills and plugins

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.shared.empty-mount` | high | the shared trees are mounted and registered in config, and they are empty: sharing exists on paper only | populate them with the canonical copies, owned so the runtime accepts them | the trees list content from **inside** the container and loaded assets resolve to the shared path | R2 |
| `fleet.shared.plugins-none` | info | the instance loads no plugins at all | decide, do not repair blindly: a plugin-free instance is legitimate, but on an instance whose siblings share a tree it means the mount or the registration never took (`fleet.shared.empty-mount`, `fleet.shared.install-global-invisible`) | the loaded list matches what this instance is meant to run, or a note records that it runs none | R0 |
| `fleet.shared.duplicate-skill` | warn | the same skill exists on N instances with identical content on all N | promote one canonical copy into the shared tree, then remove the shadows by moving them | one copy on disk, N instances loading it from the shared path | R2 |
| `fleet.shared.local-shadow` | high | a per-instance copy shadows the shared one: extra directories are the **lowest** load priority, so sharing looks live while the old copies are what runs | move the local copy away, do not delete it. **If its content differs from the shared one, stop** — automation does not get to decide whose version is right; report the divergence | the loaded asset's path is the shared one | R2 |
| `fleet.shared.ownership-blocked` | high | a candidate is refused for suspicious ownership on the bind mount: mounted, present, and silently inactive | align ownership on the host side | the candidate loads; the refusal disappears from the log | R2 |
| `fleet.shared.plugins-load-no-restart` | warn | plugin load paths changed after the process started — changes to them require a restart | restart the gateway | the loaded plugin list reflects the config | R2 |
| `fleet.shared.install-global-invisible` | high | files installed by a global copy exist on disk and nothing is registered | manage shared assets by file layout plus config, never by the global install path | the asset appears in the registered list, not just on disk | R2 |
| `fleet.shared.lock-corrupt` | critical | the install lock file is unreadable or inconsistent — the next install removes the other assets | **stop**. Back up and read the lock before any install (`gate.RETRY_RULES`: zero attempts) | the lock parses and lists what is actually installed | R3 |

## Versions and upgrades

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.version.drift` | warn | instances report different versions | plan waves: reference first, then low-load, then loaded, then the money instance in its own window | versions converge, with the drift consciously left where it belongs | R4 per instance |
| `fleet.version.unknown` | warn | the runtime did not report a version | find out why before any upgrade: drift, the soak gate and the rollback target all reason about a version, so an unknown one silently excludes this instance from every version decision | the instance reports a version and appears in the drift table | R0 |
| `fleet.version.channel-misread` | high | the target was chosen by version ordering or by release dates rather than by registry dist-tags — ordering skips correction releases, release dates hand back the trailing channel | resolve the target from dist-tags only | the target matches the dist-tag for `policy.update_channel` | R0 |
| `fleet.version.soak-not-met` | high | the target was promoted less than `policy.soak_days` ago, or a correction release followed it | wait, or pick the previous accepted version | the soak gate passes | R0 |
| `fleet.version.moving-tag-pin` | high | the deployment pins a moving tag, which is rebuilt on its own schedule: what runs is not what was reviewed | pin a plain version or a digest (`gate.pin`, `gate.is_moving_tag`) | the running digest matches the recorded pin | R2 |
| `fleet.upgrade.no-verified-backup` | critical | an upgrade is proposed without a backup that passed verification | **reject**, do not warn. State-schema migration happens in place with no pre-migration backup, so the tar of a stopped state directory is the only real rollback | a verified backup exists, with path and fingerprint in the BACKUP block | red line `upgrade-without-verified-backup` |
| `fleet.upgrade.gateway-stopped` | critical | the gateway is stopped after an upgrade — by design, when startup repairs cannot complete safely | treat it as a failed upgrade: read the startup log, restore from the backup. Zero restart retries | the gateway starts and stays up, or the restore completes | R4 |
| `fleet.upgrade.new-lint-findings` | high | post-upgrade lint reports findings that were not in the pre-upgrade baseline | act on the **new** ones only; a pre-existing finding must not block every future upgrade | the new-findings set is empty | R2 |
| `fleet.upgrade.batch-widened` | critical | a batch touched more than the canary in one step | stop the batch. Anything past the canary needs its own confirmation | the plan's target list is one instance | red line `fleet-wide-mutation` |

## Wrappers

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.wrapper.drift` | warn | a site wrapper is missing a verb its siblings have — the template moved on and the clones did not | update the wrapper from the template. **Never reimplement the verb inside this plugin**: it encodes site knowledge the plugin does not have | the verb list matches across managed instances | R2 |
| `fleet.wrapper.absent` | info | no wrapper for an instance that should have one | create it from the template, or record that this instance does not use one | `capabilities.wrapper` is true, or the exception is in `notes` | R2 |

## Security and exposure

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.security.port-non-loopback` | critical | a published gateway port does not bind to loopback while `policy.loopback_only` is set — images publish outward by default | republish on loopback | `port.loopback` is true on every managed instance | R2 |
| `fleet.security.docker-user-chain` | high | container-aware firewall rules are absent: published ports bypass the ordinary input chain, so a host firewall that looks correct is not applied to them | add the rules to the container-aware chain | a probe from off-host is refused | R2 |
| `fleet.security.token-reuse` | critical | the same operator bearer token fingerprint on more than one instance — the trust boundary is one per gateway, and access is all-or-nothing | issue a unique token per instance | fingerprints differ per instance | R4, red line `gateway-token-rotation` |
| `fleet.security.metrics-unauthenticated` | critical | the metrics endpoint answers without a bearer | require the bearer; scrape from inside the container so the token never leaves the gateway | an unauthenticated request is refused | R2 |
| `fleet.security.state-perms` | high | state or auth-secret directories are readable beyond their owner | tighten the modes | the permission check passes | R2 |
| `fleet.security.capability-consent-pending` | info | the runtime is waiting on capability consent | **print** the consent line for a human. Never pass the accept flag; upstream deliberately made bulk-approval flags unable to grant consent | the operator ran it; the pending state clears | R0 |

## Upstream pass-through families

These come from the runtime, with their own id, message and fix hint. Carry all three into the report
unchanged; add the instance and the evidence around them.

| Family | Emitted by | Operational reading |
|---|---|---|
| `fs.*` | lint, security audit | paths, permissions, ownership on the state tree and its mounts |
| `gateway.*` | lint, security audit | gateway configuration, binding, authentication |
| `tools.exec.*` | security audit | what the agent is permitted to execute |
| `plugins.*` | lint, security audit | plugin loading, registration, trust |
| `security.exposure.*` | security audit | what is reachable from outside the intended boundary |

One id belongs to us inside this family: a lint finding that arrives **without** a `checkId` cannot be
passed through verbatim, because there is nothing to pass through.

| id | sev | detect | fix | verify | risk |
|---|---|---|---|---|---|
| `fleet.lint.unclassified` | warn | the runtime's lint returned a finding carrying no `checkId` | read the message and the path it names, then find the matching documented check. Never invent an id in one of the upstream families to file it under | the same run reports the finding with an id, or a row is added here for a symptom upstream does not check | R0 |

Two rules for pass-through findings: the automatic repair flags of lint and security audit are a red
line (`doctor-fix-or-security-fix`) — narrow, opaque, and they choose what they touch, so they are
`--yes` plus a typed confirmation, never a default. And a finding whose fix hint is missing or unclear
needs the relevant documentation page fetched and **quoted in the report**: no citation, no action.
