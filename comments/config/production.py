#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Production Configurations
'''

from __future__ import absolute_import, unicode_literals
from os.path import join
from .common import *  # noqa


# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env("DJANGO_SECRET_KEY")

# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# django-secure
INSTALLED_APPS += ("djangosecure", )
SECURITY_MIDDLEWARE = (
    'djangosecure.middleware.SecurityMiddleware',
)

# Make sure djangosecure.middleware.SecurityMiddleware is listed first
MIDDLEWARE_CLASSES = SECURITY_MIDDLEWARE + MIDDLEWARE_CLASSES

# set this to 60 seconds and then to 518400 when you can prove it works
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_FRAME_DENY = env.bool("DJANGO_SECURE_FRAME_DENY", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)

# SITE CONFIGURATION
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])

# STATIC FILES
STATIC_ROOT = str(ROOT_DIR.path('static'))
MEDIA_ROOT = str(ROOT_DIR.path('media'))
TEMP_DIR = str(ROOT_DIR.path('temp'))
STATICFILES_DIRS = (
    str(BASE_DIR.path('static/bin')),
)

# EMAIL
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL")
EMAIL_HOST = env("DJANGO_EMAIL_HOST")
EMAIL_PORT = env.int("DJANGO_EMAIL_PORT")
EMAIL_HOST_USER = env("DJANGO_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env.bool("DJANGO_EMAIL_USE_TLS")


# CACHING
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

