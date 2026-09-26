---
name: instance-clone
description: Use when a new OpenClaw instance is to be created from an existing one — cloning the reference, standing up a canary or a throwaway test instance, adding an instance for a new workload or tenant, picking a free gateway port for one, deciding what a new instance may share with its source and what it must not — and also when an instance created earlier behaves like its source, answers on the wrong port, has no credentials, or is suspected of not being isolated from the instance it was copied from.
---

# Instance clone

Cloning has two halves. A script owns the deterministic half; the credential half is deliberately not
automated. Almost every "the clone does not work" report is the second half never having happened —
which is why the steps that were not performed are **printed** rather than silently skipped.

## What the script does, and what it refuses to do

```
${CLAUDE_PLUGIN_ROOT}/scripts/clone.py <new-name> [--from <reference>] [--port auto|<n>]
                                       [--plan | --apply --yes] [--provisioner CMD]
```

| Does | Does not |
|---|---|
| validate the name against the fleet and the prefix | mint a machine identity or grant it project access |
| choose a genuinely free host port | create or copy any secret value |
| run the isolation preflight and print it, passes and failures alike | perform a provider login |
| materialise the compose directory, the state directories and a patched config | apply the model chain |
| create credential directories **empty**, mode 0700 | populate or register skills and plugins |
| print every remaining manual step | start anything, or give the instance work |

Exit codes: 0 planned or applied · 1 runtime · 2 fleet config missing or invalid · 3 refused · 4
reference not found · 5 isolation preflight failed. A refused preflight is the script working.

## Isolation preflight

Four properties must be unique per gateway, and one more depends on the network mode:

| Requirement | Why a clash is not loud |
|---|---|
| config path | both instances read one file; an edit meant for one lands on both |
| state directory | startup **enforces unique state-directory ownership**, so the second instance to start loses. The clone looks fine today and something else breaks tomorrow |
| agents workspace | two instances writing one workspace corrupt each other's working state |
| published host port | the second publication fails at `up` time, or worse, silently binds elsewhere |
| network namespace | if the source runs with host networking, the **in-container** port must differ too — the published-port check does not cover that case |

**An unknown value is a failed requirement.** Uniqueness that could not be asserted has not been
established, and the preflight refuses rather than assuming.

## A free port means free by four measures

Not published by any container on this host · not written into any compose file of the fleet — a
**stopped** instance still owns its port · not bindable-in-use at this moment · not already claimed by
another entry in the fleet config. Any single measure passes on a port that another instance owns.
Publish on loopback: images publish outward by default, and a clone is the easiest place to lose that.

## Credentials are never copied

- **OAuth material is not portable.** An API key or a static token would survive a copy; an OAuth
  profile does not, and copying one gives two instances a single refresh chain — the exact
  configuration that logs one of them out at the next rotation (`fleet.auth.token-sink`).
- Credential directories for the clone are created **empty**. If the fleet deliberately shares one
  owner credential directory by mount, the clone mounts the same directory — sharing by mount is a
  decision with one owner; sharing by copy is two owners and a race.
- The embedding key is **per instance**. Sharing one hides which instance burns the quota, and changing
  a key later changes the index identity and forces a full reindex everywhere it was used.
- Secret references travel; secret values do not. The patched config carries the same references and
  resolves none of them.

## After the script: the half nobody automated

1. Machine identity for the new instance, with read access to the same secret project.
2. The per-instance secrets the source declares — compared **by name and count**, never by value.
3. Provider logins registered on the new instance, from the credential owner, never copied.
4. The model chain applied at all three levels: default, per agent, per schedule.
5. Skills and plugins: shared paths registered; plugin load paths need a **restart**, not a reload.
6. The fleet config entry — role, criticality, aliases — then `fleet.py config --diff` clean.
7. Bring it up, run the health battery, and only then give it work.

Each step with its verification and its failure mode: `references/post-clone-checklist.md`.

## Prove the isolation, do not assume it

- **Mount tables side by side.** No host path of the source appears under the clone except the ones the
  fleet deliberately shares.
- **The rendered compose file must not name the source anywhere.** A surviving occurrence means the
  clone carries the source's identity into some path, label or variable.
- **If the source compose file never names its own instance**, it is not templated: the clone would
  share every path with it. Template the deployment first; that is a prerequisite, not a nicety.
- **Config points at the clone's own tree**: workspace, state directory, config path, port.
- **Secret delivery matches** the source by key name and count. A short count is the wrong project id
  or a broken identity, not a missing feature.
- **The source is unchanged**: same config mtime, same restart count, same port, before and after.

## Common mistakes

- Cloning to get the source's *state*. The copy carries layout and config; memory, sessions and
  schedules are not transplantable, and a config that is copied wholesale carries the source's
  identity with it.
- Copying the credential directory "just to make it work". It works until the next token rotation, and
  then two instances are logged out instead of one.
- Choosing the port with a single check, usually "nothing is listening". Stopped instances own ports.
- Cloning whatever instance was nearest. Clone the **reference**; a clone inherits every unfixed
  finding, and a clone of a zombie is a second zombie. If the reference is not healthy, fix it first.
- Cloning the legacy instance. Its layout is a different deployment shape, every mutation on it is
  refused, and re-creating it multiplies a migration project.
- Passing `--yes` in the same turn the plan was first shown, or `--apply` without reading the printed
  preflight rows — which are printed on success too, precisely so that they are read.
- Adding the clone to the fleet config after handing it work. Until it is in the config it is
  unmanaged, and every mutation on it is refused — discovered at the least convenient moment.
