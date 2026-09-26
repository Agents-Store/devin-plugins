---
name: security-audit
description: Use when the security posture of an OpenClaw instance or of the whole fleet is in question — a gateway port that may be reachable from outside the host, firewall rules that read correctly but may not apply to published ports, an operator bearer token that may be shared between instances or sitting in a plaintext file, permissions on state, credential or identity trees, a metrics or admin endpoint answering without authentication, a secret found in a backup or an identity copy, a question about who can reach an instance and what that access grants, before exposing an instance to a new network or new people, and after any suspected compromise.
---

# Security audit

Two layers, and the second is the one nobody runs. The runtime audits itself; nothing inside the
process can audit how it is exposed, which firewall chain applies to it, who else holds its token, or
what the host filesystem lets other people read.

## Layer one: the built-in audit

Run it through the one door: `${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py <instance> --json -- security audit --deep`.

- **Exit code is the verdict, the document is the evidence**: 0 clean, 1 error, 2 warn. Findings carry
  `checkId`, `severity`, `message`, `path`, `ocPath`, `fixHint`.
- **Ids pass through verbatim.** Families `fs.*`, `gateway.*`, `tools.exec.*`, `plugins.*`,
  `security.exposure.*` belong to the runtime. Quote what the live `--json` returned; never compose an
  id, a message or a fix hint from memory. Field meanings and family scope: `references/checkids.md`.
- **`--fix` is narrow and is not a follow-up step.** It repairs only the subset it declares, it is R4,
  it sits behind the red line `doctor-fix-or-security-fix`, and it cannot approve capabilities —
  upstream made bulk-approval flags unable to grant consent on purpose. Propose it as a plan; never
  chain it onto the audit in the same turn.
- **A clean audit is not a secure instance.** It is one process reporting on itself.

## Layer two: the deployment class

Checks the runtime cannot make, because the answers live outside it.

| Check | Why it exists here | Evidence | Finding |
|---|---|---|---|
| every publication binds loopback | images publish **outward by default**; a bind on all interfaces is reachable the moment the host has a public address | `fleet.py discover --json` → `port.loopback`, against `policy.loopback_only` | `fleet.security.port-non-loopback` |
| container-aware firewall rules exist | published ports **bypass the ordinary input chain** — a host firewall that reads correctly is simply not applied to them | a reachability test **from off-host**, not a rule listing | `fleet.security.docker-user-chain` |
| the operator token is unique per instance | one trust boundary per gateway; a token accepted by two gateways silently merges two boundaries | compare token **fingerprints** across instances | `fleet.security.token-reuse` |
| permissions on state and auth-secret trees | credential material readable beyond its owner is compromised by anyone with a shell | mode and owner checks | `fleet.security.state-perms` |
| metrics require the bearer | a public unauthenticated metrics endpoint is prohibited; scrape from **inside** the container so the token never crosses the boundary | an unauthenticated request must be refused | `fleet.security.metrics-unauthenticated` |

**The `fleet.secrets.*` family is not audited here.** Plaintext env files, leaked-in-backup values,
identity-file modes, the unencrypted store and the whole rotate-or-not decision belong to
**`secrets-infisical`** — a secret finding raised by this audit is handed to that skill, not resolved here.

## Trust boundary — repeat it in every report

- **One trust boundary per gateway.** This is not a hostile multi-tenant boundary: everything inside
  one gateway shares one boundary, including every skill, plugin and channel it loads.
- **Bearer auth is all-or-nothing operator access.** There is no read-only token, so "give them the
  token for monitoring" means "make them an operator".
- **Store values are not encrypted at rest.** Host access is store access.
- Therefore "who can reach the port" and "who can read the host filesystem" are the same question as
  "who operates this instance". Write that sentence into the report; a boundary nobody stated is a
  boundary nobody defended.

## Triage order

Sort by what makes the other findings moot, not by severity alone.

1. **Reachability.** A hardening finding inside a gateway anyone can reach is academic.
2. **Credential exposure.** Rank it second, then hand it to **`secrets-infisical`**, which owns the
   classification and the rotation procedure.
3. **Merged boundaries.** Shared operator token, credential directory with no declared owner, one
   instance holding another's material.
4. **Permissions and hygiene**, then **informational statements** — which are still printed, because
   an accepted risk that was never written down becomes a surprise.

Inside a tier: `critical > high > warn > info`; among equals, the instance with the higher
`criticality` first. Every finding leaves the audit as an id plus a ready `/openclaw-ops:repair` line.

## Incident response

1. **Contain without destroying evidence.** Cut reachability or stop the gateway. Do not restart, do
   not run any `--fix`, do not delete the file — a restart rotates away the log lines holding the
   entry point.
2. **Hand every exposed credential to `secrets-infisical`** — scoping by fingerprint, the rotation
   order and the zero-retry rule on a secret write live there, and one owner keeps them consistent.
3. **Re-run both** the audit and the health battery afterwards. A triage with no clean re-run is not
   finished, it is abandoned.
4. Record what could not be verified. An unverifiable claim is itself a finding.

## Common mistakes

- Treating `--fix` as the natural next step after the audit. Detection is R0; the fix is R4 with a
  typed confirmation, and it is a red line for a reason.
- Reading firewall rules instead of testing reachability from off-host. The rules can be perfect and
  irrelevant, because published ports do not traverse the chain those rules live in.
- Comparing gateway tokens by value instead of by fingerprint.
- Quoting a `checkId`, its message or its fix hint from memory. Ids and hints are version-specific;
  the live `--json` is the only source, and any recommendation needs the `docs-research` ladder.
- Calling an instance secure because the built-in audit was green. It never looked at the network, the
  host, or the neighbours it shares that host with.
