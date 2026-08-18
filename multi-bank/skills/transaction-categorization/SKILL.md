---
name: transaction-categorization
description: This skill should be used when categorizing bank transactions, mapping MCC codes to spending categories, matching Ukrainian merchant names, or analyzing spending by category. Relevant for queries like "what category is this transaction", "show spending by category", "add a custom category rule", or "where does my money go". Use this skill whenever the user asks about spending categories, where their money goes, merchant classification, or wants to analyze transactions by type.
---

# Transaction Categorization

Transactions from Monobank and PrivatBank arrive with raw data — MCC codes, merchant names, amounts — but users think in categories: "How much did I spend on food?" This skill maps raw transaction data to human-meaningful spending categories.

## Input/Output Example

**Input:** Transaction with description "Сільпо" and MCC 5411

**Categorization process:**
1. Check user overrides — no override for this merchant
2. Check MCC code 5411 (Grocery Stores) — maps to "Groceries"
3. Merchant pattern "сільпо" also matches "Groceries" — consistent, no conflict

**Output:** Category: Groceries, Subcategory: Supermarkets

**Another example showing why priority order matters:**

**Input:** Transaction with description "Bolt" and MCC 4121 (Taxicabs)

1. Check user overrides — none
2. Check MCC 4121 — maps to "Transportation"
3. Merchant pattern "bolt" — also matches "Transportation"

But what if "Bolt" had MCC 5812 (Restaurants)? That happens when Bolt Food processes a food delivery. The MCC says "Dining" but the merchant pattern for /bolt/ says "Transportation". This is why the priority chain exists — and why user overrides sit at the top.

## Why This Priority Chain

The categorization priority is:

1. **Transaction-specific override** (txn_id) — the user explicitly corrected this one transaction
2. **Merchant-specific override** (merchant_name) — the user said "always categorize Amazon as Shopping"
3. **MCC code mapping** — the most reliable automated signal, assigned by the payment network based on the merchant's registered business type
4. **Merchant name patterns** — a fallback for when MCC is too generic or missing
5. **Default: "Other"** — uncategorizable transactions

MCC codes rank above merchant patterns because MCC is assigned by the payment network and reflects the actual business category, while merchant name matching is regex-based and can produce false positives (e.g., "Bolt" could be rides or food delivery). User overrides rank above everything because the user always knows best — if they categorize their gym membership as "Healthcare" instead of "Entertainment", that is their intent and should be respected.

## Standard Category Mapping

| Budget Category | MCC Codes / Description |
|----------------|-----------------|
| Groceries | Food and Drink > Groceries |
| Dining | Food and Drink > Restaurants, Coffee Shop, Bar |
| Transportation | Transportation > Taxi, Ride Share, Gas, Parking |
| Housing | Rent, Mortgage, Home Improvement |
| Utilities | Service > Utilities > Electric, Gas, Water, Internet |
| Entertainment | Recreation > Arts, Music, Movies, Streaming |
| Shopping | Shops > Clothing, Electronics, General Merchandise |
| Healthcare | Healthcare > Medical, Pharmacy, Dental |
| Income | Transfer > Payroll, Deposit |
| Transfer | Transfer > Internal Account Transfer, Wire |
| Subscriptions | Service > Subscription |
| Insurance | Service > Insurance |
| Education | Education > Tuition, Student Loan |
| Travel | Travel > Airlines, Hotels, Vacation |
| Fees | Bank Fees > ATM, Overdraft, Service Charge |
| Other | Uncategorized or unmatched |

## Merchant Pattern Matching (Ukrainian Market)

MCC codes can be too generic — many small Ukrainian businesses register under broad codes. These patterns catch well-known Ukrainian merchants by name, improving accuracy for the local market.

```javascript
const merchantPatterns = [
  { pattern: /сільпо|атб|metro|fozzy|novus|ашан/i, category: 'Groceries' },
  { pattern: /glovo|bolt\s*food|rocket/i, category: 'Dining' },
  { pattern: /uber|bolt|uklon/i, category: 'Transportation' },
  { pattern: /megogo|spotify|sweet\.tv|netflix/i, category: 'Subscriptions' },
  { pattern: /rozetka|prom\.ua|алло|comfy|ельдорадо/i, category: 'Shopping' },
  { pattern: /aroma\s*kava|lviv\s*croissants|пузата\s*хата/i, category: 'Dining' },
  { pattern: /окко|wog|upg|socar/i, category: 'Transportation' },
  { pattern: /аптека|подорожник|доброго\s*дня/i, category: 'Healthcare' },
  { pattern: /sport\s*life|gym/i, category: 'Healthcare' },
  { pattern: /київстар|vodafone|lifecell|укртелеком/i, category: 'Utilities' },
];
```

## Categorization Function

```javascript
function categorize(transaction, overrides) {
  // 1. Transaction-specific override — user explicitly corrected this transaction
  if (overrides[`txn:${transaction.id}`]) {
    return overrides[`txn:${transaction.id}`];
  }

  // 2. Merchant-specific override — user said "always categorize X as Y"
  const merchantKey = `merchant:${transaction.merchantName}`;
  if (overrides[merchantKey]) {
    return overrides[merchantKey];
  }

  // 3. MCC code — most reliable automated signal
  const mccCategory = mapMCC(transaction.mcc);
  if (mccCategory && mccCategory !== 'Other') {
    return mccCategory;
  }

  // 4. Merchant name patterns — fallback for generic/missing MCC
  for (const { pattern, category } of merchantPatterns) {
    if (pattern.test(transaction.description || transaction.merchantName)) {
      return category;
    }
  }

  // 5. Default
  return 'Other';
}
```

## Auto-Tagging Rules

Tags add metadata beyond the single category. They help with queries like "show me recurring expenses" or "flag large purchases."

| Tag | Rule | Why useful |
|-----|------|-----------|
| `recurring` | Same merchant + similar amount (+/-10%) appears monthly | Identifies subscriptions the user might have forgotten about |
| `large-expense` | Amount exceeds ₴5,000 (configurable) | Flags unusual spending for review |
| `refund` | Credit from a merchant with a prior debit | So refunds are not counted as income |
| `pending` | Transaction still pending at the bank | Amount may change when settled |
| `international` | Currency differs from account default | Useful for travel expense tracking |
| `cash` | ATM withdrawal | Cash spending is harder to categorize — flag it |
| `income` | Category is Income or credit > ₴1,000 | Separates inflows from outflows |

```javascript
function autoTag(transaction, history) {
  const tags = [];
  if (transaction.pending) tags.push('pending');
  if (Math.abs(transaction.amount) > 5000) tags.push('large-expense');
  if (transaction.amount < 0 && hasRecentCharge(transaction, history)) tags.push('refund');
  if (isRecurring(transaction, history)) tags.push('recurring');
  if (transaction.iso_currency_code !== transaction.account_currency) tags.push('international');
  return tags;
}
```

## Manual Override

Users can correct categorization at two levels:

```json
{
  "overrides": {
    "merchant:Costco": "Groceries",
    "merchant:Amazon": "Shopping",
    "txn:txn_abc123": "Business Expense"
  }
}
```

When a user says "це бізнес-витрата" about a specific transaction, save a `txn:` override. When they say "Amazon — це завжди шопінг", save a `merchant:` override. Merchant overrides apply to all future transactions from that merchant.

## Spending Analysis Queries

Adapt the response to what the user is actually asking:

| User says | What to do |
|-----------|-----------|
| "Скільки я витратив на їжу минулого місяця?" | Filter category=Dining, date range=last month. Sum amounts, count transactions. Compare to budget if set. |
| "Покажи регулярні витрати" | Filter tag=recurring. Group by merchant, show monthly cost. Highlight forgotten subscriptions. |
| "Куди йдуть мої гроші?" | Group all transactions by category. Sort by total spent descending. Show as percentage of total spending. |
