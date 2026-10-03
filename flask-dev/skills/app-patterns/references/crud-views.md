# CRUD Views: Routes, Forms and Templates

List, create, edit, delete, a dashboard and a select box, for rows that belong to the signed-in user. The example entity is `Client` (with `Appointment` for the dashboard); the models are in the `sqlalchemy-dev` plugin (`model-patterns`, `references/flask-login-user.md`), and the scoped queries `owned_by()` and `month_earnings()` are in `queries.py` (`query-patterns`, `references/owner-scoped-queries.md`). Use `db.session.execute(db.select(...))` and the helpers; `Model.query` is the legacy interface.

```
Request → route → scoped select → template → response
Form POST → validate → change model → db.session.commit() → redirect (Post/Redirect/Get)
```

Rules for every view below:

- `@login_required`, and every query starts from `owned_by(Model, current_user.id)`.
- Every `POST` form carries `csrf_token` (`CSRFProtect` rejects the request without it).
- A successful `POST` ends in a redirect, so a browser refresh does not submit the form again.
- A failed validation flashes a message and shows the form again; it never commits half of the data.
- The route owns the transaction: one `commit()` at the end of the successful path (see `stack-flask-sqlalchemy`, `layers-and-boundaries`).

## List View: Read, Filter, Render

```python
# routes/clients.py
import datetime as dt

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import undefer

from extensions import db
from models import Client
from queries import owned_by

clients_bp = Blueprint('clients', __name__)

STATUSES = ('new', 'regular', 'vip')


def parse_date(value):
    try:
        return dt.date.fromisoformat(value) if value else None
    except ValueError:
        return None


@clients_bp.route('/clients')
@login_required
def clients():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')

    stmt = owned_by(Client, current_user.id).order_by(Client.name, Client.id)
    if search:
        stmt = stmt.where(Client.name.icontains(search, autoescape=True))
    if status_filter in STATUSES:
        stmt = stmt.where(Client.status == status_filter)

    clients_list = db.session.scalars(stmt.options(undefer(Client.visit_count))).all()
    return render_template('clients.html', clients=clients_list, search=search,
                           status=status_filter, statuses=STATUSES)
```

`Client.visit_count` is the computed `column_property` of `model-patterns` (Computed Values); drop the `undefer(...)` option and the template line if the model has none.

```jinja2
{# templates/clients.html #}
{% extends "base.html" %}
{% block content %}
<form method="get">
    <input type="text" name="search" value="{{ search }}" placeholder="Search clients...">
    <select name="status">
        <option value="">All</option>
        {% for s in statuses %}
            <option value="{{ s }}" {{ 'selected' if status == s }}>{{ s|title }}</option>
        {% endfor %}
    </select>
    <button type="submit">Filter</button>
</form>

{% for client in clients %}
    <div class="client-card">
        <h3>{{ client.name }}</h3>
        <p>{{ client.phone or '' }}</p>
        <span class="badge">{{ client.status }}</span>
        <span>{{ client.visit_count }} visits</span>
    </div>
{% else %}
    <p>No clients found.</p>
{% endfor %}
{% endblock %}
```

A `GET` search form needs no CSRF token. The template reads only what the route loaded: `lazy='raise'` relationships turn a forgotten `selectinload` into an error.

## Create: Form Submit, Save, Redirect

```python
# routes/clients.py (continued)
@clients_bp.route('/clients/add', methods=['POST'])
@login_required
def add_client():
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    status = request.form.get('status', 'new')
    if not name or not phone or status not in STATUSES:
        flash('Name and phone are required', 'error')
        return redirect(url_for('clients.clients'))

    db.session.add(Client(
        user_id=current_user.id,
        name=name,
        phone=phone,
        birthday=parse_date(request.form.get('birthday')),
        notes=request.form.get('notes', ''),
        status=status,
    ))
    db.session.commit()
    flash('Client added successfully', 'success')
    return redirect(url_for('clients.clients'))
```

```jinja2
<form method="post" action="{{ url_for('clients.add_client') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <input type="text" name="name" required placeholder="Client name">
    <input type="tel" name="phone" required placeholder="Phone">
    <input type="date" name="birthday">
    <textarea name="notes" placeholder="Notes"></textarea>
    <select name="status">
        {% for s in statuses %}<option value="{{ s }}">{{ s|title }}</option>{% endfor %}
    </select>
    <button type="submit">Add Client</button>
</form>
```

`user_id` comes from `current_user`, never from the form.

## Update: Pre-Filled Form, Save

```python
# routes/clients.py (continued)
@clients_bp.route('/clients/<int:client_id>/edit', methods=['POST'])
@login_required
def edit_client(client_id):
    client = db.one_or_404(owned_by(Client, current_user.id).where(Client.id == client_id))
    status = request.form.get('status', client.status)
    if status not in STATUSES:
        flash('Unknown status', 'error')
        return redirect(url_for('clients.clients'))
    client.name = request.form.get('name', client.name).strip() or client.name
    client.phone = request.form.get('phone', client.phone or '').strip()
    client.status = status
    db.session.commit()
    flash('Client updated', 'success')
    return redirect(url_for('clients.clients'))
```

The record is fetched together with its owner: another user's id answers `404` (see `owner-scoped-queries.md`). Each card has an edit button that carries the current values and the form's URL in `data-` attributes; one edit form per page is filled from them by a few lines of JavaScript. The form is a `POST` form like every other, so it carries the CSRF token:

```jinja2
<button class="edit-client-btn"
    data-action="{{ url_for('clients.edit_client', client_id=client.id) }}"
    data-name="{{ client.name }}"
    data-phone="{{ client.phone or '' }}"
    data-status="{{ client.status }}">
    Edit
</button>
```

```jinja2
{# once per page, outside the loop #}
<form method="post" id="edit-client-form" action="" hidden>
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <input type="text" name="name" required>
    <input type="tel" name="phone">
    <select name="status">
        {% for s in statuses %}<option value="{{ s }}">{{ s|title }}</option>{% endfor %}
    </select>
    <button type="submit">Save</button>
</form>
```

```javascript
// static/js/clients.js
document.querySelectorAll('.edit-client-btn').forEach(function (button) {
  button.addEventListener('click', function () {
    var form = document.getElementById('edit-client-form');
    form.action = button.dataset.action;
    form.elements['name'].value = button.dataset.name;
    form.elements['phone'].value = button.dataset.phone;
    form.elements['status'].value = button.dataset.status;
    form.hidden = false;
    form.elements['name'].focus();
  });
});
```

Load the script from the page with `{% block scripts %}<script src="{{ url_for('static', filename='js/clients.js') }}" defer></script>{% endblock %}`.

## Delete: Confirm, Remove

```python
# routes/clients.py (continued)
@clients_bp.route('/clients/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    client = db.one_or_404(owned_by(Client, current_user.id).where(Client.id == client_id))
    db.session.delete(client)    # the ORM cascade removes the client's appointments
    db.session.commit()
    flash('Client deleted', 'success')
    return redirect(url_for('clients.clients'))
```

```jinja2
<form method="post" action="{{ url_for('clients.delete_client', client_id=client.id) }}"
      onsubmit='return confirm({{ ("Delete " ~ client.name ~ "?")|tojson }})'>
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button type="submit">Delete</button>
</form>
```

Deletion is `POST`, never a link: a `GET` that deletes is triggered by link prefetchers and by other sites. `|tojson` is the safe way to put a value into a JavaScript string inside a single-quoted attribute.

## Dashboard: Aggregates and Related Rows

This replaces the scaffold's `routes/dashboard.py`:

```python
# routes/dashboard.py
import datetime as dt

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from extensions import db
from models import Appointment
from queries import month_earnings, owned_by

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    today = dt.date.today()
    todays_appointments = db.session.scalars(
        owned_by(Appointment, current_user.id)
        .where(Appointment.date == today)
        .options(joinedload(Appointment.client))
        .order_by(Appointment.time, Appointment.id)
    ).all()
    return render_template(
        'dashboard.html',
        appointments=todays_appointments,
        visit_count=len(todays_appointments),
        month_earnings=month_earnings(current_user.id, today),
    )
```

The template prints `appt.client.name` for each appointment; `joinedload` loaded the client with the row. The aggregate is a helper that returns one number; the template never runs a query.

## Select from a Related Model

```python
# routes/appointments.py
import datetime as dt

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Appointment, Client
from queries import owned_by

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('/appointments')
@login_required
def appointments():
    options = db.session.execute(
        owned_by(Client, current_user.id).with_only_columns(Client.id, Client.name).order_by(Client.name)
    ).all()
    return render_template('appointments.html', client_options=options)


@appointments_bp.route('/appointments/add', methods=['POST'])
@login_required
def add_appointment():
    # The id in the form is user input: fetch the client through the owner scope first.
    client = db.one_or_404(
        owned_by(Client, current_user.id).where(Client.id == request.form.get('client_id', type=int))
    )
    try:
        day = dt.date.fromisoformat(request.form['date'])
        at = dt.time.fromisoformat(request.form['time'])
    except (KeyError, ValueError):
        flash('Date and time are required', 'error')
        return redirect(url_for('appointments.appointments'))
    db.session.add(Appointment(user_id=current_user.id, client_id=client.id, date=day, time=at))
    db.session.commit()
    flash('Appointment added', 'success')
    return redirect(url_for('appointments.appointments'))
```

```jinja2
{# templates/appointments.html #}
{% extends "base.html" %}
{% block content %}
<form method="post" action="{{ url_for('appointments.add_appointment') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <select name="client_id" required>
        <option value="">Select client...</option>
        {% for client_id, client_name in client_options %}
            <option value="{{ client_id }}">{{ client_name }}</option>
        {% endfor %}
    </select>
    <input type="date" name="date" required>
    <input type="time" name="time" required>
    <button type="submit">Add</button>
</form>
{% endblock %}
```

`request.form.get('client_id', type=int)` is `None` for a missing or non-numeric field, and `Client.id == None` matches no row, so the view answers `404`. Fetching the chosen client through `owned_by` is what stops a user from attaching an appointment to somebody else's client (`owner-scoped-queries.md`, Foreign Keys the User Submits).

## Tests

```python
# tests/test_clients.py
def test_client_crud(client):
    client.post('/register', data={'name': 'Ann', 'email': 'ann@example.com', 'password': 'correct horse battery'})
    client.post('/clients/add', data={'name': 'Bea', 'phone': '123', 'status': 'vip'})
    assert b'Bea' in client.get('/clients').data
    assert b'Bea' not in client.get('/clients?status=new').data
    client.post('/clients/1/edit', data={'name': 'Bea B', 'status': 'regular'})
    assert b'Bea B' in client.get('/clients').data
    client.post('/clients/1/delete')
    assert b'Bea' not in client.get('/clients').data
```

Add the two-user check from `owner-scoped-queries.md` for every owned entity, and a statement-count assertion for each list view (`stack-flask-sqlalchemy`, `layers-and-boundaries`).
