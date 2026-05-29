from .base import *
import dj_database_url
from decouple import config
import os

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

database_url = os.environ.get('DATABASE_URL') or config('DATABASE_URL', default='')

if not database_url:
    raise Exception("DATABASE_URL environment variable is not set")

DATABASES = {
    'default': dj_database_url.parse(database_url, conn_max_age=600)
}


MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CORS_ALLOW_CREDENTIALS = True

SECRET_KEY = config('SECRET_KEY')

WHITENOISE_ROOT = BASE_DIR / 'frontend' / 'dist'
TEMPLATES[0]['DIRS'] = [BASE_DIR / 'frontend' / 'dist']