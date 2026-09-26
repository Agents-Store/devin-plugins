# Scenario: clone the reference and prove the isolation

A new workload needs its own instance. The deterministic half takes minutes; the half that decides
whether the clone actually works is manual and is the half people skip. This scenario ends with the
proof, not with the files.

## Step 0 — clone the reference, not the nearest instance

A clone inherits every unfixed finding of its source. Cloning the instance that happened to be in the
terminal produces a second copy of that instance's problems, and cloning a zombie produces a second
zombie. If the reference is not healthy, that is the work — the clone waits.

Cloning `legacy-one` is refused: only a template-layout instance is a usable source, and re-creating
the legacy shape multiplies a migration project.

## Step 1 — plan, and read the preflight even when it passes

```
${CLAUDE_PLUGIN_ROOT}/scripts/clone.py epsilon --from alpha --port auto --plan
```

Five properties must be unique per gateway, and the fifth depends on the network mode:

| Property | Why a collision is quiet |
|---|---|
| config path | both instances read one file; an edit meant for one lands on both |
| state directory | startup enforces unique state-directory ownership, so the **second to start loses**. The clone looks fine today; something else breaks tomorrow |
| agents workspace | two instances writing one workspace corrupt each other's working state |
| published host port | the second publication fails at start, or binds somewhere you did not intend |
| in-container port | only if the source runs with host networking — then the published-port check does not cover it |

**An unknown value is a failed requirement.** Uniqueness that could not be asserted has not been
established. Exit 5 is a failed preflight, and a failed preflight is the script working.

The rows are printed on success too, precisely so they get read.

## Step 2 — a free port means free by four measures

Not published by any container on this host · not written into any compose file of the fleet, because
a **stopped** instance still owns its port · not bindable-in-use right now · not already claimed by
another entry in the fleet config. Any one measure alone passes on a port another instance owns.

The publication is on loopback. Images publish outward by default, and a clone is the easiest place in
the whole fleet to lose that (`fleet.security.port-non-loopback`).

## Step 3 — apply, in a later turn

```
${CLAUDE_PLUGIN_ROOT}/scripts/clone.py epsilon --from alpha --port auto --apply --yes
```

What it does: name validation, port selection, preflight, materialising the compose directory, the
state directories and a patched config; credential directories created **empty**, owner-only.

What it will not do: mint an identity, create or copy a secret value, perform a login, apply the model
chain, register skills or plugins, or start anything. Those are printed as remaining steps. A printed
step is honest; a silently skipped one is how a clone ends up looking finished with no credentials.

**Credentials are never copied.** A static key or token would survive a copy; an OAuth profile would
not, and copying one gives two instances a single refresh chain — the exact configuration that logs
one of them out at the next rotation (`fleet.auth.oauth-copied`).

## Step 4 — the manual half

Full text with verifications and failure modes:
`instance-clone/references/post-clone-checklist.md`. In order:

1. machine identity with read access to the same secret project;
2. the per-instance secrets the source's config references, compared by **name and count**;
3. provider logins, printed and run by the credential owner, never copied;
4. the model chain at all three levels — defaults, per-agent, per-schedule — with every model id an
   echo from this instance's own catalogue (`docs-research`);
5. shared skills and plugins registered by path; plugin load paths need a **restart**, not a reload;
6. the fleet config entry: role, criticality, aliases — a clone meant to be the canary is only the
   canary once the policy names it;
7. bring it up, run the health battery, and only then give it work.

Skipping step 1 produces the classic outcome: green health, no work, three delivered keys instead of
the source's full set (`fleet.secrets.identity-broken`, `fleet.secrets.delivery-short`).

## Step 5 — prove the isolation

Run these **after** it has started; several only become observable then.

| Assertion | How to see it | Failure means |
|---|---|---|
| no shared host paths beyond the intended ones | mount tables of clone and source, side by side | the clone writes into the source's state |
| the source's name appears nowhere in the clone's rendered compose file or config | search the rendered files | the source compose file is not templated, and the clone carries its identity into some path or label |
| config path, state dir, workspace and port are unique | re-run the preflight against the live instance | the second to start will lose |
| delivered secret **names and count** match the source | name-only comparison, never values | wrong project or broken identity, not a missing feature (`fleet.secrets.wrong-project`) |
| the source is untouched | its config mtime, restart count and port equal the values recorded before the clone | the clone edited its source |
| loaded assets resolve to the shared trees | list them from inside the container | a leftover local copy shadows the shared one — extra directories are the **lowest** load priority (`fleet.shared.local-shadow`) |
| `fleet.py config --diff` | nothing under `added` or `changed` | the instance is unmanaged, and every mutation on it will be refused during the first incident |

## Step 6 — the health battery decides, not the file listing

```
${CLAUDE_PLUGIN_ROOT}/scripts/healthcheck.py epsilon --table
```

`HEALTH` and `LIVENESS` must agree, the log must move, the first scheduled run must complete, and the
layer-two security checks must pass on it — loopback publication first. A clone that joins the fleet
carrying findings makes the next fleet report unable to distinguish a new problem from an unfinished
setup.

## Common mistakes in this scenario

- Cloning to obtain the source's *state*. Layout and config copy; memory, sessions and schedules do
  not, and a config copied wholesale carries the source's identity with it.
- Choosing the port by "nothing is listening on it".
- Copying the credential directory to make it work faster. It works until the next rotation, and then
  two instances are logged out instead of one.
- Passing `--apply --yes` in the same turn the plan was first rendered.
- Handing the clone work before it exists in the fleet config.
