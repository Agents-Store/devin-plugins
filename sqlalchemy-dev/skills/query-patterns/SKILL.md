---
name: query-patterns
description: >
  Use when the user asks about "SQLAlchemy queries", "filter records",
  "SQLAlchemy select", "join tables", "aggregate query", "order by",
  "pagination", "N+1 query problem", "eager loading", "SQLAlchemy session",
  or needs patterns for querying data with SQLAlchemy.
---

# SQLAlchemy Query Patterns

Production patterns for querying, filtering, and optimizing database access with SQLAlchemy 2.0+.

## Basic Queries (Flask-SQLAlchemy)

```python
# Get all records
users = User.query.all()

# Get by primary key (SQLAlchemy 2.0 style — preferred)
user = db.session.get(User, 1)

# Filter by column value
active_clients = Client.query.filter_by(status='vip').all()

# First match (or None)
client = Client.query.filter_by(email='test@example.com').first()

# First match (or 404)
client = Client.query.get_or_404(client_id)
```

## SQLAlchemy 2.0 Select Style

```python
from sqlalchemy import select

# Preferred in SQLAlchemy 2.0+
stmt = select(User).where(User.email == 'test@example.com')
user = db.session.execute(stmt).scalar_one_or_none()

# Multiple results
stmt = select(Client).where(Client.user_id == current_user.id)
clients = db.session.execute(stmt).scalars().all()
```

## Filtering

```python
# Equality
Client.query.filter_by(status='vip')
Client.query.filter(Client.status == 'vip')

# Not equal
Client.query.filter(Client.status != 'cancelled')

# LIKE (case-sensitive)
Client.query.filter(Client.name.like('%anna%'))

# ILIKE (case-insensitive)
Client.query.filter(Client.name.ilike(f'%{search_term}%'))

# IN
Client.query.filter(Client.status.in_(['vip', 'regular']))

# IS NULL / IS NOT NULL
Client.query.filter(Client.birthday.is_(None))
Client.query.filter(Client.birthday.isnot(None))

# Date range
from datetime import date
Appointment.query.filter(
    Appointment.date >= date(2026, 3, 1),
    Appointment.date <= date(2026, 3, 31)
)

# AND (multiple filters)
Appointment.query.filter(
    Appointment.user_id == user_id,
    Appointment.date == today,
    Appointment.status == 'on plan'
)

# OR
from sqlalchemy import or_
Client.query.filter(or_(
    Client.status == 'vip',
    Client.status == 'regular'
))
```

## Ordering

```python
# Ascending (default)
Client.query.order_by(Client.name)

# Descending
Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc())

# Multiple columns
Client.query.order_by(Client.status, Client.name)
```

## Aggregation

```python
from sqlalchemy import func

# Count
count = Client.query.filter_by(user_id=user_id).count()

# Sum
total = db.session.query(func.sum(Spending.amount)).filter_by(
    user_id=user_id
).scalar() or 0

# Average
avg_price = db.session.query(func.avg(Appointment.price)).scalar()

# Group by
spending_by_category = db.session.query(
    Spending.category,
    func.sum(Spending.amount).label('total')
).filter_by(user_id=user_id).group_by(Spending.category).all()
```

## Joins

```python
# Implicit join via relationship
appointments = Appointment.query.filter_by(user_id=user_id).all()
for appt in appointments:
    print(appt.client.name)  # Accesses related client (lazy load)

# Explicit join
results = db.session.query(Appointment, Client).join(
    Client, Appointment.client_id == Client.id
).filter(Appointment.date == today).all()

# Left outer join
results = db.session.query(Client).outerjoin(Appointment).all()
```

## Eager Loading (Avoid N+1)

```python
from sqlalchemy.orm import joinedload, selectinload

# Join load — single query with JOIN
appointments = Appointment.query.options(
    joinedload(Appointment.client)
).filter_by(user_id=user_id).all()

# Select-in load — 2 queries (better for collections)
clients = Client.query.options(
    selectinload(Client.appointments)
).filter_by(user_id=user_id).all()
```

## Pagination

```python
# Flask-SQLAlchemy pagination
page = request.args.get('page', 1, type=int)
pagination = Client.query.filter_by(user_id=user_id).paginate(
    page=page, per_page=20, error_out=False
)
clients = pagination.items
# pagination.has_next, pagination.has_prev, pagination.pages
```

## Session Operations (CRUD)

```python
# Create
client = Client(name='Anna', phone='+380501234567', user_id=user_id)
db.session.add(client)
db.session.commit()

# Update
client.status = 'vip'
db.session.commit()

# Delete
db.session.delete(client)
db.session.commit()

# Bulk insert
db.session.add_all([client1, client2, client3])
db.session.commit()

# Rollback on error
try:
    db.session.add(client)
    db.session.commit()
except Exception:
    db.session.rollback()
    raise
```

## Subqueries

```python
# Clients with at least one done appointment
subq = db.session.query(Appointment.client_id).filter(
    Appointment.status == 'done'
).distinct().subquery()

active_clients = Client.query.filter(Client.id.in_(select(subq))).all()
```
