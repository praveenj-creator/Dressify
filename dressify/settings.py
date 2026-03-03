import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Detect if running on Render
IS_RENDER = "RENDER_EXTERNAL_HOSTNAME" in os.environ

# SECURITY
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

DEBUG = not IS_RENDER

ALLOWED_HOSTS = ['*']


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
if IS_RENDER:
    # PostgreSQL (Production - Render)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT'),
        }
    }
else:
    # MySQL (Local Development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'dressify_db',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306',
            'OPTIONS': {'charset': 'utf8mb4'},
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# DEFAULT PRIMARY KEY
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# LOGIN SETTINGS
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'


MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'