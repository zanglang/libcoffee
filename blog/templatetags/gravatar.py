# From: http://code.google.com/p/django-gravatar/

from django import template
from django.utils.html import escape
from django.utils.hashcompat import md5_constructor
from google.appengine.api import memcache

register = template.Library()

@register.simple_tag
def gravatar_for_email(email, size=80):
	data = memcache.get(email, namespace='gravatar')
	if data is None:
		data = md5_constructor(email).hexdigest()
		memcache.add(email, data, namespace='gravatar')
	return "http://www.gravatar.com/avatar/%s?s=%d&d=identicon" % (data, size)

@register.simple_tag
def gravatar_img_for_email(email, size=80):
	url = gravatar_for_email(email, size)
	return """<img class="gravatar" src="%s" height="%s" width="%s"/>""" \
		% (escape(url), size, size)
