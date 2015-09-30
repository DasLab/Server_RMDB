"""
Django settings for repository project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import environ
import os
import simplejson

from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from config.t47_dev import *
# SECURITY WARNING: don't run with debug turned on in production!
TEMPLATE_DEBUG = DEBUG = T47_DEV

root = environ.Path(os.path.dirname(os.path.dirname(__file__)))
MEDIA_ROOT = root()
# MEDIA_ROOT = os.path.join(os.path.abspath("."))
FILEMANAGER_STATIC_ROOT = root('media/admin') + '/'

env = environ.Env(DEBUG=DEBUG,) # set default values and casting
environ.Env.read_env('%s/config/env.conf' % MEDIA_ROOT) # reading .env 

ALLOWED_HOSTS = env('ALLOWED_HOSTS')
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = '' # MEDIA_ROOT + '/media/'
STATICFILES_DIRS = (root('data'), root('media'))

env_oauth = simplejson.load(open('%s/config/oauth.conf' % MEDIA_ROOT))
AWS = env_oauth['AWS']
GA = env_oauth['GA']
DRIVE = env_oauth['DRIVE']
GIT = env_oauth['GIT']
APACHE_ROOT = '/var/www'


ADMINS = (
    ('Siqi Tian', 't47@stanford.edu'),
    # ('Pablo Cordero', 'tsuname@stanford.edu'),
)
EMAIL_NOTIFY = ADMINS[0][1]
(EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_USE_TLS, EMAIL_PORT, EMAIL_HOST) = [v for k, v in env.email_url().items() if k in ['EMAIL_HOST_PASSWORD', 'EMAIL_HOST_USER', 'EMAIL_USE_TLS', 'EMAIL_PORT', 'EMAIL_HOST']]
EMAIL_SUBJECT_PREFIX = '[Django] {daslab.stanford.edu}'

ROOT_URLCONF = 'repository.urls'
WSGI_APPLICATION = 'repository.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': env.db_url(),
}
LOGIN_URL = '/login/'

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
from repository.path import *
PATH = SYS_PATH()


env_cron = simplejson.load(open('%s/config/cron.conf' % MEDIA_ROOT))
#     os.getlogin()
CRONJOBS = env_cron['CRONJOBS'][0:2]
CRONTAB_LOCK_JOBS = env_cron['CRONTAB_LOCK_JOBS']
KEEP_BACKUP = env_cron['KEEP_BACKUP']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_crontab.crontab': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

class ExceptionUserInfoMiddleware(object):
    def process_exception(self, request, exception):
        try:
            if request.user.is_authenticated():
                request.META['USERNAME'] = str(request.user.username)
                request.META['USER_EMAIL'] = str(request.user.email)
        except:
            pass


# Application definition
INSTALLED_APPS = (
    'django_crontab',
    'filemanager',
    'adminplus',
    'suit',
    # 'django.contrib.admin',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
    'repository.settings.ExceptionUserInfoMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
TEMPLATE_DIRS = (
    root('media'),
    root(),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


SUIT_CONFIG = {
    # header
    'ADMIN_NAME': 'RMDB',
    'HEADER_DATE_FORMAT': 'F d, Y (l)',
    'HEADER_TIME_FORMAT': 'h:i a (e)',

    # forms
    'SHOW_REQUIRED_ASTERISK': True,  # Default True
    'CONFIRM_UNSAVED_CHANGES': True, # Default True

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    'MENU_OPEN_FIRST_CHILD': True, # Default True

    # misc
    'LIST_PER_PAGE': 25
}


# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')