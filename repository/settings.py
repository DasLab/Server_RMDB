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
MEDIA_ROOT = BASE_DIR
# MEDIA_ROOT = os.path.join(os.path.abspath("."))

from django.utils.translation import ugettext_lazy as _

from t47_dev import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = T47_DEV
TEMPLATE_DEBUG = DEBUG

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_ROOT = MEDIA_ROOT + '/media/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

ADMINS = (
    ('Siqi Tian', 't47@stanford.edu'),
    # ('Pablo Cordero', 'tsuname@stanford.edu'),
)
MANAGERS = ADMINS
EMAIL_NOTIFY = ADMINS[0][1]
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'daslabsu@gmail.com'
EMAIL_HOST_PASSWORD = 'l4bd4s2014'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[Django] {rmdb.stanford.edu}'

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
TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', _('English')),
)
SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"

class SYS_PATH:
    def __init__(self):
        self.HTML_PATH = {
            'index': MEDIA_ROOT + '/media/html/index.html',
            'browse': MEDIA_ROOT + '/media/html/browse.html',
            'detail': MEDIA_ROOT + '/media/html/detail.html',

            'about': MEDIA_ROOT + '/media/html/about.html',
            'license': MEDIA_ROOT + '/media/html/license.html',
            'history': MEDIA_ROOT + '/media/html/history.html',

            'specs': MEDIA_ROOT + '/media/html/specs.html',
            'validate': MEDIA_ROOT + '/media/html/validate.html',
            'upload': MEDIA_ROOT + '/media/html/submit.html',

            'predict': MEDIA_ROOT + '/media/html/predict.html',
            'predict_res': MEDIA_ROOT + '/media/html/predict_results.html',
            'repos': MEDIA_ROOT + '/media/html/tools.html',
            'tools_license': MEDIA_ROOT + '/media/html/tools_license.html',
            'tools_download': MEDIA_ROOT + '/media/html/tools_download.html',
            'tutorial': MEDIA_ROOT + '/media/html/tutorial_xxx.html',

            'search_res': MEDIA_ROOT + '/media/html/search_results.html',
            'adv_search': MEDIA_ROOT + '/media/html/search_advanced.html',
            'adv_search_res': MEDIA_ROOT + '/media/html/search_advanced_results.html',

            'register': MEDIA_ROOT + '/media/html/register.html',

            '404': MEDIA_ROOT + '/media/html/_404.html',
            '500': MEDIA_ROOT + '/media/html/_500.html',
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

