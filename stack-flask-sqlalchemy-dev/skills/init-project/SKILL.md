---
name: init-project
description: >
  Use when the user asks to "set up Flask project", "initialize Flask SQLAlchemy project",
  "scaffold Flask app", "create Flask project structure", "bootstrap Flask application",
  or needs to set up a new Flask + SQLAlchemy project from scratch with all integrations wired.
---

# Initialize Flask + SQLAlchemy Project

Set up a complete Flask project with SQLAlchemy, Flask-Login, and Flask-Migrate properly wired together.

## Step 1: Create Project Structure

```
project/
├── app.py                  # Application factory
├── models.py               # SQLAlchemy models
├── extensions.py           # Extension instances (optional, for larger projects)
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (git-ignored)
├── .gitignore
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Login, register, logout
│   ├── dashboard.py        # Landing page
│   └── ...                 # Feature blueprints
├── templates/
│   ├── base.html           # Base template with nav + flash messages
│   ├── login.html
│   ├── register.html
│   └── ...
├── static/
│   ├── css/
│   │   └── base.css
│   └── js/
│       └── app.js
└── instance/               # SQLite DB lives here (git-ignored)
```

## Step 2: Install Dependencies

```bash
pip install Flask Flask-SQLAlchemy Flask-Login Flask-Migrate Werkzeug python-dotenv
pip freeze > requirements.txt
```

## Step 3: Create Application Factory

```python
# app.py
import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    from models import db
    db.init_app(app)

    from flask_migrate import Migrate
    Migrate(app, db)

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in first'
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

    # Create tables (for development — use migrations in production)
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
```

## Step 4: Create Models

```python
# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```

## Step 5: Create Auth Blueprint

```python
# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        flash('Wrong email or password', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
```

## Step 6: Create Environment File

```bash
# .env
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=sqlite:///app.db
FLASK_DEBUG=1
```

## Step 7: Set Up .gitignore

```
instance/
__pycache__/
*.pyc
.env
.claude/settings.local.json
```

## Step 8: Initialize Migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Step 9: Verify

```bash
flask run --port 5001 --debug
flask routes  # Should list all registered endpoints
```

Visit the app in browser and verify login/register flow works.
