# -*- coding: utf-8 -*-

# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import * #@UnusedWildImport
from djangoappengine.utils import on_production_server #@Reimport

import os, sys
BASEPATH = os.path.dirname(os.path.abspath(__file__))
LIBPATH = os.path.join(BASEPATH, "lib")
if not LIBPATH in sys.path:
	# Add the lib/ directory to the path for external apps
	sys.path.insert(0, LIBPATH)

TEMPLATE_DEBUG = DEBUG = not on_production_server

ADMINS = (
	("Jerry Chong", "zanglang@gmail.com"),
)

MANAGERS = ADMINS

# Activate django-dbindexer for the default databaset
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = { 'ENGINE': 'dbindexer', 'TARGET': 'native', 'HIGH_REPLICATION': True }
AUTOLOAD_SITECONF = 'indexes'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
# TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
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

# Add base media (jquery can be easily added via INSTALLED_APPS)
COMBINE_MEDIA = {
	#'combined-%(LANGUAGE_CODE)s.js': (
	'libcoffee.js': (
		# See documentation why site_data can be useful:
		# http://code.google.com/p/app-engine-patch/wiki/MediaGenerator
		#'.site_data.js',
	),
	#'combined-%(LANGUAGE_DIR)s.css': (
	'libcoffee.css': (
		'global/blueprintcss/reset.css',
		'global/blueprintcss/typography.css',
		'global/blueprintcss/forms.css',
		'global/blueprintcss/grid.css',
		'global/blueprintcss/plugins/buttons/screen.css',
		'global/blueprintcss/plugins/fancy-type/screen.css',
		'global/pygments.css',
		'global/screen.css',
	),
	'libcoffee-print.css': ('global/blueprintcss/print.css',),
	'ie.css': ('global/blueprintcss/ie.css',)
}

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# STATIC_ROOT = '/Library/Server/Web/Data/Sites/Default/static'
STATIC_ROOT = os.path.join(BASEPATH, "static").replace("\\", "/")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
	# Put strings here, like "/home/html/static" or "C:/www/django/static".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.abspath(os.path.join(BASEPATH, "static")),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	# 'django.contrib.staticfiles.finders.DefaultStorageFinder',
	# 'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/admin-media/'
#ADMIN_MEDIA_PREFIX = '/generated_media/media/1/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#   'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
# This loads the index definitions, so it has to come first
	'autoload.middleware.AutoloadMiddleware',
	'google.appengine.ext.appstats.recording.AppStatsDjangoMiddleware',
	'django.middleware.cache.UpdateCacheMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	#'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
	'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
	'trackback.middleware.PingbackUrlInjectionMiddleware',
	'django.middleware.cache.FetchFromCacheMiddleware',
	'debug_toolbar.middleware.DebugToolbarMiddleware'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.abspath(os.path.join(BASEPATH, "templates")),
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.request',
	'django.core.context_processors.static',
	'django.core.context_processors.tz',
	'django.contrib.auth.context_processors.auth',
	'django.contrib.messages.context_processors.messages',
	'blog.context_processors.now'
)

INSTALLED_APPS = (
	# System apps
	'django.contrib.admin',
	'django.contrib.admindocs',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.flatpages',
	'django.contrib.humanize',
	'django.contrib.markup',
	'django.contrib.messages',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.sitemaps',
	'django.contrib.staticfiles',

	# Django non-rel
	'djangotoolbox',
	'autoload',
	'dbindexer',

	# Local apps
	'blog',

	# djangoappengine should come last, so it can override a few manage.py commands
	'djangoappengine',
)

##########################################

LOGIN_URL = '/auth/login/'
LOGOUT_URL = '/auth/logout/'
LOGIN_REDIRECT_URL = '/'

COMMENTS_APP = 'djangoblog.comments'
AKISMET_API_KEY = '' # Your key here
TYPEPAD_API_KEY = '' # Your key here

OPENID_CREATE_USERS = False

FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''

TWITTER_USERNAME = ''

HUBBUB_URL = 'http://pubsubhubbub.appspot.com/'

TEMPLATE_STRING_IF_INVALID = ''


if DEBUG: CACHE_BACKEND = 'dummy:///'
#CACHE_BACKEND = 'memcached://?timeout=0'

ADMIN_EMAIL = ''

try:
	from local_settings import *  #@UnusedWildImport
except ImportError:
	pass
