# Monobank API Details

## Fetching Account Information

```
1. Call mcp__monobank__get_client_info or equivalent
   → Returns: client name, accounts list

2. Each account has:
   - id (account identifier)
   - currencyCode (980 = UAH, 840 = USD, 978 = EUR)
   - cashbackType
   - balance (in smallest currency unit, e.g., kopiykas)
   - creditLimit
   - maskedPan (card number masked: ****1234)
   - type (black, white, platinum, etc.)
   - iban
```

## Fetching Transactions (Statements)

```
Call: mcp__monobank__get_statement
Parameters:
  - account: account ID
  - from: start timestamp (Unix seconds)
  - to: end timestamp (Unix seconds)

Returns array of transactions:
  - id: transaction ID
  - time: Unix timestamp
  - description: merchant/description
  - mcc: Merchant Category Code
  - originalMcc: original MCC
  - amount: amount in kopiykas (divide by 100 for UAH)
  - operationAmount: amount in transaction currency
  - currencyCode: ISO 4217 numeric code
  - commissionRate: commission
  - cashbackAmount: cashback earned
  - balance: balance after transaction
  - comment: user comment
  - counterIban: counter-party IBAN
  - counterName: counter-party name
```

**Important:** Monobank limits statement requests to max 31 days per request and 1 request per 60 seconds per account. To fetch 90 days, make 3 sequential requests with 60s delays.
