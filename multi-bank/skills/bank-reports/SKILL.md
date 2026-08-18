---
name: bank-reports
description: This skill should be used when generating analytical financial reports — spending by category, income vs expenses, period comparisons, or spending trends across all connected banks. Use this skill whenever the user asks for a financial summary, analytics, spending breakdown, income report, period comparison, or any aggregated view of their financial data, even if they just say "where does my money go" or "скільки я витратив цього місяця".
---

# Bank Reports (Analytics)

Generate analytical financial reports by aggregating transaction data from ALL connected banks.

## Why aggregate across banks

A spending report that only covers one bank gives an incomplete picture. Someone who buys groceries with Monobank and pays rent with PrivatBank needs both accounts in the same report to understand their true spending. The BROADCAST pattern ensures all data is included.

## Report types

### 1. Spending by category

Break down expenses into categories using the `transaction-categorization` skill. Show amounts and percentages.

```
Витрати за березень 2026 (усі банки):

| Категорія     | Сума        | %     |
|---------------|-------------|-------|
| Продукти      | ₴4 520,00   | 28.3% |
| Транспорт     | ₴2 100,00   | 13.1% |
| Розваги       | ₴1 800,00   | 11.3% |
| Комуналка     | ₴3 200,00   | 20.0% |
| Підписки      | ₴890,00     |  5.6% |
| Інше          | ₴3 470,00   | 21.7% |
|               |             |       |
| **Разом**     | **₴15 980,00** | 100% |
```

### 2. Income vs expenses

Compare total income and total expenses for a period. Income = positive transactions, expenses = negative.

```
Баланс за березень 2026:

| Показник       | Сума          |
|----------------|---------------|
| Доходи         | +₴32 000,00   |
| Витрати        | -₴15 980,00   |
| **Чистий дохід** | **+₴16 020,00** |

Норма заощаджень: 50.1%
```

### 3. Period comparison

Compare two periods side by side — useful for tracking spending trends.

```
Порівняння лютий vs березень 2026:

| Категорія  | Лютий       | Березень    | Зміна      |
|------------|-------------|-------------|------------|
| Продукти   | ₴3 800,00   | ₴4 520,00   | +₴720 ↑   |
| Транспорт  | ₴2 400,00   | ₴2 100,00   | -₴300 ↓   |
| Разом      | ₴14 200,00  | ₴15 980,00  | +₴1 780 ↑ |
```

## Workflow

1. **Determine report type** — based on what the user asks. If unclear, default to "spending by category" for the current month.

2. **Determine date range** — parse from user input. For period comparison, identify both periods.

3. **Fetch transactions** — use the `bank-transactions` skill workflow (BROADCAST to all banks, merge, sort).

4. **Categorize** — use `transaction-categorization` to assign categories to each transaction.

5. **Aggregate** — sum by category, compute income/expenses, calculate percentages and deltas.

6. **Display** — show the report in a clear table. Include bank-level breakdown if the user asks.

7. **Offer export** — after displaying, suggest exporting to CSV or PDF via the `report-export` skill and `/export-report` command.

## Formatting

- Use ₴ symbol with space thousands separator: `₴15 980,00`
- Show percentages to 1 decimal: `28.3%`
- Use ↑/↓ arrows for period comparison deltas
- Positive amounts in income: `+₴32 000,00`
- Negative amounts in expenses: `-₴15 980,00`
- Sort categories by amount descending (biggest spending first)

## Related skills

| Need | Skill |
|------|-------|
| Fetch transactions from all banks | `bank-transactions` |
| Categorize transactions | `transaction-categorization` |
| Export to CSV/PDF | `report-export` |
| Budget comparison | `budget-alerts` |
