---
name: client-package
description: This skill should be used when the user asks to "send the documents to the client", "give the client something to comment on", "собрать пакет для клиента", "отдать клиенту на согласование", "показать клиенту артефакт", or needs either half of the client loop — turning the six client documents into one page a client can read and answer, and taking their answers back into the ledger.
---

# Hand the client something they can actually read and answer

Nobody sends a client an 88 KB markdown file and expects edits back. In practice the client
writes a document of their own and somebody transcribes it by hand — which is where a hundred
small changes go missing.

This skill builds one self-contained HTML page from the six client documents, and reads the
answers back. It opens in any browser, prints to PDF, and needs nothing installed.

## Build

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/client-package/references/package.py" macstack \
        [--date YYYY-MM-DD] [--slug user-cases] [--artifact] \
        [--only <sections>] [--skip <sections>]
```

Writes `macstack/history/handoffs/<date>-<slug>.html` and records itself in the ledger as a
`handoff` row. That row is what the NEXT package measures "changed since you last read this"
against — without it the next round marks either everything or nothing.

An unknown flag is refused, not ignored. A shell that collapses the arguments into one string
used to leave every flag unrecognised: the command then built the DEFAULT package under the
DEFAULT slug and journalled it as a completed round, which silently moved the "changed since"
baseline for the next one.

**The command prints what to do next, and it differs per file.** Read that output rather than
guessing — it names the file, says whether it can go to a client, and gives the exact
`file_path` and the exact follow-up command.

### Two files, and only one of them goes to the client

Without `--artifact` you get `<date>-<slug>.html`: **the file for the client.** Self-contained,
opens in any browser, prints to PDF.

With `--artifact` you get `<date>-<slug>-artifact.html`: **an artifact body, not a page.** It
carries no `<html>` and no `<body>` — the publisher adds them — so a browser will not render
it and a client must never be sent it. Publish it, then record the URL it returns:

```bash
# 1. publish with the Artifact tool, passing that exact path as file_path
# 2. put the URL it returns into the ledger — with the command, not by editing JSON:
python3 "${CLAUDE_PLUGIN_ROOT}/skills/client-package/references/package.py" macstack \
        --record-url <URL> --handoff <date>-<slug>-artifact.html
```

`--record-url` finds the `handoff` row by FILE NAME (several packages share one date) and
refuses unless it matches exactly one row.

### Splitting the package — `--only` / `--skip`

Both take section keys, comma- or space-separated: `product goals roles automation cases
questions screens handbook`. An unknown key is refused.

Open questions are the one part a client reads differently: there they do not confirm our
description, they hand over what we do not have, and until they answer the work stands still.
So they are worth sending on their own:

```bash
… --slug documents --skip questions      # everything except the questions
… --slug questions --only questions      # the questions alone
```

A package of ONE section names itself after that section — in the `<title>` and the `<h1>` —
and shows the version of that section's own document. Two packages built on one day would
otherwise reach the client under the same name and differ only by URL. A section may also
carry its own instructions at the top: `questions` does, because "mark it right / not so" is
meaningless against "give us your company's invoicing details".

## What the client sees

**Whole entities, as prose.** A case reads as a case: what it is, who does it, what has to be
true when it is done. Acceptance bullets stay inside their case, as part of it.

Acceptance bullets are test cases — written for a machine. A package that flattens them into
hundreds of separate questions is an interrogation, not a document, and the client stops
reading. One answer per entity, not one per bullet.

Eight sections: what the product is · goals · who does what · what starts work and who does
it · what must be delivered · questions for you · screens · how to use it. A section with
nothing in it is dropped, and so is an entity that holds nothing but the scaffolder's own
italic prompt — an unwritten `HANDBOOK.md` is 41 headings each saying *"describe the steps of
this procedure"*, which is an instruction addressed to US. It returns by itself the day
somebody writes the first procedure.

**Questions for you means §A — what the CLIENT owes.** §B is the work the team deferred, and
it is selected out by its pointer (`lifecycle.needs_from_client`), not by how its headings
happen to be punctuated. Closed items are filtered separately, by their strikethrough.

**Closed questions do not go in.** Six of the questions in `OPEN-QUESTIONS.md` are struck
through and marked CLOSED; asking them again spends attention the client has a fixed amount
of. Lint rule 12.6 already says the same thing.

## Permanent ids, and why `handoffs/` is immutable

The id on an entity (`C-04`) comes from the document, not from its position in the package.
It does not move when something is inserted above it, so a client quoting `C-04` from a
six-month-old email lands on the same thing.

The handoff file still never changes: the client's answers come back against THAT file. A new
round writes a new dated file, and refuses to overwrite an existing one. Never edit a file in
`handoffs/`.

## Read the answers back

The client presses **"Собрать мои ответы"** at the bottom of the page and sends you the text.
Channel does not matter — file, email, message, or pasted into the chat. If it came through
the chat, write it to `macstack/inbox/<date>-answers.json` first: the inbox is what gives a
correction a traceable source.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/client-package/references/package.py" macstack \
        --read <file.json> [--dry]
```

`--dry` prints what would be recorded and writes nothing.

Every answer becomes a `comment` row in `history/ledger.jsonl` with a `verdict` field —
including a plain "верно". Silent agreement and no answer at all look identical otherwise,
and they are not the same thing: one means somebody read it and agreed.

## What the next round then does by itself

Under each entity the client answered, the next package shows what they said with its date,
and pre-selects their previous verdict — **still changeable**. Locking a client into an old
answer is wrong: the document may have moved since, and a "верно" from six months ago can
stop being true.

An answer the client did not touch is not re-asked. Otherwise every round returns all two
hundred answers and nobody can see what actually got reconsidered.

## Then it is ordinary incoming material

An answer that asks for a change goes through `intake`: delta → ruling → apply. Do not put a
client's comment straight into a document. A comment is a request; what it costs to be wrong
about it is the owner's call, not this session's.

## Language

The page follows `docs.language`. Ids and keys stay Latin. The client never sees a key.
