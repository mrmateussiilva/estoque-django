import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "change-this-secret-key-in-production-with-at-least-50-characters",
)
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,.vercel.app").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "accounts",
    "dashboard",
    "inventory",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middleware.CompanyContextMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.company_context",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

VERCEL = os.getenv("VERCEL", "false").lower() == "true"
DOCKER = os.getenv("DOCKER", "false").lower() == "true"

if os.getenv("DATABASE_URL"):
    parsed_db_url = urlparse(os.getenv("DATABASE_URL"))
    if parsed_db_url.scheme == "mysql":
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": parsed_db_url.path.lstrip("/"),
                "USER": parsed_db_url.username,
                "PASSWORD": parsed_db_url.password,
                "HOST": parsed_db_url.hostname,
                "PORT": parsed_db_url.port or 3306,
                "OPTIONS": {
                    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                    "charset": "utf8mb4",
                },
            }
        }
    else:
        db_engine_map = {
            "postgres": "django.db.backends.postgresql",
            "postgresql": "django.db.backends.postgresql",
        }
        DATABASES = {
            "default": {
                "ENGINE": db_engine_map.get(
                    parsed_db_url.scheme, "django.db.backends.postgresql"
                ),
                "NAME": parsed_db_url.path.lstrip("/"),
                "USER": parsed_db_url.username,
                "PASSWORD": parsed_db_url.password,
                "HOST": parsed_db_url.hostname,
                "PORT": parsed_db_url.port or "",
                "CONN_MAX_AGE": 600,
                "OPTIONS": {"sslmode": "require"} if not DEBUG else {},
            }
        }
elif os.getenv("MYSQL_HOST"):
    db_options = {
        "init_command": "SET sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'",
        "charset": "utf8mb4",
        "isolation_level": "read committed",
    }
    if DOCKER:
        db_options["host"] = os.getenv("MYSQL_HOST", "host.docker.internal")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("MYSQL_NAME", "estoquefb"),
            "USER": os.getenv("MYSQL_USER", "mateus1"),
            "PASSWORD": os.getenv("MYSQL_PASSWORD", ""),
            "HOST": os.getenv("MYSQL_HOST", "estoquefb.mysql.uhserver.com"),
            "PORT": int(os.getenv("MYSQL_PORT", 3306)),
            "OPTIONS": db_options,
            "CONN_MAX_AGE": 60,
        }
    }
elif VERCEL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "/tmp/db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("DATABASE_NAME", "db.sqlite3"),
        }
    }

if VERCEL:
    ALLOWED_HOSTS = [
        os.getenv("VERCEL_URL", "localhost"),
        f"https://{os.getenv('VERCEL_URL')}"
        if os.getenv("VERCEL_URL")
        else "localhost",
    ]

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

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"

HOST = os.getenv("HOST", "0.0.0.0")
HOST_PORT = int(os.getenv("HOST_PORT", "8000"))

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

DOMAIN = os.getenv("DOMAIN", "")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
