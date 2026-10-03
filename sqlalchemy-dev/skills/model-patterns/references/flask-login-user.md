# Flask-Login User Model and Owned Entities

The `User` model of a Flask application that signs people in with Flask-Login, and the base for every row that belongs to a user. It is written for Flask-SQLAlchemy 3.1 with the `Base`, `db` and `extensions.py` of the `flask-dev` plugin (`project-scaffold`), and the 2.0 typed style of `model-patterns`. The login routes themselves are in `flask-dev` (`auth-flask-login`); the scoped queries are in `query-patterns` (`references/owner-scoped-queries.md`).

## User

```python
# models.py
import datetime as dt
from decimal import Decimal

from flask_login import UserMixin
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship, validates

from extensions import db


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    clients: Mapped[list['Client']] = relationship(
        back_populates='user', cascade='all, delete-orphan', lazy='raise'
    )

    @validates('email')
    def normalise_email(self, key: str, value: str) -> str:
        return value.strip().lower()
```

- `UserMixin` comes first in the bases. It supplies `is_authenticated`, `is_active`, `is_anonymous` and `get_id()`; Flask-Login stores `get_id()` (the primary key as a string) in the session and hands that string back to the `user_loader`.
- The email is normalised in the model, so every code path that creates a user (a route, a CLI command, a test) stores the same form. `unique=True` makes the database the judge of duplicates: a unique index compares bytes, so `Ann@example.com` and `ann@example.com` are different values unless the model lower-cases them.
- The model keeps only `password_hash`, never a password. A Werkzeug 3 scrypt hash is about 160 characters, so `String(256)` has room for a stronger setting. Do not put the hash in `__repr__`, in logs or in a JSON response.
- `lazy='raise'` on `User.clients` makes an accidental `user.clients` in a template an error instead of a hidden query; load it on purpose with `selectinload(User.clients)`.
- The `user_loader` is `db.session.get(User, int(user_id))`: a primary-key lookup that goes through the identity map, one query per request at most.
- Look a user up by email with `db.session.scalar(db.select(User).filter_by(email=email))`; it is `None` when there is no such user.

To let an administrator switch accounts off, shadow the mixin's `is_active` property with a column; Flask-Login then refuses to sign in or keep signed in an inactive user:

```python
from sqlalchemy import true


class User(UserMixin, db.Model):
    ...
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
```

## Owned Entities

Most rows in such an app belong to one user. Give them one shared `user_id` column, so a single helper can scope any query (`owned_by()` in `owner-scoped-queries.md`) and a missing column is a model error, not a leak.

```python
# models.py (continued)
class OwnedMixin:
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)


class Client(OwnedMixin, db.Model):
    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default='new')  # new / regular / vip
    birthday: Mapped[dt.date | None]
    notes: Mapped[str | None]

    user: Mapped['User'] = relationship(back_populates='clients')
    appointments: Mapped[list['Appointment']] = relationship(
        back_populates='client', cascade='all, delete-orphan', lazy='raise'
    )


class Appointment(OwnedMixin, db.Model):
    __tablename__ = 'appointments'

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.id'), index=True)
    date: Mapped[dt.date]
    time: Mapped[dt.time]
    status: Mapped[str] = mapped_column(String(20), default='on plan')
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0'))

    client: Mapped['Client'] = relationship(back_populates='appointments', lazy='raise')


# A computed column for list views (see Computed Values in model-patterns): a correlated
# subquery, loaded only when a query asks for it with undefer(Client.visit_count)
Client.visit_count = column_property(
    select(func.count(Appointment.id))
    .where(Appointment.client_id == Client.id, Appointment.status == 'done')
    .correlate_except(Appointment)
    .scalar_subquery(),
    deferred=True,
)
```

- Put `OwnedMixin` before `db.Model`. A plain `Mapped[...]` column on a mixin is copied onto each model, `ForeignKey` and `index=True` included; a `relationship()` on a mixin would need `declared_attr`, so each model declares its own `user` relationship.
- A foreign key to another owned row (`Appointment.client_id`) is checked at write time: the database only knows the client exists, not that it is the same user's. See "Foreign keys the user submits" in `owner-scoped-queries.md`.
- `lazy='raise'` on the collections and on `Appointment.client` is the N+1 guard for template loops (see `model-patterns`, Loader Strategies): every view names the loaders it needs.
- `Mapped[Decimal]` with `Numeric(10, 2)` is exact on PostgreSQL. SQLite has no decimal type: SQLAlchemy stores it as a float and emits a warning when it converts a result back to `Decimal`; develop money columns against PostgreSQL, or store integer cents.
