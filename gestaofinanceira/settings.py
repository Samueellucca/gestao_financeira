import os
from pathlib import Path
import dj_database_url

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY vinda do ambiente, com fallback só para desenvolvimento
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-fallback-key-for-development"
)

# Em produção (Render) DEBUG fica False automaticamente
DEBUG = "RENDER" not in os.environ

ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Aplicações instaladas
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # WhiteNoise para servir estáticos em produção
    "whitenoise.runserver_nostatic",

    # Outras apps
    "django.contrib.humanize",
    "financeiro",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gestaofinanceira.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # templates globais
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

WSGI_APPLICATION = "gestaofinanceira.wsgi.application"
ASGI_APPLICATION = "gestaofinanceira.asgi.application"

# Database
# Em produção (Render): usa Postgres via DATABASE_URL
# Em desenvolvimento: usa SQLite local
if "RENDER" in os.environ:
    DATABASES = {
        "default": dj_database_url.config(
            # Render recomenda isso para conexões persistentes
            conn_max_age=600,
            # Normalmente True para Postgres do Render; se der erro de SSL, mude para False
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Validação de senha
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

# Internacionalização
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Arquivos estáticos
STATIC_URL = "/static/"

# Pasta "static" na raiz do projeto para arquivos globais
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Em produção, o WhiteNoise usa esta pasta
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Armazenamento para WhiteNoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# URLs de login/logout e redirect
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "financeiro:dashboard"
LOGOUT_REDIRECT_URL = "login"

# Tipo padrão de chave primária
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
