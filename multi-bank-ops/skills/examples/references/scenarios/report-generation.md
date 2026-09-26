# Scenario: Report Generation

End-to-end walkthrough of exporting financial reports in CSV and PDF formats.

## CSV Export

```
User: /export-report csv 90d

Agent:
1. Calculate date range: 2025-12-24 to 2026-03-23
2. Ask: "Where should I save the CSV file?" → User: "Desktop"
3. Fetch transactions from Monobank and PrivatBank via MCP
4. Merge transactions from all accounts
5. Sort by date descending
6. Build input JSON
7. Run: node <plugin_dir>/scripts/export_csv.js /tmp/export_input.json
8. Verify output

Output:
CSV exported successfully!
  Path: /Users/user/Desktop/transactions_2026-03-23.csv
  Size: 45.2 KB
  Transactions: 287
  Date range: Dec 24, 2025 – Mar 23, 2026
  Accounts: 5 (Monobank + PrivatBank)
```

### CSV Output Sample

```csv
date,account,merchant,category,amount,balance
2026-03-22,Monobank ****1234,Сільпо,Groceries,-345.67,15432.10
2026-03-22,Monobank ****1234,Bolt,Transportation,-89.00,15777.77
2026-03-21,PrivatBank ****3456,Rozetka,Shopping,-1299.00,2150.30
2026-03-21,Monobank ****5678,Нарахування %,Income,15.23,8200.00
...
,,,,,
,,,SUMMARY,,
,,,Total Transactions,287,
,,,Total Debits,-82345.60,
,,,Total Credits,124500.00,
,,,Net Change,42154.40,
```

## PDF Export

```
User: /export-report pdf 2026-Q1

Agent:
1. Calculate date range: 2026-01-01 to 2026-03-31
2. Ask: "Where should I save the PDF?" → User: "current folder"
3. Fetch data from both banks via MCP
4. Build comprehensive report data:
   - Account summary with current balances
   - Category breakdown with percentages
   - Budget status comparison
   - Top 20 recent transactions
   - Monthly totals
5. Check pdfkit dependency (silent if installed)
6. Build input JSON
7. Run: node <plugin_dir>/scripts/export_pdf.js /tmp/report_input.json
8. Verify output

Output:
PDF report generated successfully!
  Path: ./financial_report_2026-03-23.pdf
  Size: 128.5 KB
  Pages: 3
  Date range: Jan 1 – Mar 31, 2026
  Accounts: 5 (Monobank + PrivatBank)
```

### PDF Content Structure

**Page 1: Summary**
- Title: "Financial Report — Q1 2026"
- Account table: 5 accounts with balances
- Total: ₴120 782,40
- Period cash flow: +₴42 154,40

**Page 2: Spending Analysis**
- Category breakdown bar chart
- Budget vs actual table
- Top merchants by spend

**Page 3: Recent Transactions**
- Last 20 transactions table
- Monthly spending comparison (Jan vs Feb vs Mar)

## Report for Specific Bank

```
User: /export-report pdf 90d --account Monobank

Agent filters to only Monobank accounts
Output includes only Monobank transactions and balances
```

## Report for Specific Category

```
User: "Generate a report of all dining expenses this year"

Agent:
1. Filter: category=Dining, dateRange=ytd
2. Include: merchant breakdown, weekly trend, budget comparison
3. Export as PDF with focused layout
```
