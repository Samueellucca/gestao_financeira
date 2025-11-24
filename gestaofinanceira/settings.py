import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ATENÇÃO: A SECRET_KEY não deve ser mantida no código em produção.
# Considere usar variáveis de ambiente.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-for-development')

# ATENÇÃO: DEBUG = True não deve ser usado em produção.
# A variável 'RENDER' é definida automaticamente pelo ambiente do Render.
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',

    'django.contrib.humanize', # Para formatação de números (ex: 1.000,00)
    'financeiro',
]

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

ROOT_URLCONF = 'gestaofinanceira.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # opcional: global templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestaofinanceira.wsgi.application'
ASGI_APPLICATION = 'gestaofinanceira.asgi.application'

# Database
# Se estiver em produção (no Render), usa a DATABASE_URL. Senão, usa o SQLite local.
if 'RENDER' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}
    }

# Password validation
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
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Diretório onde o `collectstatic` irá procurar por arquivos estáticos adicionais.
# A pasta 'static' na raiz do projeto é um bom lugar para arquivos globais.
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Em produção, o WhiteNoise usará esta pasta para servir os arquivos.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Estratégia de armazenamento para o WhiteNoise.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Login e Redirecionamento
# URL para onde o usuário é redirecionado se não estiver logado.
LOGIN_URL = 'login'
# URL para onde o usuário é redirecionado após um login bem-sucedido.
LOGIN_REDIRECT_URL = 'financeiro:dashboard'
# URL para onde o usuário é redirecionado após o logout.
LOGOUT_REDIRECT_URL = 'login'

# Define o tipo de chave primária padrão para novos modelos/apps
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
