---
name: report-export
description: This skill should be used when exporting transaction data to CSV or PDF, generating financial reports for a date range, or configuring report layout and format options. Relevant for queries like "export my transactions to CSV", "generate a PDF report for last quarter", "export 90 days of data", or "create a monthly financial report". Use this skill whenever the user wants to export, download, save, or generate any file from their financial data — CSV, PDF, report, or statement.
---

# Report Export

Export financial data as CSV or PDF. Both formats support date range filtering and multi-account merging.

## When to Use CSV vs. PDF

| Format | Best for | Why |
|--------|----------|-----|
| **CSV** | Data analysis, importing into Excel/Google Sheets, automated processing | Raw structured data that can be sorted, filtered, and calculated on. Accountants and analysts need this for reconciliation and custom reports. |
| **PDF** | Sharing with management, formal reports, printing, archiving | Formatted, read-only document that looks professional and preserves layout. Good for board meetings, tax submissions, or sending to partners. |

When the user's intent is unclear, ask: "Вам потрібен файл для аналізу (CSV) чи готовий звіт для друку/відправки (PDF)?"

## Practical Example

**User says:** "зроби PDF звіт за квартал"

**Step-by-step workflow:**

1. **Interpret the request:** "За квартал" means the current or most recent quarter. Since today is 2026-03-24, Q1 2026 is the current quarter: Jan 1 - Mar 31, 2026. If it were April, "за квартал" would likely mean the just-completed Q1.

2. **Ask which accounts to include** (if multiple are connected). Default to all accounts if the user does not specify.

3. **Fetch transaction data** from bank MCP servers for the date range. Use the encrypted cache if available to avoid redundant API calls.

4. **Build the input JSON** with account summaries, category breakdown, budget status, and recent transactions.

5. **Ask where to save** (default: current directory).

6. **Run the export script:**
   ```bash
   node <plugin_dir>/scripts/export_pdf.js <input.json>
   ```

7. **Verify and report:**
   ```
   Звіт створено:
     Файл: /Users/user/report_2026-Q1.pdf
     Період: 01.01.2026 – 31.03.2026
     Рахунки: 2 (Monobank, PrivatBank)
     Розмір: 245 KB

   Звіт містить:
     - Баланси по рахунках
     - Витрати за категоріями
     - Статус бюджетів
     - Останні 20 транзакцій
   ```

## CSV Export

### Script Invocation

```bash
node <plugin_dir>/scripts/export_csv.js <input.json>
```

### Input JSON Format

```json
{
  "outputPath": "/path/to/report_2026-Q1.csv",
  "dateRange": { "start": "2026-01-01", "end": "2026-03-31" },
  "accounts": ["acc_mono_1234", "acc_privat_3456"],
  "columns": ["date", "account", "merchant", "category", "amount", "balance"],
  "transactions": [
    {
      "date": "2026-03-22",
      "account": "Monobank ****1234",
      "merchant": "Сільпо",
      "category": "Groceries",
      "amount": -345.67,
      "balance": 15432.10
    }
  ],
  "includeHeaders": true,
  "includeSummary": true
}
```

### CSV Columns

| Column | Description | Format |
|--------|-------------|--------|
| date | Transaction date | YYYY-MM-DD |
| account | Account name with mask | "Monobank ****1234" |
| merchant | Merchant or description | String |
| category | Budget category | String |
| amount | Transaction amount | -345.67 (negative = debit) |
| balance | Running balance | 15432.10 |
| tags | Auto-tags | "recurring, large-expense" |
| pending | Pending status | true/false |

### Summary Section

When `includeSummary: true`, append summary rows at the bottom:

```csv
date,account,merchant,category,amount,balance
2026-03-22,Monobank ****1234,Сільпо,Groceries,-345.67,15432.10
...
,,,,,
,,,SUMMARY,,
,,,Total Transactions,287,
,,,Total Debits,-45234.50,
,,,Total Credits,62000.00,
,,,Net Change,16765.50,
```

## PDF Export

### Script Invocation

```bash
node <plugin_dir>/scripts/export_pdf.js <input.json>
```

### Input JSON Format

```json
{
  "outputPath": "/path/to/report_2026-Q1.pdf",
  "title": "Financial Report",
  "currencySymbol": "₴",
  "dateRange": { "start": "2026-01-01", "end": "2026-03-31" },
  "accounts": [
    {
      "name": "Monobank Чорна картка ****1234",
      "currentBalance": 15432.10,
      "institution": "Monobank"
    }
  ],
  "categoryBreakdown": [
    { "category": "Groceries", "amount": 6234.50, "count": 23, "percent": 25.2 }
  ],
  "budgetStatus": [
    { "category": "Dining", "budget": 5000, "spent": 4756.70, "percent": 95.1 }
  ],
  "recentTransactions": [],
  "totals": {
    "totalBalance": 120782.40,
    "totalDebits": -31286.20,
    "totalCredits": 62000.00,
    "netChange": 30713.80
  }
}
```

### PDF Layout

```
┌──────────────────────────────────────┐
│          Financial Report            │
│       Jan 1 - Mar 31, 2026          │
├──────────────────────────────────────┤
│ Account Summary                      │
│ ┌──────────────────┬────────────┐   │
│ │ Monobank ****1234│ ₴15 432,10 │   │
│ │ PrivatBank ****34│  ₴2 150,30 │   │
│ ├──────────────────┼────────────┤   │
│ │ Total            │₴120 782,40 │   │
│ └──────────────────┴────────────┘   │
├──────────────────────────────────────┤
│ Spending by Category                 │
│ Groceries     ████████████ ₴6 234   │
│ Dining        ██████████   ₴4 757   │
├──────────────────────────────────────┤
│ Budget Status                        │
│ Dining       [████████████░] 95.1%   │
│ Groceries    [█████████░░░░] 77.9%   │
├──────────────────────────────────────┤
│ Recent Transactions (last 20)        │
│ ... transaction table ...            │
└──────────────────────────────────────┘
```

## Workflow

1. Determine format (CSV or PDF) and date range from user request.
2. Ask where to save the file (default: current directory).
3. Resolve plugin directory to find export scripts.
4. Fetch data from banks via MCP (or use encrypted cache).
5. Build the input JSON with requested date range and accounts.
6. Write input JSON to a temp file.
7. Run the appropriate export script.
8. Verify output file exists and report file path + size.
9. Delete temp input JSON — it may contain transaction data that should not persist on disk.

## Date Range Shortcuts

| Input | Interpreted As |
|-------|---------------|
| `30d` | Last 30 days |
| `90d` | Last 90 days |
| `2026-Q1` | Jan 1 - Mar 31, 2026 |
| `2026-03` | Mar 1 - Mar 31, 2026 |
| `2026-01-01 to 2026-03-31` | Explicit range |
| `ytd` | January 1 to today |
| `last-month` | Previous calendar month |

When the user says "за квартал" or "за місяць" without specifying which one, default to the most recent completed period — or the current one if more than halfway through.
