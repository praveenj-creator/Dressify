import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-dressify-2026")

# Debug setting - explicit from environment
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Allow localhost and render domain
RENDERED_DOMAIN = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost")
ALLOWED_HOSTS = [RENDERED_DOMAIN, "localhost", "127.0.0.1", "*.onrender.com"]

# CORS and CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    f"https://{RENDERED_DOMAIN}",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Security headers for production
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True


# APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]


# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'dressify.urls'

AUTH_USER_MODEL = 'app.User'


# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'app' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.nav_categories',
            ],
        },
    },
]


WSGI_APPLICATION = 'dressify.wsgi.application'


# DATABASE CONFIGURATION
# Use PostgreSQL on Render, MySQL for local development
if os.environ.get('DB_HOST'):  # Render provides DB_HOST
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'dressify_db'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,
            'OPTIONS': {
                'connect_timeout': 10,
                'sslmode': 'require',
            }
        }
    }
else:
    # Local MySQL configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DB', 'dressify_db'),
            'USER': os.environ.get('MYSQL_USER', 'root'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
            'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
        }
    }


# PASSWORD VALIDATORS
AUTH_PASSWORD_VALIDATORS = []


# INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# STATIC FILES
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'app' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Use simple storage for production/Render to avoid compression issues during build
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'


# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# DEFAULT PRIMARY KEY
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# LOGIN SETTINGS
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'


MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# LOGGING CONFIGURATION
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}