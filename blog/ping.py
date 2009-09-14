from trackback import signals
from trackback.utils import handlers
from django.contrib.sites.models import Site
from django.contrib.sitemaps import ping_google
from blog.models import Post
import xmlrpclib

signals.send_pingback.connect(handlers.send_pingback, sender = Post)
signals.send_trackback.connect(handlers.send_trackback, sender = Post)


def send_trackback(object):
	signals.send_pingback.send(sender = object.__class__, instance = object)
	signals.send_trackback.send(sender = object.__class__, instance = object)


def send_ping(object):
	site = Site.objects.get_current()
	URLS = (
		('technorati', 'http://rpc.technorati.com/rpc/ping'),
		('google', 'http://blogsearch.google.com/ping/RPC2'),
	)
	for (site, urls) in URLS:
		try:
			rpc = xmlrpclib.Server(url);
			rpc.weblogUpdates.ping(site.name, site.domain)
		except:
			pass
	return
	

def send_sitemap(sitemap_url=None):
	URLS = (
		('google', 'http://www.google.com/webmasters/tools/ping'),
		('yahoo', 'http://search.yahooapis.com/SiteExplorerService/V1/ping'),
		('ask', 'http://submissions.ask.com/ping'),
		('live', 'http://webmaster.live.com/ping.aspx'),
	)
	for (site, url) in URLS:
		try:
			ping_google(sitemap_url=sitemap_url, ping_url=url)
		except:
			pass # log failure if needed
	return