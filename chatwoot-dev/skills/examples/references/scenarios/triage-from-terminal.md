# Scenario: Triage conversations from the terminal

Goal: a realistic support-triage loop with the `chatwoot` CLI — find the queue, read context,
and act safely. Uses `cli-recipes` (grammar, output contract, safety).

## 1. See the unassigned open queue

```bash
chatwoot convs --assignee unassigned -s open -o json \
  | jq '.data.payload[] | {id, contact: .meta.sender.name, last: .messages[-1].content}'
```

## 2. Read one conversation's recent messages

```bash
chatwoot conv 123 messages -o json \
  | jq '.payload[-6:][] | {dir: (if .message_type==0 then "in" else "out" end), private, content}'
```

## 3. Act — each of these is a customer-visible write; confirm before running

```bash
chatwoot conv 123 assign --agent me           # take ownership
chatwoot conv 123 priority high               # flag for SLA
chatwoot conv 123 reply "Hi! Looking into your order now."   # SHOWN to the customer
chatwoot conv 123 reply "billing checked, refund issued" --private   # internal note
chatwoot conv 123 resolve                      # close it out
```

## 4. Append a label without wiping existing ones

```bash
set -o pipefail
existing=$(chatwoot conv 123 -o json | jq -r '.labels // [] | join(",")')
chatwoot conv 123 label "${existing:+$existing,}refund"
```

## 5. Bulk-resolve spam (preview, then confirm)

```bash
chatwoot convs -l spam -q                       # preview the IDs first
chatwoot convs -l spam -q | xargs -I{} chatwoot conv {} resolve
```

## Safety reminder

`reply`, `assign`/`unassign`, `resolve`/`open`/`pending`/`snooze`, `label`, `priority`, and
any `api -X`/`--data` are writes. Show the exact command and get approval before each one;
approval on one conversation does not carry to the next. See `cli-recipes` → Safety.
