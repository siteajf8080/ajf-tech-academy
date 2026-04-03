import os
from pathlib import Path
from django.contrib.messages import constants as messages

# 1. PATHS
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECURITY (Pa bliye chanje SECRET_KEY sa si w ap mete l an liy)
SECRET_KEY = 'django-insecure-28r_kco--lgm_hh%yfy!%yqfl8e663_(((#o!6erh3y)@$t6b!'
DEBUG = True
ALLOWED_HOSTS = ['*']

# 3. APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # App AJF-Tech la
    'academy', 
]

# 4. MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# 5. TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Sa a enpòtan pou foto (signatures, screenshots) ka parèt
                'django.template.context_processors.media',
            ],
        },
    },    
]

WSGI_APPLICATION = 'config.wsgi.application'

# 6. DATABASE (Pou kòmanse, SQLite3 bon nèt)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 7. PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 8. INTERNATIONALIZATION (Konfigirasyon Ayiti)
LANGUAGE_CODE = 'fr' 
TIME_ZONE = 'America/Port-au-Prince' 
USE_I18N = True
USE_TZ = True

# 9. STATIC FILES (CSS, JS, Images pwojè a)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 10. MEDIA FILES (Foto pwofil, Siyati, Screenshot peman)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 11. AUTHENTICATION CONFIG
LOGIN_URL = 'login' 
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# 12. MESSAGE TAGS (Pou Bootstrap alerts)
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# 13. EMAIL CONFIGURATION (Gmail SMTP pou sètifika yo)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ajftech.infos@gmail.com' 
EMAIL_HOST_PASSWORD = 'afgx hmnv lamy iknj' # App Password ou an
DEFAULT_FROM_EMAIL = 'AJF-Tech <ajftech.infos@gmail.com>'

# 14. DEFAULT AUTO FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'