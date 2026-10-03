---
name: model-patterns
description: >
  Use when the user asks about "SQLAlchemy models", "define database model",
  "Mapped and mapped_column", "DeclarativeBase", "SQLAlchemy relationships",
  "one-to-many relationship", "many-to-many", "SQLAlchemy column types",
  "model constraints", "Flask-SQLAlchemy model", "convert db.Column to Mapped
  2.0 style", "upgrade to SQLAlchemy 2.1", "Flask-Login User model",
  "models owned by a user", or needs patterns for defining database models
  with SQLAlchemy.
---

# SQLAlchemy Model Patterns

Production patterns for defining models, relationships, and constraints in the SQLAlchemy 2.0 typed style: `DeclarativeBase`, `Mapped[...]`, `mapped_column()`, `relationship(back_populates=...)`. Every example runs unchanged on SQLAlchemy 2.0 and 2.1 and uses Python 3.10+ syntax (`str | None`, `list[...]`).

Reading or migrating older code (`db.Column`, `backref`, `Model.query`)? See [Legacy 1.x style](../api-reference/references/legacy-1x-style.md). Queries are in the `query-patterns` skill.

## Declarative Base

One `Base` per project. Give its `MetaData` a naming convention so every constraint and index gets a stable, predictable name; Alembic autogenerate and `ALTER` statements depend on those names.

```python
import datetime as dt
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Index, MetaData, Numeric,
    String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

The `ck` pattern uses `%(constraint_name)s`, so every `CheckConstraint` must be given a `name=`. The other tokens need no extra input.

## Model Definition

```python
def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    bio: Mapped[str | None] = mapped_column(Text)  # "| None" makes the column nullable
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    clients: Mapped[list["Client"]] = relationship(back_populates="user")
    profile: Mapped["Profile | None"] = relationship(back_populates="user")
```

The annotation drives the column: `Mapped[str]` is `NOT NULL`, `Mapped[str | None]` is nullable, and `mapped_column()` with no type uses the annotation's type. `__tablename__` is required in plain SQLAlchemy.

## Flask-SQLAlchemy Model Definition

Flask-SQLAlchemy 3.1 takes the same kind of `Base`: pass it as `model_class` and subclass `db.Model`. The `Mapped` syntax is identical. (In a Flask project this is your only `Base`; it is called `FlaskBase` here so the snippets on this page stay independent.)

```python
from flask_sqlalchemy import SQLAlchemy


class FlaskBase(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


db = SQLAlchemy(model_class=FlaskBase)


class Member(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
```

- Table names are derived from the class name (`Member` becomes `member`, `BlogPost` becomes `blog_post`); set `__tablename__` when you want plural or custom names.
- `db.session`, `db.select`, `db.get_or_404` and `db.paginate` replace `Model.query` (see `query-patterns`).
- Install Flask-SQLAlchemy 3.1 together with `"SQLAlchemy<2.1"`: a `MappedAsDataclass` base fails on SQLAlchemy 2.1 ([pallets-eco/flask-sqlalchemy#1420](https://github.com/pallets-eco/flask-sqlalchemy/issues/1420)); a plain `DeclarativeBase` works, so the pin is a precaution until a Flask-SQLAlchemy release supports 2.1. Plain SQLAlchemy projects use 2.1 freely.

### Flask-Login User and User-Owned Models

The `User` model for Flask-Login (`UserMixin`, normalised email, password hash column) and the `OwnedMixin` that gives every user-owned table a `user_id`, with `Client` and `Appointment` as examples: [Flask-Login User model](references/flask-login-user.md). Its counterpart for queries is `references/owner-scoped-queries.md` in `query-patterns`.

## Column Types

`Mapped[...]` picks a default SQL type from the Python type. Pass an explicit type to `mapped_column()` when you need a length, precision or time zone.

| Python annotation | Default SQL type | Explicit form | Use case |
|-------------------|------------------|---------------|----------|
| `int` | `Integer` | `BigInteger` | IDs, counts |
| `str` | `String` (no length) | `String(N)` | Short text (name, email); give MySQL a length |
| `str` | `String` | `Text` | Long text (notes, content) |
| `bool` | `Boolean` | | Flags |
| `float` | `Float` (`Double` on 2.1) | | Approximate numbers |
| `Decimal` | `Numeric` | `Numeric(10, 2)` | Exact numbers (money) |
| `dt.date` / `dt.time` | `Date` / `Time` | | Date only, time only |
| `dt.datetime` | `DateTime` (naive) | `DateTime(timezone=True)` | Date + time |
| `bytes` | `LargeBinary` | | Binary data |
| `uuid.UUID` | `Uuid` | | UUID keys |
| `enum.Enum` subclass | `Enum` | | Fixed value sets (see Enum Columns) |
| `dict` / `list` | no default (`MappedAnnotationError`) | `mapped_column(JSON)` | JSON documents |

More types and options: the `api-reference` skill.

## Defaults, Nullability and Constraints

```python
class Spending(Base):
    __tablename__ = "spendings"
    __table_args__ = (
        UniqueConstraint("user_id", "spent_on", "category", name="uq_spendings_day_category"),
        CheckConstraint("amount >= 0", name="amount_non_negative"),
        Index("ix_spendings_user_spent_on", "user_id", "spent_on"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    note: Mapped[str | None]
    spent_on: Mapped[dt.date]
    currency: Mapped[str] = mapped_column(String(3), default="USD", server_default="USD")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

- `unique=True` and `index=True` on `mapped_column()` cover single-column cases; use `__table_args__` for composite ones. A dict, if present, must be the last item of `__table_args__`.
- `default=` is applied by SQLAlchemy in Python when it builds the `INSERT`. A callable default must be passed uncalled (`default=utcnow`, or a `lambda`): `default=utcnow()` runs once at import time and stamps every row with the same moment.
- `server_default=` puts the default in the table definition (`DEFAULT CURRENT_TIMESTAMP`), so rows inserted outside the ORM get it too. `default=func.now()` is not a server default: SQLAlchemy sends the expression with each `INSERT`. Use `server_default=func.now()` for a database-side timestamp, and quote a literal default: `server_default="USD"`.
- In a `mapped_column()` use either `default=` or `insert_default=`, not both: SQLAlchemy 2.1 rejects the combination.
- Index foreign key columns you filter or join on (`index=True`); databases do not do it for you.

## Timestamps and Time Zones

Store UTC. `DateTime(timezone=True)` emits `TIMESTAMP WITH TIME ZONE` on PostgreSQL, which keeps the instant correct; a plain `DateTime` is `TIMESTAMP WITHOUT TIME ZONE` and silently drops the offset. SQLite and MySQL have no time zone type: the value comes back as a naive `datetime` even with `timezone=True`. If your code compares against aware datetimes on those databases, restore UTC on the way out:

```python
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    """Aware UTC datetimes in, aware UTC datetimes out, on any database."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            raise ValueError("naive datetime: pass an aware value")
        return value.astimezone(dt.timezone.utc) if value is not None else None

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=dt.timezone.utc)
        return value
```

Use it as `mapped_column(UTCDateTime)`. Do not default to `datetime.utcnow()`: it returns a naive value and is deprecated since Python 3.12.

## Relationships

Declare both sides with `back_populates`, and annotate the collection side `Mapped[list["Child"]]`. The annotation decides the shape: a list is a collection, `Mapped["Parent"]` a required scalar, `Mapped["Parent | None"]` an optional scalar.

### One-to-Many with Cascade Delete

```python
class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="new")  # new / regular / vip
    birthday: Mapped[dt.date | None]

    user: Mapped["User"] = relationship(back_populates="clients")
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship(secondary="client_tags", back_populates="clients")


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    date: Mapped[dt.date]
    time: Mapped[dt.time]
    status: Mapped[str] = mapped_column(String(20), default="on plan")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))

    client: Mapped["Client"] = relationship(back_populates="appointments")
```

`cascade="all, delete-orphan"` deletes a client's appointments with the client (through the ORM, so load or delete via the session, not a bulk `DELETE`). Add `ondelete="CASCADE"` to the foreign key and `passive_deletes=True` to the relationship to let the database do it without loading the children.

### One-to-One

```python
class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    avatar_url: Mapped[str | None] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="profile")
```

`User.profile` is annotated `Mapped["Profile | None"]` (a scalar, so `uselist=False` is implied) and `unique=True` on the foreign key enforces one row per user.

### Many-to-Many

```python
from sqlalchemy import Column, Table

# A pure association table: no extra columns, no mapped class
client_tags = Table(
    "client_tags",
    Base.metadata,
    Column("client_id", ForeignKey("clients.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    clients: Mapped[list["Client"]] = relationship(secondary=client_tags, back_populates="tags")
```

When the link itself carries data (a role, a date), map it as a class and use two one-to-many relationships instead of `secondary`.

### Self-Referential (Hierarchical)

```python
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))

    parent: Mapped["Category | None"] = relationship(back_populates="children", remote_side=[id])
    children: Mapped[list["Category"]] = relationship(back_populates="parent")
```

`remote_side=[id]` marks the "one" end, which makes `parent` the many-to-one side.

### Loader Strategies

The default `lazy="select"` loads a collection on first access, one query per parent row: the N+1 pattern. Pick a strategy deliberately:

| `lazy=` | Behavior | Use when |
|---------|----------|----------|
| `"select"` (default) | Query on first access | Rarely-read relationships |
| `"selectin"` | Second `SELECT ... WHERE id IN (...)` with the parents | Collections you almost always read |
| `"joined"` | `LEFT OUTER JOIN` in the parent query | Small many-to-one targets |
| `"raise"` | Raises `InvalidRequestError` on lazy access | Catch accidental N+1 in tests and hot paths |
| `"write_only"` | No loading; explicit `select()` and `add()`/`remove()` | Huge collections (see `api-reference`) |

Per-query `selectinload()` and `joinedload()` options override the mapping (see `query-patterns`).

## Computed Values

Do not compute a database aggregate inside a `@property` that runs a query: a template loop calls it once per row. Declare it as a SQL expression on the mapped class instead:

```python
from sqlalchemy import select
from sqlalchemy.orm import column_property

# Correlated scalar subquery. deferred=True loads it only on request:
# select(Client).options(undefer(Client.visit_count))
Client.visit_count = column_property(
    select(func.count(Appointment.id))
    .where(Appointment.client_id == Client.id, Appointment.status == "done")
    .correlate_except(Appointment)
    .scalar_subquery(),
    deferred=True,
)
```

Type checkers do not see an attribute attached after the class body. When the referenced class is defined first, put the same `column_property(...)` in the class body with a `Mapped[int]` annotation. For Python-and-SQL computed values use a `hybrid_property` (see `api-reference`).

## Model Mixins

Share common columns across models. Annotated columns on a plain mixin class are copied onto each model:

```python
class TimestampMixin:
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), onupdate=utcnow)


class Note(TimestampMixin, Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    # inherits created_at and updated_at
```

Put the mixin before `Base` in the bases. A `ForeignKey` column works on a mixin like any other; a `relationship()` or `column_property()` on a mixin must be wrapped in `declared_attr`.

## Enum Columns

```python
import enum

from sqlalchemy import Enum


class Priority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, values_callable=lambda e: [m.value for m in e]),
        default=Priority.NORMAL,
    )
```

By default SQLAlchemy stores the member names (`HIGH`); `values_callable` stores the values (`high`). On PostgreSQL an `Enum` is a named `CREATE TYPE`, and changing its members needs a migration (`ALTER TYPE ... ADD VALUE`). For a set that changes often, use a `String` column with a named `CheckConstraint`, or a lookup table with a foreign key.

## Dataclass Models

`MappedAsDataclass` generates `__init__`, `__repr__` and `__eq__` from the annotations:

```python
from sqlalchemy.orm import MappedAsDataclass


class DataclassBase(MappedAsDataclass, DeclarativeBase):
    pass


class Widget(DataclassBase):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]
    status: Mapped[str] = mapped_column(default="new")
```

SQLAlchemy 2.1 changes how dataclass defaults reach the object (the default is delivered on attribute access and is no longer placed in `__dict__`), and `relationship(default=...)` accepts only `None`. Flask-SQLAlchemy 3.1 cannot use a `MappedAsDataclass` base on 2.1 (see the pin above). Details: the 2.1 reference in `api-reference`.
