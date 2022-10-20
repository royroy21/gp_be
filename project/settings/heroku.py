from os import environ
import dj_database_url
from .base import *  # noqa

SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = [
    "gigpig-backend.herokuapp.com",
]

# Redirect to HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

# Database
DATABASES["default"] = dj_database_url.config()
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

# Build packs for GDAL: https://elements.heroku.com/buildpacks/daegun/heroku-buildpack-geodjango
GEOS_LIBRARY_PATH = environ.get('GEOS_LIBRARY_PATH')
GDAL_LIBRARY_PATH = environ.get('GDAL_LIBRARY_PATH')

DEBUG = False
