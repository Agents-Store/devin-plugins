# Flask Extensions Reference

## Flask-Login

```python
from flask_login import login_required, current_user, login_user, logout_user

@login_required              # Decorator: redirect to login if unauthenticated
def dashboard():
    ...

current_user.is_authenticated  # Check if logged in
login_user(user)             # Log user in (sets session)
login_user(user, remember=True)  # Persistent login
logout_user()                # Log user out (clears session)
```

## Blueprint API

```python
from flask import Blueprint

bp = Blueprint('name', __name__)                    # Basic
bp = Blueprint('name', __name__, url_prefix='/api')  # With URL prefix
bp = Blueprint('name', __name__, template_folder='templates')  # Custom templates

app.register_blueprint(bp)  # Register in factory
```

## Database Session (Flask-SQLAlchemy)

```bash
pip install Flask-SQLAlchemy "SQLAlchemy<2.1"
```

A `MappedAsDataclass` base fails on SQLAlchemy 2.1 with Flask-SQLAlchemy 3.1.1 (open issue [#1420](https://github.com/pallets-eco/flask-sqlalchemy/issues/1420); plain `db.Model` works), so pin `SQLAlchemy<2.1` to be safe.

```python
from extensions import db

db.session.add(obj)           # Stage new object
db.session.delete(obj)        # Stage deletion
db.session.commit()           # Commit transaction
db.session.rollback()         # Rollback on error
db.session.get(Model, id)     # Get by primary key
db.get_or_404(Model, id)      # Same, but aborts with 404 when missing
db.session.scalars(db.select(Model).filter_by(k=v)).all()   # Query with filters
db.session.scalars(
    db.select(Model).order_by(Model.date.desc()).limit(1)
).first()                                                    # Ordered query
db.session.execute(db.select(Model).filter_by(k=v)).scalar_one_or_none()  # One row or None
db.first_or_404(db.select(Model).filter_by(k=v))             # First row or 404
```

`Model.query` is the legacy query interface; prefer `db.session.execute(db.select(...))`. See the `sqlalchemy-dev` plugin for query patterns.

## Flask-Migrate (Alembic)

```bash
pip install Flask-Migrate
```

```python
from flask_migrate import Migrate
migrate = Migrate(app, db)
```

```bash
flask db init          # Initialize migrations directory (once)
flask db migrate -m "Add users table"  # Generate migration
flask db upgrade       # Apply pending migrations
flask db downgrade     # Revert last migration
flask db current       # Show current revision
flask db history       # Show migration history
```

## Flask-WTF (Forms + CSRF)

```bash
pip install Flask-WTF
```

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()      # extensions.py
csrf.init_app(app)        # in create_app(); checks every POST/PUT/PATCH/DELETE
```

Without `CSRFProtect`, `{{ csrf_token() }}` is undefined in templates. A `FlaskForm` carries its own token (`{{ form.hidden_tag() }}`); `CSRFProtect` also covers plain forms and AJAX (`X-CSRFToken` header, `{{ csrf_meta_tag() }}` in Flask-WTF 1.3+). Flask-WTF 1.3 needs Python 3.10+.

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Login')
```

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # form.email.data, form.password.data
        ...
    return render_template('login.html', form=form)
```

```jinja2
<form method="POST">
    {{ form.hidden_tag() }}
    {{ form.email.label }} {{ form.email() }}
    {% for error in form.email.errors %}
        <span class="error">{{ error }}</span>
    {% endfor %}
    {{ form.submit() }}
</form>
```

## Flask-Mail

```bash
pip install Flask-Mail
```

```python
from flask_mail import Mail, Message

mail = Mail(app)

msg = Message('Subject', sender='from@example.com', recipients=['to@example.com'])
msg.body = 'Plain text body'
msg.html = '<h1>HTML body</h1>'
mail.send(msg)
```

## Flask-Caching

```bash
pip install Flask-Caching     # 2.5 needs Python 3.11+
```

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

@app.route('/expensive')      # route decorator stays outermost
@cache.cached(timeout=300)    # cache decorator sits right above the function
def expensive_view():
    ...
```

With the order reversed, `@cache.cached` wraps the already-registered route function and the view that Flask serves is never cached.

## Werkzeug Security

```python
from werkzeug.security import generate_password_hash, check_password_hash

hashed = generate_password_hash(password, method='scrypt')   # Werkzeug 3 default, stated explicitly
is_valid = check_password_hash(hashed, password)
```

The hash string starts with the method (`scrypt:...`), so `check_password_hash` still verifies older `pbkdf2:` hashes; rehash after a successful login to migrate them.
