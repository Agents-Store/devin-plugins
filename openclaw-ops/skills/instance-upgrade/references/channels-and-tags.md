# Channels, tags and how the target version is decided

Read this before quoting a target version, before pinning an image, and before "simplifying" the
version logic in `versions.py`. The naive simplifications are all in here, with the reason each one
returns a wrong answer.

## What a channel is, and what it is not

A channel is a **pointer in the package registry** — a dist-tag whose value is the exact version that
channel currently means. It is not a git branch, not a docker tag, and not a property of a release
entry. Asking "what is the current stable" is therefore one lookup: read the dist-tag.

| Channel | Behaviour | Use here |
|---|---|---|
| stable | the promoted line | the default target for a production gateway |
| trailing / extended stable | the stable line held back by roughly a month; fail-closed by design | deliberate conservatism only, never as an accident of sorting |
| pre-release (beta) | where a build lands **before** promotion | never a fleet target; a build here may later be promoted with no version change |
| development | unstable head | explicitly not for production gateways |

The channel **names** above are families, not literals: read the actual dist-tag set from the
registry (`versions.py --json` reports `all_tags`) rather than assuming a spelling. A channel name
that resolves to nothing is a finding, not a fallback opportunity.

**A channel name is not the dist-tag it resolves through, and the two must never be swapped.** The
operator-facing names are `stable`, `extended-stable`, `beta`, `dev` — exactly the values
`policy.update_channel` accepts. Each resolves onto a registry dist-tag under a different spelling:
channel `stable`, for instance, points at dist-tag `latest`. `versions.py` prints the whole hop
(`channel X -> dist-tag Y -> version`) so a report never leaves the reader guessing which of the two a
string is. Writing a dist-tag into `policy.update_channel` fails schema validation, which is the
intended outcome: the config records the operator's decision, not the registry's current spelling of it.

## Three reconstructions, three wrong answers

### 1. Highest version among the non-pre-releases

Correction releases are published as the base version with a numeric suffix after a hyphen. Version
ordering interprets **any** hyphen suffix as a pre-release and sorts it *below* the bare version — so
filtering pre-releases out drops exactly the releases whose only purpose is to fix the release you
keep.

<!-- example-only -->
```
published:   9.9.9        (has a defect)
             9.9.9-1      (the fix)
semver-max over non-prereleases  ->  9.9.9      wrong: ships the defect
this plugin's ordering           ->  9.9.9-1    an all-numeric hyphen suffix is a CORRECTION and sorts ABOVE
```
<!-- /example-only -->

The rule is deliberately not standard version ordering, and the deviation is exactly one case: an
all-numeric suffix is a correction and ranks above the bare version. Alphabetic markers
(pre-release, release-candidate, development names) still rank below.

### 2. Newest release entry with "pre-release = false", sorted by date

The trailing channel is published the same way the stable line is: as a normal, non-pre-release
entry. Sorted by date, the first non-pre-release you meet may belong to either line, and **no
machine-readable field says which**. Taking it hands the whole fleet a month-long rollback that
looks like an upgrade — including a state-schema migration you cannot reverse.

### 3. Comparing registry publish dates with release dates

They disagree by weeks and neither is wrong. A build is published to the pre-release tag when it is
built; it becomes stable later, by **promotion of the same version**, with no new version and no new
publish. So:

- the **publish date** answers "when was this artefact built";
- the **release date** answers "when did this version become stable" — and only that one starts the
  soak clock.

Using the publish date makes a version look soaked before it was ever promoted.

## The soak gate

A target is accepted only when every one of these holds. Anything unproven is a refusal, not a
warning — a missing release entry means the promotion date is unknown, which means the clock never
started.

- no pre-release marker in the version;
- not older than the version already installed anywhere in the selection;
- promoted at least `policy.soak_days` ago, measured by **release** date;
- no correction release on the same line published after it;
- when a digest check is requested, the digest resolved for the pinned reference equals the digest
  of the channel's current build.

`versions.py [selector] [--channel …] [--target …] [--soak-days N] [--image REF] [--json|--table]`.
Exit codes: `0` no drift and the target passes · `1` runtime error · `2` fleet config missing or
invalid · `3` target rejected by the gate · `4` selector matched nothing · `5` version drift across
the selection. `--no-net` reports installed versions and drift only — useful on a host without
egress, and honest about what it cannot verify.

## Image tags and digests

| Reference form | Mutable? | Use |
|---|---|---|
| channel or branch tag | **yes** — rebuilt on a schedule under the same name | never for a pin, never for a rollback target |
| dated tag published at each refresh | no | a readable pin |
| plain version tag | no | a readable pin |
| digest | no, by construction | the pin a mutation is allowed to run against |

Pin-before-mutate is enforced in `gate.require_pin`; `gate.is_moving_tag` decides what counts as
moving. A deployment found pinned to a moving tag is `fleet.version.moving-tag-pin` — worth raising
even when nothing is being upgraded today, because it means the reviewed artefact and the running
artefact are two different things.

Lowercase hex identifiers — digests, image ids, commit shas — are deliberately **not** redacted by
`redact.scrub`. They are not secrets, and pin-before-mutate cannot work if they are masked out of
the plan.

## Version literals in this plugin

Any concrete version, digest or date in plugin text is a fetched value with a shelf life, so it does
not get written down as knowledge. The procedure to obtain it is the durable part. The only version
literals allowed in this repository sit inside an `<!-- example-only -->` block, and are obviously
synthetic so nobody can mistake one for a recommendation. The same rule applies with more force to
model identifiers: those are echoed from the instance's own catalogue or they do not enter a diff.
