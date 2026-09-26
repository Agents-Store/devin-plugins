# Scenario: first run on an unfamiliar host

You are on a host that runs OpenClaw instances. You do not know how many, what they are called, which
one matters, or what is broken. Nothing on this page changes anything: the whole scenario is read-only
by construction, and the artifact at the end is a baseline snapshot everything later is compared to.

All names, ports and paths below are invented.

## Step 0 — is this even the right host

| Run | Skill | What proves it |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}/scripts/fleet.py config --show` | `fleet-model` | exit 2 means no config anywhere on the ladder — expected on first contact. A config that loads but reports `readonly` with a host mismatch means this file was written for a **different** machine, and every path in it is a guess |

A host mismatch is not a warning to click through. Re-run `config --init` here; never edit the recorded
fingerprint to make the complaint stop.

## Step 1 — inventory before opinions

```
${CLAUDE_PLUGIN_ROOT}/scripts/fleet.py discover --table
```

Reads `docker compose ls --all`, so a **stopped** instance is still an instance. Exit 1 means docker
itself is unreachable — stop, that is a host problem, not a fleet problem.

```
NAME         STATE     PROFILE   ROLE     MANAGED  PORT               VERSION  HEALTH  LOG-AGE  NOTE
alpha        ok        template  unknown  true     127.0.0.1:<port-a>  <ver>   ok      0.2h
beta         ok        template  unknown  true     127.0.0.1:<port-b>  <ver>   ok      1.1h
gamma        ok        template  unknown  true     127.0.0.1:<port-c>  <ver>   ok      0.4h
delta        degraded  template  unknown  true     127.0.0.1:<port-d>  <ver>   ok      —        log has not moved
legacy-one   ok        legacy    unknown  true     127.0.0.1:<port-e>  <ver>   ok      2.0h     legacy layout
neighbour-x  ok        alien     unknown  true     0.0.0.0:8080        —       —       —        failed layout markers
```

Read it in this order, because each row changes what the next one means:

1. **`alien`** — matched the prefix, failed the layout fingerprint. It is printed on purpose: an
   invisible object on the host is worse than an unexplained one (`fleet.inventory.alien`).
2. **`legacy`** — the same product, a different deployment shape. Inventory yes, mutation never.
3. **`degraded` with a green container** — the reason this plugin exists. Do not resolve it here.
4. **A non-loopback publication** on any row is a security finding today, whether or not the instance
   is up: a stopped instance still owns its publication in its compose file.

## Step 2 — write the fleet config

Autodetect fills what it can read. The four things it cannot read are decisions:

| Decision | Why no host can answer it |
|---|---|
| `reference` | which instance is the shape the others are compared against |
| `canary` | which one may break first — lowest criticality, no revenue-bearing schedule |
| `manage: false` | which instances are deliberately out of scope |
| `criticality` | what an outage of this one costs |

```
${CLAUDE_PLUGIN_ROOT}/scripts/fleet.py config --init --detect-only          # look first
${CLAUDE_PLUGIN_ROOT}/scripts/fleet.py config --init --reference alpha --canary beta --out <path>
${CLAUDE_PLUGIN_ROOT}/scripts/fleet.py config --validate
```

Written 0600, outside the plugin repository, with a host fingerprint. Group- or world-writable is
fatal, not a warning: that file decides which instances are mutable. `legacy-one` cannot be
`manage:true`, and there is exactly one reference and one canary — the validator enforces both.

## Step 3 — health is not liveness

```
${CLAUDE_PLUGIN_ROOT}/scripts/healthcheck.py --table
```

`HEALTH` is what the instance says about itself. `LIVENESS` is what an outside observer sees it **do**.
The columns are printed side by side because the disagreement is the finding (`VERSION`, `CREDS` and
`PLUGINS` elided here for width):

```
NAME   STATE     HEALTH  LIVENESS              CRON   MEM-DB  LOG-AGE  FINDINGS
alpha  ok        ok      ok                    1/1    6MB     0.2h     -
beta   ok        ok      ok                    3/3    8MB     1.1h     -
gamma  ok        ok      ok                    10/10  118MB   0.4h     warn:1
delta  degraded  ok      stale  <-- diverges   0/0    -       —        warn:1 critical:1
```

`delta` answers every probe and has done no work since some date: that is
`fleet.liveness.zombie`, and no additional HTTP probe will ever reveal it. Exit 5 means at least one
`critical` or `high` finding, 6 means `warn` only — a monitor reads the exit code, a human reads the
table.

## Step 4 — version truth, not version feelings

```
${CLAUDE_PLUGIN_ROOT}/scripts/versions.py --table
```

Channel resolution comes from the package registry dist-tags; promotion age comes from the release
entry for that exact version; what is actually running comes from the **image digest**, not the tag it
was pulled by. `--no-net` still gives you the installed-version drift across the fleet, and says so.
Do not restate a version from memory afterwards — quote the run, dated (`docs-research`).

## Step 5 — the security pass nobody runs

Layer one, per instance, R0:

```
${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py alpha --json -- security audit --deep
```

Layer two is the one the runtime structurally cannot make: loopback publication, whether the
container-aware firewall chain has any rule at all, operator-token uniqueness by fingerprint,
permissions on state and credential trees, metrics behind the bearer (`security-audit`). A clean
layer-one audit on an instance published on all interfaces is a clean report about the wrong question.

## Step 6 — the baseline artifact

```
${CLAUDE_PLUGIN_ROOT}/scripts/healthcheck.py --json --snapshot > /dev/null
${CLAUDE_PLUGIN_ROOT}/scripts/report.py --format md --out <path>
```

The first report has no delta by definition. Its value is that the second one will: "gamma's memory
database grew 60 MB in a week" is a sentence no single run can produce.

## What must not happen on first contact

- No `--yes`, anywhere. Nothing on this host has earned trust yet.
- No restart "just to see". A restart on an instance whose secret delivery is broken converts a
  working instance into a dead one, and erases the log lines that explain why.
- No `models status --probe`: it requires a stopped gateway. The monitoring form is `--check`.
- No chat or completion request as a health check — each one opens a full agent session.
- No conclusions about `delta` yet. Triage is `fleet-diagnostics`; first contact only names it.

## Verify the run changed nothing

Config file mtimes, container restart counts and the compose project list are identical before and
after. If any of them moved, something in the session was not read-only, and finding out what matters
more than the inventory you just collected.
