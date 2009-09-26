# From: http://code.google.com/p/django-gravatar/

from django import template
from django.utils.html import escape
from django.conf import settings
from django.utils.hashcompat import md5_constructor

import urllib

register = template.Library()

def gravatar_for_email(email, size=80):
    return "http://www.gravatar.com/avatar/%s?s=%d&d=identicon" % \
    		(md5_constructor(email).hexdigest(), size)

def gravatar_img_for_email(email, size=80):
    url = gravatar_for_email(email, size)
    return """<img class="gravatar" src="%s" height="%s" width="%s"/>""" \
    		% (escape(url), size, size)

register.simple_tag(gravatar_for_email)
register.simple_tag(gravatar_img_for_email)
