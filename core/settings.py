"""
Django settings for core project.

Configuração única, lendo credenciais e parâmetros de ambiente do arquivo
``.env`` na raiz do projeto (via django-environ). Ver seção 42 do PRD.md.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/topics/settings/
"""

from pathlib import Path

import environ
from django.contrib import messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
)

# Carrega o .env da raiz, se existir (em produção as variáveis podem vir do ambiente).
environ.Env.read_env(BASE_DIR / '.env')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'django_celery_beat',
    'django_celery_results',
    'dj_celery_panel',
]

LOCAL_APPS = [
    'base',
    'tenants',
    'accounts',
    'documents',
    'clients',
    'insurers',
    'insurance',
    'claims',
    'partners',
    'commissions',
    'crm',
    'notifications',
    'ai_agents',
    'dashboard',
    'reports',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tenants.middleware.TenantMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
# Lê DATABASE_URL do ambiente; em dev local (sem Docker/Postgres) usa SQLite.

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
    ),
}


# Custom user model — fixado antes do primeiro migrate (ver Sprint 1).
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# E-mail — console backend em dev; SMTP em produção via .env (seção 42 do PRD).
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = env('LANGUAGE_CODE', default='pt-br')

TIME_ZONE = env('TIME_ZONE', default='America/Sao_Paulo')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = env('STATIC_ROOT', default=BASE_DIR / 'staticfiles')

# Estáticos do projeto (tokens) + assets do Design System (Duralux) servidos sob
# o prefixo `vendor/duralux/` direto da pasta de referência — sem duplicar arquivos.
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    ('vendor/duralux', BASE_DIR / 'design_system' / 'refs' / 'duralux'),
]

# WhiteNoise: compressão dos estáticos coletados (servir via app em prod).
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}


# Media protegida — nunca servida publicamente (ver seção 16 do PRD).
# Os arquivos são servidos SOMENTE via ProtectedDocumentDownloadView, que verifica
# autenticação + tenant + permissão. NÃO adicionar MEDIA_URL/url ao urls.py.

MEDIA_URL = '/protected-media/'  # Prefixo interno; NÃO mapeado em urls.py.
MEDIA_ROOT = env('MEDIA_ROOT', default=BASE_DIR / 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Messages tags for Bootstrap 5 alert classes
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


# Celery
# https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://guest:guest@localhost:5672//')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'


# OpenAI / LangChain
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4o-mini')


# Production security (active when DEBUG=False)
if not DEBUG:
    # TLS é terminado no Traefik; o app recebe HTTP interno com o header
    # X-Forwarded-Proto. Sem isto o Django não reconhece que a request original
    # foi HTTPS e entra em loop de redirect atrás do proxy.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
    # O healthcheck do container/load balancer bate em http://localhost:8000/health/
    # (sem passar pelo Traefik), então precisa ficar isento do redirect p/ HTTPS.
    SECURE_REDIRECT_EXEMPT = [r'^health/$']

    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'ai_agents': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
