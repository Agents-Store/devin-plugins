# Owner-Scoped Queries (Per-User Data Isolation)

In an app where every row belongs to a user, each query is scoped to the signed-in user. Forgetting the filter once shows one user another user's data, so the scope lives in one helper and the unscoped form is the one that takes extra typing. The models are `User`, `OwnedMixin`, `Client` and `Appointment` from `model-patterns` (`references/flask-login-user.md`); the views that call these queries are in the `flask-dev` plugin (`app-patterns`, `references/crud-views.md`).

## The Helper

```python
# queries.py
import datetime as dt
from typing import TypeVar

from sqlalchemy import Select, func, select

from extensions import db
from models import Appointment, OwnedMixin

T = TypeVar('T', bound=OwnedMixin)


def owned_by(model: type[T], user_id: int) -> Select[tuple[T]]:
    """SELECT of one entity, already limited to the rows of this user."""
    return select(model).where(model.user_id == user_id)


def month_earnings(user_id: int, today: dt.date):
    first = today.replace(day=1)
    next_first = (first + dt.timedelta(days=32)).replace(day=1)
    return db.session.scalar(
        select(func.coalesce(func.sum(Appointment.price), 0)).where(
            Appointment.user_id == user_id,
            Appointment.status == 'done',
            Appointment.date >= first,       # half-open range: an index on date can be used,
            Appointment.date < next_first,   # unlike func.extract('month', ...) on every row
        )
    )
```

Every view then starts from `owned_by(Client, current_user.id)` and adds its own `where`, `order_by` and `options`. Because the result is an ordinary `Select`, everything in `query-patterns` still applies.

## One Record by Id from the URL

A route such as `/clients/42/edit` takes an id the user can change. Fetch the record together with its owner, and answer `404`, not `403`, when it is somebody else's: a `403` confirms that the id exists.

```python
from flask_login import current_user

client = db.one_or_404(owned_by(Client, current_user.id).where(Client.id == client_id))
```

Plain SQLAlchemy has the same query with `session.scalars(...).one_or_none()`. `db.get_or_404(Client, client_id)` and `session.get(Client, client_id)` do not know the owner: use them only on tables that hold no per-user data, or check `client.user_id` yourself.

## List with Search and Filter

```python
from sqlalchemy.orm import undefer

stmt = owned_by(Client, current_user.id).order_by(Client.name, Client.id)
if search:
    stmt = stmt.where(Client.name.icontains(search, autoescape=True))  # "%" and "_" typed by the user stay literal
if status_filter:
    stmt = stmt.where(Client.status == status_filter)
clients = db.session.scalars(stmt.options(undefer(Client.visit_count))).all()
```

`undefer(Client.visit_count)` loads the deferred computed column of `model-patterns` (Computed Values) in the same statement, so a template loop does not run one query per row.

## Related Rows for a Page

A page that prints each appointment with its client name loads both in one statement:

```python
from sqlalchemy.orm import joinedload

todays = db.session.scalars(
    owned_by(Appointment, current_user.id)
    .where(Appointment.date == today)
    .options(joinedload(Appointment.client))
    .order_by(Appointment.time, Appointment.id)
).all()
```

With `lazy='raise'` on `Appointment.client` the line that forgets `joinedload` fails in the first test instead of costing a query per row in production.

## Options for a Dropdown

A select box needs an id and a label, not whole objects:

```python
options = db.session.execute(
    owned_by(Client, current_user.id).with_only_columns(Client.id, Client.name).order_by(Client.name)
).all()   # rows of (id, name)
```

## Foreign Keys the User Submits

A form field that names another owned row (`client_id` on a new appointment) is input like any other. The foreign key proves the client exists, not that it is the user's: without a check, a user can attach their appointment to another user's client and read that client's name through the join. Fetch the parent through the scoped query first:

```python
client = db.one_or_404(owned_by(Client, current_user.id).where(Client.id == client_id))
appointment = Appointment(user_id=current_user.id, client_id=client.id, date=day, time=at)
```

## Update and Delete by Owner

For one loaded record, fetch it with `owned_by` and change it (`client.status = 'vip'`, `db.session.delete(client)`). For a bulk statement put the owner in the `WHERE`:

```python
from sqlalchemy import delete, update

db.session.execute(
    update(Client)
    .where(Client.user_id == current_user.id, Client.status == 'new')
    .values(status='regular')
)
db.session.execute(delete(Appointment).where(Appointment.user_id == current_user.id,
                                              Appointment.status == 'cancelled'))
db.session.commit()
```

A bulk `delete()` skips ORM cascades (see Bulk Operations in `query-patterns`).

## Test the Isolation

One test per owned table, with two users. Ann owns a client; Ben is signed in and asks for it:

```python
# tests/test_isolation.py
from extensions import db
from models import Client, User


def test_other_users_client_is_a_404(app, client):
    with app.app_context():
        ann = User(name='Ann', email='ann@example.com', password_hash='x')
        ben = User(name='Ben', email='ben@example.com', password_hash='x')
        db.session.add_all([ann, ben])
        db.session.flush()
        row = Client(user_id=ann.id, name='Ann client')
        db.session.add(row)
        db.session.commit()
        row_id, ben_id = row.id, ben.id            # plain ints: the instances die with the context

    with client.session_transaction() as session:
        session['_user_id'] = str(ben_id)          # Flask-Login's session key: Ben is signed in
    assert client.post(f'/clients/{row_id}/edit', data={'name': 'Hacked'}).status_code == 404
    assert client.post(f'/clients/{row_id}/delete').status_code == 404
    with app.app_context():
        assert db.session.get(Client, row_id).name == 'Ann client'
```

The test uses the `app` and `client` fixtures of `flask-dev` → `app-patterns` (Testing), which yield the app outside an app context; the test opens one for its own database access. Repeat the two requests for every owned entity. A view that forgets `owned_by` answers `302` and changes the row, and this test fails.

The 1.x forms of these queries (`Client.query.filter_by(user_id=...)`, `.first_or_404()`) are translated in [Legacy 1.x style](../../api-reference/references/legacy-1x-style.md).
