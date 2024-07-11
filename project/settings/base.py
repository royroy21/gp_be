"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path
from typing import List

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS: List[str]


# Application definition
LOCAL_APPS = [
    "project.audio",
    "project.chat",
    "project.country",
    "project.custom_user",
    "project.genre",
    "project.gig",
    # HTTP, HTTP2 and WebSocket protocol server.
    # Takes over from WSGI for development server.
    "daphne",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "django_extensions",
    "rest_framework",
    "rest_framework_simplejwt",
    "whitenoise.runserver_nostatic",
]

INSTALLED_APPS = (
    LOCAL_APPS  # Order matters for template path resolution
    + [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.gis",
        "django.contrib.sites",
    ]
    + THIRD_PARTY_APPS
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

ASGI_APPLICATION = "project.core.asgi.application"
WSGI_APPLICATION = "project.core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "level": "WARNING",
            "handlers": ["console"],
        },
        "daphne": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
        },
        "project": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = "en-uk"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = os.path.join(BASE_DIR, "project/static")
STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache. Using django-redis https://github.com/jazzband/django-redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}


# User
AUTH_USER_MODEL = "custom_user.User"


# Authentications backend
AUTHENTICATION_BACKENDS = {
    "django.contrib.auth.backends.ModelBackend",
    "middleware.email_password.EmailPasswordBackend",
}

# DRF
PAGE_SIZE = 25
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": (
        "project.core.drf.pagination.DefaultPageNumberPagination"
    ),
    "PAGE_SIZE": PAGE_SIZE,
    "SEARCH_PARAM": "search",
    "ORDERING_PARAM": "order_by",
}

# DRF simple JWT
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=360),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("JWT",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "TOKEN_OBTAIN_SERIALIZER": (
        "custom_token.serializers.CustomTokenObtainPairSerializer"
    ),
}


# Celery settings
CELERY_BROKER_URL = os.environ["CELERY_BROKER_URL"]


# Push notifications
PUSH_NOTIFICATIONS_ENABLED = False


# Thumbnails
CREATE_THUMBNAILS_ENABLED = False


# Media
MEDIA_ROOT = os.path.join(BASE_DIR, "project/media")
MEDIA_URL = "/media/"


# Sites.
# Used for accessing site domain names when request object is not available
# https://docs.djangoproject.com/en/4.2/ref/contrib/sites/
SITE_ID = 1  # Corresponds to the ID of the site in the database.
# TODO - Add another site with the correct domain name for production
SITE_SCHEME = "http"


# Search stop words for use in Postgres free text search.
ENGLISH_STOP_WORDS = [
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "such",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "to",
    "was",
    "will",
    "with",
]
