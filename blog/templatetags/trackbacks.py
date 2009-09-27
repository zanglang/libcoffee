from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from trackback.models import Trackback

register = template.Library()

class TrackbackUrlNode(template.Node):
    def __init__(self, obj):
        self.obj_name = obj

    def render(self, context):
        self.object = template.resolve_variable(self.obj_name, context)
        self.object.ct = ContentType.objects.get_for_model(self.object).pk
        return 'http://%s%s' % (Site.objects.get_current().domain, \
							reverse('receive_trackback', kwargs = {
									'content_type_id': self.object.ct,
									'object_id': self.object.pk}))

@register.tag        
def get_trackback_url(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise template.TemplateSyntaxError, "get_trackback_rdf_for tag takes exactly one argument"
    return TrackbackUrlNode(bits[1])


class TrackbacksNode(template.Node):
    def __init__(self, obj, varname):
        self.varname = varname
        self.obj_name = obj
    
    def render(self, context):
        self.object = template.resolve_variable(self.obj_name, context)
        context[self.varname] = Trackback.objects.filter(
				content_type = ContentType.objects.get_for_model(self.object),
				object_id=self.object.pk).filter(is_public=True)
        return ''

@register.tag
def get_trackbacks_for(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError, "get_trackbacks tag takes exactly three arguments"
    if bits[2] != 'as':
        raise template.TemplateSyntaxError, "second argument to get_trackbacks tag must be 'as'"
    return TrackbacksNode(bits[1], bits[3])