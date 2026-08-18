---
name: jinja2-patterns
description: >
  Use when the user asks about "Jinja2 templates", "Flask templates",
  "template inheritance", "Jinja2 macros", "Jinja2 filters",
  "Flask render_template", "base template", "template blocks",
  or needs patterns for Jinja2 template engine in Flask.
---

# Jinja2 Template Patterns

Production patterns for Jinja2 templating in Flask applications.

## Template Inheritance

### Base Template

```jinja2
{# templates/base.html #}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% if current_user.is_authenticated %}
    <nav>
        <a href="{{ url_for('dashboard.dashboard') }}">Dashboard</a>
        <a href="{{ url_for('auth.logout') }}">Logout</a>
    </nav>
    {% endif %}

    <main>
        {# Flash messages #}
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Child Template

```jinja2
{# templates/clients.html #}
{% extends "base.html" %}

{% block title %}Clients - NailBook{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/clients.css') }}">
{% endblock %}

{% block content %}
<h1>Clients</h1>
<div class="client-list">
    {% for client in clients %}
        <div class="client-card">
            <h3>{{ client.name }}</h3>
            <p>{{ client.phone }}</p>
        </div>
    {% else %}
        <p>No clients yet.</p>
    {% endfor %}
</div>
{% endblock %}
```

## Control Structures

### Conditionals

```jinja2
{% if user.status == 'vip' %}
    <span class="badge vip">VIP</span>
{% elif user.status == 'regular' %}
    <span class="badge regular">Regular</span>
{% else %}
    <span class="badge new">New</span>
{% endif %}
```

### Loops

```jinja2
{% for item in items %}
    <div class="{{ 'even' if loop.index is even else 'odd' }}">
        {{ loop.index }}. {{ item.name }}
    </div>
{% endfor %}
```

Loop variables: `loop.index` (1-based), `loop.index0` (0-based), `loop.first`, `loop.last`, `loop.length`.

## Filters

### Built-in Filters

```jinja2
{{ name|title }}              {# "john doe" → "John Doe" #}
{{ price|int }}               {# 19.99 → 19 #}
{{ items|length }}            {# List length #}
{{ text|truncate(50) }}       {# Truncate with ellipsis #}
{{ date|default('N/A') }}     {# Default if None #}
{{ html_content|safe }}       {# Mark as safe HTML (no escaping) #}
{{ list|join(', ') }}         {# Join list items #}
{{ date_obj|string }}         {# Convert to string #}
```

### Custom Filters

```python
# In app.py or a filters module
@app.template_filter('currency')
def currency_filter(value):
    return f"{value:,.0f} \u20B4"  # Ukrainian hryvnia

@app.template_filter('timeformat')
def timeformat_filter(time_obj):
    return time_obj.strftime('%H:%M')
```

```jinja2
{{ appointment.price|currency }}   {# "1,500 ₴" #}
{{ appointment.time|timeformat }}  {# "14:30" #}
```

## Forms

### Basic Form

```jinja2
<form method="POST" action="{{ url_for('clients.add_client') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

    <label for="name">Name</label>
    <input type="text" name="name" id="name" required
           value="{{ request.form.get('name', '') }}">

    <label for="phone">Phone</label>
    <input type="tel" name="phone" id="phone" required>

    <button type="submit">Add Client</button>
</form>
```

### Select with Pre-selected Value

```jinja2
<select name="status">
    {% for option in ['new', 'regular', 'vip'] %}
        <option value="{{ option }}"
                {{ 'selected' if client.status == option }}>
            {{ option|title }}
        </option>
    {% endfor %}
</select>
```

## Macros

Reusable template components:

```jinja2
{# templates/macros/forms.html #}
{% macro input(name, label, type='text', value='', required=false) %}
<div class="form-group">
    <label for="{{ name }}">{{ label }}</label>
    <input type="{{ type }}" name="{{ name }}" id="{{ name }}"
           value="{{ value }}" {{ 'required' if required }}>
</div>
{% endmacro %}
```

```jinja2
{# Usage in templates #}
{% from "macros/forms.html" import input %}

{{ input('name', 'Client Name', required=true) }}
{{ input('email', 'Email', type='email') }}
{{ input('phone', 'Phone', type='tel', required=true) }}
```

## Static Files

```jinja2
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
```

Always use `url_for('static', ...)` instead of hardcoded paths — it handles URL prefixes and cache busting correctly.

## Context Variables

Variables available in all templates without explicit passing:

| Variable | Source | Description |
|----------|--------|-------------|
| `current_user` | Flask-Login | Authenticated user object |
| `request` | Flask | Current request object |
| `session` | Flask | Session data |
| `config` | Flask | App configuration |
| `g` | Flask | Per-request globals |
| Custom | `@app.context_processor` | User-defined globals |
