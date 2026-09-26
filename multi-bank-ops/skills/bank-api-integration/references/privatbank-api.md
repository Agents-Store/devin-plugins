# PrivatBank API Details

## Fetching Account Information

PrivatBank has multiple balance endpoints — discover which are available:

```
Balance types (search for keywords: balance, interim, final):
  - getBalances(acc, startDate, endDate) — historical balances for date range
  - getInterimBalances(acc?) — intraday balances (lastday to today)
  - getFinalBalances(acc?) — end-of-day confirmed balances

Parameters:
  - acc: IBAN (optional — omit for all accounts)
  - startDate/endDate: DD-MM-YYYY format (NOT ISO!)
  - limit: 1-500 (default 20)
  - followId: pagination cursor for next page

Returns account list with:
  - IBAN
  - balance (string, e.g., "15432.50" — NOT kopiykas!)
  - currency (text: "UAH", "USD", "EUR")
  - account name
```

**CRITICAL difference from Monobank:** PrivatBank returns amounts as **decimal strings** (e.g., `"100.50"`), NOT in kopiykas. Do NOT divide by 100.

## Fetching Transactions (Statements)

PrivatBank has multiple transaction endpoints — discover which are available:

```
Transaction types (search for keywords: transaction, interim, final):
  - getTransactions(acc, startDate, endDate) — historical transactions for date range
  - getInterimTransactions(acc?) — intraday transactions (lastday to today)
  - getFinalTransactions(acc?) — end-of-day confirmed transactions

Parameters:
  - acc: IBAN (optional — omit for all accounts)
  - startDate/endDate: DD-MM-YYYY format (NOT ISO!)
  - limit: 1-500 (default 20)
  - followId: pagination cursor for next page

Also available:
  - getStatementSettings() — get server dates and operational day settings
```

**Date format difference:** PrivatBank uses `DD-MM-YYYY` (e.g., `"23-03-2026"`), NOT `YYYY-MM-DD`.
