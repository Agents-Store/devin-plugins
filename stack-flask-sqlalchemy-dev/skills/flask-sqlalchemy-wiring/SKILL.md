---
name: flask-sqlalchemy-wiring
description: >
  Use when the user asks about "connect Flask to SQLAlchemy", "Flask-SQLAlchemy wiring",
  "blueprint model integration", "pass query data to template", "form to database",
  "render database data in template", "Flask model view pattern",
  or needs patterns for connecting Flask routes, SQLAlchemy models, and Jinja2 templates.
---

# Flask + SQLAlchemy Wiring Patterns

Integration patterns for connecting Flask blueprints, SQLAlchemy models, and Jinja2 templates into a working data flow.

## The Data Flow

```
User Request → Route Handler → SQLAlchemy Query → Template Rendering → Response
     ↑                              ↓
Form Submit → Validate → Create Model Instance → db.session.commit()
```

## Pattern 1: List View (Read from DB → Render in Template)

### Route

```python
# routes/clients.py
@clients_bp.route('/clients')
@login_required
def clients():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')

    query = Client.query.filter_by(user_id=current_user.id)
    if search:
        query = query.filter(Client.name.ilike(f'%{search}%'))
    if status_filter:
        query = query.filter_by(status=status_filter)

    clients_list = query.order_by(Client.name).all()
    return render_template('clients.html', clients=clients_list, search=search, status=status_filter)
```

### Template

```jinja2
{# templates/clients.html #}
{% extends "base.html" %}
{% block content %}
<form method="GET">
    <input type="text" name="search" value="{{ search }}" placeholder="Search clients...">
    <select name="status">
        <option value="">All</option>
        {% for s in ['new', 'regular', 'vip'] %}
            <option value="{{ s }}" {{ 'selected' if status == s }}>{{ s|title }}</option>
        {% endfor %}
    </select>
    <button type="submit">Filter</button>
</form>

{% for client in clients %}
    <div class="client-card">
        <h3>{{ client.name }}</h3>
        <p>{{ client.phone }}</p>
        <span class="badge">{{ client.status }}</span>
        <span>{{ client.visit_count }} visits</span>  {# computed property #}
    </div>
{% else %}
    <p>No clients found.</p>
{% endfor %}
{% endblock %}
```

## Pattern 2: Create (Form Submit → Save to DB)

### Route

```python
@clients_bp.route('/clients/add', methods=['POST'])
@login_required
def add_client():
    # Validate required fields
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    if not name or not phone:
        flash('Name and phone are required', 'error')
        return redirect(url_for('clients.clients'))

    client = Client(
        user_id=current_user.id,
        name=name,
        phone=phone,
        birthday=parse_date(request.form.get('birthday')),
        notes=request.form.get('notes', ''),
        status=request.form.get('status', 'new'),
    )
    db.session.add(client)
    db.session.commit()
    flash('Client added successfully', 'success')
    return redirect(url_for('clients.clients'))
```

### Template (Modal Form)

```jinja2
<form method="POST" action="{{ url_for('clients.add_client') }}">
    <input type="text" name="name" required placeholder="Client name">
    <input type="tel" name="phone" required placeholder="Phone">
    <input type="date" name="birthday">
    <textarea name="notes" placeholder="Notes"></textarea>
    <select name="status">
        <option value="new">New</option>
        <option value="regular">Regular</option>
        <option value="vip">VIP</option>
    </select>
    <button type="submit">Add Client</button>
</form>
```

## Pattern 3: Update (Pre-filled Form → Update DB)

### Route

```python
@clients_bp.route('/clients/edit/<int:client_id>', methods=['POST'])
@login_required
def edit_client(client_id):
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
    client.name = request.form['name']
    client.phone = request.form['phone']
    client.status = request.form.get('status', client.status)
    db.session.commit()
    flash('Client updated', 'success')
    return redirect(url_for('clients.clients'))
```

### Template (Edit button with data attributes)

```jinja2
<button class="edit-client-btn"
    data-id="{{ client.id }}"
    data-name="{{ client.name }}"
    data-phone="{{ client.phone }}"
    data-status="{{ client.status }}">
    Edit
</button>
```

JavaScript reads data attributes and populates a modal form.

## Pattern 4: Delete (Confirm → Remove from DB)

### Route

```python
@clients_bp.route('/clients/delete/<int:client_id>', methods=['POST'])
@login_required
def delete_client(client_id):
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted', 'success')
    return redirect(url_for('clients.clients'))
```

### Template (Delete form with confirmation)

```jinja2
<form method="POST" action="{{ url_for('clients.delete_client', client_id=client.id) }}"
      data-confirm="Are you sure you want to delete {{ client.name }}?">
    <button type="submit">Delete</button>
</form>
```

## Pattern 5: Dashboard (Aggregate Queries → Summary View)

```python
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    todays_appointments = Appointment.query.filter_by(
        user_id=current_user.id, date=today
    ).order_by(Appointment.time).all()

    month_earnings = db.session.query(func.sum(Appointment.price)).filter(
        Appointment.user_id == current_user.id,
        Appointment.status == 'done',
        func.extract('month', Appointment.date) == today.month,
        func.extract('year', Appointment.date) == today.year,
    ).scalar() or 0

    return render_template('dashboard.html',
        appointments=todays_appointments,
        visit_count=len(todays_appointments),
        month_earnings=month_earnings,
    )
```

## Pattern 6: Select from Related Model

```python
# In appointment creation — select client from dropdown
@appointments_bp.route('/appointments')
@login_required
def appointments():
    clients = Client.query.filter_by(user_id=current_user.id).order_by(Client.name).all()
    return render_template('appointments.html', clients=clients)
```

```jinja2
<select name="client_id" required>
    <option value="">Select client...</option>
    {% for client in clients %}
        <option value="{{ client.id }}">{{ client.name }}</option>
    {% endfor %}
</select>
```
