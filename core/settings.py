import os
from pathlib import Path
from dotenv import load_dotenv
from str2bool import str2bool

from django.utils.translation import gettext_lazy as _

import dj_database_url


load_dotenv()  # take environment variables from .env.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.environ.get("SECRET_KEY")
# if not SECRET_KEY:
#     SECRET_KEY = "".join(random.choice(string.ascii_lowercase) for i in range(32))

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("La variable SECRET_KEY doit être définie !")

# Enable/Disable DEBUG Mode
DEBUG = str2bool(os.environ.get("DEBUG", "False"))


ALLOWED_HOSTS = ["*"]

# Add here your deployment HOSTS
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:5085",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5085",
]

X_FRAME_OPTIONS = "SAMEORIGIN"

# RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# Application definition

INSTALLED_APPS = [
    "admin_datta.apps.AdminDattaConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_select2",
    "apps.common",  # Application pour gérer les  relations entre filière et matière
    "apps.courses",  # Application pour gérer les filières
    "apps.home",  # Application pour gérer les fonction de base de  l'application comme  les  notification systeme  d'alert et  autre
    "apps.subjects",  # Application pour gérer les matières
    "apps.users",  # Application pour gérer les utilisateurs
    "corsheaders",
    "rest_framework",  # Include DRF           # <-- NEW
    "rest_framework.authtoken",  # Include DRF Auth      # <-- NEW
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

HOME_TEMPLATES = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [HOME_TEMPLATES],  # <-- UPD: Dynamic_DT
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    raise ValueError("DATABASE_URL doit être défini dans l'environnement.")

if not os.path.exists(BASE_DIR / ".env"):
    print("⚠️  Fichier .env non trouvé ! Certaines variables risquent de manquer.")

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGES = [
    ("fr", _("French")),
    ("en", _("English")),
]

LANGUAGE_CODE = "fr"  # Par défaut en français


TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


MEDIA_URL = "/media/"  # URL accessible depuis le navigateur
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # Répertoire de stockage des fichiers

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# Pour mieux gérer les fichiers statiques sur Render
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
    if not DEBUG
    else "django.contrib.staticfiles.storage.StaticFilesStorage"
)


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "users:login"
# LOGIN_REDIRECT_URL = '/'

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

AUTH_USER_MODEL = "users.CustomUser"

if not DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[{asctime}] {levelname} {name}: {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }

INTERNAL_IPS = [
    "127.0.0.1",
]

# Pour autoriser toutes les origines (à restreindre en prod)
CORS_ALLOW_ALL_ORIGINS = True

# Ou bien définir des origines spécifiques
# CORS_ALLOWED_ORIGINS = [
#    "https://monappmobile.com",
# ]

# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration

# if not DEBUG:
#     sentry_sdk.init(
#         dsn=os.environ.get("SENTRY_DSN"),  # Ex: dans ton .env ou sur Render
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=1.0,  # change selon besoin (0.1 = 10% des requêtes)
#         send_default_pii=True,
#     )

# if not DEBUG:
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True

#     SECURE_HSTS_SECONDS = 3600
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_PRELOAD = True
