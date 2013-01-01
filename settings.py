"""
settings.py

Configuration for Flask app

Important: Place your keys in the secret_keys.py module, 
           which should be kept out of version control.

"""

import os


# Auto-set debug mode based on App Engine dev environ
DEBUG_MODE = False
if 'SERVER_SOFTWARE' in os.environ and \
	os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    DEBUG_MODE = True
DEBUG = DEBUG_MODE

# Caching
CACHE_TYPE = 'gaememcached'

# Set secret keys for CSRF protection
from secret_keys import CSRF_SECRET_KEY as SECRET_KEY  # @UnusedImport
from secret_keys import SESSION_KEY as CSRF_SESSION_KEY  # @UnusedImport
CSRF_ENABLED = True

