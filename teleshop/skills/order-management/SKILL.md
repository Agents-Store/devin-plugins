---
name: order-management
description: Order listing, filtering, status updates, payment management, and tracking. Use when viewing orders, changing order status, updating payment, or adding tracking numbers.
---

# Order Management

This skill covers all order operations — listing orders with filters, viewing order details, updating status, payment, and order information.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_orders` | List orders with pagination and filters |
| `get_order` | Get single order with full details |
| `update_order` | Update order info (tracking, notes, customer details) |
| `update_order_status` | Change order status |
| `update_order_payment` | Mark order as paid/unpaid |

## Listing Orders

### List with Filters
```
Tool: list_orders
Input: {
  "search": "John",
  "sortBy": "createdAt",
  "sortOrder": "DESC",
  "status": "processing",
  "paymentType": "onlinePayment",
  "isPayed": true
}
```

**Filter Parameters:**

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| search | string | any | Search by customer name, phone, email |
| sortBy | string | id, orderNumber, totalAmount, status, createdAt, updatedAt, deliveryType | Sort field |
| sortOrder | string | ASC, DESC | Sort direction |
| status | string | created, processing, awaiting, shipped, ready, completed, canceled | Filter by status |
| paymentType | string | offlineCard, offlineCash, onlinePayment, cardPrepay, cardPartialPrepay, telegramStars | Payment type |
| deliveryType | string | selfPickup, delivery, novaPoshtaCourier, novaPoshtaSelfPickup, electronicDelivery | Delivery type |
| isPayed | boolean | true/false | Filter by payment status |
| customerId | number | any | Filter by customer ID |
| isArchived | boolean | true/false | Filter archived orders |

## Getting Order Details

```
Tool: get_order
Input: {"id": 456}

Returns full order with: id, orderNumber, statusCode, totalAmount, bonusAmount,
moneyAmount, accruedBonusAmount, isPayed, paymentType, fullName, phoneNumber,
email, comment, ttn (tracking number), shippingAddress, orderItems[],
customer, deliveryType, customFields, createdAt, updatedAt.
```

## Order Status Flow

```
created → processing → awaiting → shipped → ready → completed
                ↘                                      ↗
                  → → → → → canceled → → → → → → → →
```

**Status descriptions:**
| Status | Description |
|--------|-------------|
| `created` | New order, just placed by customer |
| `processing` | Merchant is processing the order |
| `awaiting` | Awaiting pickup/delivery |
| `shipped` | Order has been shipped |
| `ready` | Ready for pickup |
| `completed` | Order fulfilled |
| `canceled` | Order canceled |

### Update Order Status
```
Tool: update_order_status
Input: {
  "id": 456,
  "status": "processing"
}
```

## Payment Management

### Mark Order as Paid
```
Tool: update_order_payment
Input: {
  "id": 456,
  "isPayed": true
}
```

### Mark Order as Unpaid
```
Tool: update_order_payment
Input: {
  "id": 456,
  "isPayed": false
}
```

**Payment types reference:**
| Type | Description |
|------|-------------|
| `offlineCard` | Card payment on delivery |
| `offlineCash` | Cash on delivery |
| `onlinePayment` | Online payment (Way4Pay, Mono, Stripe, etc.) |
| `cardPrepay` | Full card prepayment (P2P transfer) |
| `cardPartialPrepay` | Partial card prepayment |
| `telegramStars` | Telegram Stars (XTR) for digital goods |

## Updating Order Information

### Add Tracking Number
```
Tool: update_order
Input: {
  "id": 456,
  "ttn": "20450123456789"
}
```

### Update Customer Info and Add Comment
```
Tool: update_order
Input: {
  "id": 456,
  "fullName": "John Smith",
  "phoneNumber": "+380991234567",
  "email": "john@example.com",
  "comment": "Customer requested express delivery",
  "skipConfirmationCall": true
}
```

**Updatable fields:**

| Field | Type | Description |
|-------|------|-------------|
| ttn | string | Tracking number (TTN) |
| comment | string | Merchant comment/notes |
| email | string | Customer email |
| fullName | string | Customer full name |
| phoneNumber | string | Customer phone number |
| skipConfirmationCall | boolean | Skip confirmation call |

## Delivery Types Reference

| Type | Description |
|------|-------------|
| `selfPickup` | Customer picks up at store |
| `delivery` | General delivery |
| `novaPoshtaCourier` | Nova Poshta courier delivery |
| `novaPoshtaSelfPickup` | Nova Poshta self-pickup at branch |
| `electronicDelivery` | Electronic/digital delivery |

## Common Workflows

### Process New Orders
```
1. list_orders(status="created", sortBy="createdAt", sortOrder="ASC") -> Get new orders
2. get_order(id) -> Review order details
3. update_order_status(id, status="processing") -> Start processing
4. update_order(id, comment="Started preparing") -> Add notes
```

### Ship Order with Tracking
```
1. get_order(id) -> Verify order is ready
2. update_order(id, ttn="20450123456789") -> Add tracking number
3. update_order_status(id, status="shipped") -> Mark as shipped
```

### Complete Order After Payment
```
1. update_order_payment(id, isPayed=true) -> Mark as paid
2. update_order_status(id, status="completed") -> Complete order
```

### Daily Order Summary
```
1. list_orders(status="created") -> Count new orders
2. list_orders(status="processing") -> Count in-progress
3. list_orders(status="shipped") -> Count shipped
4. list_orders(status="completed", sortBy="updatedAt", sortOrder="DESC") -> Recent completions
```

## Best Practices

1. **Always get_order before status update** to verify current state
2. **Add tracking number before marking as shipped**
3. **Use comment field** to log important notes about the order
4. **Check isPayed** before completing orders with offline payment types
5. **Use search** to quickly find orders by customer name or phone
