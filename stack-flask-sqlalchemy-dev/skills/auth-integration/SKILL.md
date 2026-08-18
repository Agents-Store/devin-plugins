---
name: auth-integration
description: >
  Use when the user asks about "Flask-Login with SQLAlchemy", "user authentication",
  "login registration flow", "password hashing", "protect routes",
  "current_user with database", "session management Flask",
  or needs patterns for integrating Flask-Login authentication with SQLAlchemy user models.
---

# Flask-Login + SQLAlchemy Auth Integration

Patterns for wiring Flask-Login session authentication with SQLAlchemy user models.

## User Model with UserMixin

```python
# models.py
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # UserMixin provides: is_authenticated, is_active, is_anonymous, get_id()
```

## Login Manager Setup

```python
# In create_app()
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'          # Redirect target for @login_required
login_manager.login_message = 'Please sign in first'  # Flash message text
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # SQLAlchemy 2.0 style
```

## Registration Flow

```python
from werkzeug.security import generate_password_hash
import re

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        # Check if already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')

        # Validate password strength
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('register.html')
        if not re.search(r'[0-9]', password):
            flash('Password must contain at least one number', 'error')
            return render_template('register.html')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must contain at least one special character', 'error')
            return render_template('register.html')

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('register.html')
```

## Login Flow

```python
from werkzeug.security import check_password_hash
from flask_login import login_user

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("You haven't registered yet!", 'error')
            return render_template('login.html')
        if not check_password_hash(user.password_hash, password):
            flash('Wrong email or password', 'error')
            return render_template('login.html')

        login_user(user)
        return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html')
```

## Protecting Routes

```python
from flask_login import login_required, current_user

# Require authentication
@clients_bp.route('/clients')
@login_required
def clients():
    # current_user is the logged-in User model instance
    my_clients = Client.query.filter_by(user_id=current_user.id).all()
    return render_template('clients.html', clients=my_clients)
```

## Data Isolation Pattern

Every query must filter by `current_user.id` to ensure users see only their own data:

```python
# Always scope queries to current user
Client.query.filter_by(user_id=current_user.id)
Appointment.query.filter_by(user_id=current_user.id)
Spending.query.filter_by(user_id=current_user.id)

# When accessing by ID, also verify ownership
client = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
```

## Template Auth Patterns

```jinja2
{# Show/hide nav based on auth state #}
{% if current_user.is_authenticated %}
    <nav>
        <span>Welcome, {{ current_user.name }}</span>
        <a href="{{ url_for('auth.logout') }}">Logout</a>
    </nav>
{% else %}
    <a href="{{ url_for('auth.login') }}">Login</a>
    <a href="{{ url_for('auth.register') }}">Register</a>
{% endif %}
```

## Password Visibility Toggle

```jinja2
<div class="password-field">
    <input type="password" name="password" id="password" required>
    <button type="button" onclick="togglePassword('password')">
        <span class="eye-icon">Show</span>
        <span class="eye-off-icon" style="display:none">Hide</span>
    </button>
</div>
```

```javascript
function togglePassword(inputId) {
    var input = document.getElementById(inputId);
    input.type = input.type === 'password' ? 'text' : 'password';
}
```
