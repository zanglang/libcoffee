"""
Blog blueprint

"""

from flask import Blueprint
app = Blueprint('blog', __name__, template_folder='templates')

import markup
import views
