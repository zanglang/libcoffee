from django.conf import settings
from django.contrib.syndication.feeds import Feed
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from comments.models import Comment
from memoize import memoize

@memoize()
def get_comments():
	return Comment.objects_public() \
        	.order('-submit_date').fetch(40)
        	#.filter('site =', Site.objects.get_current())


class LatestCommentFeed(Feed):
    """Feed of latest comments on the current site."""

    def title(self):
        if not hasattr(self, '_site'):
            self._site = Site.objects.get_current()
        return _("%(site_name)s comments") % dict(site_name=self._site.name)

    def link(self):
        if not hasattr(self, '_site'):
            self._site = Site.objects.get_current()
        return "http://%s/" % (self._site.domain)

    def description(self):
        if not hasattr(self, '_site'):
            self._site = Site.objects.get_current()
        return _("Latest comments on %(site_name)s") % dict(site_name=self._site.name)

    def items(self):
        return get_comments() 
        
    def item_pubdate(self, item):
        return item.submit_date
       