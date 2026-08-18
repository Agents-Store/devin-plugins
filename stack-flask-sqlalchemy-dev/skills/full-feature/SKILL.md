---
name: full-feature
description: >
  Use when the user asks to "add a new feature", "create a new page",
  "build CRUD for a new entity", "add a new section to the app",
  "implement a full feature end-to-end", or needs a step-by-step
  recipe for building a complete feature across Flask + SQLAlchemy layers.
---

# Full Feature Recipe

Step-by-step guide for building a complete feature that spans model, routes, and templates in a Flask + SQLAlchemy application.

Follow this template for each new feature. The steps must be completed in order — each step depends on the previous.

## Feature Template

Use the template in `template.md` for the step-by-step implementation checklist.

## Step 1: Define the Model

Add the SQLAlchemy model in `models.py`:

```python
class NewEntity(db.Model):
    __tablename__ = 'new_entities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Add entity-specific columns
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```

Then create and apply a migration:

```bash
flask db migrate -m "Add new_entities table"
flask db upgrade
```

## Step 2: Create the Blueprint

Create `routes/new_entity.py`:

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, NewEntity

new_entity_bp = Blueprint('new_entity', __name__)

@new_entity_bp.route('/new-entities')
@login_required
def list_entities():
    entities = NewEntity.query.filter_by(user_id=current_user.id).all()
    return render_template('new_entity.html', entities=entities)
```

Register in `create_app()`:

```python
from routes.new_entity import new_entity_bp
app.register_blueprint(new_entity_bp)
```

## Step 3: Add CRUD Routes

Add create, edit, and delete routes in the blueprint (see `flask-sqlalchemy-wiring` skill for patterns).

## Step 4: Create the Template

Create `templates/new_entity.html` extending `base.html`:
- List view with search/filter
- Add form (modal or inline)
- Edit form (modal with data attributes)
- Delete form with confirmation

## Step 5: Add Styles

Create `static/css/new_entity.css` and link it in the template:

```jinja2
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/new_entity.css') }}">
{% endblock %}
```

## Step 6: Add Navigation

Add a nav link in `base.html`:

```jinja2
<a href="{{ url_for('new_entity.list_entities') }}"
   class="{% if 'new_entity' in request.endpoint %}active{% endif %}">
    New Entity
</a>
```

## Step 7: Verify

1. Run the app: `flask run --debug --port 5001`
2. Navigate to the new page
3. Test Create → Read → Update → Delete
4. Test with a different user to verify data isolation
5. Test validation (required fields, duplicates)
6. Check `flask routes` to confirm all endpoints registered

## Checklist

- [ ] Model defined with `user_id` foreign key
- [ ] Migration created and applied
- [ ] Blueprint created and registered
- [ ] CRUD routes with `@login_required`
- [ ] All queries filtered by `current_user.id`
- [ ] Template extends `base.html`
- [ ] Flash messages for success/error
- [ ] CSS file created and linked
- [ ] Nav link added to `base.html`
- [ ] Tested end-to-end
