"""
Django settings for repository project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from t47_dev import *


# SECURITY WARNING: don't run with debug turned on in production!
if T47_DEV:
    MEDIA_ROOT = '/MATLAB_code/RMDB_Server'
    # ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    MEDIA_ROOT = '/home/daslab/rdat/rmdb'
    # ALLOWED_HOSTS = ['rmdb.stanford.edu']

DEBUG = 0 #T47_DEV
TEMPLATE_DEBUG = DEBUG

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/media/admin/'

ADMINS = (
    ('Siqi Tian', 't47@stanford.edu'),
    # ('Pablo Cordero', 'tsuname@stanford.edu'),
)
MANAGERS = ADMINS
EMAIL_NOTIFY = ADMINS[0][1]
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'stanfordrmdb@gmail.com'
EMAIL_HOST_PASSWORD = 'daslab4ever'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.humanize',

    'repository',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",

    "repository.helper.helper_register.include_login_form"
)
gettext = lambda s: s
CMS_TEMPLATES = (
    ('default.html', gettext('default')),
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
TEMPLATE_DIRS = (
    MEDIA_ROOT,
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

ROOT_URLCONF = 'repository.urls'
WSGI_APPLICATION = 'repository.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'rmdb',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'beckman',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"

class SYS_PATH:
    def __init__(self):
        self.HTML_PATH = {
            'index': 'media/html/index.html',
            'browse': 'media/html/browse.html',
            'detail': 'media/html/detail.html',

            'about': 'media/html/about.html',
            'license': 'media/html/license.html',
            'history': 'media/html/history.html',

            'specs': 'media/html/specs.html',
            'validate': 'media/html/validate.html',
            'upload': 'media/html/submit.html',

            'predict': 'media/html/predict.html',
            'predict_res': 'media/html/predict_results.html',
            'repos': 'media/html/tools.html',
            'license_mapseeker': 'media/html/tools_mapseeker_license.html',
            'link_mapseeker': 'media/html/tools_mapseeker_download.html',
            'tt_predict': 'media/html/tutorial_predict.html',
            'tt_api': 'media/html/tutorial_api.html',
            'tt_rdatkit': 'media/html/tutorial_rdatkit.html',
            'tt_hitrace': 'media/html/tutorial_hitrace.html',
            'tt_mapseeker': 'media/html/tutorial_mapseeker.html',

            'search_res': 'media/html/search_results.html',
            'adv_search': 'media/html/search_advanced.html',
            'adv_search_res': 'media/html/search_advanced_results.html',

            'register': 'media/html/register.html',

            '404': 'media/html/_404.html',
            '500': 'media/html/_500.html',
        }

        self.DATA_DIR = {
            'CONSTRUCT_IMG_DIR': MEDIA_ROOT + '/data/construct_img/',
            'CONSTRUCT_THMB_DIR': MEDIA_ROOT + '/data/thumbs/',
            'RDAT_FILE_DIR': MEDIA_ROOT + '/data/files/',
            'ISATAB_FILE_DIR': MEDIA_ROOT + '/data/files/',
            'TMPDIR': MEDIA_ROOT + '/temp/',

        }
PATH = SYS_PATH()


# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '!9g7%50idfw-=(ii6mr3kmt@a*&-b%32q^!a!tkrwt%%+p^iu#'
SECRET_KEY = 'xas()lrqak#89v7k+di9!infy&+1+jk0-zzzr__y#0agy^c1n@'

