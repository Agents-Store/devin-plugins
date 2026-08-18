---
name: currency-rates
description: This skill should be used when checking currency exchange rates, viewing USD or EUR rate history, comparing rates across banks, or monitoring rate fluctuations. Relevant for queries like "what is the dollar rate today", "show EUR exchange rate history", "compare bank rates for USD", or "how has the rate changed this week". Use this skill whenever the user asks about dollars, euros, exchange rates, currency conversion, or any mention of USD, EUR, or курс.
---

# Currency Rates via Bank MCP

Query currency exchange rates from bank MCP servers. Banks expose current and historical rates for major currency pairs against UAH (Ukrainian Hryvnia).

## Practical Example

**User asks:** "який зараз курс долара"

**Workflow:**
1. Detect intent: the user wants current USD/UAH exchange rate. When users say "курс долара" without specifying buy/sell, show both directions — they may be deciding whether to buy or sell.
2. Search for currency tools using keywords: `currency`, `rate`, `курс`, `exchange`.
3. Call the rate tool (e.g., `getCurrencyRates` for PrivatBank, `get_currency_rates` for Monobank).
4. Format the response with Ukrainian labels:

**Output:**
```
Курси валют (станом на 24.03.2026):

| Валюта | Купівля | Продаж | Спред |
|--------|---------|--------|-------|
| USD    | 41.20   | 41.80  | 0.60  |
| EUR    | 44.50   | 45.30  | 0.80  |
```

5. If multiple banks are connected, show a cross-bank comparison automatically — the user likely wants the best deal.

## Tool Discovery

Search for currency-related MCP tools using keywords: `currency`, `rate`, `курс`, `exchange`.

Not all bank MCP servers provide currency rate tools. If none are found, tell the user rate data is unavailable for that bank. PrivatBank typically exposes `getCurrencyRates` and `getCurrencyRatesHistory`; Monobank may expose `get_currency_rates` or similar.

## Understanding Buy vs. Sell Rates

The buy rate is always lower than the sell rate. This is how banks earn money on currency exchange — the difference (spread) is the bank's margin.

- **Buy (Купівля):** the rate at which the bank buys foreign currency from you. You sell dollars, you receive UAH at this rate.
- **Sell (Продаж):** the rate at which the bank sells foreign currency to you. You buy dollars, you pay UAH at this rate.

A typical spread of 0.50-1.00 UAH on USD/UAH is normal. Wider spreads may indicate market volatility or less competitive pricing.

When the user asks "скільки коштує долар" (how much does a dollar cost), they usually want the sell rate — the price they would pay to buy dollars. When they say "хочу продати долари" (I want to sell dollars), show the buy rate.

## Current Rates

Get today's exchange rates. No parameters needed — the tool returns current buy/sell rates.

### Response Fields

| Field | Description |
|-------|-------------|
| **currency** / **ccy** | Currency code (`USD`, `EUR`) or ISO 4217 numeric code |
| **baseCurrency** | Base currency, typically `UAH` (980) |
| **buy** | Bank buys from you (you receive UAH) |
| **sell** | Bank sells to you (you pay UAH) |
| **date** | When the rate was published |

### Display Format

Right-align numeric columns. Show exactly 2 decimal places. Use Ukrainian labels when the user communicates in Ukrainian.

```
Курси валют (станом на 24.03.2026):

| Валюта | Купівля | Продаж | Спред  |
|--------|---------|--------|--------|
| USD    | 41.20   | 41.80  | 0.60   |
| EUR    | 44.50   | 45.30  | 0.80   |
```

When the user asks "what is the exchange rate" without specifying a currency, default to showing both USD/UAH and EUR/UAH — these are the most commonly needed pairs.

## Rate History

Get historical rates for a date range.

| Parameter | Required | Format |
|-----------|----------|--------|
| startDate | Yes | DD-MM-YYYY |
| endDate | Yes | DD-MM-YYYY |

### 15-Day Pagination Limit

The API allows a maximum of 15 days per request. This is a bank-side limitation, not something to ask the user about — handle it automatically.

To fetch a longer period (e.g., 01.01.2026 to 28.02.2026):

1. Split the range into 15-day chunks:
   - `startDate=01-01-2026`, `endDate=15-01-2026`
   - `startDate=16-01-2026`, `endDate=30-01-2026`
   - (continue until the range is covered)
2. Concatenate results and de-duplicate boundary dates.
3. Present as a single continuous table.

### Multi-Day Rate Trend Display

Show historical data with daily rows and a delta column for change from the previous day:

```
Динаміка курсу USD/UAH (01.03.2026 – 10.03.2026):

| Дата       | Купівля | Продаж | Δ Купівля | Δ Продаж |
|------------|---------|--------|-----------|----------|
| 01.03.2026 | 41.10   | 41.70  |     —     |     —    |
| 02.03.2026 | 41.15   | 41.75  |   +0.05   |   +0.05  |
| 03.03.2026 | 41.05   | 41.65  |   −0.10   |   −0.10  |
```

After the table, add a summary: direction (зріс/знизився), total change, min, max values.

For longer periods, summarize the trend rather than listing every row — a 60-day table is hard to read. Mention overall direction, extremes, and average.

## Cross-Bank Rate Comparison

When multiple banks are connected, compare rates side by side to help the user find the best deal.

1. Fetch rates from all connected banks in parallel.
2. Normalize data — ensure both use the same currency pair and date.
3. Present side-by-side:

```
Порівняння курсів USD/UAH (24.03.2026):

| Банк       | Купівля | Продаж | Спред |
|------------|---------|--------|-------|
| Monobank   | 41.20   | 41.80  | 0.60  |
| ПриватБанк | 41.15   | 41.75  | 0.60  |
|            |         |        |       |
| Найкращий  | 41.20 * | 41.75 *|       |
```

4. Highlight best rates:
   - Best **buy** = highest (you get more UAH when selling foreign currency).
   - Best **sell** = lowest (you pay less UAH when buying foreign currency).
5. If a bank does not expose rate tools, note it: "Monobank: курси недоступні через MCP".

## Formatting Rules

- Right-align all numeric columns.
- Always 2 decimal places (`41.20`, not `41.2`).
- Use `+` / `−` for delta values. Use `—` (em-dash) for the first row.
- Show currency pairs explicitly: `USD/UAH`, `EUR/UAH`.
- Date format in display: `DD.MM.YYYY` (Ukrainian standard).
- Date format for API calls: `DD-MM-YYYY` (PrivatBank standard).

## Error Handling

| Scenario | Action |
|----------|--------|
| No currency rate tools found | Tell the user: "This bank's MCP server does not expose currency rate tools." |
| Empty result | The bank may lack rates for weekends/holidays. Suggest adjacent business days. |
| 15-day limit exceeded | Split automatically — never pass a range > 15 days in a single call. |
| Date format error | Convert to `DD-MM-YYYY` before calling. |
| Timeout / server error | Retry once. If still failing, report and continue with other banks if available. |

## Notes

- Rates are typically available for USD and EUR; some banks may also provide GBP, PLN, CHF.
- Weekend/holiday rates may be unavailable — the bank may return the last business day's rates.
- Some banks return ISO 4217 numeric codes (840 = USD, 978 = EUR, 980 = UAH) instead of letter codes. Map them for display.
