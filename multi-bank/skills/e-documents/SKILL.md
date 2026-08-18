---
name: e-documents
description: This skill should be used when listing electronic documents (EDO) from bank inbox or outbox, viewing document signatures, downloading documents, or managing document exchange. Relevant for queries like "show my document inbox", "list outgoing documents for March", "check signature on document", or "download document from bank". Use this skill whenever the user mentions documents from bank, EDO, inbox/outbox, acts, invoices, or any bank document exchange.
---

# Electronic Documents (EDO) via Bank MCP

Manage electronic document exchange (EDO / ЕДО — Електронний Документообіг) with bank counterparties. EDO is the standard way Ukrainian companies exchange legally binding documents (invoices, acts, contracts) through their bank.

## Practical Example

**User asks:** "покажи вхідні документи за березень"

**Workflow:**
1. Detect intent: the user wants incoming (inbox) documents for March 2026. "Вхідні" means inbox — documents sent to the user's company by counterparties.
2. Determine the OKPO/EDRPOU to use. If the user has multiple companies, ask which one. If only one is configured, use it automatically.
3. Call `getEdocJournalInbox` with `dateBegin=2026-03-01`, `dateEnd=2026-03-31`.
4. Format results as a summary table:

**Output:**
```
Вхідні документи за березень 2026:

| # | Дата       | Тип         | Відправник (ЄДРПОУ) | Сума       | Статус |
|---|------------|-------------|----------------------|------------|--------|
| 1 | 2026-03-05 | Рахунок     | 12345678             | ₴25 000,00 | new    |
| 2 | 2026-03-12 | Акт         | 87654321             | ₴12 500,00 | signed |
| 3 | 2026-03-20 | Договір     | 12345678             |     —      | new    |

Знайдено 3 документи. 2 потребують уваги (статус: new).
```

5. Proactively highlight documents needing action (status: `new` or `partially_signed`) — the user likely wants to know what requires their attention.

## Tool Discovery

Search for EDO-related MCP tools using keywords: `edoc`, `document`, `journal`, `inbox`, `outbox`, `sign`.

Typical PrivatBank tools: `getEdocJournalAll`, `getEdocJournalInbox`, `getEdocJournalOutbox`, `getEdocBase64`, `getEdocSignInfo`, `deleteEdocDocument`.

## Understanding OKPO / EDRPOU

Many EDO operations require an `okpo` parameter. This is the company's unique identifier in Ukraine's corporate registration system.

**Why it matters:** Ukraine assigns every legal entity an 8-digit code called EDRPOU (ЄДРПОУ — Єдиний державний реєстр підприємств та організацій України). In bank APIs, this code appears as the `okpo` parameter (OKPO is the statistical classification name for the same number). The system needs this code to know which company's documents you want to access — a single user may manage multiple companies.

- **okpo** identifies your company (sender/recipient in the document).
- **relatedOkpo** identifies the counterparty.
- If the user does not know their OKPO/EDRPOU, suggest checking bank account details or company registration documents.

## Common Document Types

| Ukrainian Name | English | Description |
|---------------|---------|-------------|
| **Рахунок** | Invoice | Bill requesting payment |
| **Акт** (виконаних робіт) | Act of completed works | Confirms services rendered; both parties sign |
| **Договір** | Contract | Formal agreement |
| **Податкова накладна** | Tax invoice (VAT) | Required for VAT-registered businesses |
| **Видаткова накладна** | Delivery note | Accompanies shipped goods |
| **Додаткова угода** | Supplementary agreement | Amendment to existing contract |
| **Довіреність** | Power of attorney | Authorizes acting on behalf of company |

When filtering by `docType`, use exact type strings from the bank's API. Query unfiltered first to discover available types.

## Document Status Values

| Status | Meaning |
|--------|---------|
| **new** | Just received, not yet reviewed |
| **signed** | All required digital signatures applied |
| **partially_signed** | Some signatures missing |
| **rejected** | Explicitly rejected by a party |
| **expired** | Signing deadline passed |
| **delivered** | Delivered to recipient |
| **read** | Opened/viewed by recipient |
| **processing** | Being processed by the system |
| **deleted** | Marked for deletion |

Exact status strings vary by bank API — check actual response data.

## Document Journals

Three journal views:

| View | Description | Tool keyword |
|------|-------------|--------------|
| All | All documents (inbox + outbox + in-process) | `journal`, `all` |
| Inbox | Incoming documents | `inbox` |
| Outbox | Outgoing documents | `outbox` |

### Query Parameters

| Parameter | Required | Description | Format |
|-----------|----------|-------------|--------|
| dateBegin | Yes | Start date | YYYY-MM-DD |
| dateEnd | Yes | End date | YYYY-MM-DD |
| docType | No | Filter by document types | Array of strings |
| status | No | Filter by statuses | Array of strings |
| okpo | No | Your company ЄДРПОУ | Array of strings |
| relatedOkpo | No | Counterparty ЄДРПОУ | String |
| docSumFrom | No | Minimum amount | String |
| docSumTo | No | Maximum amount | String |
| sortBy | No | Sort field | doc_id, type, status, sending_time, receipt_time, last_modify_time, amount, doc_date, create_time, sender_okpo, recipient_okpo |
| orderBy | No | Sort direction | asc, desc |
| limit | No | Page size | String (number) |
| offset | No | Page offset | String (number) |

## Document Operations

### Get Document Content (Base64)

Retrieve the actual document file (typically PDF or XML), encoded as Base64.

- **Parameters:** `id` (document ID), `okpo` (company ЄДРПОУ)
- **Returns:** Base64-encoded document content

**Handling Base64 content:**
1. Identify format — most EDO documents are PDF or XML. Check if the response includes a content type or filename.
2. Decode to file — convert Base64 to binary and save with the appropriate extension.
3. For PDFs — you cannot render them inline. Report metadata (type, size, sender, date) and offer to save the decoded file.
4. For XML — parse to extract structured data (amounts, dates, counterparty info).

### Get Signature Info

View digital signature (EDS / ЕЦП) details.

- **Parameters:** `id` (document ID), `okpo` (company ЄДРПОУ)
- **Returns:** Signer name, timestamp, certificate info, validity status

### Delete Document

Remove a document from the journal. Confirm with the user before deleting — this action is irreversible, and the document cannot be recovered.

- **Parameters:** `id` (document ID), `okpo` (company ЄДРПОУ)
- Only documents in certain statuses (`new`, `rejected`) may be deletable.

## Workflow: Receive, Review, and Respond

### Step 1 — List Inbox

Query the inbox journal for the desired date range:

```
Call: getEdocJournalInbox
Params: dateBegin=2026-03-01, dateEnd=2026-03-24
```

Display as a summary table sorted by date descending (newest first) — users typically care about recent documents.

### Step 2 — View a Document

Fetch the content for a document the user wants to review:

```
Call: getEdocBase64
Params: id=<doc_id>, okpo=<your_company_okpo>
```

Report document details. If PDF, offer to decode and save.

### Step 3 — Check Signatures

Verify who has signed and whether signatures are valid:

```
Call: getEdocSignInfo
Params: id=<doc_id>, okpo=<your_company_okpo>
```

### Step 4 — Respond

Based on document status and signatures:
- If the document requires your signature and signing tools are available, proceed.
- If the document should be rejected, check if rejection is available.
- If informational only, confirm receipt.

## Error Handling

| Error | Action |
|-------|--------|
| Document not found | Verify the ID; it may have been removed by the counterparty |
| Insufficient permissions | Check that `okpo` matches your company; user may need elevated permissions |
| OKPO mismatch | Verify which company OKPO to use; if user has multiple, ask |
| Invalid date range | Dates must be `YYYY-MM-DD` with `dateBegin <= dateEnd` |
| Empty journal | Widen date range or remove filters; confirm OKPO is correct |
| Rate limit / timeout | Retry once; inform user if the issue persists |

## Display Guidelines

- Format amounts with `₴` symbol and thousand separators: `₴25 000,00`.
- Use Ukrainian decimal separator (comma): `12 500,50` not `12500.50`.
- Sort inbox by date descending (newest first) by default.
- For status values, show Ukrainian translation alongside raw status when the user communicates in Ukrainian.
- Mask OKPO codes if the user requests it (e.g., `1234****`).
