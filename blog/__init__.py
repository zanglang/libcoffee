"""
Blog blueprint

"""

from flask import Blueprint

app = Blueprint('blog', __name__, template_folder='templates')

# Pull in URL dispatch routes
import views
