---
name: bank-transactions
description: This skill should be used when listing transaction history across all connected banks for a given period as a single chronological list. It covers fetching transactions via BROADCAST, merging results, date range handling, and pagination across different bank APIs. Use this skill whenever the user asks about transactions, recent purchases, spending history, what they spent money on, or wants to see operations across banks — even for a single bank, because the plugin always queries all.
---

# Bank Transactions (Broadcast)

Fetch and display transaction history from ALL connected banks as a single merged chronological list.

## Why merge transactions across banks

People pay for things from different accounts — groceries from Monobank, rent from PrivatBank, subscriptions from either. A chronological view across all banks gives the complete picture of their financial activity without manual aggregation.

## Workflow

1. **Parse the date range** — if the user says "last month" or "за березень", convert to concrete dates. Default to the last 30 days if no range specified.

2. **Discover transaction tools** — search for tools with keywords: `statement`, `transaction`, `extract`, `виписка` across all connected MCP servers.

3. **Fetch from ALL banks in parallel** — call each bank's transaction/statement endpoint with the date range. Be aware of format differences:
   - Monobank: `from`/`to` as Unix timestamps (seconds), max 31 days per request, rate limit 1 req/60s per account
   - PrivatBank: `startDate`/`endDate` as DD-MM-YYYY, cursor-based pagination via `followId`

   For full API details, read `references/` in the `bank-api-integration` skill.

4. **Handle pagination** — some banks limit results per request. Follow pagination cursors until all transactions for the period are fetched.

5. **Handle rate limits** — Monobank allows 1 statement request per 60 seconds per account. For 90-day ranges, split into 3 × 31-day chunks with 60s delays between requests. Inform the user this will take a moment.

6. **Normalize amounts** — Monobank returns kopiykas (÷100), PrivatBank returns decimal strings. Normalize to UAH decimal before merging.

7. **Merge and sort** — combine all transactions into one list, sort by date descending (newest first). Include the bank name as a column so the user knows which account each transaction came from.

8. **Display as table:**

```
Транзакції (01.03.2026 – 23.03.2026):

| Дата       | Банк       | Опис              | Категорія    | Сума        |
|------------|------------|-------------------|-------------|-------------|
| 23.03.2026 | Monobank   | Сільпо            | Продукти    | -₴345,67    |
| 22.03.2026 | PrivatBank | Bolt              | Транспорт   | -₴89,00     |
| 22.03.2026 | Monobank   | Зарплата          | Дохід       | +₴25 000,00 |
| 21.03.2026 | PrivatBank | Rozetka           | Покупки     | -₴1 299,00  |

Знайдено: 47 транзакцій | Monobank: 28 | PrivatBank: 19
⚠ PrivatBank: отримано тільки 19 з можливих (ліміт API)
```

9. **Auto-categorize** — use the `transaction-categorization` skill to assign categories based on MCC codes and merchant patterns. This enriches the raw transaction data with spending categories.

10. **Emit events** — emit `transaction_added` events for new transactions. See the `broadcast-pattern` skill.

## Filtering

After fetching, support filtering by:
- **Category** — "покажи тільки продукти"
- **Bank** — "тільки Monobank" (filter the merged list, don't skip fetching)
- **Amount** — "більше 1000 грн"
- **Search** — "знайди Rozetka"

Fetch from ALL banks first, then filter locally — this is consistent with the BROADCAST pattern.

## Related skills

| Need | Skill |
|------|-------|
| Bank API details, date formats, pagination | `bank-api-integration` |
| Auto-categorization of transactions | `transaction-categorization` |
| Budget tracking against transactions | `budget-alerts` |
| Export transactions to CSV/PDF | `report-export` |
