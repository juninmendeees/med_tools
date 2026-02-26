
import os
from pathlib import Path

import whitenoise
from django.conf.global_settings import EMAIL_BACKEND

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gd%!pc$^e-@j1i#$uw-e8$x&xgtfoasvsdnf7ziaarxkf5^4@)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['undefined-thornily-laine.ngrok-free.dev', '127.0.0.1', 'localhost']

# 2. Autoriza o domínio para verificações de segurança CSRF (Crucial para o Ngrok)
CSRF_TRUSTED_ORIGINS = [
    'https://undefined-thornily-laine.ngrok-free.dev'
]


# Application definition

INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'core',
    'stdimage',
]

# Essencial para o Allauth saber qual site usar
SITE_ID = 1

SOCIALACCOUNT_LOGIN_ON_GET = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
   # 'whitenoise.middleware.WhiteNoiseMiddleware', # Necessário apenas para publicação em produção
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'Django1.urls'
SILENCED_SYSTEM_CHECKS = ["models.W036"]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'Django1.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'medtools',
        'USER': 'root',
        'PASSWORD': 'admin',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

#CONFIGURAÇÕES DE EMAIL

# Bloqueia login sem validar e-mail
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_CONFIRM_EMAIL_ON_GET = False       # Valida ao clicar no link
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_ADAPTER = 'core.adapter.CustomAccountAdapter'

# Para testar sem servidor de e-mail real agora:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Impede que o Django quebre as linhas do e-mail no console
EMAIL_PAGE_WIDTH = 999

# Configuração de email de produção
#EMAIL_HOST  = 'localhost'
#EMAIL_HOST_USER= 'no-reply@medtools.com.br'
#EMAIL_HOST_PASSWORD 'sua senha'
#EMAIL_PORT= 587
#EMAIL_USE_TLS = True


LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'dashboard' # Para onde o usuário vai após logar
LOGOUT_REDIRECT_URL = 'account_login' # Para onde o usuário vai após deslogar

AUTH_USER_MODEL = 'core.Usuario'

#CONFIGURAÇÕES DE PAGAMENTO
MERCADO_PAGO_ACCESS_TOKEN = 'APP_USR-1721733035858480-012708-21561ebffc09453ec73c27d7c7a579f0-263069598'

# URL para acessar os arquivos via navegador
MEDIA_URL = '/media/'

# Caminho no servidor onde os arquivos serão salvos
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')