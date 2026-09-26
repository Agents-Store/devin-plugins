---
name: payments
description: This skill should be used when preparing or sending payments, checking payment status, validating IBAN numbers, making tax or budget payments, or tracking payments by reference. Relevant for queries like "send a payment to this IBAN", "check payment status", "make a tax payment", "is my payment processed yet", or "prepare a payment of 10000 UAH". Use this skill whenever the user mentions sending money, paying someone, IBAN, payment status, or any transfer operation.
---

# Payments via Bank MCP

Prepare and track payments through bank MCP tools. This covers corporate payment operations for Monobank and PrivatBank.

## Practical Example

**User says:** "відправ 10000 грн на цей IBAN UA293220010000026000000000001"

**Step-by-step workflow:**

1. **Parse intent:** The user wants to send 10,000 UAH to the specified IBAN.

2. **Validate IBAN format:** Check that it matches `UA` + 27 digits = 29 characters total. This IBAN is valid.

3. **Convert amount to the correct format:**
   - For Monobank: convert to kopiykas. 10000 UAH = `1000000` kopiykas (multiply by 100).
   - For PrivatBank: use decimal string `"10000.00"`.
   Getting this wrong causes a 100x error — sending 100 kopiykas instead of 100 UAH, or 1,000,000 UAH instead of 10,000 UAH.

4. **Collect missing info:** Ask the user for:
   - Recipient name and EDRPOU (required by bank API)
   - Payment purpose/destination (6-420 characters)
   - Which sender account to use (if multiple)

5. **Confirm before sending:** Display a summary and ask for explicit confirmation:
   ```
   Підтвердіть платіж:
     Відправник: UA29322001... (ваш рахунок)
     Отримувач: ТОВ "Компанія" (ЄДРПОУ: 12345678)
     IBAN: UA29322001...0001
     Сума: ₴10 000,00
     Призначення: "Оплата за послуги згідно рахунку №123"

   Підтверджуєте? (так/ні)
   ```

   **Why confirm?** Once a payment is signed in the mobile app, it cannot be cancelled or reversed. A wrong amount, wrong IBAN, or wrong recipient means the money is gone. This is the last safety checkpoint.

6. **Call the payment tool** only after user confirms.

7. **Report result:** Show payment ID, status (CREATED = awaiting mobile signature), and next steps.

**Output:**
```
Платіж створено:
  ID: pay_abc123
  Статус: CREATED (очікує підпису в мобільному додатку)

Відкрийте додаток банку для підписання.
```

## Tool Discovery

Search for payment-related MCP tools using keywords: `payment`, `prepare`, `pay`, `платіж`.

Typical tools:
- **Prepare/create payment** — creates a payment and sends it for mobile signing
- **Get payment status by ID** — check state after preparation
- **Get payment status by external reference** — track by your own reference ID

## Amount Formats: Kopiykas vs. Decimal

Monobank and PrivatBank use different amount formats. Getting this wrong is the single most common payment error — it causes amounts to be 100x too large or 100x too small.

| Bank | Format | Example for ₴10 000,00 | Why |
|------|--------|------------------------|-----|
| Monobank | Integer in **kopiykas** | `1000000` | API works with smallest currency unit, like cents |
| PrivatBank | **Decimal string** | `"10000.00"` | API works with human-readable amounts |

Conversion examples:
```
₴1 000,00  → Monobank: 100000    PrivatBank: "1000.00"
₴15 432,50 → Monobank: 1543250   PrivatBank: "15432.50"
₴0,01      → Monobank: 1         PrivatBank: "0.01"
```

Maximum amount: ₴100 000 000,00 (Monobank: `10000000000`).

Always double-check: if the user says "10 тисяч гривень", that is 10,000 UAH = 1,000,000 kopiykas. Do not confuse the two.

## Monobank Payment Parameters

### Required

| Parameter | Description | Format |
|-----------|------------|--------|
| senderIban | Sending account IBAN | UA + 27 digits |
| receiver.iban | Recipient IBAN | UA + 27 digits |
| receiver.edrpou | Recipient ЄДРПОУ | 8 digits |
| receiver.name | Recipient legal name | String |
| destination | Payment purpose | 6-420 characters |
| amount | Amount in kopiykas | Integer, 1-10,000,000,000 |
| currency | ISO 4217 numeric code | "980" for UAH |

### Optional

| Parameter | Description | When needed |
|-----------|------------|-------------|
| externalReference | Your tracking ID | 3-256 chars, for idempotency and tracking |
| payCode | Budget classification code | 3 chars, for government/tax payments |
| additionalInfo | Budget payment extra info | 6-130 chars, required when payCode is set |

## PrivatBank Payment Parameters

### Required

| Parameter | Description | Format |
|-----------|------------|--------|
| document_number | Unique document number | String |
| payer_account | Sender IBAN | UA + 27 digits |
| recipient_account | Recipient IBAN | UA + 27 digits (or use recipient_card) |
| recipient_nceo | Recipient ЄДРПОУ | String ("0000000000" for individuals) |
| payment_naming | Recipient name | String |
| payment_amount | Amount as decimal | e.g., "1000.50" |
| payment_destination | Purpose | 5-420 chars |

### Optional

| Parameter | Description |
|-----------|------------|
| payment_ccy | Currency, default "UAH" |
| payment_date | Execution date DD.MM.YYYY |
| recipient_card | Card number (alternative to IBAN) |
| externalReference | Your tracking ID |
| struct_type | Budget classification code |
| struct_code | Tax payment code |
| struct_category | Tax notice info (1-140 chars) |

## IBAN Validation

Ukrainian IBAN format: `UA` + 2 check digits + 6 bank code digits + 19 account digits = 29 characters total.

```
UA 29 322001 0000026000000000001
│  │  │       └── Account number (19 digits)
│  │  └── Bank code (MFO, 6 digits)
│  └── Check digits
└── Country code
```

Validate before calling the API — an invalid IBAN will be rejected and wastes a round-trip.

## Payment States

| State | Meaning |
|-------|---------|
| CREATED | Prepared, awaiting signature in mobile app |
| PROCESSING | Signed, being processed by bank |
| SUCCESS | Payment completed |
| FAILURE | Payment failed |
| EXPIRED | Not signed in time |

## Budget Payments

For government/tax payments, provide additional fields:

- **payCode** — 3-character classification code (e.g., "058")
- **additionalInfo** — description required by budget rules (6-130 chars)

```
Example:
  destination: "Сплата ПДВ за березень 2026"
  payCode: "058"
  additionalInfo: "30968899; ПДВ; березень 2026"
```

## PrivatBank-Specific Features

**Payment lifecycle:**
```
1. createPayment → returns ref
2. getPayment(ref) → check status
3. addPaymentSign(ref, sign) → add digital signature (multi-level signing supported)
4. deletePayment(ref) → cancel unsigned payment
```

**Key differences from Monobank:**
- PrivatBank supports payment deletion before signing.
- Multi-level signing — multiple signatures may be required.
- `createPaymentWithForecast` — same as create but includes balance prediction.
- Card payments — use `recipient_card` instead of `recipient_account`.

## Bank-Specific Comparison

| Feature | Monobank | PrivatBank |
|---------|----------|------------|
| Amount format | Kopiykas (integer) | Decimal string |
| Currency | ISO 4217 code ("980") | Text ("UAH") |
| Signing | Mobile app | Digital signature (Base64) |
| Deletion | Not supported | Before signing only |
| Card payments | Not available | recipient_card field |

## Safety Rules

1. **Confirm payment details before calling the API** — display amount, recipient, IBAN, and purpose. Ask for explicit "yes". Payments are irreversible after signing, so this confirmation is the last chance to catch errors.
2. **Display amounts in human-readable UAH** — always convert kopiykas back to UAH for display. A user seeing "1000000" cannot easily verify that is ₴10,000.
3. **Verify the amount format** for the target bank before sending. A kopiykas/decimal mixup causes 100x errors.
4. **Mask IBANs** in output: show only last 4 digits (`UA...****0001`) to protect account information.
5. **Log external references** for tracking — these are safe to display and useful for follow-up.
