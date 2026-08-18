# Scenario: Multi-Bank Setup

End-to-end walkthrough of connecting Monobank and PrivatBank via MCP and verifying the setup.

## Prerequisites

- MCP servers for Monobank and PrivatBank deployed and accessible
- `.mcp.json` configured with correct server URLs
- Node.js 18+ installed (for utility scripts)

## Step 1: Verify MCP Configuration

```
User: /connect-bank monobank

Agent:
1. List available MCP tools matching mcp__monobank__*
2. If tools found → server is connected
3. If no tools → check .mcp.json configuration

Output:
Monobank MCP server connected!
Available tools:
  • mcp__monobank__get_client_info
  • mcp__monobank__get_accounts
  • mcp__monobank__get_statement
  • mcp__monobank__get_currency_rates
```

## Step 2: Connect Monobank

```
User: /connect-bank monobank

Agent:
1. Call mcp__monobank__get_client_info (or equivalent)
2. Retrieve account list
3. Display accounts with masked card numbers

Output:
Monobank connected!
Accounts found:
  • Чорна картка ****1234    Balance: ₴15 432,10
  • Біла картка ****5678      Balance: ₴8 200,00
  • Накопичувальна ****9012   Balance: ₴45 000,00
```

## Step 3: Connect PrivatBank

```
User: /connect-bank privatbank

Agent:
1. Call mcp__privatbank__get_balance (or equivalent)
2. Retrieve card/account info
3. Display with masked numbers

Output:
PrivatBank connected!
Accounts found:
  • Картка ****3456            Balance: ₴2 150,30
  • Депозит ****7890           Balance: ₴50 000,00
```

## Step 4: Initial Sync

```
User: /sync-accounts

Agent:
1. Fetch balances from Monobank (all accounts in parallel)
2. Fetch balances from PrivatBank (all accounts in parallel)
3. Fetch statements from Monobank (last 31 days, respecting 60s rate limit)
4. Fetch statements from PrivatBank (last 90 days)
5. Auto-categorize transactions
6. Emit broadcast events

Output:
Sync complete!
• 2 banks synced, 5 accounts updated
• 287 transactions loaded
• 0 budget alerts triggered

Broadcast events emitted:
  balance_updated    ×5
  transaction_added  ×287
  sync_complete      ×1
```

## Step 5: Verify Balances

```
User: /balances

Output:
Account Summary
─────────────────────────────────────────────
Monobank
  Чорна картка ****1234     ₴15 432,10
  Біла картка ****5678       ₴8 200,00
  Накопичувальна ****9012   ₴45 000,00

PrivatBank
  Картка ****3456            ₴2 150,30
  Депозит ****7890          ₴50 000,00
─────────────────────────────────────────────
Total:                     ₴120 782,40
```

## Troubleshooting

### MCP server not found

```
Error: No tools matching mcp__monobank__* found

Fix:
1. Check .mcp.json has correct URL for monobank
2. Verify MCP server is running and accessible
3. Restart Claude Code session to reload MCP connections
```

### Rate limit hit (Monobank)

```
Error: 429 Too Many Requests

Fix:
Monobank limits statement requests to 1 per 60 seconds per account.
Wait 60 seconds and retry. The sync command handles this automatically.
```
