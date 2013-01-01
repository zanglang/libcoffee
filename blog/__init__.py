"""
Blog blueprint

"""

from flask import Blueprint
app = Blueprint('blog', __name__, template_folder='templates')

from werkzeug.contrib.cache import GAEMemcachedCache
cache = GAEMemcachedCache()

import markup
import views
