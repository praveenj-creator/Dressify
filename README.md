# Dressify — Django Dress eCommerce

## Quick Start (3 steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Start server
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## Login Credentials

| Role  | Username | Password |
|-------|----------|----------|
| Admin | admin    | admin    |
| User  | (signup) | (yours)  |

Admin account is **auto-created** on first login — no setup needed.

---

## Pages

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/login/` | Login (shared for user + admin) |
| `/signup/` | User registration |
| `/products/` | Product listing + filters |
| `/products/<id>/` | Product detail |
| `/cart/` | Shopping cart |
| `/checkout/` | Checkout |
| `/orders/` | Order history |
| `/feedback/` | Leave feedback |
| `/admin-dashboard/` | Admin dashboard |
| `/admin-dashboard/products/` | Manage products |
| `/admin-dashboard/categories/` | Manage categories |
| `/admin-dashboard/orders/` | Manage orders |
| `/admin-dashboard/customers/` | Manage customers |
| `/admin-dashboard/feedback/` | Manage feedback |

---

## MySQL Setup (optional)

In `dressify/settings.py`, comment out SQLite and uncomment MySQL block:

```python
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'dressify_db',
        'USER':     'root',
        'PASSWORD': 'yourpassword',
        'HOST':     'localhost',
        'PORT':     '3306',
    }
}
```

Then: `pip install mysqlclient` and `python manage.py migrate`
