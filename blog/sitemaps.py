from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sitemaps import Sitemap, ping_google
from django.db.models.signals import post_save
from blog.models import Post
from memoize import memoize
import logging


@memoize()
def get_posts():
	return Post.objects_published().order('-created_at').fetch(1000)

class BlogSitemap(Sitemap):
	changefreq = 'never'
	priority = 0.5

	def items(self):
		return get_posts()

	def lastmod(self, obj):
		return obj.updated_at


def send_sitemap(sender, sitemap_url=None, **kwargs):
	if settings.DEBUG: return
	if type(sender) is Post:
		if not sender.published or sender._was_published:
			return
	URLS = (
		('google', 'http://www.google.com/webmasters/tools/ping'),
		('yahoo', 'http://search.yahooapis.com/SiteExplorerService/V1/ping'),
		('ask', 'http://submissions.ask.com/ping'),
		('live', 'http://webmaster.live.com/ping.aspx'),
	)
	if not sitemap_url:
		sitemap_url = 'http://%s' % Site.objects.get_current().domain
	logging.debug('sending sitemap url %s' % sitemap_url)

	for (site, url) in URLS:
		try:
			ping_google(sitemap_url=sitemap_url, ping_url=url)
			logging.info('pinging %s (%s) successful' % (url, site))
		except:
			logging.warning('pinging %s (%s) failed' % (url, site))
	return


post_save.connect(send_sitemap, sender=Post, dispatch_uid='send-sitemap')
