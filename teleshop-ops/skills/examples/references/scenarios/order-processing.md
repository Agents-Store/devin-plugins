# Order Processing Scenario

Complete scenario for handling orders throughout their lifecycle in a Teleshop store.

## Scenario: Daily Order Management

A merchant processes orders daily — reviewing new orders, preparing shipments, tracking payments, and handling cancellations.

### Morning Routine: Review New Orders

```
1. Check new orders:
   list_orders(status="created", sortBy="createdAt", sortOrder="ASC")
   -> 5 new orders

2. Review each order:
   get_order(id=101)
   -> Order #2001: Maria, 2x "Blue T-Shirt" + 1x "Jeans", Total: $89.97
      Payment: onlinePayment, isPayed: true
      Delivery: novaPoshtaCourier

   get_order(id=102)
   -> Order #2002: Petro, 1x "Leather Jacket", Total: $199.99
      Payment: offlineCash, isPayed: false
      Delivery: selfPickup

3. Start processing paid orders first:
   update_order_status(id=101, status="processing")
   update_order(id=101, comment="Preparing package - 3 items")
```

### Preparing Shipments

```
1. Check processing orders:
   list_orders(status="processing")

2. For shipped orders, add tracking:
   update_order(id=101, ttn="20450123456789")
   update_order_status(id=101, status="shipped")

3. For pickup orders, mark as ready:
   update_order_status(id=102, status="ready")
   update_order(id=102, comment="Ready at counter. Customer notified.")
```

### Handling Payments

```
1. Check unpaid orders:
   list_orders(isPayed=false)

2. For cash-on-delivery after pickup:
   update_order_payment(id=102, isPayed=true)
   update_order_status(id=102, status="completed")

3. For online-paid delivered orders:
   update_order_status(id=101, status="completed")
```

### Handling Cancellations

```
1. Customer requests cancellation:
   get_order(id=103)
   -> Order #2003, status: "processing"

2. Cancel the order:
   update_order_status(id=103, status="canceled")
   update_order(id=103, comment="Canceled per customer request via Telegram")

3. If already paid, note refund:
   update_order(id=103, comment="Refund processed via Way4Pay")
   update_order_payment(id=103, isPayed=false)
```

### End of Day: Summary

```
1. Today's completed orders:
   list_orders(status="completed", sortBy="updatedAt", sortOrder="DESC")
   -> 12 orders completed today

2. Still processing:
   list_orders(status="processing")
   -> 3 orders still being prepared

3. Shipped and in transit:
   list_orders(status="shipped")
   -> 5 orders in transit

4. Canceled today:
   list_orders(status="canceled", sortBy="updatedAt", sortOrder="DESC")
   -> 1 cancellation
```

## Payment Type Workflows

### Online Payment (prepaid)
```
Order created -> isPayed: true automatically
1. update_order_status(id, "processing") -> Start preparing
2. update_order(id, ttn="...") -> Add tracking
3. update_order_status(id, "shipped") -> Ship
4. update_order_status(id, "completed") -> Complete
```

### Cash on Delivery
```
Order created -> isPayed: false
1. update_order_status(id, "processing") -> Start preparing
2. update_order(id, ttn="...") -> Add tracking
3. update_order_status(id, "shipped") -> Ship
4. update_order_payment(id, isPayed=true) -> Mark paid on receipt
5. update_order_status(id, "completed") -> Complete
```

### Self-Pickup
```
Order created -> isPayed: may vary
1. update_order_status(id, "processing") -> Prepare
2. update_order_status(id, "ready") -> Ready for pickup
3. update_order_payment(id, isPayed=true) -> Mark paid at pickup
4. update_order_status(id, "completed") -> Picked up
```

### Telegram Stars (Digital)
```
Order created -> isPayed: true automatically
1. update_order_status(id, "processing") -> Process
2. update_order_status(id, "completed") -> Deliver digitally and complete
   (Digital delivery is instant — no shipping needed)
```

## Customer Lookup for Orders

```
1. Find customer:
   list_customers(search="Maria")
   -> Customer #789: Maria K., +380991234567

2. View all their orders:
   list_orders(customerId=789, sortBy="createdAt", sortOrder="DESC")
   -> 5 orders total

3. Get full customer profile:
   get_customer(id=789)
   -> Profile with all order history
```

## Bulk Order Processing Tips

```
1. Process by payment type:
   list_orders(status="created", paymentType="onlinePayment", isPayed=true)
   -> Paid orders first (ready to ship immediately)

2. Process by delivery type:
   list_orders(status="processing", deliveryType="novaPoshtaCourier")
   -> Batch all Nova Poshta shipments together

3. Process by customer:
   list_orders(customerId=789)
   -> Combine multiple orders from same customer into one shipment
```
