---
name: api-reference
description: >
  Use when the user asks for "Flask API reference", "Flask decorators",
  "Flask request object", "Flask response", "Flask config options",
  "Flask url_for", "Flask flash messages", or needs specific Flask
  framework API details.
disable-model-invocation: true
---

# Flask API Reference

Curated Flask framework API. For full docs, see https://flask.palletsprojects.com/

## Route Decorators

```python
@app.route('/path')                          # GET only (default)
@app.route('/path', methods=['GET', 'POST']) # Multiple methods
@app.route('/user/<int:id>')                 # URL variable (int)
@app.route('/user/<username>')               # URL variable (string)
@app.route('/file/<path:filepath>')          # URL variable (path with slashes)
```

## Request Object

```python
from flask import request

request.method          # 'GET', 'POST', etc.
request.form['key']     # POST form data (raises 400 if missing)
request.form.get('key') # POST form data (returns None if missing)
request.args.get('q')   # URL query parameters (?q=value)
request.files['file']   # Uploaded file
request.json            # Parsed JSON body
request.headers['X-Key'] # Request headers
request.cookies.get('k') # Cookies
request.endpoint        # Current endpoint name (e.g., 'auth.login')
request.url             # Full URL
request.remote_addr     # Client IP address
```

## Response Helpers

```python
from flask import render_template, redirect, url_for, flash, jsonify, abort, make_response

render_template('page.html', var=value)  # Render Jinja2 template
redirect(url_for('blueprint.view'))      # HTTP redirect
url_for('blueprint.view', id=1)          # Generate URL from endpoint name
url_for('static', filename='css/style.css') # Static file URL
flash('Message text', 'success')         # Flash message (success/error/warning/info)
jsonify({'key': 'value'})                # JSON response with correct Content-Type
abort(404)                               # Raise HTTP error
make_response(body, status, headers)     # Custom response
```

## Flash Messages (in templates)

```jinja2
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for category, message in messages %}
    <div class="alert alert-{{ category }}">{{ message }}</div>
  {% endfor %}
{% endwith %}
```

## Configuration

```python
app.config['SECRET_KEY']                 # Required for sessions/CSRF
app.config['SQLALCHEMY_DATABASE_URI']    # Database connection string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']  # Set to False
app.config['MAX_CONTENT_LENGTH']         # Max upload size in bytes
app.config['PERMANENT_SESSION_LIFETIME'] # Session timeout (timedelta)
```

## Decorators and Hooks

```python
@app.before_request       # Run before every request
@app.after_request        # Run after every request (receives response)
@app.teardown_request     # Run after request, even on error
@app.context_processor    # Add variables to all templates
@app.errorhandler(404)    # Custom error page
@app.template_filter('name')  # Custom Jinja2 filter
```

For Flask-Login, Blueprint API, SQLAlchemy session, and extension patterns, see `references/extensions-reference.md`.
