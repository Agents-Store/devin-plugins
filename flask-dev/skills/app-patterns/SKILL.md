---
name: app-patterns
description: >
  Use when the user asks about "Flask application factory", "Flask blueprints",
  "Flask config management", "Flask extensions", "organize Flask project",
  "Flask app structure", "register Flask blueprint", "Flask context processors",
  or needs patterns for structuring a Flask application.
---

# Flask Application Patterns

Production-tested patterns for Flask application structure, configuration, and extension management.

## Application Factory

Always use the factory pattern. It enables testing, multiple instances, and avoids circular imports.

```python
import os
from flask import Flask

def create_app(config_class=None):
    app = Flask(__name__)

    # Load config
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-fallback'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if config_class:
        app.config.from_object(config_class)

    # Initialize extensions
    from models import db
    db.init_app(app)

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
```

## Blueprint Organization

Each blueprint is a self-contained module with its own routes, templates, and static files.

### Basic Blueprint

```python
# routes/clients.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Client

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/clients')
@login_required
def clients():
    clients_list = Client.query.filter_by(user_id=current_user.id).all()
    return render_template('clients.html', clients=clients_list)

@clients_bp.route('/clients/add', methods=['POST'])
@login_required
def add_client():
    client = Client(
        user_id=current_user.id,
        name=request.form['name'],
        phone=request.form['phone'],
    )
    db.session.add(client)
    db.session.commit()
    flash('Client added successfully', 'success')
    return redirect(url_for('clients.clients'))
```

### Blueprint with URL Prefix

```python
# For API-style routes
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# All routes under /api/v1/
@api_bp.route('/clients')
def list_clients():
    ...
```

### Blueprint Registration Order

Register blueprints in the factory. Order matters only when URL rules overlap:

```python
# In create_app()
app.register_blueprint(auth_bp)        # /login, /register, /logout
app.register_blueprint(dashboard_bp)   # /dashboard
app.register_blueprint(clients_bp)     # /clients
app.register_blueprint(api_bp)         # /api/v1/*
```

## Configuration Management

### Environment-Based Config

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

### Loading Config

```python
def create_app(config_class=None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)
    else:
        env = os.environ.get('FLASK_ENV', 'development')
        configs = {
            'development': DevelopmentConfig,
            'production': ProductionConfig,
            'testing': TestingConfig,
        }
        app.config.from_object(configs.get(env, DevelopmentConfig))
    return app
```

## Extension Initialization

Initialize extensions outside the factory, then bind them in `create_app()`:

```python
# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
```

```python
# app.py
from extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    return app
```

## Context Processors

Add variables available in all templates:

```python
@app.context_processor
def inject_globals():
    return {
        'now': datetime.now(),
        'app_name': 'NailBook',
    }
```

## Error Handlers

Register custom error pages:

```python
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500
```

## Request Hooks

```python
@app.before_request
def require_login():
    """Redirect unauthenticated users to login for protected pages."""
    public_endpoints = {'auth.login', 'auth.register', 'static'}
    if request.endpoint not in public_endpoints and not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
```
