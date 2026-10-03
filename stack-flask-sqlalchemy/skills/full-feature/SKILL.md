---
name: full-feature
description: >
  Use when the user asks to "add a new feature", "create a new page",
  "build CRUD for a new entity", "add a new section to the app",
  "implement a full feature end-to-end", or needs a step-by-step
  recipe for building a complete feature across Flask + SQLAlchemy layers.
---

# Full Feature Recipe

Step-by-step guide for building a feature that spans model, migration, routes and templates in a Flask + SQLAlchemy application. The order matters: each step depends on the one before it. The details of each step live in the plugins this stack depends on; this skill keeps the order, the boundaries and the checks. `template.md` is the checklist to fill in for each new feature.

Start from a project that follows `flask-dev` → `project-scaffold` (factory, `extensions.py`, a `User` model, migrations) and read `layers-and-boundaries` once: it explains the commit, the app context and the loader rules that the steps below rely on.

## Step 1: Define the Model and Migrate

Add the model in `models.py` (typed 2.0 style; `OwnedMixin` gives it the `user_id` that scopes every query; models: `sqlalchemy-dev` → `model-patterns`, `references/flask-login-user.md`):

```python
# models.py (continued)
class NewEntity(OwnedMixin, db.Model):
    __tablename__ = 'new_entities'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
```

Then create, read and apply the migration. The schema reaches the database only through a revision; no table-building call belongs in the app factory (`flask-dev` → `app-patterns` says which one and why):

```bash
flask db migrate -m "Add new_entities table"
grep -n "create_table\|add_column" migrations/versions/*.py   # the revision must contain your change
flask db upgrade
flask db check                                                # models and revisions agree
```

A revision without your table means the model module is not imported by `create_app()` (see `layers-and-boundaries`, section 1).

## Step 2: Create the Blueprint

Create `routes/new_entity.py`. Every query starts from `owned_by(Model, current_user.id)` (`sqlalchemy-dev` → `query-patterns`, `references/owner-scoped-queries.md`):

```python
# routes/new_entity.py
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from extensions import db
from models import NewEntity
from queries import owned_by

new_entity_bp = Blueprint('new_entity', __name__)


@new_entity_bp.route('/new-entities')
@login_required
def list_entities():
    entities = db.session.scalars(
        owned_by(NewEntity, current_user.id).order_by(NewEntity.name, NewEntity.id)
    ).all()
    return render_template('new_entity.html', entities=entities)
```

Register it in `create_app()`:

```python
from routes.new_entity import new_entity_bp
app.register_blueprint(new_entity_bp)
```

## Step 3: Add CRUD Routes

Add create, edit and delete routes in the blueprint. The patterns are in `flask-dev` → `app-patterns`, `references/crud-views.md`. The boundary rules for each of them:

- `@login_required`, and a record fetched by an id from the URL is fetched together with its owner (`db.one_or_404(owned_by(...).where(...))`): another user's id is a `404`.
- A foreign key the form submits (`client_id`) is fetched through `owned_by` before it is used.
- Every `POST` form has `csrf_token`; delete is a `POST`.
- The route ends a successful write with one `commit()` and a redirect (`layers-and-boundaries`, sections 3 and 4).

## Step 4: Create the Template

Create `templates/new_entity.html` extending `base.html`:

```jinja2
{# templates/new_entity.html #}
{% extends "base.html" %}
{% block title %}New entities{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/new_entity.css') }}">
{% endblock %}
{% block content %}
{% for entity in entities %}
    <div class="entity-card">{{ entity.name }}</div>
{% else %}
    <p>Nothing here yet.</p>
{% endfor %}
{% endblock %}
```

Add the list view with search and filter, the add form, the edit form and the delete form with confirmation as in `crud-views.md`. The template only reads what the route loaded: a relationship it touches must be named in the route's `options(...)` (`lazy='raise'` on the model turns a forgotten one into an error).

## Step 5: Add Styles

Create `static/css/new_entity.css`; the template above links it in the `extra_css` block. Follow the design tokens in `base.css`.

## Step 6: Add Navigation

Add a nav link in `base.html`:

```jinja2
<a href="{{ url_for('new_entity.list_entities') }}"
   class="{% if request.blueprint == 'new_entity' %}active{% endif %}">
    New Entity
</a>
```

## Step 7: Verify

1. `flask routes` shows every endpoint of the blueprint; `flask run` and click through Create, Read, Update, Delete.
2. `pytest` (`pytest.ini` turns SQLAlchemy deprecation warnings into errors) with these tests for the feature:
   - CRUD round trip through the test client.
   - A second user gets `404` for the first user's id on edit and delete (`owner-scoped-queries.md`, Test the Isolation).
   - The list view issues the same number of statements for 2 rows and for 22 (`layers-and-boundaries`, section 5).
   - Every write is committed: assert in a fresh `with app.app_context():` after the request (`layers-and-boundaries`, section 7).
3. Validation: required fields, duplicates, unknown ids.
4. `flask db check` is clean.

## Checklist

- [ ] Model defined with `OwnedMixin` (a `user_id` foreign key)
- [ ] Migration created, read, applied; `flask db check` clean
- [ ] Blueprint created and registered
- [ ] CRUD routes with `@login_required`
- [ ] All queries start from `owned_by(Model, current_user.id)`; foreign keys from forms fetched the same way
- [ ] Template extends `base.html`; no query or unloaded relationship in it
- [ ] Every `POST` form carries `csrf_token`; delete is a `POST`
- [ ] Flash messages for success and error
- [ ] CSS file created and linked
- [ ] Nav link added to `base.html`
- [ ] Tests: CRUD, two-user isolation, statement count, commit
