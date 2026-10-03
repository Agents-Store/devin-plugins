---
name: layers-and-boundaries
description: >
  Use when the user asks about "Flask SQLAlchemy architecture", "where to create db in
  Flask", "Flask app context and SQLAlchemy session", "when to commit in Flask", "Flask
  transaction boundary", "expire_on_commit in Flask-SQLAlchemy", "DetachedInstanceError in
  Flask", "Working outside of application context", "N+1 in a Jinja template", "lazy raise
  in Flask", "data saved in tests but lost in production", or needs the rules for where each
  layer of a Flask + SQLAlchemy app starts and ends.
---

# Flask + SQLAlchemy: Layers and Boundaries

Flask and SQLAlchemy are taught by their own plugins: `flask-dev` (factory, blueprints, auth, templates) and `sqlalchemy-dev` (models, queries, migrations). This skill is about the places where the two meet, and the bugs that live exactly there: a session that outlives its context, a commit nobody wrote, an object read after it expired, a query hidden in a template.

## Layers

| Layer | Owns | Must not |
|-------|------|----------|
| `extensions.py` | `Base`, `db`, `migrate`, `login_manager`, `csrf`, created without an app | import the app, a model or a blueprint |
| Models (`models.py`) | tables, relationships, loader strategy (`lazy='raise'`), validators | call `commit()`, read `request` or `current_user`, render anything |
| Routes (blueprints) | HTTP in and out, validation, the owner scope, which loaders a view uses, the one `commit()` | hold a half-finished transaction open, build SQL by string |
| Templates | rendering what the route loaded | run a query: touching an unloaded relationship must fail |
| `migrations/` | the only way the schema changes | be bypassed by a table-building call in the factory |

## 1. Where `db` is created

In `extensions.py`, with no app: `db = SQLAlchemy(model_class=Base)`. The factory calls `db.init_app(app)` once; models import `db` from `extensions`; `create_app()` imports the models (`from models import User`) so that `db.metadata` is full before Flask-Migrate reads it. Creating `db` inside `app.py` makes `app` import `models` and `models` import `app`: `ImportError: cannot import name 'db' from partially initialized module`. Code: `flask-dev` → `project-scaffold`.

## 2. The app context owns the session

`db.session` is scoped to the current app context: one session per request, and one per `with app.app_context():` block. Flask-SQLAlchemy closes it when the context ends. Anything that runs outside a request opens a context itself: a script, a thread, a Celery task. A `flask` CLI command already has one.

Pass ids across the boundary, not model instances. An instance whose context has closed is detached: attributes that were loaded still read, expired ones and lazy relationships raise `DetachedInstanceError`.

```python
def send_reminders(app):
    with app.app_context():
        ids = db.session.scalars(db.select(Appointment.id).where(Appointment.status == 'on plan')).all()
    for appointment_id in ids:
        with app.app_context():              # a fresh session for each unit of work
            appointment = db.session.get(Appointment, appointment_id)
            notify(appointment.client_id)
            appointment.status = 'reminded'
            db.session.commit()
```

## 3. The transaction boundary is the route

The session starts a transaction on first use, and nothing commits it for you. A route that adds an object and returns without `commit()` loses the object when the context closes. Rules:

- One `commit()` per unit of work, in the route or in a service function the route calls; never in a model method or a query helper, which cannot know whether more changes follow.
- `db.session.flush()` when a later step needs a generated id inside the same transaction; `commit()` once at the end, so both steps happen or neither.
- After an `IntegrityError` call `rollback()` before the session is used again (a failed flush leaves it unusable).

```python
client = Client(user_id=current_user.id, name=name)
db.session.add(client)
db.session.flush()                           # client.id exists now, nothing is committed yet
db.session.add(Appointment(user_id=current_user.id, client_id=client.id, date=day, time=at))
try:
    db.session.commit()                      # the client and the appointment, or neither
except IntegrityError:
    db.session.rollback()
    flash('Could not save', 'error')
```

## 4. `expire_on_commit`

By default `commit()` marks every loaded object expired, and the next attribute read reloads the row: one extra `SELECT` per object. It costs you in two places: code that commits inside a loop and then reads each object, and objects read after the app context closed (`DetachedInstanceError`). Post/Redirect/Get avoids both: commit, redirect, and the next request loads fresh rows.

When you must read an object after the commit, read it before the context closes, or switch expiry off for the whole session factory:

```python
db = SQLAlchemy(model_class=Base, session_options={'expire_on_commit': False})
```

The price is that objects keep the values they had at commit, so a value that the database computed or another transaction changed is not reloaded: `db.session.refresh(obj)` when you need it. Assigning `db.session.expire_on_commit = False` afterwards has no effect; the option belongs in `session_options` (see `sqlalchemy-dev` → `troubleshoot`).

## 5. N+1 at the route-to-template edge

A template loop that reads `client.appointments` runs one `SELECT` per client. The loader strategy is decided on both sides of the edge:

- The model says `lazy='raise'` on relationships, so a forgotten loader raises `InvalidRequestError: 'Client.appointments' is not available due to lazy='raise'` from the template instead of querying quietly.
- The route names what its template needs: `selectinload(Client.appointments)` for a collection, `joinedload(Appointment.client)` for a many-to-one, `undefer(Client.visit_count)` for a computed column. Queries: `sqlalchemy-dev` → `query-patterns`.
- A template never calls a method that queries. A `@property` that runs a query is N+1 in a loop; use a `column_property` (`sqlalchemy-dev` → `model-patterns`, Computed Values).

Pin it with a test that counts statements, so the guard does not depend on someone remembering:

```python
# tests/conftest.py (continued)
from sqlalchemy import event


@pytest.fixture()
def count_queries(app):
    """The SQL statements executed while a test runs."""
    statements = []

    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    with app.app_context():
        engine = db.engine
    event.listen(engine, 'before_cursor_execute', record)
    yield statements
    event.remove(engine, 'before_cursor_execute', record)
```

```python
# tests/test_query_counts.py
def test_client_list_does_not_grow_with_the_rows(client, count_queries):
    client.post('/register', data={'name': 'Ann', 'email': 'ann@example.com', 'password': 'correct horse battery'})

    def statements_for_list():
        count_queries.clear()
        assert client.get('/clients').status_code == 200
        return len(count_queries)

    for i in range(2):
        client.post('/clients/add', data={'name': f'a{i}', 'phone': '1'})
    few = statements_for_list()
    for i in range(20):
        client.post('/clients/add', data={'name': f'b{i}', 'phone': '1'})
    assert statements_for_list() == few
```

## 6. The schema boundary

The schema changes through `flask db migrate`, a read of the revision (it must contain the `create_table` or `add_column` you expect), and `flask db upgrade`; CI runs `flask db check`. A table-building call in the factory builds the tables first, so `flask db migrate` answers "No changes in schema detected", creates no revision, and a production database never gets the table. That call belongs in test fixtures only.

## 7. What a test fixture must not do

A fixture that keeps one app context open for the whole test (`yield app` inside the `with app.app_context():` block) makes every request reuse it: one session, one Flask `g`, one cached Flask-Login user. A view that forgets `commit()` then passes (the next request sees the pending row, production rolls it back), and a second client looks signed in as the first user. The `app` fixture of `flask-dev` → `app-patterns` (Testing) yields outside the context, so each request is a real one; a test that reads the database opens its own `with app.app_context():` and sees only what was committed:

```python
# tests/test_commit.py
from extensions import db
from models import Client


def test_add_client_is_committed(app, client):
    client.post('/register', data={'name': 'Ann', 'email': 'ann@example.com', 'password': 'correct horse battery'})
    client.post('/clients/add', data={'name': 'Bea', 'phone': '1'})
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Client)) == 1
```

## Symptom to boundary

| Symptom | Boundary | Fix |
|---------|----------|-----|
| `RuntimeError: Working outside of application context` | app context | `with app.app_context():` around the code |
| Saved in tests, missing in production | transaction | the route never calls `commit()` (section 7) |
| `DetachedInstanceError` | context and expiry | read inside the context, pass ids, or `session_options` (sections 2, 4) |
| One query per row on a list page | route to template | `lazy='raise'`, `selectinload` / `joinedload` (section 5) |
| `flask db migrate`: "No changes in schema detected" | schema | remove the table-building call from the factory, import the models in `create_app()` |
| `ImportError ... partially initialized module` | where `db` lives | create `db` in `extensions.py` (section 1) |
