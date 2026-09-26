---
name: budget-alerts
description: This skill should be used when setting spending budgets, checking budget utilization, configuring alert thresholds at 50/75/90/100%, or troubleshooting budget alerts. Relevant for queries like "set a monthly dining budget", "how much budget do I have left", "why did I not get a budget alert", or "show budget status for all categories". Use this skill whenever the user mentions spending limits, budgets, overspending, or wants to track expenses against targets, even for simple budget questions.
---

# Budget Alerts

Budget alerts monitor spending against user-defined limits and broadcast `budget_alert` events when thresholds are crossed. The goal is to give users progressive warnings so they can adjust spending before it is too late — not just a single "you're over budget" after the fact.

## Input/Output Example

**User says:** "встанови бюджет на їжу 5000"

**What happens step by step:**
1. Parse intent: category = "Dining" (їжа maps to Dining via the transaction-categorization skill), amount = ₴5,000, period = monthly (default)
2. Create budget definition with standard thresholds [50, 75, 90, 100]
3. Encrypt and save to `~/.multi-bank/data/budgets.enc`
4. Confirm to user:

```
Бюджет створено:
  Категорія: Їжа (Dining)
  Ліміт: ₴5 000,00 / місяць
  Сповіщення: при 50%, 75%, 90%, 100%
```

Later, when a transaction at a restaurant pushes Dining spending to ₴3,800 (76%):

```
Увага: бюджет на Їжу використано на 76%
  Витрачено: ₴3 800,00 з ₴5 000,00
  Залишок: ₴1 200,00 (до кінця місяця — 8 днів)
```

## Why Four Threshold Levels

Each threshold serves a distinct psychological purpose:

| Threshold | Level | Why it exists |
|-----------|-------|---------------|
| **50%** | Awareness | Halfway through the budget — a neutral check-in. Users often do not realize they have spent half the budget with most of the period still remaining. |
| **75%** | Attention | Three-quarters spent. Time to consciously slow down or decide that overspending this month is acceptable. |
| **90%** | Danger | Almost out. A last chance to redirect a meal plan or skip a restaurant visit. |
| **100%** | Over budget | The limit is breached. No blocking — just visibility. Users can still spend, but they know the cost. |

These defaults work for most users. Users can customize thresholds if they want fewer or more granular alerts.

## Budget Definition Schema

```json
{
  "budgets": [
    {
      "id": "budget_dining_monthly",
      "category": "Dining",
      "amount": 5000.00,
      "currency": "UAH",
      "period": "monthly",
      "thresholds": [50, 75, 90, 100],
      "accountFilter": [],
      "enabled": true
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique budget identifier |
| `category` | string | Spending category (matches transaction-categorization output) |
| `amount` | number | Budget limit for the period |
| `currency` | string | Currency code (default: UAH) |
| `period` | string | `weekly`, `monthly`, `quarterly`, `yearly` |
| `thresholds` | number[] | Percentages at which to fire alerts |
| `accountFilter` | string[] | Account IDs to include (empty = all accounts, which is the common case since users want total spending visibility regardless of which card they used) |
| `enabled` | boolean | Whether this budget is active |

## Period Calculations

| Period | Start | End |
|--------|-------|-----|
| weekly | Monday 00:00 | Sunday 23:59 |
| monthly | 1st of month 00:00 | Last day 23:59 |
| quarterly | Jan/Apr/Jul/Oct 1st | Mar/Jun/Sep/Dec last day |
| yearly | Jan 1st | Dec 31st |

```javascript
function getPeriodRange(period) {
  const now = new Date();
  switch (period) {
    case 'weekly': {
      const start = new Date(now);
      start.setDate(now.getDate() - now.getDay() + 1);
      start.setHours(0, 0, 0, 0);
      const end = new Date(start);
      end.setDate(start.getDate() + 6);
      end.setHours(23, 59, 59, 999);
      return { start, end };
    }
    case 'monthly': {
      const start = new Date(now.getFullYear(), now.getMonth(), 1);
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);
      return { start, end };
    }
    case 'quarterly': {
      const q = Math.floor(now.getMonth() / 3);
      const start = new Date(now.getFullYear(), q * 3, 1);
      const end = new Date(now.getFullYear(), q * 3 + 3, 0, 23, 59, 59);
      return { start, end };
    }
    case 'yearly': {
      return {
        start: new Date(now.getFullYear(), 0, 1),
        end: new Date(now.getFullYear(), 11, 31, 23, 59, 59),
      };
    }
  }
}
```

## Alert Trigger Logic

After each `transaction_added` event (received via the broadcast-pattern skill), check all active budgets. Only the highest newly-crossed threshold fires — so if a single large purchase jumps from 60% to 95%, the user sees the 90% alert, not both 75% and 90%.

```javascript
function checkBudgets(transaction, budgets, transactionHistory) {
  const alerts = [];

  for (const budget of budgets) {
    if (!budget.enabled) continue;
    if (budget.category !== transaction.category) continue;
    if (budget.accountFilter.length && !budget.accountFilter.includes(transaction.accountId)) continue;

    const { start, end } = getPeriodRange(budget.period);
    const spent = transactionHistory
      .filter(t => t.category === budget.category
        && new Date(t.date) >= start
        && new Date(t.date) <= end
        && t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);

    const percentUsed = (spent / budget.amount) * 100;

    for (const threshold of budget.thresholds.sort((a, b) => b - a)) {
      if (percentUsed >= threshold) {
        if (!wasAlreadyTriggered(budget.id, threshold, start)) {
          alerts.push({
            type: 'budget_alert',
            payload: {
              budgetId: budget.id,
              category: budget.category,
              budgetAmount: budget.amount,
              spentAmount: spent,
              percentUsed: Math.round(percentUsed * 10) / 10,
              threshold,
              period: budget.period,
              periodStart: start.toISOString().split('T')[0],
              periodEnd: end.toISOString().split('T')[0],
              remainingBudget: Math.max(0, budget.amount - spent),
            },
          });
          markThresholdTriggered(budget.id, threshold, start);
        }
        break;
      }
    }
  }

  return alerts;
}
```

## Alert Deduplication

Each threshold fires only once per budget period. Without deduplication, every transaction in a category would re-trigger all crossed thresholds, flooding the user with noise.

```json
{
  "triggered": {
    "budget_dining_monthly:2026-03": [50, 75, 90],
    "budget_groceries_monthly:2026-03": [50]
  }
}
```

When a new period starts, triggered thresholds reset automatically.

## Multi-Account Budget Aggregation

Users often pay for food with both their Monobank personal card and PrivatBank business card. By default, budgets aggregate across all accounts so the total spending picture is accurate.

- `accountFilter: []` — aggregate all accounts (default, recommended)
- `accountFilter: ["acc_mono_1234"]` — single account only
- `accountFilter: ["acc_mono_1234", "acc_privat_3456"]` — specific accounts

## Budget Status Display

When the user asks "покажи бюджети" or similar, present a table with visual severity indicators:

```
Category     | Budget     | Spent      | Remaining  | Used
-------------|------------|------------|------------|------
Dining       | ₴5 000,00  | ₴4 756,70  | ₴243,30    | 95.1% !!
Groceries    | ₴8 000,00  | ₴4 231,50  | ₴3 768,50  | 52.9%
Transport    | ₴2 000,00  | ₴895,00    | ₴1 105,00  | 44.8%
Shopping     | ₴3 000,00  | ₴3 124,00  | -₴124,00   | 104.1% !!!
```

Indicators: no marker = under 50%, `!` = 50-74%, `!!` = 75-99%, `!!!` = 100%+ (over budget).

Adapt the presentation to context. If the user only asks about one category, show that category with trend context ("you spent 30% more on dining this month compared to last month"). If they ask for all budgets, show the table.

## Default Budget Templates

Offer these as starting points when a user is new to budgeting. The amounts are based on typical Ukrainian urban household spending and should be adjusted to the user's actual income and lifestyle.

```json
[
  { "category": "Dining", "amount": 5000, "period": "monthly" },
  { "category": "Groceries", "amount": 8000, "period": "monthly" },
  { "category": "Transportation", "amount": 2000, "period": "monthly" },
  { "category": "Shopping", "amount": 3000, "period": "monthly" },
  { "category": "Entertainment", "amount": 1500, "period": "monthly" },
  { "category": "Subscriptions", "amount": 1000, "period": "monthly" }
]
```
