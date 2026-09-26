# Secret playbook

Procedures. Every path is a placeholder — `<data-root>`, `<identity-dir>`, `<quarantine>`,
`<instance>`, `<project-id>`, `<KEY_NAME>`. Command spellings are intent: confirm each against the
store CLI's own `--help` on this host before quoting it (skill `docs-research`).

Any fingerprint shown here is a synthetic stub (`fp:0000aaaa`), never a real digest prefix.

## P1 — Delivery audit (R0)

The one procedure the others depend on.

1. **Required.** Collect every secret reference from the effective config — each reference carries a
   key **name**, never a value — plus the names the compose file passes into the container. Read the
   config through `ocexec.py`, so you get what the process reads and not what a file on the host says.
2. **Delivered.** Run the wrapper's own environment listing inside the container and keep **names
   only** (`${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py <instance> -- …` in `hot` mode, so the wrapper
   is in the chain). For a non-empty check, count the characters of a value; never print it.
3. **Compare by name.** `required − delivered` is the finding set. `delivered − required` is noise
   worth one line in the report — usually a leftover from a removed feature.
4. **Cross-check the fleet.** Delivered counts per instance next to `secrets.expected_key_count`. On a
   fleet of clones, one instance receiving a fraction of what its siblings receive is
   `fleet.secrets.wrong-project` or `fleet.secrets.identity-broken`, and the difference between those
   two is whether *some* keys arrive or almost none.
5. **Report** names, counts and fingerprints. No values, ever, including in the "expected" column.

Verification for any later fix is a rerun of this procedure with an empty `required − delivered`.

## P2 — Add a key (R4, red line on overwrite)

Used whenever an instance needs its own credential — the per-instance embedding key being the common
case, since a subscription OAuth session covers chat and **does not satisfy embedding requests**.

1. **Check first.** If the key already exists, capture its fingerprint. A different fingerprint means
   this is a rotation (P3), not an addition — red line
   `secret-overwrite-different-fingerprint`.
2. **Print the write line, do not run it.** The plugin never accepts a key in chat. Emit a single line
   that reads the value with echo disabled, feeds it to the write over stdin, and discards both output
   streams:
   - value never in argv → out of the process table;
   - both streams discarded → the `KEY=VALUE` table the write prints does not reach the terminal;
   - nothing typed into chat → nothing in the transcript.
3. **Operator runs it.** One attempt. On failure, stop and verify by fingerprint
   (`gate.RETRY_RULES["secret-write"]` — zero retries; a repeat risks a partial write).
4. **Verify by name and fingerprint**, per instance: the key appears in delivered names, and its
   fingerprint matches what was intended.
5. **Reference it from the config** — a reference by name through `config-surgery`, never a literal.
6. **Restart**, not reload, when the consuming subsystem caches its client. Run P1 first as the
   restart precondition.
7. **Consequences the caller must be told about.** A changed embedding credential changes the index
   identity: vector search pauses with an identity warning and only an explicit reindex restores it,
   on **every** instance, including the ones where the key was merely replaced. See `memory-ops`.

## P3 — Rotate (R4)

Rotation is required whenever a value has been exposed, not only when it expires.

1. Record the old fingerprint and every place it is delivered (P1 across the fleet).
2. Write the new value (P2 steps 2–4). Both fingerprints now exist; they must differ.
3. Roll instances canary first (`gate.canary_barrier`), P1 before each restart.
4. **Invalidate the old value at the provider — last, never first.** Until that happens nothing has
   been rotated: a new key next to a live old key is an addition. Revoking before the new value is
   delivered and verified everywhere converts a compromise into an outage. The dependency order is
   fixed: mint → deliver → verify delivery **by name** → restart → revoke.
5. Verify: the old fingerprint no longer authenticates, the new one is delivered everywhere the audit
   said it was required.

## P4 — Plaintext env file: six steps

`fleet.secrets.plaintext-env`, red line `delete-plaintext-env`. Stop points are load-bearing: at each
one the fleet is left in a state that still works.

1. **Classify by fingerprint parity.** For every key in the file, compare its fingerprint against the
   delivered value of the same name. Every key matching → **redundant**. Any key absent from delivery
   or with a different fingerprint → **load-bearing**, and this file is currently the only source.
   Existence of the file proves nothing either way. **Stop point.**
2. **Close the gap first.** For each load-bearing key, add it to the store (P2) and re-run P1 until
   `required − delivered` is empty. Nothing is moved while a key still has one source. **Stop point.**
3. **Re-prove parity.** Repeat step 1 in full. The file is now redundant by evidence, not by
   assumption. If any key still fails parity, return to step 2 — do not "mostly" proceed.
4. **Quarantine.** `gate.snapshot` the file, then **move** it to `<quarantine>/<instance>/`, outside
   every container volume, mode 0600. Never `rm`. The inverse move is the ROLLBACK line.
5. **Canary restart.** Restart exactly one instance — the canary, never the reference — and verify:
   delivery unchanged (P1), health green, and one feature that consumes a key from that file actually
   working. **Stop point: nothing else moves until this is green.**
6. **Roll the rest**, one at a time, same verification each time. Direction is good → changed, so the
   batch is fail-fast. Separately: any value that was in that file and left the box gets P3.

## P5 — Identity repair (R2)

Symptoms: almost no keys delivered, or a delivered set that belongs to another project.

1. Confirm the identity file exists, one per instance, mode 0600, owned by root
   (`fleet.secrets.identity-file-mode`).
2. Confirm the project and environment binding names — names, not values. A wrong `<project-id>` is
   the usual cause of a fleet clone receiving a stranger's key set.
3. **Capture stdout only** when scripting the login. The CLI writes its update banner to stderr and a
   merged capture concatenates it onto the token; every later call then fails while blaming the
   credentials.
4. Verify with P1: delivered count matches the siblings and `secrets.expected_key_count`.
5. If the identity file itself ever contained a token or client id in a backup copy, that value has
   leaked — P3, not a delete (`fleet.secrets.leaked-in-backup`).
