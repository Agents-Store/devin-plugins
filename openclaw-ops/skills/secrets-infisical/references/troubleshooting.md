# Secret troubleshooting

Symptom to cause to check. Every check here is R0 and runs through
`${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py <instance> --json -- <args>` or `fleet.py`. No check in this
file prints a value.

## Delivery

| Symptom | Cause | Check | Finding |
|---|---|---|---|
| a feature is off, the config looks correct, nothing is logged | the referenced key is not delivered — resolution failures are silent by design | P1: `required − delivered`, names only | `fleet.secrets.delivery-short` |
| one instance receives a fraction of what its siblings receive | wrong project or environment binding on that instance's identity | delivered count vs siblings and `secrets.expected_key_count` | `fleet.secrets.wrong-project` |
| the container starts with almost no keys at all | the wrapper cannot mint a token — identity file missing, unreadable, or revoked | identity file presence and mode; wrapper start lines in the log | `fleet.secrets.identity-broken` |
| a key is delivered but the value behaves as empty | the store holds an empty string, which is not the same as absent | size bucket via `redact.len_bucket`; fingerprint exists but bucket is `empty` | `fleet.secrets.delivery-short` |
| an instance was fine and died after a restart | a reference stopped resolving while the old value lived on in memory | P1 as a restart precondition — before, not after | `fleet.secrets.delivery-short` |
| a key appears in delivery but nothing uses it | leftover reference from a removed feature | `delivered − required` | none — one report line |

## Writing and login

| Symptom | Cause | Check | Rule |
|---|---|---|---|
| the token works when pasted by hand and fails from a script | the login capture merged stderr, so the update banner is concatenated onto the token | capture stdout alone and compare lengths | never `2>&1` around a token-producing login |
| a `KEY=VALUE` table appeared in the terminal | the write command prints its full table even in quiet mode | discard both streams on the write | value is now in the transcript — treat as leaked, P3 |
| a value showed up in the process table | passed as an argument | pass by stdin or environment | zero retries on writes |
| a write failed halfway | partial write | verify by fingerprint before anything else | `gate.RETRY_RULES["secret-write"]` — stop, do not repeat |
| the new fingerprint equals the old one | the write did not take, or the same value was rewritten | compare fingerprints before and after | a rotation that does not change the fingerprint is not a rotation |
| the old fingerprint still authenticates after a rotation | the old value was never invalidated at the provider | provider-side check | the rotation is incomplete |

## Plaintext files and leaks

| Symptom | Cause | Check | Finding |
|---|---|---|---|
| an env file sits inside the state tree | left over from before injection | fingerprint parity per key, not file existence | `fleet.secrets.plaintext-env` |
| the file was deleted and instances died at the next restart | it was load-bearing — at least one key had no other source | restore from the snapshot, then run P4 properly | red line `delete-plaintext-env` |
| a backup or identity copy holds a token or client id | it has already left the box | scan by key class (`redact.classify_key`), never print | `fleet.secrets.leaked-in-backup` |
| a gateway operator token is identical on several instances | the trust boundary is per gateway and access is all-or-nothing | fingerprint the token per instance and compare | `fleet.security.token-reuse` |
| "we removed the file, so it is handled" | deletion removes the evidence, not the exposure | did the value leave the box at any point | rotation required, not optional |

## Traps

- **Config is not delivery.** Every reference can be perfect while the identity delivers nothing. Only
  the wrapper's own output is evidence.
- **Exec without the wrapper is not delivery either.** A bare exec sees an environment with no
  injected secrets and reports every key missing. `hot` mode exists for this.
- **Absent, empty and wrong are three different states.** Absent has no fingerprint; empty has one with
  an `empty` size bucket; wrong has a fingerprint that does not match its counterpart. The three have
  different fixes and identical symptoms.
- **A count is not a set.** "Thirteen keys delivered" says nothing about *which* thirteen. Compare
  names.
- **Fingerprint parity is directional.** Parity between a file and the store proves the file is
  redundant. It never proves the store is correct — both can hold the same stale value.
- **Restart, not reload,** when a consumer caches its client at construction. A reload that appears to
  do nothing is often this.
- **Never diagnose by rewriting.** Writing a value to "make sure it is right" costs a process-table
  appearance and destroys the fingerprint evidence you needed.
