import os
from pathlib import Path
from dotenv import load_dotenv
from str2bool import str2bool

from django.utils.translation import gettext_lazy as _

import dj_database_url


load_dotenv()  # take environment variables from .env.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = os.environ.get("SECRET_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY", default="change-me")
if not SECRET_KEY:
    raise ValueError("La variable SECRET_KEY doit être définie !")

# Enable/Disable DEBUG Mode
# DEBUG = str2bool(os.environ.get("DEBUG", "False"))
DEBUG = "False"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
ALLOWED_HOSTS += ["timelya.onrender.com"]


SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Add here your deployment HOSTS
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:5085",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5085",
    "https://timelya.onrender.com",  # <-- Ajout du sous-domaine
]

X_FRAME_OPTIONS = "SAMEORIGIN"


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
    "whitenoise.runserver_nostatic",
    "apps.common",  # Application pour gérer les  relations entre filière et matière
    "apps.courses",  # Application pour gérer les filières
    "apps.home",  # Application pour gérer les fonction de base de  l'application comme  les  notification systeme  d'alert et  autre
    "apps.subjects",  # Application pour gérer les matières
    "apps.users",  # Application pour gérer les utilisateurs
    "apps.attendance",  # Application pour gérer les Présence
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
]

LANGUAGE_CODE = "fr"  # Par défaut en français


TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


MEDIA_URL = "/media/"  # URL accessible depuis le navigateur
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # Répertoire de stockage des fichiers


# Pour mieux gérer les fichiers statiques sur Render
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
    if not DEBUG
    else "django.contrib.staticfiles.storage.StaticFilesStorage"
)


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "users:login"  # fallback utilisé si @login_required est appelé sans redirection personnalisée

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


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_SANDBOX_NUMBER = os.getenv("TWILIO_WHATSAPP_SANDBOX_NUMBER")

# ========= EMAIL CONFIG DEV =========
# L’adresse "from" par défaut
DEFAULT_FROM_EMAIL = "lpinacle229@gmail.com"

# Optionnel : pour tester le file backend au lieu de la console
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"  # Dossier où seront stockés les mails

# # ========= EMAIL CONFIG PROD (Gmail) =========
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# # ⚠️ Utilise ton adresse Gmail
EMAIL_HOST_USER = "lpinacle229@gmail.com"

# # ⚠️ Utilise un "App Password" et PAS ton mot de passe Gmail normal
EMAIL_HOST_PASSWORD = "fjeu vfwj ehnt alpl"

# # Expéditeur par défaut
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

EMAIL_FILE_PATH = BASE_DIR / "sent_emails"  # Dossier où seront stockés les mails


import ssl, certifi

ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())
