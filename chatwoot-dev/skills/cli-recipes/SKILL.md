---
name: cli-recipes
description: This skill should be used when the user asks about the "Chatwoot CLI", "chatwoot command line", "chatwoot convs/conv/contact commands", "triage Chatwoot from the terminal", "run Chatwoot in CI", or needs ready-to-use `chatwoot` CLI commands, the noun/verb grammar, output-format rules, or safety guidance for customer-visible writes.
---

# Chatwoot CLI Recipes

Operate Chatwoot helpdesks from the terminal with the official `chatwoot` CLI — list and
triage conversations, send replies and notes, assign, change status, set labels/priority,
search contacts, inspect inboxes, and search help-center articles.

> Adapted from the official Chatwoot `chatwoot-cli` agent skill (MIT, https://github.com/chatwoot/cli).
> The CLI is in active development — run `chatwoot --help` to confirm flags for your version.

## Install & authenticate

```bash
# macOS / Linux — detects OS/arch, verifies SHA256
curl -fsSL https://chwt.app/install-cli | sh

# Interactive setup (prompts for Base URL, API Key, Account ID).
# Non-secret config -> ~/.chatwoot/config.yaml; API key -> OS keyring.
chatwoot auth login

# CI / headless / agent contexts — bypass the keyring with the env var.
# auth login is interactive and FAILS in non-TTY; never script it.
export CHATWOOT_API_KEY="your_access_token"
```

## Agent output contract

The CLI defaults to **human-readable text**. It does NOT auto-switch to JSON in non-TTY
environments. When a script or agent will consume the output, opt in explicitly:

- `-o json` — parse with `jq`. Never grep the text format (it is for humans and can change).
- `-q` — IDs only, one per line, for piping to `xargs` or chaining `chatwoot` calls.
- `-o csv` — spreadsheet-friendly.
- Exit `0` = success; non-zero = error (errors go to stderr).
- `-v` (verbose) shows the underlying HTTP request/response when debugging.

## Grammar

Every command is one of three shapes:

| Shape | Meaning | Example |
|-------|---------|---------|
| `<plural-noun>` | list | `chatwoot convs`, `chatwoot contacts` |
| `<singular-noun> <id>` | view | `chatwoot conv 123` |
| `<singular-noun> <id> <verb> [..]` | act | `chatwoot conv 123 reply "hi"` |

The id always comes **before** the verb. Nouns: `conv`/`convs`, `contact`/`contacts`,
`inbox`/`inboxes`, `agents`, `labels`, `teams`, `hc`/`hcs`.

## Global flags

| Flag | Description |
|------|-------------|
| `-o, --output` | `text` (default), `json`, `csv` |
| `-a, --account` | Override account ID for this invocation |
| `-q, --quiet` | IDs only, one per line |
| `-v, --verbose` | Show request/response (debugging) |
| `--no-color` | Disable colored output |

## Command reference

| Command | What it does |
|---------|--------------|
| `convs` | List conversations (filters: `-s` status, `--inbox`, `--assignee`, `--team`, `-l` label, `--query`, `-p` page) |
| `conv <id>` | View one conversation |
| `conv <id> messages` | List messages in a conversation |
| `conv <id> reply <text>` | Send a public reply (`--private` for an internal note) |
| `conv <id> resolve` \| `open` \| `pending` | Change status |
| `conv <id> snooze [--until X]` | Snooze (default: until next reply; pass `--until 7d` for a fixed window) |
| `conv <id> assign` | Assign `--agent me\|alice\|42` and/or `--team 7` |
| `conv <id> unassign` | Remove the assignee |
| `conv <id> label <a,b,c>` | **Replace** labels with this set (comma-separated, single flag) |
| `conv <id> priority <level>` | `urgent` \| `high` \| `medium` \| `low` \| `none` |
| `conv <id> contact` | View the sender contact |
| `contacts` | List/search contacts (`--search "name\|email\|phone"`) |
| `contact <id> [conversations]` | View a contact / list their conversations |
| `inboxes` \| `inbox <id>` | List inboxes / view one |
| `agents` \| `labels` \| `teams` | List account-level resources |
| `hcs` \| `hc default [slug]` \| `hc articles [--query]` \| `hc article <slug>` | Help-center listing & search |
| `me` \| `whoami` \| `auth status` | Current identity / session |
| `api <path>` | Call any Chatwoot endpoint with saved auth (account-relative path) |
| `auth login` \| `logout` | Interactive login / remove credentials |
| `config path` \| `config view` | Inspect config file |

## Common patterns

List responses are wrapped in `.data.payload[]`:

```bash
chatwoot convs --assignee me -s open -o json \
  | jq '.data.payload[] | {id, contact: .meta.sender.name, last: .messages[-1].content}'

chatwoot convs --query "refund" --assignee all -s open -q   # IDs only
```

Read recent messages (`message_type`: `0` customer, `1` agent, `2` activity, `3` template):

```bash
chatwoot conv 123 messages -o json \
  | jq '.payload[-5:][] | {dir: (if .message_type==0 then "in" else "out" end), private, content}'
```

Append a label (the `label` verb **replaces** — fetch first, then merge). `set -o pipefail`
is required so a failed fetch surfaces instead of silently clearing every label:

```bash
set -o pipefail
existing=$(chatwoot conv 123 -o json | jq -r '.labels // [] | join(",")')
chatwoot conv 123 label "${existing:+$existing,}billing"
```

Bulk resolve via `-q | xargs` (list what would be affected first, then confirm):

```bash
chatwoot convs -l spam -q | xargs -I{} chatwoot conv {} resolve
```

Chain contact → conversations:

```bash
id=$(chatwoot contacts --search "jane@example.com" -o json | jq '.payload[0].id')
chatwoot contact "$id" conversations -o json
```

Raw API call — account-relative paths expand under `/api/v1/accounts/<account_id>`, so do
not include that prefix. Prefer first-class commands; use `api` only when no command exists:

```bash
chatwoot api /conversations/123 -o json
chatwoot api -X PATCH /conversations/123 --data '{"status":"open"}'
```

## Common mistakes

1. **Parsing text output** — always `-o json` (or `-q`) when an agent consumes output.
2. **`convs` defaults to your open queue** — it is implicitly `--assignee me -s open`. Pass `--assignee all` + the right `-s` for "everything".
3. **`label` replaces, not appends** — fetch-then-merge (see above).
4. **`--query` ≠ contact search** — `convs --query` searches message content; use `contacts --search` for a person.
5. **Ambiguous `--agent <name>`** — matches a case-insensitive substring; prefer agent IDs in scripts (`chatwoot agents -o json` to resolve).
6. **Labels are comma-separated on one flag** — `-l a,b`, not `-l a -l b`.
7. **A list is one page** — inspect `meta` and advance with `-p N`.
8. **Bare `snooze` is not forever** — it snoozes until the next reply; pass `--until`.
9. **Never run `auth login` in a script** — use `CHATWOOT_API_KEY` + saved config (or `-a`).

## Safety — customer-visible writes

Treat all writes as privileged. Before running any of these in an agent context, **show the
exact command and get explicit approval**. Approval on one conversation does not extend to
another.

Irreversible / customer- or team-visible: `reply` (sent, cannot be unsent — confirm tone),
`assign`/`unassign` (queues, notifications), `resolve`/`open`/`pending`/`snooze` (status,
SLA), `label` (overwrites the set), `priority` (dashboards, SLA routing), `api -X <method>`
or `api --data` (treat non-GET as a write), and any `-q | xargs` bulk operation.

Read-only and safe to run freely: `convs`, `conv <id>` view, `conv <id> messages`,
`conv <id> contact`, `contacts`, `contact <id>`, `inboxes`, `inbox <id>`, `agents`,
`labels`, `teams`, `me`, `whoami`, `auth status`, `config path/view`, and `api <path>` GETs.
