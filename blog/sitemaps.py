from django.conf import settings
from django.contrib.sitemaps import Sitemap, ping_google
from django.db.models.signals import post_save
from blog.models import Post
import logging

class BlogSitemap(Sitemap):
	changefreq = 'never'
	priority = 0.5
	
	def items(self):
		return Post.objects_published()
	
	def lastmod(self, obj):
		return obj.updated_at


def send_sitemap(sender, sitemap_url=None, **kwargs):
	if settings.DEBUG: return
	logging.debug('sending sitemap')
	URLS = (
		('google', 'http://www.google.com/webmasters/tools/ping'),
		('yahoo', 'http://search.yahooapis.com/SiteExplorerService/V1/ping'),
		('ask', 'http://submissions.ask.com/ping'),
		('live', 'http://webmaster.live.com/ping.aspx'),
	)
	for (site, url) in URLS:
		try:
			ping_google(sitemap_url=sitemap_url, ping_url=url)
			logging.info('pinging %s successful' % url)
		except:
			pass # log failure if needed
	return

post_save.connect(send_sitemap, sender=Post, dispatch_uid='send-sitemap')