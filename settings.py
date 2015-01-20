# Django settings for rmdb project.
import os


T47_DEV = 1
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
if T47_DEV:
    MEDIA_ROOT = '/MATLAB_code/rmdb/design'
else:
    MEDIA_ROOT = '/home/daslab/rdat/rmdb/design'
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Pablo Cordero', 'tsuname@stanford.edu'),
    ('Siqi Tian', 't47@stanford.edu'),
)
MANAGERS = ADMINS
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

SUBMISSION_NOTIFY_EMAIL = 't47@stanford.edu'
SUBMISSION_HOST_EMAIL = 'stanfordrmdb@gmail.com'
SUBMISSION_HOST_PWD = 'daslab4ever'
SUBMISSION_HOST_SMTP = 'smtp.gmail.com:587'

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

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

USE_I18N = True
USE_L10N = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
#    'cms.middleware.page.CurrentPageMiddleware',
#    'cms.middleware.user.CurrentUserMiddleware',
#    'cms.middleware.multilingual.MultilingualURLMiddleware'
)

ROOT_URLCONF = 'rmdb.urls'

TEMPLATE_DIRS = (
    MEDIA_ROOT,
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.flatpages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
#    'cms',
#    'cms.plugins.text',
#    'cms.plugins.picture',
#    'cms.plugins.link',
#    'cms.plugins.file',
#    'cms.plugins.snippet',
#    'cms.plugins.googlemap',
#    'mptt',
#    'publisher'
    'rmdb.repository',
    'rmdb.structureserver',
    # 'south',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
#    "cms.context_processors.media",
    "rmdb.repository.context_processors.include_login_form"
)
gettext = lambda s: s
CMS_TEMPLATES = (
    ('default.html', gettext('default')),
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'xas()lrqak#89v7k+di9!infy&+1+jk0-zzzr__y#0agy^c1n@'
