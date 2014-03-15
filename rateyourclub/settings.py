# Django settings for rateyourclub project.
from datetime import datetime
import os
import djcelery
from django.utils import timezone
djcelery.setup_loader()

DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEV_MODE = False

ROOTDIR = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
CONFIGURATION_YAML = os.path.join(ROOTDIR, 'config.yaml')

ADMINS = (
    ('Daniel Liu', 'hpec.liu@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = 'staticfiles'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'bkpyas1p_8r1gvc^np2k07!n*-p^6o$ltmn&amp;=o7eet_4hac0%v'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
    'hamlpy.template.loaders.HamlPyFilesystemLoader',
    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rateyourclub.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'rateyourclub.wsgi.application'

TEMPLATE_DIRS = (
    # ROOTDIR+'/templates/',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'south',
    'compressor',
    'rateyourclub',
    'clubreview',
    'registration',
    'selectable',
    'djcelery',
    'constance',
    'constance.backends.database',
    'djrill'

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

MANDRILL_API_KEY = "f3eZklctlBE786-dZQNKMQ"
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',

  )
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES['default'] =  dj_database_url.config()


# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# https://pypi.python.org/pypi/django-constance
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'FACEBOOK_APP_ID': ('APP_SECRET', 'Facebook app id used to retrieve facebook graph data'),
    'FACEBOOK_APP_SECRET_ID': ('APP_SECRET', 'Facebook app secret id used to retrireve facebook graph data'),
    'FACEBOOK_USER_ACCESS_TOKEN': ('USER_ACCESS_TOKEN', 'Used to retrieve group events'),
    'FACEBOOK_USER_ACCESS_TOKEN_EXPIRATION': (timezone.make_aware(datetime.now(), timezone.get_default_timezone()), 'Datetime that extended access token expire.'),
    'FACEBOOK_USER_EMAIL': ('test@example.com', 'Dummy user email to login to m.facebook.com and parse DOM for group ids'),
    'FACEBOOK_USER_PASSWORD': ('password', 'Dummy user password to login to m.facebook.com and parse DOM for group ids'),
}
if os.path.exists(os.path.normpath(os.path.join(os.path.dirname(__file__), 'local_settings.py'))):
  from local_settings import *

ACCOUNT_ACTIVATION_DAYS = 14

AUTH_USER_MODEL = 'registration.User'
LOGIN_URL = '/accounts/login/'

DEFAULT_FROM_EMAIL = 'noreply@calbeat.com'

# django celery
# http://docs.celeryproject.org/en/latest/getting-started/brokers/django.html#broker-django
BROKER_URL = 'django://'
INSTALLED_APPS += ('kombu.transport.django',)
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
