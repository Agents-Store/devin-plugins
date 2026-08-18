---
name: bank-statements
description: This skill should be used when creating a bank statement (виписка) for a specific account and period — a formal document listing all transactions with opening and closing balances. Use this skill whenever the user asks for a statement, виписка, account extract, or needs a formal record of transactions for a specific account, even if they just say "зроби виписку" or "I need a statement for my account".
---

# Bank Statements

Generate a bank statement (виписка) for a specific account over a specific period. Unlike `bank-transactions` (which merges all banks), a statement is account-specific and includes opening/closing balances.

## When statements vs transactions

The difference matters because users mean different things:
- **"Show my transactions"** → merged chronological list from all banks → use `bank-transactions`
- **"Make a statement for my Monobank account"** → formal single-account document with balances → use this skill

A statement is a formal document. It has an opening balance, a list of operations, and a closing balance for one specific account.

## Workflow

1. **Identify the account** — ask which account if the user hasn't specified. List available accounts from all connected banks and let them pick. Show masked numbers (`****1234`) with bank name.

2. **Determine the period** — parse date range from user input. Default to current month if not specified.

3. **Fetch the data:**
   - **Opening balance** — balance at the start of the period. Some APIs provide this directly; otherwise, fetch the balance for the day before the start date.
   - **Transactions** — all transactions for the account during the period.
   - **Closing balance** — balance at the end of the period (or current balance if the period extends to today).

   API differences:
   - Monobank: Unix timestamps, amounts in kopiykas, 31-day max per request
   - PrivatBank: DD-MM-YYYY dates, decimal amounts, cursor pagination via `followId`

   For full API details, read references in the `bank-api-integration` skill.

4. **Format the statement:**

```
ВИПИСКА ПО РАХУНКУ

Банк:       Monobank
Рахунок:    ****1234
Період:     01.03.2026 – 31.03.2026

Залишок на початок:  ₴12 500,00

| Дата       | Опис                | Дебет       | Кредит      | Залишок     |
|------------|---------------------|-------------|-------------|-------------|
| 01.03.2026 | Зарплата            |             | ₴25 000,00  | ₴37 500,00  |
| 03.03.2026 | Сільпо              | ₴345,67     |             | ₴37 154,33  |
| 05.03.2026 | Комуналка           | ₴3 200,00   |             | ₴33 954,33  |
| ...        |                     |             |             |             |

Залишок на кінець:   ₴28 432,10

Всього операцій: 47
Дебет (витрати):   ₴9 067,90
Кредит (надходження): ₴25 000,00
```

5. **Offer export** — suggest saving as CSV or PDF via the `report-export` skill. A PDF statement is particularly useful for formal purposes (tax, audit, etc.).

## Statement vs combined report

This skill generates a statement for ONE account. If the user wants a combined multi-bank report, redirect to the `bank-reports` skill. If they want a raw transaction list from all banks, redirect to `bank-transactions`.

## Debit/Credit formatting

In bank statements, the convention is:
- **Debit** = money leaving the account (expenses) — shown without sign
- **Credit** = money entering the account (income) — shown without sign
- **Balance** = running balance after each transaction

This is clearer than +/- signs for a formal statement document.

## Related skills

| Need | Skill |
|------|-------|
| Bank API details, pagination, rate limits | `bank-api-integration` |
| Export statement to CSV/PDF | `report-export` |
| Multi-bank merged view | `bank-transactions` |
| Multi-bank analytics | `bank-reports` |
