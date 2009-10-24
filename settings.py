# -*- coding: utf-8 -*-
from ragendja.settings_pre import *

# Increase this when you update your media on the production site, so users
# don't have to refresh their cache. By setting this your MEDIA_URL
# automatically becomes /media/MEDIA_VERSION/
MEDIA_VERSION = 1

import os.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

#DEBUG = False
#TEMPLATE_DEBUG = DEBUG

SITE_ID = ''

DATABASE_ENGINE = 'appengine'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
# TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# ENABLE_PROFILER = True
# ONLY_FORCED_PROFILE = True
# PROFILE_PERCENTAGE = 25
# SORT_PROFILE_RESULTS_BY = 'cumulative' # default is 'time'
# Profile only datastore calls
# PROFILE_PATTERN = 'ext.db..+\((?:get|get_by_key_name|fetch|count|put)\)'

# Enable I18N and set default language to 'en'
USE_I18N = True

# Restrict supported languages (and JS media generation)
LANGUAGES = (
	('en', 'English'),
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
#MEDIA_URL = ''

# By hosting media on a different domain we can get a speedup (more parallel
# browser connections).
#if on_production_server or not have_appserver:
#	MEDIA_URL = 'http://media.mydomain.com/media/%d/'

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
	'libcoffee-print.css': ( 'global/blueprintcss/print.css',),
	'ie.css': ( 'global/blueprintcss/ie.css',)
}

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/admin-media/'
#ADMIN_MEDIA_PREFIX = '/generated_media/media/1/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

MIDDLEWARE_CLASSES = (
	'ragendja.middleware.ErrorMiddleware',
	'django.middleware.cache.UpdateCacheMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	# Django authentication
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	# Google authentication
	#'ragendja.auth.middleware.GoogleAuthenticationMiddleware',
	# Hybrid Django/Google authentication
	#'ragendja.auth.middleware.HybridAuthenticationMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
	'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
	'trackback.middleware.PingbackUrlInjectionMiddleware',
	'ragendja.sites.dynamicsite.DynamicSiteIDMiddleware',
	'django.middleware.cache.FetchFromCacheMiddleware',
)

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.join(PROJECT_ROOT, "templates"),
)

# Google authentication
#AUTH_USER_MODULE = 'ragendja.auth.google_models'
#AUTH_ADMIN_MODULE = 'ragendja.auth.google_admin'
# Hybrid Django/Google authentication
#AUTH_USER_MODULE = 'ragendja.auth.hybrid_models'

LOGIN_URL = '/auth/login/'
LOGOUT_URL = '/auth/logout/'
LOGIN_REDIRECT_URL = '/'

# Add the lib/ directory to the path for external apps
import sys
sys.path.insert(0, os.path.join(PROJECT_ROOT, "lib"))

INSTALLED_APPS = (
	# System apps
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.flatpages',
	'django.contrib.humanize',
	'django.contrib.markup',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.sitemaps',
	
	# External apps
	'django_openid_auth',
	
	# App engine
	'appenginepatcher',
	'ragendja',
	'mediautils',
	
	# Local apps
	'auth',
	'blog',
	'trackback',
	'comments',
)

# List apps which should be left out from app settings and urlsauto loading
IGNORE_APP_SETTINGS = IGNORE_APP_URLSAUTO = (
	'django.contrib.admin',
	'django.contrib.auth',
	'trackback',
	'comments',
)

# Remote access to production server (e.g., via manage.py shell --remote)
DATABASE_OPTIONS = {
	# Override remoteapi handler's path (default: '/remote_api').
	# This is a good idea, so you make it not too easy for hackers. ;)
	# Don't forget to also update your app.yaml!
	'remote_url': '/remote_api',

	# !!!Normally, the following settings should not be used!!!

	# Always use remoteapi (no need to add manage.py --remote option)
	'use_remote': False,

	# Change appid for remote connection (by default it's the same as in
	# your app.yaml)
	'remote_id': 'libcoffeeblog',

	# Change domain (default: <remoteid>.appspot.com)
	'remote_host': 'www.libcoffee.net',
}

COMMENTS_APP = 'djangoblog.comments'
AKISMET_API_KEY = '' # Your key here
TYPEPAD_API_KEY = '' # Your key here

OPENID_CREATE_USERS = False

FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''

TWITTER_USERNAME = ''

HUBBUB_URL = 'http://pubsubhubbub.appspot.com/'

TEMPLATE_STRING_IF_INVALID = ''
TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.request',
	'blog.context_processors.now',
)

if DEBUG: CACHE_BACKEND = 'dummy:///'
#CACHE_BACKEND = 'memcached://?timeout=0'

ADMIN_EMAIL = ''

try:
	from local_settings import *
except ImportError:
	pass
   
from ragendja.settings_post import *