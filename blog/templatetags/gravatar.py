# From: http://code.google.com/p/django-gravatar/

from django import template
from django.core.cache import cache as memcache
from django.utils.html import escape
from django.utils.hashcompat import md5_constructor

register = template.Library()


@register.simple_tag
def gravatar_for_email(email, size=80):
	hash = memcache.get('gravatar' + email)
	if not hash:
		hash = md5_constructor(email).hexdigest()
		memcache.set('gravatar' + email, hash)
	return "http://www.gravatar.com/avatar/%s?s=%d&d=identicon" % (hash, size)

@register.simple_tag
def gravatar_img_for_email(email, size=80):
	url = gravatar_for_email(email, size)
	return """<img class="gravatar" src="%s" height="%s" width="%s"/>""" \
		% (escape(url), size, size)
