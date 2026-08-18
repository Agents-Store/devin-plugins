---
name: customer-management
description: Customer listing and details with order history. Use when viewing customer information, searching customers, or checking a customer's order history.
---

# Customer Management

This skill covers customer operations — listing customers with search and sorting, and viewing detailed customer profiles with order history.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_customers` | List customers with search and sorting |
| `get_customer` | Get customer details with order history |

## Listing Customers

```
Tool: list_customers
Input: {
  "search": "John",
  "sortBy": "createdAt",
  "sortOrder": "DESC"
}
```

**Parameters:**

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| search | string | any | Search by name, phone, email, Telegram username |
| sortBy | string | id, firstName, lastName, createdAt, updatedAt | Sort field |
| sortOrder | string | ASC, DESC | Sort direction |

**Response:** Paginated list of CustomerDto

## Getting Customer Details

```
Tool: get_customer
Input: {"id": 789}

Returns: {
  id, firstName, lastName, phoneNumber, email,
  telegramUsername, telegramUserId,
  createdAt, updatedAt,
  orders[]  // Full order history
}
```

## CustomerDto Fields

| Field | Type | Description |
|-------|------|-------------|
| id | number | Customer ID |
| firstName | string | First name |
| lastName | string | Last name |
| phoneNumber | string | Phone number |
| email | string | Email address |
| telegramUsername | string | Telegram @username |
| telegramUserId | string | Telegram user ID |
| createdAt | datetime | Registration date |
| updatedAt | datetime | Last update date |
| orders | array | Order history (when using get_customer) |

## Common Workflows

### Find Customer by Phone
```
1. list_customers(search="+380991234567") -> Find customer
2. get_customer(id) -> View full profile with orders
```

### View Customer Order History
```
1. list_customers(search="John") -> Find customer
2. get_customer(id) -> Get profile with all orders
3. Or: list_orders(customerId=id) -> Get orders with filters
```

### Customer Analytics
```
1. list_customers(sortBy="createdAt", sortOrder="DESC") -> Recent customers
2. For top customers: get_customer(id) -> Check order counts and amounts
```

## Best Practices

1. **Use search broadly** — it checks name, phone, email, and Telegram username
2. **Use get_customer** to see full order history in one call
3. **Use list_orders with customerId** when you need filtered order views for a customer
4. **Customers are created automatically** when they place orders — no manual creation needed
