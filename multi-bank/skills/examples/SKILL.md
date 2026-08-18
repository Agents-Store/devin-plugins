---
name: examples
description: This skill should be used when looking for complete workflow examples, step-by-step setup guides, architecture diagrams, or command references. Relevant for queries like "how do I set up multi-bank", "show me an example of the budget alert flow", "walk me through generating a report", or "show first-time setup guide". Use this skill whenever the user asks "how do I...", wants a walkthrough, needs a step-by-step guide, or is setting up the plugin for the first time.
---

# Examples & References

Starting point for the Multi-Bank Account Manager plugin. Use this skill to find the right workflow, reference, or guide.

## New User? Start Here

If you are setting up for the first time or unsure what this plugin can do, follow this path:

1. **Connect your banks** — verify MCP connectivity to each bank.
   ```
   /connect-bank monobank
   /connect-bank privatbank
   ```
2. **Sync accounts** — pull in all account data.
   ```
   /sync-accounts
   ```
3. **Check balances** — verify everything loaded correctly.
   ```
   /balances
   ```
4. **Set a budget** — try tracking one spending category.
   ```
   /set-budget Dining 5000 monthly
   ```
5. **Export a report** — generate your first report to see the data in action.
   ```
   /export-report pdf 30d
   ```

After these steps, you have a working multi-bank setup with budgeting and reporting.

## What Can I Do? (By Use Case)

### Money & Payments
| Task | Command / Skill | Example |
|------|----------------|---------|
| Check all balances | `/balances` | `/balances` |
| Send a payment | `payments` skill | "відправ 10000 грн на IBAN UA29..." |
| Check payment status | `payments` skill | "який статус мого платежу?" |
| Make a tax payment | `payments` skill | "сплати ПДВ за березень" |

### Currency & Rates
| Task | Command / Skill | Example |
|------|----------------|---------|
| Current exchange rate | `currency-rates` skill | "який курс долара?" |
| Rate history | `currency-rates` skill | "динаміка курсу EUR за тиждень" |
| Compare bank rates | `currency-rates` skill | "порівняй курси в Моно і Приваті" |

### Documents (EDO)
| Task | Command / Skill | Example |
|------|----------------|---------|
| View inbox | `e-documents` skill | "покажи вхідні документи за березень" |
| Check signatures | `e-documents` skill | "хто підписав документ #123?" |
| Download a document | `e-documents` skill | "завантаж акт від контрагента" |

### Salary & Payroll
| Task | Command / Skill | Example |
|------|----------------|---------|
| Manage employees | `salary-management` skill | "додай працівника до зарплатного проєкту" |
| Create salary registry | `salary-management` skill | "створи відомість за березень" |
| Send payslips | `salary-management` skill | "розішли розрахункові листки" |

### Reports & Export
| Task | Command / Skill | Example |
|------|----------------|---------|
| PDF report | `report-export` skill | `/export-report pdf 2026-Q1` |
| CSV for spreadsheet | `report-export` skill | `/export-report csv last-month` |
| Transaction history | `/transactions` | `/transactions 30 Groceries` |

### Budgeting
| Task | Command / Skill | Example |
|------|----------------|---------|
| Set a budget | `/set-budget` | `/set-budget Dining 5000 monthly` |
| Check budget status | `/budget-status` | `/budget-status` |
| Budget alerts | `budget-alert-flow` reference | See reference file below |

## Quick Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `/connect-bank` | Verify MCP connectivity | `/connect-bank monobank` |
| `/balances` | Show all account balances | `/balances` |
| `/transactions` | List recent transactions | `/transactions 30 Groceries` |
| `/set-budget` | Create/update a budget | `/set-budget Dining 5000 monthly` |
| `/budget-status` | Check spending vs budgets | `/budget-status` |
| `/export-report` | Export CSV or PDF report | `/export-report pdf 90d` |
| `/sync-accounts` | Force-sync all accounts | `/sync-accounts` |
| `/broadcast-status` | Show broadcast system info | `/broadcast-status` |

## Reference Files

### Architecture
| File | What it covers |
|------|---------------|
| [broadcast-pattern.md](references/architecture/broadcast-pattern.md) | Broadcast architecture, sequence diagrams, code samples |
| [event-schemas.md](references/architecture/event-schemas.md) | JSON schemas for all 9 event types |

### Scenario Walkthroughs
| File | What it covers |
|------|---------------|
| [multi-bank-setup.md](references/scenarios/multi-bank-setup.md) | End-to-end: configure MCP, connect banks, verify balances |
| [budget-alert-flow.md](references/scenarios/budget-alert-flow.md) | Set budget, spend reaches threshold, alert triggers |
| [report-generation.md](references/scenarios/report-generation.md) | Select date range, aggregate transactions, export CSV/PDF |

## Daily Workflow

A typical daily check takes under a minute:

```
/balances              → Quick balance overview
/budget-status         → Check budget utilization
/transactions 7        → This week's transactions
```

## Monthly Workflow

End-of-month routine:

```
/export-report pdf last-month    → Formal PDF report
/export-report csv last-month    → CSV for accounting/analysis
```

For salary: use the `salary-management` skill to create registries and distribute payslips.
