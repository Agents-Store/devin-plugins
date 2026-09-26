# Scenario: Budget Alert Flow

Walkthrough of setting a budget, spending towards the limit, and receiving broadcast alerts.

## Step 1: Set Budget

```
User: /set-budget Dining 5000 monthly

Agent:
1. Create budget definition:
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
2. Encrypt and store in budgets.enc
3. Confirm to user

Output:
Budget created!
  Category: Dining
  Limit: ₴5 000,00/month
  Alerts at: 50%, 75%, 90%, 100%
  Tracking: All accounts
  Period: Mar 1 - Mar 31, 2026
```

## Step 2: Spending Accumulates

Over the month, dining transactions come in via sync:

| Date | Merchant | Amount | Running Total | % of Budget |
|------|----------|--------|---------------|-------------|
| Mar 3 | Пузата Хата | ₴155 | ₴155 | 3.1% |
| Mar 7 | Мафія (ресторан) | ₴623 | ₴778 | 15.6% |
| Mar 10 | Aroma Kava | ₴67 | ₴845 | 16.9% |
| ... | ... | ... | ... | ... |
| Mar 18 | Ресторан Остання Барикада | ₴1 680 | ₴2 525 | 50.5% |

## Step 3: 50% Alert Triggers

When the restaurant transaction is synced:

```
Broadcast event emitted:
{
  "id": "evt_abc123",
  "type": "budget_alert",
  "timestamp": "2026-03-18T20:15:00Z",
  "payload": {
    "category": "Dining",
    "budgetAmount": 5000.00,
    "spentAmount": 2525.00,
    "percentUsed": 50.5,
    "threshold": 50,
    "period": "monthly",
    "periodStart": "2026-03-01",
    "periodEnd": "2026-03-31",
    "remainingBudget": 2475.00
  }
}

Subscribers notified:
  • budget-monitor widget: displays yellow indicator
  • dashboard: updates budget bar to 50%
```

## Step 4: 75% Alert

```
Mar 22 | Сушія | ₴950 | ₴3 787 | 75.7%

Budget alert emitted: threshold=75, percentUsed=75.7%
Subscribers notified: orange indicator, warning notification
```

## Step 5: 90% Alert

```
Mar 25 | Піца Челентано | ₴520 | ₴4 561 | 91.2%

Budget alert emitted: threshold=90, percentUsed=91.2%
Subscribers notified: red indicator, urgent notification
Remaining: ₴439 for 6 days
```

## Step 6: 100% Alert (Over Budget)

```
Mar 27 | Trattoria Famiglia | ₴685 | ₴5 246 | 104.9%

Budget alert emitted: threshold=100, percentUsed=104.9%
Subscribers notified: red flashing, over-budget notification
Over by: ₴246
```

## Step 7: Check Budget Status

```
User: /budget-status

Output:
Budget Status — March 2026
─────────────────────────────────────────────────
Category     Budget      Spent       Left        Status
─────────────────────────────────────────────────
Dining       ₴5 000,00   ₴5 246,00   -₴246,00   OVER !!!
Groceries    ₴8 000,00   ₴6 234,50   ₴1 765,50  78% !!
Transport    ₴2 000,00   ₴895,00     ₴1 105,00  45%
Shopping     ₴3 000,00   ₴1 452,00   ₴1 548,00  48%
─────────────────────────────────────────────────

Alerts triggered this month:
  Dining: 50% (Mar 18) → 75% (Mar 22) → 90% (Mar 25) → 100% (Mar 27)
  Groceries: 50% (Mar 15) → 75% (Mar 21)
```

## Alert Deduplication

Note that each threshold fires only once per period:
- The 50% alert fires on Mar 18 and does NOT fire again
- The 75% alert fires on Mar 22 — the next threshold up
- When April starts, all thresholds reset
