---
name: query-patterns
description: >
  Use when the user asks about "SQLAlchemy queries", "filter records",
  "SQLAlchemy select", "session.scalars", "join tables", "aggregate query",
  "order by", "pagination", "N+1 query problem", "eager loading",
  "SQLAlchemy session", "bulk insert", "convert Model.query to select() 2.0
  style", "upgrade to SQLAlchemy 2.1", "filter queries by current user",
  "owner-scoped queries", or needs patterns for querying data with SQLAlchemy.
---

# SQLAlchemy Query Patterns

Production patterns for querying, filtering, and optimizing database access in the SQLAlchemy 2.0 style: build a statement with `select()`, run it with `session.scalars()` / `session.execute()`. Every example runs unchanged on SQLAlchemy 2.0 and 2.1.

The examples use the models from the `model-patterns` skill (`User`, `Client`, `Appointment`, `Spending`, `Tag`) and a `session` that is a `sqlalchemy.orm.Session`. In Flask-SQLAlchemy use `db.session` and `db.select` (see Flask-SQLAlchemy Shortcuts below).

Reading or migrating `Model.query` / `session.query()` code? See [Legacy 1.x style](../api-reference/references/legacy-1x-style.md).

## Engine and Session

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine("sqlite:///app.db")  # URL from an environment variable in real code
SessionLocal = sessionmaker(engine)

with SessionLocal() as session:  # closes the session on exit
    ...
```

`create_engine` once per process; one short-lived `Session` per unit of work (a request, a job). A `Session` is not thread-safe and not meant to be shared.

## Basic Queries

```python
from sqlalchemy import select

# Get by primary key: returns the object or None, and uses the identity map
user = session.get(User, 1)

# All rows of an entity
users = session.scalars(select(User)).all()

# Filter by keyword equality (single entity, no joins)
vip_clients = session.scalars(select(Client).filter_by(status="vip")).all()

# First match or None
client = session.scalars(select(Client).where(Client.email == "test@example.com")).first()

# Exactly one row: raises NoResultFound / MultipleResultsFound otherwise
user = session.scalars(select(User).where(User.email == "ann@example.com")).one()
```

`session.scalars(stmt)` unwraps the single entity column of each row. Use `session.execute(stmt)` when the statement returns several columns or entities, and read `Row` objects.

| Method | Returns |
|--------|---------|
| `.all()` | list of every row |
| `.first()` | first row or `None` (no error if more rows exist) |
| `.one()` | the only row; raises if there are zero or several |
| `.one_or_none()` | the only row or `None`; raises if several |
| `session.scalar(stmt)` | first column of the first row, or `None` |

Selecting columns instead of entities returns `Row` objects (tuple-like, with attribute access):

```python
rows = session.execute(select(Client.id, Client.name).where(Client.status == "vip")).all()
for client_id, name in rows:
    print(client_id, name)

as_dicts = session.execute(select(Client.id, Client.name)).mappings().all()
```

## Filtering

```python
import datetime as dt

from sqlalchemy import and_, not_, or_, select

# Equality and inequality
select(Client).where(Client.status == "vip")
select(Client).where(Client.status != "cancelled")

# Several where() arguments are ANDed
select(Appointment).where(
    Appointment.user_id == 1,
    Appointment.date == dt.date(2026, 3, 1),
    Appointment.status == "on plan",
)

# LIKE (case-sensitive) and ILIKE (case-insensitive)
select(Client).where(Client.name.like("Ann%"))
select(Client).where(Client.name.ilike("%anna%"))

# User-supplied search text: autoescape stops "%" and "_" acting as wildcards
search_term = "50%"
select(Client).where(Client.name.icontains(search_term, autoescape=True))

# IN
select(Client).where(Client.status.in_(["vip", "regular"]))

# IS NULL / IS NOT NULL
select(Client).where(Client.birthday.is_(None))
select(Client).where(Client.birthday.is_not(None))

# Ranges
select(Appointment).where(Appointment.date.between(dt.date(2026, 3, 1), dt.date(2026, 3, 31)))
select(Appointment).where(Appointment.date >= dt.date(2026, 3, 1), Appointment.date < dt.date(2026, 4, 1))

# OR, explicit AND, NOT
select(Client).where(or_(Client.status == "vip", Client.status == "regular"))
select(Client).where(and_(Client.status == "vip", or_(Client.phone.is_(None), Client.email.is_(None))))
select(Client).where(not_(Client.status == "new"))

# Relationship comparison: EXISTS under the hood
select(Client).where(Client.appointments.any(Appointment.status == "done"))
select(Appointment).where(Appointment.client.has(Client.status == "vip"))
```

For a half-open date range prefer `>= start, < next_start` over `between`, which includes both ends.

## Ordering

```python
# Ascending (default)
select(Client).order_by(Client.name)

# Descending, several keys
select(Appointment).order_by(Appointment.date.desc(), Appointment.time.desc())

select(Client).order_by(Client.status, Client.name)

# NULLs last (supported by PostgreSQL and SQLite 3.30+)
select(Client).order_by(Client.birthday.asc().nulls_last())
```

Add a unique key (`Client.id`) as the last sort key when paginating: without a total order, rows can repeat or vanish between pages.

## Aggregation

```python
from sqlalchemy import func

# Count
count = session.scalar(select(func.count()).select_from(Client).where(Client.user_id == 1))

# Sum; SUM over zero rows is NULL, so coalesce it
total = session.scalar(
    select(func.coalesce(func.sum(Spending.amount), 0)).where(Spending.user_id == 1)
)

# Average
avg_price = session.scalar(select(func.avg(Appointment.price)))

# Group by
spending_by_category = session.execute(
    select(Spending.category, func.sum(Spending.amount).label("total"))
    .where(Spending.user_id == 1)
    .group_by(Spending.category)
    .order_by(func.sum(Spending.amount).desc())
).all()
for category, total in spending_by_category:
    print(category, total)

# HAVING
busy_clients = session.execute(
    select(Appointment.client_id, func.count().label("visits"))
    .group_by(Appointment.client_id)
    .having(func.count() > 1)
).all()
```

## Joins

```python
# Navigating a relationship issues a lazy-load query per object (see Eager Loading)
appointments = session.scalars(select(Appointment).where(Appointment.user_id == 1)).all()
for appt in appointments:
    print(appt.client.name)

# Join along a relationship: returns the entities of both sides
today = dt.date(2026, 3, 1)
rows = session.execute(
    select(Appointment, Client)
    .join(Appointment.client)
    .where(Appointment.date == today)
).all()
for appt, client in rows:
    print(client.name, appt.time)

# Explicit ON clause
select(Appointment, Client).join(Client, Appointment.client_id == Client.id)

# Left outer join: clients with or without appointments
select(Client, Appointment).join(Client.appointments, isouter=True)

# Clients with no appointments at all
select(Client).outerjoin(Client.appointments).where(Appointment.id.is_(None))
```

After a join, qualify filters with the entity (`.where(Client.status == "vip")`). `filter_by()` is shorthand for one entity: SQLAlchemy 2.0 applies it to the last joined entity, 2.1 searches every entity in the FROM clause and raises `AmbiguousColumnError` when a name such as `id` exists in several.

## Eager Loading (Avoid N+1)

```python
from sqlalchemy.orm import joinedload, selectinload

# Many-to-one: one query with a JOIN
appointments = session.scalars(
    select(Appointment).options(joinedload(Appointment.client)).where(Appointment.user_id == 1)
).all()

# Collections: a second query, SELECT ... WHERE client_id IN (...)
clients = session.scalars(
    select(Client).options(selectinload(Client.appointments)).where(Client.user_id == 1)
).all()

# joinedload on a collection repeats parent rows: unique() is required
clients = session.scalars(
    select(Client).options(joinedload(Client.tags)).where(Client.user_id == 1)
).unique().all()
```

Rule of thumb: `joinedload` for many-to-one, `selectinload` for collections. Nested paths chain: `selectinload(Client.appointments).joinedload(Appointment.client)`.

Detect N+1 by logging statements (`create_engine(url, echo=True)`, or `logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)`), or make a lazy load fail loudly:

```python
from sqlalchemy.orm import raiseload

# Any relationship not eagerly loaded raises InvalidRequestError instead of querying
appointments = session.scalars(
    select(Appointment).options(joinedload(Appointment.client), raiseload("*"))
).all()
```

## Pagination

```python
# Offset pagination: simple, but slows down on deep pages
page, per_page = 2, 20
stmt = select(Client).where(Client.user_id == 1).order_by(Client.id)
clients = session.scalars(stmt.limit(per_page).offset((page - 1) * per_page)).all()
total = session.scalar(select(func.count()).select_from(Client).where(Client.user_id == 1))

# Keyset pagination: pass the last id of the previous page
last_seen_id = 100
next_page = session.scalars(
    select(Client).where(Client.user_id == 1, Client.id > last_seen_id).order_by(Client.id).limit(per_page)
).all()
```

In Flask-SQLAlchemy, `db.paginate(select_stmt, page=..., per_page=..., error_out=False)` returns a `Pagination` object (below).

## Session Operations (CRUD)

```python
from sqlalchemy.exc import IntegrityError

# Create
client = Client(name="Anna", phone="+380501234567", user_id=1)
session.add(client)
session.commit()

# Update: change attributes on a loaded object
client.status = "vip"
session.commit()

# Delete
session.delete(client)
session.commit()

# Several objects
session.add_all([Client(name="Ben", user_id=1), Client(name="Cleo", user_id=1)])
session.commit()

# Roll back on error: a failed flush leaves the session unusable until rollback()
try:
    session.add(User(name="Dup", email="ann@example.com"))
    session.commit()
except IntegrityError:
    session.rollback()
    raise
```

Prefer a transaction block: it commits when the block ends and rolls back if an exception leaves it.

```python
with SessionLocal() as session, session.begin():
    session.add(Client(name="Dina", user_id=1))
```

### Bulk Operations

For thousands of rows, send dictionaries instead of building objects. ORM-enabled `insert()`, `update()` and `delete()` run as single statements (the `where` clause uses the model attributes):

```python
from sqlalchemy import delete, insert, update

# Bulk INSERT: executemany, no object per row
session.execute(
    insert(Client),
    [{"user_id": 1, "name": "Eve"}, {"user_id": 1, "name": "Finn"}],
)

# INSERT ... RETURNING: new primary keys without a second query (PostgreSQL, SQLite 3.35+, MariaDB)
new_ids = session.scalars(
    insert(Client).returning(Client.id),
    [{"user_id": 1, "name": "Gus"}, {"user_id": 1, "name": "Hana"}],
).all()

# Bulk UPDATE by primary key: every dictionary carries the key
session.execute(update(Client), [{"id": new_ids[0], "status": "vip"}])

# UPDATE and DELETE by criteria
session.execute(update(Client).where(Client.status == "new").values(status="regular"))
session.execute(delete(Appointment).where(Appointment.status == "cancelled"))
session.commit()
```

A bulk `DELETE` does not run ORM cascades; delete through the session when `cascade="all, delete-orphan"` must apply.

## Subqueries

```python
# Clients with at least one done appointment: a select() goes straight into in_()
done_client_ids = select(Appointment.client_id).where(Appointment.status == "done").distinct()
active_clients = session.scalars(select(Client).where(Client.id.in_(done_client_ids))).all()

# The same with EXISTS
has_done = select(Appointment.id).where(
    Appointment.client_id == Client.id, Appointment.status == "done"
).exists()
active_clients = session.scalars(select(Client).where(has_done)).all()

# Subquery in FROM: visits per client, joined back to the client
visits = (
    select(Appointment.client_id, func.count().label("visits"))
    .group_by(Appointment.client_id)
    .subquery()
)
rows = session.execute(
    select(Client.name, visits.c.visits).join(visits, visits.c.client_id == Client.id)
).all()
```

## Flask-SQLAlchemy Shortcuts

With Flask-SQLAlchemy 3.1 every query above works with `db.session` in place of `session`. The extension adds helpers that need an application context:

```python
from flask import request

# Inside a view function
client = db.get_or_404(Client, client_id)  # session.get() or abort(404)
client = db.first_or_404(db.select(Client).filter_by(email=email))  # first row or abort(404)
client = db.one_or_404(db.select(Client).where(Client.id == client_id))  # exactly one or abort(404)

page = request.args.get("page", 1, type=int)
pagination = db.paginate(
    db.select(Client).where(Client.user_id == 1).order_by(Client.id),
    page=page,
    per_page=20,
    error_out=False,
)
clients = pagination.items  # also: pagination.has_next, .has_prev, .pages, .total
```

`db.select` is `sqlalchemy.select`, and `db.session.execute(db.select(...))` is the Flask-SQLAlchemy documented style. Install Flask-SQLAlchemy with `"SQLAlchemy<2.1"` (see `model-patterns`).

For an app where every row belongs to a signed-in user, scope each query to that user through one helper, fetch records by id together with their owner, and check the foreign keys a form submits: [Owner-scoped queries](references/owner-scoped-queries.md).

## SQLAlchemy 2.1 Behavior

- **`filter_by()`**: after a join, a name present in several entities raises `AmbiguousColumnError`. Use `.where(Entity.column == value)`.
- **Autoflush is unconditional**: pending objects are flushed before every execution, including `text()` statements (2.0 flushed only before ORM statements). Wrap deliberate reads of stale state in `with session.no_autoflush:`.
- **`JSON.contains()`** now emits a deprecation warning: cast to `String` for a substring match, or use PostgreSQL `JSONB`.

All 2.1 changes: [SQLAlchemy 2.1](../api-reference/references/sqlalchemy-2.1.md).
