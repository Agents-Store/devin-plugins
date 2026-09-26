---
name: docs-research
description: Use when anything about OpenClaw is about to be stated or recommended that could have changed — a config key, a CLI flag or subcommand spelling, an auth method, a release channel, a current version, a model name, whether a feature exists or is deprecated — and whenever a claim needs a citation, two sources disagree, an instance's own documentation looks older than the project's, or the situation is offline and it must be decided what may still be said without a live source.
---

# Docs research

Two sources, two different questions, not interchangeable.

| Source | Answers | Cost and caveat |
|---|---|---|
| the instance's own docs command, through `ocexec.py <instance> -- docs "<query>"` | **what my runtime thinks** — the vocabulary, flags and defaults of the version actually installed | not free: it loads the config and the plugins, so on a `degraded` instance it can fail for reasons unrelated to your question. On an old instance the answer is old by exactly the age of that instance |
| the project documentation site | **what is recommended now** | says nothing about whether this instance supports it |

**Divergence between them is a finding, not an obstacle.** An instance whose own docs describe a flag
the site no longer documents is an instance running behind — record it, do not paper over it.

## Which source, when

- **"How does this work on my box?"** → the box first. Its `--help`, its docs command, its config, its
  catalogue. The site cannot tell you what this build supports.
- **Any recommendation to change something** → a live source is mandatory. Memory does not qualify, and
  neither does an in-box doc page when the change is "adopt the current recommendation".
- **Neither network nor CLI reachable** → **unverified-knowledge mode**: observations yes,
  recommendations no. Say what was observed on the host, state that no source could be reached, and
  stop. A recommendation with no source is the failure mode this whole skill exists to prevent.

## Fetch ladder

Use the first tool actually available in the session; detect availability, never assume it. Whatever
answers, **quote the URL** in the finding.

1. A connected search-and-scrape MCP tool (full-page scrape → markdown, or a schema-driven extract).
2. A semantic code-aware search tool, for "find the page that explains X".
3. A ranked-search or answer-with-citations tool, for "what is the current recommended way to X".
4. A clean-reader tool, for a known URL that other tools rendered empty.
5. A library-documentation tool, for the **surrounding** CLIs — the secret-injection CLI, the model
   vendors' CLIs, the container runtime — rather than OpenClaw's own site.
6. The built-in web fetch and search, always available, the floor of the ladder.

When a page returns empty, it is usually client-rendered: retry with a longer wait, or move one step
down the ladder. A tool returning nothing is not evidence that the page says nothing.

## Documentation map

Entry points; if a path 404s, search within the site rather than guessing a new path.

| Topic | Where |
|---|---|
| docs home, configuration reference | `https://docs.openclaw.ai/` |
| gateway authentication, providers | `https://docs.openclaw.ai/gateway/authentication` |
| OAuth concepts, profiles, PKCE | `https://docs.openclaw.ai/concepts/oauth` |
| model providers, refs and runtimes | `https://docs.openclaw.ai/concepts/model-providers` |
| CLI backends | `https://docs.openclaw.ai/gateway/cli-backends` |
| the models subcommand | `https://docs.openclaw.ai/cli/models` |
| memory and embeddings | `https://docs.openclaw.ai/` (search "embeddings", "memory index") |
| skills and plugins loading | `https://docs.openclaw.ai/` (search "skills load", "plugins load paths") |
| health endpoints and monitoring | `https://docs.openclaw.ai/` (search "healthz", "readyz") |
| release channels and upgrades | `https://docs.openclaw.ai/` (search "release channels") |
| releases and changelog | `https://github.com/openclaw/openclaw/releases` |

## Version truth — three sources, three questions

This is where confident guessing does the most damage, so each fact has exactly one authority.

| Question | Authority | Never use |
|---|---|---|
| what does channel X point at **right now**? | the package registry **dist-tags** | version ordering over the release list |
| when was that version **promoted** (the soak clock)? | the **release entry's date** for that exact version | the registry publish date — a build is published to a pre-release tag first and promoted later **without a version bump** |
| what is **actually running**? | the **image digest** of the running container | the tag it was pulled by |

Three wrong methods that all look reasonable and all ship regularly:

- **Highest non-prerelease version.** Correction releases are published as `<version>-1`, `<version>-2`;
  a hyphen suffix parses as a pre-release, so a correct semver maximum discards exactly the releases
  that fix the one it keeps.
- **Newest non-prerelease release entry by date.** The trailing channel is also published as a
  non-prerelease and lags the main line by about a month. This hands back a month-old fleet-wide
  rollback while you believe you are current.
- **Comparing publish dates across the two sources.** They disagree by weeks, and the disagreement is
  the promotion mechanism, not an error.

`${CLAUDE_PLUGIN_ROOT}/scripts/versions.py` implements all of this, including the soak gate and the
digest comparison. Use it rather than re-deriving; if you must state a version in prose, state it as
the script's output, dated.

Moving tags — the channel-named ones — are rebuilt on a schedule under the same name. Pin a plain
version or a digest for any mutation (`gate.is_moving_tag`, `gate.pin`).

## Model names

- **Zero real model ids in a recommendation position.** Not in this repository, not in a skill, not in
  a report. Model ids expire, get renamed and change price; a frozen one is a defect with a long fuse.
- Write the **shape** instead: `<provider>/<model-id>`, with the runtime override attached separately.
  When a literal is unavoidable in an illustration, it must be visibly fake and inside a comment
  marked as example-only.
- **Procedure for a real name**: read this instance's catalogue — `ocexec.py <instance> --json --
  models list` — and take the id from there.
- **Substitution rule**: any model id entering a diff must be an **echo from the box** — present in
  that instance's catalogue. An id that came from memory, from another instance, or from a
  documentation page is not an echo (`fleet.config.model-id-unverified`).
- Pin ids; do not follow a moving alias. An automatic move to a new model on a production fleet is a
  change in price and behaviour with no change in the config.

## Common mistakes

- Quoting a flag, a subcommand spelling or a config key from memory because it "has always been that".
  Spellings drift between versions, and this fleet spans several.
- Treating the in-box docs command as free. It loads config and plugins; on a broken instance it fails
  for its own reasons and the failure gets misread as an answer.
- Resolving "the current version" from the release list because the registry felt like an
  implementation detail. It is the only mechanical statement of where a channel points.
- Reporting a recommendation with no URL. A finding outside the runtime's own check contract needs the
  citation quoted in the report — no citation, no action.
- Letting a documentation page override an observation. The site describes the current release; the box
  describes what is running. When they differ, both go in the report.
