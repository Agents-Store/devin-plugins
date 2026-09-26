# Event Schemas

Complete JSON Schema definitions for all broadcast event types.

## Base Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BroadcastEvent",
  "type": "object",
  "required": ["id", "type", "timestamp", "payload"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^evt_",
      "description": "Unique event identifier"
    },
    "type": {
      "type": "string",
      "enum": ["balance_updated", "transaction_added", "budget_alert", "sync_complete", "payment_prepared", "payment_completed", "salary_registry_created", "salary_registry_status_changed", "payslips_sent"]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "accountId": {
      "type": ["string", "null"],
      "description": "Source account ID (null for sync_complete)"
    },
    "payload": {
      "type": "object"
    }
  }
}
```

## balance_updated

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BalanceUpdatedPayload",
  "type": "object",
  "required": ["institutionName", "accountName", "currentBalance", "currency"],
  "properties": {
    "institutionName": {
      "type": "string",
      "description": "Bank name (Monobank, PrivatBank)"
    },
    "accountName": {
      "type": "string",
      "description": "Account name with masked number (Checking ****1234)"
    },
    "currentBalance": {
      "type": "number",
      "description": "Current balance in account currency"
    },
    "availableBalance": {
      "type": ["number", "null"],
      "description": "Available balance (may differ from current)"
    },
    "currency": {
      "type": "string",
      "pattern": "^[A-Z]{3}$",
      "description": "ISO 4217 currency code"
    },
    "previousBalance": {
      "type": ["number", "null"],
      "description": "Balance from previous sync"
    },
    "delta": {
      "type": ["number", "null"],
      "description": "Change since last sync"
    }
  }
}
```

## transaction_added

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TransactionAddedPayload",
  "type": "object",
  "required": ["transactionId", "amount", "category", "date"],
  "properties": {
    "transactionId": {
      "type": "string"
    },
    "amount": {
      "type": "number",
      "description": "Negative = debit, positive = credit"
    },
    "category": {
      "type": "string",
      "description": "Mapped budget category"
    },
    "subcategory": {
      "type": ["string", "null"]
    },
    "merchantName": {
      "type": ["string", "null"]
    },
    "date": {
      "type": "string",
      "format": "date"
    },
    "pending": {
      "type": "boolean"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" }
    },
    "location": {
      "type": ["object", "null"],
      "properties": {
        "city": { "type": "string" },
        "state": { "type": "string" },
        "country": { "type": "string" }
      }
    }
  }
}
```

## budget_alert

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BudgetAlertPayload",
  "type": "object",
  "required": ["category", "budgetAmount", "spentAmount", "percentUsed", "threshold", "period"],
  "properties": {
    "budgetId": {
      "type": "string"
    },
    "category": {
      "type": "string"
    },
    "budgetAmount": {
      "type": "number"
    },
    "spentAmount": {
      "type": "number"
    },
    "percentUsed": {
      "type": "number"
    },
    "threshold": {
      "type": "integer",
      "enum": [50, 75, 90, 100]
    },
    "period": {
      "type": "string",
      "enum": ["weekly", "monthly", "quarterly", "yearly"]
    },
    "periodStart": {
      "type": "string",
      "format": "date"
    },
    "periodEnd": {
      "type": "string",
      "format": "date"
    },
    "remainingBudget": {
      "type": "number"
    }
  }
}
```

## sync_complete

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SyncCompletePayload",
  "type": "object",
  "required": ["accountsSynced", "failedAccounts", "transactionsAdded"],
  "properties": {
    "accountsSynced": {
      "type": "array",
      "items": { "type": "string" }
    },
    "failedAccounts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "accountId": { "type": "string" },
          "error": { "type": "string" }
        }
      }
    },
    "totalBalanceUAH": {
      "type": "number"
    },
    "transactionsAdded": {
      "type": "integer"
    },
    "syncDurationMs": {
      "type": "integer"
    },
    "nextSyncScheduled": {
      "type": ["string", "null"],
      "format": "date-time"
    }
  }
}
```

## Subscription Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Subscription",
  "type": "object",
  "required": ["subscriberId", "eventTypes", "callbackType", "callbackTarget"],
  "properties": {
    "subscriberId": {
      "type": "string",
      "description": "Unique subscriber identifier"
    },
    "eventTypes": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["balance_updated", "transaction_added", "budget_alert", "sync_complete", "payment_prepared", "payment_completed", "salary_registry_created", "salary_registry_status_changed", "payslips_sent"]
      },
      "minItems": 1
    },
    "accountFilter": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Empty array = all accounts"
    },
    "callbackType": {
      "type": "string",
      "enum": ["websocket", "polling", "file"]
    },
    "callbackTarget": {
      "type": "string",
      "description": "ws:// URL, HTTP endpoint, or file path"
    }
  }
}
```
