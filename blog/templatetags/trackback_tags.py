from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.views.decorators.cache import cache_page
from django.core.cache import cache as memcache
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from trackback.models import Trackback
from keycache import serialize_models, deserialize_models

register = template.Library()

class TrackbackUrlNode(template.Node):
	def __init__(self, obj):
		self.obj_name = obj

	def render(self, context):
		self.object = template.resolve_variable(self.obj_name, context)
		return 'http://%s%s' % (Site.objects.get_current().domain, \
							reverse('receive_trackback', kwargs = {
									'object_id': self.object.pk}))

@register.tag		
def get_trackback_url(parser, token):
	bits = token.contents.split()
	if len(bits) != 2:
		raise template.TemplateSyntaxError, "get_trackback_url tag takes exactly one argument"
	return TrackbackUrlNode(bits[1])


class TrackbacksNode(template.Node):
	def __init__(self, obj, varname):
		self.varname = varname
		self.obj_name = obj
	
	def render(self, context):
		self.object = template.resolve_variable(self.obj_name, context)
		trackbacks = deserialize_models(memcache.get('trackback-for-' + self.object.pk))
		if trackbacks is None:
			trackbacks = Trackback.all() \
					.filter('content_object =', self.object) \
					.filter('is_public =', True)
			memcache.set('trackback-for-' + self.object.pk, trackbacks)
		context[self.varname] = trackbacks
		return ''

@register.tag
def get_trackbacks_for(parser, token):
	bits = token.contents.split()
	if len(bits) != 4:
		raise template.TemplateSyntaxError, "get_trackbacks tag takes exactly three arguments"
	if bits[2] != 'as':
		raise template.TemplateSyntaxError, "second argument to get_trackbacks tag must be 'as'"
	return TrackbacksNode(bits[1], bits[3])
   
   
class TrackbackRdfNode(template.Node):
	def __init__(self, obj):
		self.obj_name = obj
				
	def render(self, context):
		self.object = template.resolve_variable(self.obj_name, context)
		return cache_page(render_to_string('trackback/rdf_include.xml',
				{'object': self.object, 'SITE_URL': "http://%s" % Site.objects.get_current().domain}),
				key_prefix='trackback-rdf-' + self.object.pk)

@register.tag
def get_trackback_rdf_for(parser, token):
	bits = token.contents.split()
	if len(bits) != 2:
		raise template.TemplateSyntaxError, "get_trackback_rdf_for tag takes exactly one argument"
	return TrackbackRdfNode(bits[1])
   

class PingbackUrlNode(template.Node):
	def __init__(self):
		self.site = Site.objects.get_current()
		
	def render(self, context):
		return u"http://%s%s" % (self.site.domain, reverse('receive_pingback'))
		
@register.tag
def get_pingback_url(parser, token):
	return PingbackUrlNode()