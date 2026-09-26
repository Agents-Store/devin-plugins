---
name: bank-balances
description: This skill should be used when showing account balances across all connected banks as a unified table. It covers the BROADCAST pattern for fetching balances from every bank simultaneously and merging them into one view. Use this skill whenever the user asks about their balance, account totals, how much money they have, or wants to see all accounts — even if they only mention one bank, because the plugin always queries all connected banks.
---

# Bank Balances (Broadcast)

Show balances across ALL connected banks in a single unified table. This is the plugin's core use case and the primary demonstration of the BROADCAST pattern.

## Why broadcast matters here

Users with accounts at multiple banks want one answer to "how much money do I have?" — not separate queries to each bank. The broadcast approach queries every connected MCP server in parallel and merges results, so the user sees a single consolidated view regardless of how many banks they have.

## Workflow

1. **Discover bank MCP tools** — search for tools with keywords like `account`, `balance`, `iban` across all connected MCP servers. Group discovered tools by bank.

2. **Fetch balances from ALL banks in parallel** — call each bank's balance/account tool simultaneously. Do not ask the user which bank — always query all.

3. **Handle failures gracefully** — if a bank's MCP server is unavailable or returns an error, skip it. Note the failure in the output but still show results from the other banks. The user should never get an empty result just because one bank is down.

4. **Normalize the data** — different banks return balances in different formats:
   - Monobank: integer in kopiykas (divide by 100 for UAH)
   - PrivatBank: decimal string (parse directly, no division needed)

   For API-specific details, read the `bank-api-integration` skill and its `references/monobank-api.md` or `references/privatbank-api.md`.

5. **Display as unified table** sorted by bank, then account:

```
Баланси (станом на 23.03.2026):

| Банк       | Рахунок     | Баланс       | Валюта |
|------------|-------------|-------------|--------|
| Monobank   | ****1234    | ₴15 432,10  | UAH    |
| Monobank   | ****5678    | $1 200,00   | USD    |
| PrivatBank | ****3456    | ₴8 200,00   | UAH    |
| PrivatBank | ****7890    | €500,00     | EUR    |
|            |             |             |        |
| **Разом (UAH)** |        | **₴23 632,10** |     |

⚠ Wells Fargo: MCP сервер недоступний
```

6. **Emit events** — after fetching, emit `balance_updated` broadcast events for each account. See the `broadcast-pattern` skill for event payload details.

## Formatting rules

- Show currency symbol before amount: `₴`, `$`, `€`
- Use space as thousands separator, comma for decimals: `₴15 432,10`
- Mask account numbers: show only last 4 digits (`****1234`)
- If multiple currencies, show a total per currency or note that conversion is not applied
- Show the timestamp of when balances were fetched

## Multi-currency totals

When accounts span multiple currencies, show separate totals per currency rather than converting everything to UAH (exchange rates fluctuate and the user may not want an approximate conversion). If the user explicitly asks for a UAH total, use the `currency-rates` skill to get current rates and show the conversion with a disclaimer.

## Related skills

| Need | Skill |
|------|-------|
| Bank API details (parameters, formats) | `bank-api-integration` |
| Real-time balance change notifications | `broadcast-pattern` |
| Currency conversion for multi-currency totals | `currency-rates` |
| Encrypt cached balance data | `encrypted-storage` |
