---
name: bank-api-integration
description: This skill should be used when connecting to bank MCP servers, fetching account balances or transaction statements, handling MCP connection errors, or understanding bank API data formats. Relevant for queries like "show my balance", "connect my bank", "fetch last month transactions", or "why is my bank connection failing". Use this skill whenever the user mentions bank accounts, balances, transactions, MCP connections, or any bank data operation, even if they don't explicitly mention "API" or "MCP".
---

# Bank API Integration (MCP)

This is the central routing hub for all bank API operations. Two Ukrainian banks are supported via MCP (Model Context Protocol) servers — each with its own data formats, rate limits, and quirks.

## Which Skill to Use? (Decision Tree)

Before diving into API calls, pick the right skill for the job. This skill covers core account and transaction operations. Specialized domains have dedicated skills because their APIs, workflows, and error handling differ significantly from basic data fetching.

| User wants to... | Use skill |
|-------------------|-----------|
| Check balances, fetch transactions, connect a bank | **bank-api-integration** (this skill) |
| Set up spending budgets and alerts | **budget-alerts** |
| Categorize transactions, analyze spending | **transaction-categorization** |
| Make payments, track payment status | **payments** |
| Manage salary registries, contacts, payslips | **salary-management** |
| Work with electronic documents (EDO) | **e-documents** |
| Get currency exchange rates | **currency-rates** |
| Receive real-time event notifications | **broadcast-pattern** |
| Encrypt or decrypt stored financial data | **encrypted-storage** |

If the user's request spans multiple skills, start here to fetch the raw data, then hand off to the specialized skill for processing.

## Supported Banks

| Bank | MCP Server | Tool Pattern |
|------|-----------|-------------|
| Monobank | monobank | `mcp__monobank__*` |
| PrivatBank | privatbank | `mcp__privatbank__*` |

## MCP Configuration

Banks are configured in `.mcp.json` at the plugin root:

```json
{
  "mcpServers": {
    "monobank": {
      "type": "http",
      "url": "https://your-mcp-server.example.com/mcp/monobank"
    },
    "privatbank": {
      "type": "http",
      "url": "https://your-mcp-server.example.com/mcp/privatbank"
    }
  }
}
```

Users replace placeholder URLs with their actual MCP server endpoints.

## Tool Discovery

Discover available tools at runtime before executing any bank operation. Tool names vary by MCP server implementation, so hardcoding names would break when servers update their APIs.

1. List all available tools matching the bank's prefix pattern
2. Identify tool names by action suffix (e.g., `get_balance`, `get_statements`)
3. Check tool parameter schemas before calling — parameter names and types differ between banks

```
Available tools might look like:
  mcp__monobank__get_client_info
  mcp__monobank__get_accounts
  mcp__monobank__get_statement
  mcp__monobank__get_currency_rates

  mcp__privatbank__get_balance
  mcp__privatbank__get_statements
  mcp__privatbank__get_card_info
```

## Bank-Specific API Details

Each bank has a detailed reference document. Read these when working with that bank's API — they contain exact field names, parameter formats, and edge cases.

### Monobank
Accounts use `id`, `currencyCode` (980=UAH), `balance` in kopiykas, `iban`. Statements use Unix timestamps, max 31 days per request, 1 req/60s rate limit. For full API details, read `references/monobank-api.md`.

### PrivatBank
Multiple balance types (historical, interim, final). Dates in DD-MM-YYYY format, amounts as decimal strings (not kopiykas). Cursor-based pagination via `followId`. For full API details, read `references/privatbank-api.md`.

## Amount Formatting

Banks return amounts in different formats because they evolved independently — Monobank uses integer kopiykas (common in fintech APIs for precision), while PrivatBank uses decimal strings (legacy banking convention). Mixing them up produces 100x errors, so always check the tool schema.

```javascript
// Monobank: amount is in KOPIYKAS (integer)
const amountUAH = monoAmount / 100;  // 1523400 → 15234.00

// PrivatBank: amount is a DECIMAL STRING
const amountUAH = parseFloat(privatAmount);  // "15234.50" → 15234.50

// Display format: ₴15 234,00
function formatUAH(amount) {
  return '₴' + amount.toLocaleString('uk-UA', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}
```

## Date Format Differences

Different banks, different eras of API design. Convert dates before calling — passing the wrong format silently returns empty results rather than an error.

| Bank | Format | Example |
|------|--------|---------|
| Monobank | Unix timestamp (seconds) | `1711180800` |
| PrivatBank | DD-MM-YYYY | `"23-03-2026"` |

## Rate Limits

Rate limits exist because bank APIs protect against abuse and infrastructure overload. Monobank is especially strict on statement endpoints — violating the limit returns 429 and temporarily blocks the token.

| Bank | Limit | Why it matters |
|------|-------|----------------|
| Monobank | 1 request per 60 seconds per account for statements | Exceeding triggers a temporary block. Other endpoints have no strict limits. |
| PrivatBank | Varies by endpoint | Check MCP server documentation for specifics. |

## Error Handling

| Error | Meaning | Action |
|-------|---------|--------|
| MCP server not found | Server URL incorrect or server down | Check .mcp.json, verify server is running |
| 429 Too Many Requests | Rate limit exceeded | Wait and retry with exponential backoff |
| 403 Forbidden | Token expired or invalid | User needs to re-authenticate |
| Timeout | Server not responding | Retry once, then report to user |
| Connection refused | Server not running | Inform user to check MCP server |

Retry with exponential backoff for transient errors (429, timeout). Non-transient errors (403, connection refused) need user intervention — retrying won't help.

```javascript
async function mcpCallWithRetry(toolCall, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await toolCall();
    } catch (error) {
      if (error.status === 429) {
        const delay = Math.pow(2, i) * 1000;
        await new Promise(r => setTimeout(r, delay));
        continue;
      }
      throw error;
    }
  }
}
```

## Multi-Bank Sync Strategy

Users typically have accounts at both banks and expect a unified view. Fetch in parallel where possible, but respect per-bank rate limits. Emit events progressively so the user sees results as they arrive rather than waiting for everything to finish.

1. Fetch Monobank and PrivatBank accounts in parallel
2. For statements: respect Monobank's 60s rate limit per account
3. Emit `balance_updated` events as each account completes
4. Emit `transaction_added` events in batches of 50
5. Emit `sync_complete` only after all banks finish
6. Track failed banks separately — one bank failing should not block sync for the other

### Pagination Differences

| Bank | Method | Parameters |
|------|--------|-----------|
| Monobank | Offset-based | `limit`, `offset` |
| PrivatBank | Cursor/page-based | `limit`, `followId` (cursor) or `page`, `page-size` |

## Currency Codes (ISO 4217)

Bank MCP tools return numeric ISO 4217 codes. Map to symbols for user-facing display.

| Code | Currency | Symbol |
|------|----------|--------|
| 980 | Ukrainian Hryvnia (UAH) | ₴ |
| 840 | US Dollar (USD) | $ |
| 978 | Euro (EUR) | € |
| 985 | Polish Zloty (PLN) | zł |

## Input/Output Example

**User says:** "Покажи мій баланс по всіх банках"

**What happens:**
1. Discover available MCP tools for both banks
2. Call balance endpoints in parallel (Monobank + PrivatBank)
3. Convert Monobank kopiykas to UAH, parse PrivatBank decimal strings
4. Present unified view:

```
Monobank — Чорна картка ****1234:  ₴15 234,00
Monobank — Біла картка ****5678:   ₴3 100,50
PrivatBank — ФОП ****9012:          ₴48 920,33
─────────────────────────────────────────────
Загалом:                            ₴67 254,83
```
