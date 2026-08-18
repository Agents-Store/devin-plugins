# Flask Extensions Reference

## Flask-Login

```python
from flask_login import login_required, current_user, login_user, logout_user

@login_required              # Decorator: redirect to login if unauthenticated
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

```python
from models import db

db.session.add(obj)           # Stage new object
db.session.delete(obj)        # Stage deletion
db.session.commit()           # Commit transaction
db.session.rollback()         # Rollback on error
db.session.get(Model, id)     # Get by primary key (SQLAlchemy 2.0)
Model.query.filter_by(k=v).all()   # Query with filters
Model.query.order_by(Model.date.desc()).first()  # Ordered query
```

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
pip install Flask-Caching
```

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

@cache.cached(timeout=300)
@app.route('/expensive')
def expensive_view():
    ...
```

## Werkzeug Security

```python
from werkzeug.security import generate_password_hash, check_password_hash

hashed = generate_password_hash('password')
is_valid = check_password_hash(hashed, 'password')
```
