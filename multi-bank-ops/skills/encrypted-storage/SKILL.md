---
name: encrypted-storage
description: This skill should be used when encrypting or decrypting financial data files, rotating the storage passphrase, understanding where data is stored, or troubleshooting encryption errors. Relevant for queries like "encrypt my transaction data", "change my storage passphrase", "where are my bank files stored", or "decrypt accounts file". Use this skill whenever the user asks about data security, encryption, storing financial data, passphrase management, or where their data is saved.
---

# Encrypted Storage

All financial data is encrypted at rest. This matters because the plugin stores bank access tokens, full transaction histories, and account numbers on the user's local filesystem — data that, if exposed, gives direct access to bank accounts and reveals complete financial behavior.

## Practical Example

**User says:** "зашифруй мої дані"

**What happens step by step:**
1. Prompt the user for a passphrase (never store it — the user re-enters it each session)
2. Generate a random 32-byte salt and 16-byte IV (unique per file, per encryption)
3. Derive a 256-bit key from the passphrase using PBKDF2 (100k iterations, SHA-512)
4. Encrypt each data file with AES-256-GCM, producing ciphertext + auth tag
5. Write the `.enc` file containing all parameters needed for decryption (salt, IV, auth tag, ciphertext)
6. Securely delete any temporary plaintext files
7. Confirm to user:

```
Дані зашифровано:
  accounts.enc  — облікові записи банків
  transactions.enc — історія транзакцій
  budgets.enc — бюджети та ліміти

Запам'ятайте пароль — він не зберігається і потрібен щоразу.
```

## Storage Location

```
~/.multi-bank/
├── data/
│   ├── accounts.enc        # Bank accounts and access tokens
│   ├── transactions.enc    # Cached transaction history
│   └── budgets.enc         # Budget definitions and spending state
├── events.jsonl            # Broadcast event log (not encrypted — contains no PII)
└── config.json             # Non-sensitive settings (sync interval, preferences)
```

`events.jsonl` and `config.json` are not encrypted because they contain no personally identifiable information — only event metadata and user preferences. Encrypting them would add passphrase prompts for routine operations without meaningful security benefit.

## Why These Crypto Choices

| Choice | Why |
|--------|-----|
| **AES-256-GCM** | Authenticated encryption — it encrypts AND verifies integrity in one pass. If someone tampers with the ciphertext (e.g., flips a bit), decryption fails rather than silently producing corrupted data. GCM is the standard choice for this because it is fast, well-audited, and available in every crypto library. |
| **PBKDF2 with 100,000 iterations** | Brute-force resistance. A user's passphrase might be only 12-20 characters. Without key stretching, an attacker with a stolen `.enc` file could try billions of passphrases per second. 100k iterations of PBKDF2 slows each attempt to ~10ms, making brute-force impractical for reasonable passphrases. |
| **SHA-512** for PBKDF2 hash | Larger internal state than SHA-256, making GPU-based attacks less efficient. Marginal benefit, but no cost. |
| **32-byte random salt** | Prevents rainbow table attacks. Each file gets its own salt, so identical passphrases produce different keys for different files. |
| **16-byte random IV** | Ensures the same plaintext encrypted twice produces different ciphertext. Prevents pattern analysis across encryptions. |
| **16-byte auth tag** | The integrity guarantee of GCM. Full 128-bit tag — no truncation — for maximum tamper detection. |

## Encrypted File Format

Each `.enc` file is self-describing JSON. All parameters needed for decryption are stored alongside the ciphertext (except the passphrase, which only the user knows).

```json
{
  "version": 1,
  "algorithm": "aes-256-gcm",
  "kdf": "pbkdf2",
  "kdfIterations": 100000,
  "kdfHash": "sha512",
  "salt": "<base64>",
  "iv": "<base64>",
  "authTag": "<base64>",
  "ciphertext": "<base64>"
}
```

The `version` field allows future migration to stronger algorithms without breaking existing files.

## Using the Encryption Scripts

### Encrypt data

```bash
node <plugin_dir>/scripts/encrypt.js <input.json> <output.enc> <passphrase>
```

Output on success: `{ "success": true, "outputPath": "/path/to/output.enc" }`

### Decrypt data

```bash
node <plugin_dir>/scripts/decrypt.js <input.enc> <output.json> <passphrase>
```

Output on success: `{ "success": true, "outputPath": "/path/to/output.json" }`

### Error cases

| Scenario | Output |
|----------|--------|
| Wrong passphrase | `{ "success": false, "error": "Decryption failed — invalid passphrase or corrupted data" }` |
| Tampered ciphertext | Same error as wrong passphrase (auth tag verification fails — by design, these are indistinguishable to prevent oracle attacks) |
| Missing file | `{ "success": false, "error": "File not found: /path/to/file" }` |

## What Gets Encrypted

| Data | File | Why encrypted |
|------|------|---------------|
| Bank MCP credentials | accounts.enc | Full bank access — the most sensitive data in the system |
| Account numbers | accounts.enc | PII that identifies the user's bank accounts |
| Transaction history | transactions.enc | Financial PII — reveals income, spending habits, locations |
| Budget definitions | budgets.enc | Spending patterns reveal lifestyle and financial situation |
| Event log | events.jsonl | Not encrypted — no PII, only event types and timestamps |
| Config | config.json | Not encrypted — only preferences like sync interval |

## Key Derivation Flow

```
User Passphrase
       |
       v
   PBKDF2(passphrase, salt, 100000, 32, 'sha512')
       |
       v
   256-bit Encryption Key
       |
       v
   AES-256-GCM(key, iv, plaintext) -> ciphertext + authTag
```

## Key Rotation (Passphrase Change)

When the user wants to change their passphrase, re-encrypt all files. Each re-encryption generates fresh salt and IV, so the new files are cryptographically independent from the old ones.

1. Decrypt all `.enc` files with the old passphrase
2. Re-encrypt all files with the new passphrase (new salt, new IV)
3. Verify each file decrypts correctly with the new passphrase
4. Securely delete temporary plaintext files

```bash
node decrypt.js accounts.enc accounts_tmp.json OLD_PASS
node encrypt.js accounts_tmp.json accounts.enc NEW_PASS
rm -P accounts_tmp.json  # secure delete on macOS
```

Repeat for `transactions.enc` and `budgets.enc`.

## Security Principles

- **Never write plaintext financial data to disk** without encrypting it, because the filesystem may be backed up, synced, or accessed by other processes
- **Delete temporary files immediately** after re-encryption — they contain the unprotected data
- **Passphrase is never stored** — the user provides it each session. This means a stolen laptop without the passphrase yields only encrypted blobs
- **Salt is random per file, per encryption** — two files encrypted with the same passphrase produce completely different ciphertext
- **Auth tag prevents tampering** — if an attacker modifies the `.enc` file, decryption fails cleanly rather than producing corrupted financial data
